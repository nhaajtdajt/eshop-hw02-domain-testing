// FR-03 API test runner (Domain Testing + BVA, API layer).
// Run from this folder:  node run_api_tests.js [expiry-issue|expiry-use]
// Requires backend running on :3000. Uses backend's sqlite3 only to RESET/SEED state
// (passwords, reset_token) and to read the DB for verification; test inputs go through HTTP.
const path = require("path");
const fs = require("fs");
const sqlite3 = require(path.resolve(__dirname, "../../../backend/node_modules/sqlite3"));
const DB = path.resolve(__dirname, "../../../backend/database.sqlite");
const API = "http://localhost:3000/api";
const A = "test@eshop.com", A_PW = "Test1234!";
const B = "userb@eshop.com", B_PW = "Userb123!";
const C = "userc@eshop.com", C_PW = "Userc123!"; // dedicated to the long-wait expiry test, untouched by resetState()
const db = new sqlite3.Database(DB);

const run = (sql, p = []) => new Promise((r, j) => db.run(sql, p, function (e) { e ? j(e) : r(this); }));
const get = (sql, p = []) => new Promise((r, j) => db.get(sql, p, (e, row) => (e ? j(e) : r(row))));
const post = async (p, body) => {
  try {
    const res = await fetch(API + p, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) });
    let data = null; const txt = await res.text(); try { data = JSON.parse(txt); } catch { data = txt.slice(0, 120); }
    return { status: res.status, data };
  } catch (e) { return { status: 0, data: String(e) }; }
};
const pw = async (email) => (await get("SELECT password FROM users WHERE email=?", [email]))?.password;
const resetState = async () => {
  await run("UPDATE users SET password=?, reset_token=NULL, login_attempts=0, locked_until=NULL WHERE email=?", [A_PW, A]);
  if (!(await get("SELECT id FROM users WHERE email=?", [B]))) await run("INSERT INTO users (name,email,password) VALUES (?,?,?)", ["User B", B, B_PW]);
  await run("UPDATE users SET password=?, reset_token=NULL WHERE email=?", [B_PW, B]);
};
const issue = async (email) => (await post("/forgot-password", { email })).data.resetToken;
const results = [];
const rec = (id, layer, expected, actual, pass, note = "") => {
  results.push({ id, layer, expected, actual, result: pass ? "Pass" : "Fail", note, at: new Date().toISOString() });
  console.log(`${pass ? "PASS" : "FAIL"} ${id} | ${actual}${note ? " | " + note : ""}`);
};

// Submit a reset and report whether the password changed.
async function tryReset(email, token, newPassword) {
  const before = await pw(email);
  const r = await post("/reset-password", { email, resetToken: token, newPassword });
  const after = await pw(email);
  return { r, changed: before !== after, before, after };
}
const rejected = (t) => t.r.status >= 400 && !t.changed;
const desc = (t) => `HTTP ${t.r.status}, password ${t.changed ? "CHANGED" : "unchanged"}`;

