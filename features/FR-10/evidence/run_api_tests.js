// FR-10 API test runner (state machine): Domain Testing DT-01..43 and BVA BV-01..17 (API layer).
// Run:  node run_api_tests.js     (backend must be running on :3000)
// HTTP drives the system; the sqlite DB is only used to (a) verify the stored order status and
// (b) clear the orders table before the BVA id-boundary group so ids are 1..3.
const path = require("path");
const fs = require("fs");
const sqlite3 = require(path.resolve(__dirname, "../../../backend/node_modules/sqlite3"));
const db = new sqlite3.Database(path.resolve(__dirname, "../../../backend/database.sqlite"));
const API = "http://localhost:3000/api";
const run = (sql, p = []) => new Promise((r, j) => db.run(sql, p, function (e) { e ? j(e) : r(this); }));
const get = (sql, p = []) => new Promise((r, j) => db.get(sql, p, (e, row) => (e ? j(e) : r(row))));
const dbStatus = async (id) => (await get("SELECT status FROM orders WHERE id=?", [id]))?.status;

async function call(method, p, body, token) {
  const headers = { "Content-Type": "application/json" };
  if (token) headers.Authorization = "Bearer " + token;
  try {
    const res = await fetch(API + p, { method, headers, body: body === undefined ? undefined : JSON.stringify(body) });
    const txt = await res.text(); let data; try { data = JSON.parse(txt); } catch { data = txt.slice(0, 100); }
    return { status: res.status, data };
  } catch (e) { return { status: 0, data: String(e) }; }
}
const login = async (email, password) => (await call("POST", "/login", { email, password })).data.token;
const results = [];
const rec = (id, expected, actual, pass, note = "") => {
  results.push({ id, layer: "API", expected, actual, result: pass ? "Pass" : "Fail", note, at: new Date().toISOString() });
  console.log(`${pass ? "PASS" : "FAIL"} ${id} | ${actual}${note ? " | " + note : ""}`);
};

let ADMIN, A, B;
const STATES = ["pending", "confirmed", "shipping", "delivered", "canceled"];
const PATH = { pending: [], confirmed: ["confirmed"], shipping: ["confirmed", "shipping"], delivered: ["confirmed", "shipping", "delivered"], canceled: ["canceled"] };
const VALID = { pending: ["confirmed", "canceled"], confirmed: ["shipping", "canceled"], shipping: ["delivered"], delivered: [], canceled: [] };

async function newOrder(token = A) {
  const r = await call("POST", "/checkout", { total_amount: 100000, shipping_address: "FR-10 test" }, token);
  return r.data.orderId;
}
async function orderIn(state) {
  const id = await newOrder();
  for (const s of PATH[state]) await call("PUT", `/admin/orders/${id}/status`, { status: s }, ADMIN);
  return id;
}
const adminSet = (id, status, token = ADMIN) => call("PUT", `/admin/orders/${id}/status`, { status }, token);
const cancel = (id, token = A) => call("PUT", `/orders/${id}/cancel`, {}, token);
const d = (r, st) => `HTTP ${r.status} ${typeof r.data === "object" ? JSON.stringify(r.data).slice(0, 60) : r.data}; DB status=${st}`;