async function main() {
  const mode = process.argv[2];
  if (mode === "expiry-issue") {
    if (!(await get("SELECT id FROM users WHERE email=?", [C]))) await run("INSERT INTO users (name,email,password) VALUES (?,?,?)", ["User C", C, C_PW]);
    await run("UPDATE users SET password=?, reset_token=NULL WHERE email=?", [C_PW, C]); const x = await issue(C);
    fs.writeFileSync(path.join(__dirname, "expiry_token.json"), JSON.stringify({ x, issuedAt: Date.now() }));
    console.log("issued", x, new Date().toISOString()); db.close(); return;
  }
  if (mode === "expiry-use") {
    const { x, issuedAt } = JSON.parse(fs.readFileSync(path.join(__dirname, "expiry_token.json")));
    const mins = ((Date.now() - issuedAt) / 60000).toFixed(1);
    const t = await tryReset(C, x, "Newpass1!");
    rec("FR03-DT-15", "API", "OTP cũ phải bị từ chối (có thời hạn)", `after ${mins} min: ${desc(t)}`, rejected(t), "SRS không nêu thời hạn cụ thể; đây là kiểm tra khám phá");
    await run("UPDATE users SET password=?, reset_token=NULL WHERE email=?", [C_PW, C]); fs.writeFileSync(path.join(__dirname, "api_results_expiry.json"), JSON.stringify(results, null, 2)); db.close(); return;
  }

  await resetState();
  // ---- Step 1: forgot-password
  let r = await post("/forgot-password", { email: A });
  const tok = r.data.resetToken;
  rec("FR03-DT-01", "API", "Sinh OTP 6 chữ số", `HTTP ${r.status}, resetToken=${tok} (${String(tok).length} chữ số)`, r.status === 200 && /^\d{6}$/.test(String(tok)));
  const f = async (id, email, note) => {
    const x = await post("/forgot-password", { email });
    rec(id, "API", "Từ chối, không cấp OTP", `HTTP ${x.status} ${JSON.stringify(x.data).slice(0, 70)}`, x.status >= 400, note);
  };
  await f("FR03-DT-02", "", "");
  await f("FR03-DT-03", "testeshop.com", "Thông báo là 'User not found', không nêu sai định dạng");
  await f("FR03-DT-04", "nobody@eshop.com", "404 cho biết email không tồn tại (lộ danh sách email)");
  await f("FR03-DT-05", "   ", "");
  await resetState();
  await post("/forgot-password", { email: "' OR '1'='1" });
  const leaked = await get("SELECT COUNT(*) c FROM users WHERE reset_token IS NOT NULL AND email != ?", [C]);
  rec("FR03-DT-06", "API", "Không cấp OTP cho user nào, không lỗi server", `users có reset_token sau injection: ${leaked.c}`, leaked.c === 0);

  // ---- Step 2 OTP classes (valid password)
  const otpCase = async (id, mk, expected = "Từ chối, mật khẩu không đổi") => {
    await resetState(); const x = await issue(A); const v = await mk(x);
    const t = await tryReset(A, v, "Newpass1!"); rec(id, "API", expected, `otp=${JSON.stringify(v)} → ${desc(t)}`, rejected(t)); await resetState();
  };
  await otpCase("FR03-DT-08", async () => "");
  await otpCase("FR03-DT-09", async () => "12345");
  await otpCase("FR03-DT-10", async () => "1234567");
  await otpCase("FR03-DT-11", async () => "12a45!");
  await otpCase("FR03-DT-12", async (x) => String((Number(x) + 1) % 10 ** x.length).padStart(x.length, "0"));
  // DT-13: OTP of another email
  await resetState(); let xa = await issue(A), xb = await issue(B); if (xa === xb) { xb = await issue(B); }
  let t = await tryReset(A, xb, "Newpass1!"); const bUnchanged = (await pw(B)) === B_PW;
  rec("FR03-DT-13", "API", "OTP của email khác bị từ chối", `OTP của B dùng cho A → ${desc(t)}; pw B unchanged=${bUnchanged}`, rejected(t));
  // DT-14: reuse
  await resetState(); const x14 = await issue(A);
  const first = await tryReset(A, x14, "Newpass1!"); const second = await tryReset(A, x14, "Another1!");
  rec("FR03-DT-14", "API", "Lần 2 bị từ chối (OTP vô hiệu sau khi dùng)", `lần 1: ${desc(first)}; lần 2: ${desc(second)}`, first.r.status === 200 && rejected(second));
  await resetState();

  // ---- newPassword classes through API (backend validation)
  const pwCase = async (id, pass, expectAccept, label = "") => {
    await resetState(); const x = await issue(A); const t = await tryReset(A, x, pass);
    const ok = expectAccept ? t.r.status === 200 && t.after === pass : rejected(t);
    const shown = pass.length > 20 ? `<${pass.length} ký tự>` : JSON.stringify(pass);
    rec(id, "API", expectAccept ? "Chấp nhận, mật khẩu đổi" : "Từ chối, mật khẩu không đổi", `newPassword=${shown} → ${desc(t)}`, ok, label); await resetState();
  };
  await pwCase("FR03-DT-16", "", false);
  await pwCase("FR03-DT-17", "Ab1!xyz", false);
  await pwCase("FR03-DT-18", "newpass1!", false);
  await pwCase("FR03-DT-19", "NEWPASS1!", false);
  await pwCase("FR03-DT-20", "Newpass!!", false);
  await pwCase("FR03-DT-21", "Newpass12", false);
  await pwCase("FR03-DT-22", "Newpass1#", false, "diễn giải chặt");

  // ---- BVA: OTP length with seeded token
  const bvOtp = async (id, seed, submit, acceptExpected) => {
    await resetState(); await run("UPDATE users SET reset_token=? WHERE email=?", [seed, A]);
    const t = await tryReset(A, submit, "Newpass1!"); const ok = acceptExpected ? t.r.status === 200 && t.after === "Newpass1!" : rejected(t);
    rec(id, "API", acceptExpected ? "Chấp nhận" : "Từ chối, mật khẩu không đổi", `seed=${seed}, submit=${JSON.stringify(submit)} → ${desc(t)}`, ok); await resetState();
  };
  await bvOtp("FR03-BV-01", "123456", "", false);
  await bvOtp("FR03-BV-02", "123456", "1", false);
  await bvOtp("FR03-BV-03", "123456", "12345", false);
  await bvOtp("FR03-BV-04", "123456", "123456", true);
  await bvOtp("FR03-BV-05", "123456", "1234567", false);
  await bvOtp("FR03-BV-06", "012345", "012345", true);
  await bvOtp("FR03-BV-07", "012345", "12345", false);
  // BV-08 generated OTP length
  await resetState(); const gen = []; for (let i = 0; i < 20; i++) gen.push(String(await issue(A)));
  const lens = [...new Set(gen.map((g) => g.length))].sort(), nums = gen.map(Number);
  rec("FR03-BV-08", "API", "Cả 20 OTP đều đúng 6 chữ số", `độ dài quan sát: ${lens.join(",")}; min=${Math.min(...nums)}, max=${Math.max(...nums)}`, gen.every((g) => /^\d{6}$/.test(g)));
  await resetState();

  // ---- BVA: password
  await pwCase("FR03-BV-09", "Ab1!xyz", false);
  await pwCase("FR03-BV-10", "Ab1!wxyz", true);
  await pwCase("FR03-BV-11", "Ab1!vwxyz", true);
  await pwCase("FR03-BV-12", "Aa1!".repeat(64), true);
  await pwCase("FR03-BV-13", "newpass1!A", true);
  await pwCase("FR03-BV-14", "NEWPASS1!a", true);
  await pwCase("FR03-BV-15", "Newpass!1", true);
  await pwCase("FR03-BV-16", "Newpass12!", true);
  const specials = ["@", "$", "!", "%", "*", "?", "&"];
  for (let i = 0; i < specials.length; i++) await pwCase(`FR03-BV-${17 + i}`, "Newpass1" + specials[i], true);
  await pwCase("FR03-BV-24", "Newpass1+", false, "diễn giải chặt");
  await pwCase("FR03-BV-25", 'Newpass1"', false, "diễn giải chặt");

  fs.writeFileSync(path.join(__dirname, "api_results.json"), JSON.stringify(results, null, 2));
  const p = results.filter((x) => x.result === "Pass").length;
  console.log(`\nTOTAL ${results.length}: Pass ${p}, Fail ${results.length - p}`);
  db.close();
}
main().catch((e) => { console.error(e); process.exit(1); });