async function main() {
  ADMIN = await login("admin@eshop.com", "Admin123!");
  A = await login("test@eshop.com", "Test1234!");
  if (!(await get("SELECT id FROM users WHERE email='userb@eshop.com'"))) await run("INSERT INTO users (name,email,password) VALUES ('User B','userb@eshop.com','Userb123!')");
  await run("UPDATE users SET password='Userb123!', locked_until=NULL, login_attempts=0 WHERE email='userb@eshop.com'");
  B = await login("userb@eshop.com", "Userb123!");
  if (!ADMIN || !A || !B) throw new Error("cannot login admin/A/B");

  // ---- DT-01..25: transition matrix through the Admin API
  let n = 0;
  for (const src of STATES) for (const tgt of STATES) {
    n++; const id = await orderIn(src);
    const valid = VALID[src].includes(tgt) && !(src === "shipping" && tgt === "canceled");
    const r = await adminSet(id, tgt); const st = await dbStatus(id);
    const pass = valid ? r.status === 200 && st === tgt : r.status >= 400 && st === src;
    const note = !valid && r.status === 200 ? "hệ thống CHO PHÉP chuyển không hợp lệ" : "";
    rec(`FR10-DT-${String(n).padStart(2, "0")}`, valid ? `chấp nhận → ${tgt}` : "từ chối, không đổi", `${src} → ${tgt}: ${d(r, st)}`, pass, note);
  }
  // ---- DT-26..30: user cancels own order from each state (ids DT-26..30)
  const userCancelExpect = { pending: true, confirmed: true, shipping: false, delivered: false, canceled: false };
  let k = 26;
  for (const src of STATES) {
    const id = await orderIn(src); const r = await cancel(id); const st = await dbStatus(id); const ok = userCancelExpect[src];
    const pass = ok ? r.status === 200 && st === "canceled" : r.status >= 400 && st === src;
    rec(`FR10-DT-${k++}`, ok ? "chấp nhận → canceled" : "từ chối, không đổi", `User hủy đơn ${src}: ${d(r, st)}`, pass, !ok && r.status === 200 ? "User hủy được đơn không được phép hủy" : "");
  }
  // ---- DT-31..36 permissions / existence
  let id = await newOrder(); let r = await call("PUT", `/admin/orders/${id}/status`, { status: "confirmed" }); let st = await dbStatus(id);
  rec("FR10-DT-31", "401, không đổi", `Admin API không token: ${d(r, st)}`, r.status >= 400 && st === "pending");
  r = await call("PUT", `/orders/${id}/cancel`, {}); st = await dbStatus(id);
  rec("FR10-DT-32", "401, không đổi", `Hủy không token: ${d(r, st)}`, r.status >= 400 && st === "pending");
  r = await adminSet(id, "confirmed", A); st = await dbStatus(id);
  rec("FR10-DT-33", "từ chối (403), không đổi", `User thường gọi Admin API: ${d(r, st)}`, r.status >= 400 && st === "pending", r.status === 200 ? "thiếu kiểm tra role=admin (FR-12/SEC-03)" : "");
  await adminSet(id, "canceled");
  id = await newOrder(); r = await cancel(id, B); st = await dbStatus(id);
  rec("FR10-DT-34", "từ chối, đơn của A không đổi", `User B hủy đơn của A: ${d(r, st)}`, r.status >= 400 && st === "pending");
  r = await adminSet(999999, "confirmed");
  rec("FR10-DT-35", "404", `Admin API id không tồn tại: ${d(r, "-")}`, r.status === 404);
  r = await cancel(999999);
  rec("FR10-DT-36", "404", `User hủy id không tồn tại: ${d(r, "-")}`, r.status === 404);
  // ---- DT-37..41 invalid status values
  const bad = [["", "rỗng"], ["refunded", "chuỗi lạ"], ["CONFIRMED", "sai hoa/thường"], [null, "null"], [123, "số"]];
  for (let i = 0; i < bad.length; i++) {
    id = await newOrder(); r = await adminSet(id, bad[i][0]); st = await dbStatus(id);
    rec(`FR10-DT-${37 + i}`, "từ chối (400), không đổi", `status=${JSON.stringify(bad[i][0])} (${bad[i][1]}): ${d(r, st)}`, r.status >= 400 && st === "pending");
  }
  // ---- DT-42 lifecycle; DT-43 cancel path
  id = await newOrder(); let log = [];
  for (const s of ["confirmed", "shipping", "delivered"]) { r = await adminSet(id, s); log.push(`${s}:${r.status}`); }
  let after = []; for (const s of ["pending", "confirmed", "shipping", "delivered", "canceled"]) { r = await adminSet(id, s); after.push(`${s}:${r.status}`); }
  st = await dbStatus(id);
  rec("FR10-DT-42", "3 bước thành công; sau delivered mọi chuyển tiếp bị từ chối", `tiến: ${log.join(", ")}; sau delivered: ${after.join(", ")}; DB=${st}`, log.every((x) => x.endsWith(":200")) && after.every((x) => !x.endsWith(":200")) && st === "delivered");
  id = await newOrder(); await adminSet(id, "confirmed"); r = await cancel(id); const afterCancel = await dbStatus(id);
  const r2 = await adminSet(id, "delivered"); st = await dbStatus(id);
  rec("FR10-DT-43", "hủy thành công; canceled→delivered bị từ chối", `hủy: HTTP ${r.status} (DB=${afterCancel}); sau đó canceled→delivered: HTTP ${r2.status}, DB=${st}`, afterCancel === "canceled" && r2.status >= 400 && st === "canceled", r2.status === 200 ? "đơn đã hủy bị chuyển thành delivered" : "");

  // ---- BVA: order id boundaries; reset orders table so ids are 1..3
  await run("DELETE FROM orders"); await run("DELETE FROM sqlite_sequence WHERE name='orders'");
  const o1 = await newOrder(), o2 = await newOrder(), o3 = await newOrder();
  const ids = `ids=${o1},${o2},${o3}`;
  const idCase = async (tc, p, expectOk, label) => {
    const r = await call("PUT", `/admin/orders/${p}/status`, { status: "confirmed" }, ADMIN);
    const sts = [await dbStatus(o1), await dbStatus(o2), await dbStatus(o3)];
    return { r, sts, label, tc, expectOk };
  };
  const before = ["pending", "pending", "pending"];
  const bvId = [["FR10-BV-01", "0", false, 0], ["FR10-BV-02", "-1", false, 0], ["FR10-BV-03", String(o1), true, 0], ["FR10-BV-04", String(o3), true, 2], ["FR10-BV-05", String(o3 + 1), false, 0], ["FR10-BV-06", "abc", false, 0], ["FR10-BV-07", "1.5", false, 0], ["FR10-BV-08", "9223372036854775808", false, 0]];
  const cur = [...before];
  for (const [tc, p, ok, idx] of bvId) {
    const x = await idCase(tc, p, ok); const sts = x.sts;
    const changed = sts.map((s, i) => s !== cur[i]);
    let pass;
    if (ok) { pass = x.r.status === 200 && sts[idx] === "confirmed"; if (pass) cur[idx] = "confirmed"; }
    else pass = x.r.status === 404 && !changed.some(Boolean);
    rec(tc, ok ? "chấp nhận → confirmed" : "404, không đơn nào đổi", `id=${p}: HTTP ${x.r.status} ${JSON.stringify(x.r.data).slice(0, 50)}; statuses=${sts.join("/")} (${ids})`, pass);
  }
  r = await call("PUT", "/orders/0/cancel", {}, A); rec("FR10-BV-09", "404", `User hủy id=0: ${d(r, "-")}`, r.status === 404);
  r = await call("PUT", `/orders/${o3 + 1}/cancel`, {}, A); rec("FR10-BV-10", "404", `User hủy id=N+1: ${d(r, "-")}`, r.status === 404);
  // BV-11 chain length
  id = await newOrder(); log = [];
  for (const s of ["confirmed", "shipping", "delivered"]) { r = await adminSet(id, s); log.push(r.status); }
  r = await adminSet(id, "canceled"); st = await dbStatus(id);
  rec("FR10-BV-11", "3 bước đầu thành công, bước 4 bị từ chối", `3 bước: ${log.join(",")}; bước 4 (→canceled): HTTP ${r.status}; DB=${st}`, log.every((x) => x === 200) && r.status >= 400 && st === "delivered");
  // BV-12 cancel twice
  id = await newOrder(); const c1 = await cancel(id); const c2 = await cancel(id); st = await dbStatus(id);
  rec("FR10-BV-12", "lần 1 thành công, lần 2 bị từ chối", `lần 1: HTTP ${c1.status}; lần 2: HTTP ${c2.status} ${JSON.stringify(c2.data).slice(0, 40)}; DB=${st}`, c1.status === 200 && c2.status >= 400 && st === "canceled");
  // BV-13..17 status string boundaries
  const strs = [["confirme", false], ["confirmed", true], ["confirmedd", false], [" confirmed", false], ["confirmed ", false]];
  for (let i = 0; i < strs.length; i++) {
    id = await newOrder(); r = await adminSet(id, strs[i][0]); st = await dbStatus(id);
    const pass = strs[i][1] ? r.status === 200 && st === "confirmed" : r.status >= 400 && st === "pending";
    rec(`FR10-BV-${13 + i}`, strs[i][1] ? "chấp nhận → confirmed" : "từ chối, không đổi", `status=${JSON.stringify(strs[i][0])}: ${d(r, st)}`, pass);
  }
  const alive = (await call("GET", "/products")).status;
  console.log("backend alive after tests:", alive);
  fs.writeFileSync(path.join(__dirname, "api_results.json"), JSON.stringify(results, null, 2));
  const p = results.filter((x) => x.result === "Pass").length;
  console.log(`\nTOTAL ${results.length}: Pass ${p}, Fail ${results.length - p}`);
  db.close();
}
main().catch((e) => { console.error(e); process.exit(1); });
