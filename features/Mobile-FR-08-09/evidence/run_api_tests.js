// Mobile FR-08/09 API-layer tests (checkout + coupon). Run: node run_api_tests.js   (backend on :3000)
// Expected values come from the SRS formula: percent = total*value/100, fixed = value, final = total - discount.
// The DB is used only to set up/clean state (coupon_usage, is_active, test coupons/orders) - never to decide a result.
const path = require("path");
const fs = require("fs");
const sqlite3 = require(path.resolve(__dirname, "../../../backend/node_modules/sqlite3"));
const db = new sqlite3.Database(path.resolve(__dirname, "../../../backend/database.sqlite"));
const API = "http://localhost:3000/api";
const run = (sql, p = []) => new Promise((r, j) => db.run(sql, p, function (e) { e ? j(e) : r(this); }));
const get = (sql, p = []) => new Promise((r, j) => db.get(sql, p, (e, row) => (e ? j(e) : r(row))));
async function call(method, p, body, token) {
  const headers = { "Content-Type": "application/json" };
  if (token) headers.Authorization = "Bearer " + token;
  try {
    const r = await fetch(API + p, { method, headers, body: body === undefined ? undefined : JSON.stringify(body) });
    const t = await r.text(); let data; try { data = JSON.parse(t); } catch { data = t.slice(0, 80); }
    return { status: r.status, data };
  } catch (e) { return { status: 0, data: String(e) }; }
}
const results = [];
const rec = (id, expected, actual, pass, note = "") => {
  results.push({ id, layer: "API", expected, actual, result: pass ? "Pass" : "Fail", note, at: new Date().toISOString() });
  console.log(`${pass ? "PASS" : "FAIL"} ${id} | ${actual}${note ? " | " + note : ""}`);
};
const s = (r) => `HTTP ${r.status} ${typeof r.data === "object" ? JSON.stringify(r.data).slice(0, 120) : r.data}`;
let ADMIN, USER, UID;
const apply = (code, total, token, withUser = true) => call("POST", "/apply-coupon", { code, total_amount: total, ...(withUser ? { user_id: UID } : {}) }, token);
const clearUsage = () => run("DELETE FROM coupon_usage WHERE user_id = ?", [UID]);
const mk = async (code, type, value, min, expired = "2099-12-31") => {
  const r = await call("POST", "/admin/coupons", { code, type, discount_value: value, min_order_amount: min, expired_at: expired, max_uses_per_user: 1 }, ADMIN);
  return r.data.id;
};
// accept: HTTP 200, discount and final per SRS formula (tolerance 1 for fractional percent)
function acceptCheck(r, type, value, total) {
  if (r.status !== 200) return false;
  const exact = type === "percent" ? (total * value) / 100 : value;
  return Math.abs(r.data.discount_amount - exact) <= 1 && Math.abs(r.data.final_amount - (total - r.data.discount_amount)) < 1 && r.data.final_amount >= 0;
}
const fmt = (r) => `${s(r)}`;

async function main() {
  const login = async (e, p) => (await call("POST", "/login", { email: e, password: p })).data;
  ADMIN = (await login("admin@eshop.com", "Admin123!")).token; const u = await login("test@eshop.com", "Test1234!"); USER = u.token; UID = u.user.id;
  const baseOrder = (await get("SELECT COALESCE(MAX(id),0) m FROM orders")).m;
  await run("DELETE FROM coupons WHERE code LIKE 'FRM-%'"); await clearUsage();
  const seed = async (code) => (await get("SELECT id FROM coupons WHERE code=?", [code])).id;
  const SAVE10 = await seed("SAVE10"), VIP100 = await seed("VIP100");

  // ---- checkout (FR-08)
  let r = await call("POST", "/checkout", { total_amount: 100000 }); rec("MFR-DT-02", "401, không tạo đơn", s(r), r.status === 401);
  { const before = (await get("SELECT COUNT(*) c FROM orders")).c;
    r = await call("POST", "/checkout", { items: [{ id: 1, name: "iPhone 15 Pro Max", price: 30000000, quantity: 1 }], total_amount: 1, shipping_address: "x" }, USER);
    const o = await get("SELECT total_amount FROM orders WHERE id = ?", [r.data.orderId]);
    rec("MFR-DT-07", "đơn có tổng = 30,000,000 (backend tự tính) hoặc bị từ chối", `${s(r)}; tổng đơn lưu = ${o?.total_amount}`, r.status >= 400 || o?.total_amount === 30000000, o?.total_amount === 1 ? "backend lưu nguyên total_amount do client gửi" : ""); }
  for (const [id, body, label] of [["MFR-DT-32", { items: [] }, "thiếu total_amount"], ["MFR-DT-33", { items: [], total_amount: -100 }, "total_amount = -100"], ["MFR-DT-34", { items: [], total_amount: "abc" }, "total_amount = 'abc'"]]) {
    const before = (await get("SELECT COUNT(*) c FROM orders")).c; r = await call("POST", "/checkout", body, USER); const after = (await get("SELECT COUNT(*) c FROM orders")).c;
    rec(id, "400, không tạo đơn", `${label}: ${s(r)}; đơn mới +${after - before}`, r.status >= 400 && after === before, after > before ? "đơn rác đã được tạo" : "");
  }
  // ---- apply-coupon valid / type
  r = await apply("SAVE10", 400000, USER); rec("MFR-DT-09", "discount 40,000; final 360,000", fmt(r), acceptCheck(r, "percent", 10, 400000), r.data.discount_amount < 0 ? "discount ÂM: công thức total*(1-value)" : "");
  r = await apply("BIGBUY", 600000, USER); rec("MFR-DT-10", "discount 50,000; final 550,000", fmt(r), acceptCheck(r, "fixed", 50000, 600000));
  r = await apply("VIP100", 400000, USER); rec("MFR-DT-11", "discount 100,000; final 300,000", fmt(r), acceptCheck(r, "fixed", 100000, 400000));
  // ---- invalid codes
  r = await apply("NOPE", 400000, USER); rec("MFR-DT-12", "từ chối", fmt(r), r.status >= 400);
  { await mk("FRM-INACT", "fixed", 10000, 0); await run("UPDATE coupons SET is_active=0 WHERE code='FRM-INACT'"); r = await apply("FRM-INACT", 400000, USER); rec("MFR-DT-13", "từ chối (mã không hoạt động)", fmt(r), r.status >= 400); }
  r = await apply("' OR '1'='1", 400000, USER); rec("MFR-DT-17", "từ chối, không lỗi server", fmt(r), r.status >= 400 && r.status < 500);
  // ---- C2..C5
  r = await apply("EXPIRED", 200000, USER); rec("MFR-DT-18", "từ chối vì hết hạn", fmt(r), r.status >= 400 && /hết hạn/i.test(JSON.stringify(r.data)));
  r = await apply("EXPIRED", 50000, USER); rec("MFR-DT-19", "từ chối (lý do hợp lệ bất kỳ)", fmt(r), r.status >= 400, /tối thiểu/.test(JSON.stringify(r.data)) ? "báo 'chưa đủ ngưỡng' trước 'hết hạn' (thứ tự không quy định)" : "");
  r = await apply("SAVE10", 200000, USER); rec("MFR-DT-20", "từ chối (chưa đủ ngưỡng)", fmt(r), r.status >= 400);
  r = await apply("BIGBUY", 400000, USER); rec("MFR-DT-21", "từ chối (chưa đủ ngưỡng)", fmt(r), r.status >= 400);
  r = await apply("SAVE10", 400000, undefined, false); rec("MFR-DT-22", "từ chối (C4: phải đăng nhập)", fmt(r), r.status === 401 || r.status === 403, r.status === 200 ? "apply-coupon không yêu cầu token" : "");
  await call("POST", "/coupon-usage", { coupon_id: SAVE10 }, USER);
  r = await apply("SAVE10", 400000, USER); rec("MFR-DT-23", "từ chối (đã dùng hết lượt)", fmt(r), r.status >= 400);
  r = await apply("SAVE10", 400000, USER, false); rec("MFR-DT-24", "từ chối dù bỏ user_id (C5)", fmt(r), r.status >= 400, r.status === 200 ? "bỏ user_id là qua mặt được kiểm tra lượt dùng" : "");
  await clearUsage();
  // ---- calculation
  r = await apply("SAVE10", 333333, USER); rec("MFR-DT-25", "discount ≈ 33,333; final ≈ 300,000", fmt(r), acceptCheck(r, "percent", 10, 333333));
  await mk("FRM-FIXBIG", "fixed", 1000000, 0); r = await apply("FRM-FIXBIG", 100000, USER); rec("MFR-DT-26", "final không âm (0)", fmt(r), r.status === 200 && r.data.final_amount >= 0, r.data.final_amount < 0 ? "tổng thanh toán âm" : "");
  // ---- coupon-usage and request shapes
  r = await call("POST", "/coupon-usage", { coupon_id: SAVE10 }); rec("MFR-DT-35", "401", s(r), r.status === 401);
  { const b = (await get("SELECT COUNT(*) c FROM coupon_usage")).c; r = await call("POST", "/coupon-usage", { coupon_id: 99999 }, USER); const a = (await get("SELECT COUNT(*) c FROM coupon_usage")).c;
    rec("MFR-DT-36", "từ chối, không ghi bản ghi", `${s(r)}; coupon_usage +${a - b}`, r.status >= 400 && a === b, a > b ? "ghi lượt dùng cho mã không tồn tại" : ""); await clearUsage(); }
  r = await call("POST", "/apply-coupon", { total_amount: 400000, user_id: UID }, USER); rec("MFR-DT-37", "400", s(r), r.status === 400);
  r = await call("POST", "/apply-coupon", { code: "SAVE10", user_id: UID }, USER); rec("MFR-DT-38", "400, không trả final_amount", s(r), r.status === 400 && !r.data.final_amount);
  r = await apply("SAVE10", -400000, USER); rec("MFR-DT-39", "400", s(r), r.status === 400);
  r = await apply("SAVE10", "abc", USER); rec("MFR-DT-40", "400", s(r), r.status === 400);

  // ---- BVA: threshold
  for (const [id, code, total, ok, type, val] of [["MFR-BV-01", "SAVE10", 299999, false], ["MFR-BV-02", "SAVE10", 300000, true, "percent", 10], ["MFR-BV-03", "SAVE10", 300001, true, "percent", 10], ["MFR-BV-04", "BIGBUY", 499999, false], ["MFR-BV-05", "BIGBUY", 500000, true, "fixed", 50000], ["MFR-BV-06", "BIGBUY", 500001, true, "fixed", 50000]]) {
    r = await apply(code, total, USER);
    rec(id, ok ? "chấp nhận, tính tiền đúng" : "từ chối", `${code} @ ${total}: ${fmt(r)}`, ok ? acceptCheck(r, type, val, total) : r.status >= 400, ok && r.status >= 400 ? "đúng bằng ngưỡng bị từ chối (code dùng '>' thay vì '>=')" : (ok && r.data.discount_amount < 0 ? "discount âm" : ""));
  }
  // ---- BVA: expiry
  const d = (offsetDays) => new Date(Date.now() + offsetDays * 86400000).toISOString().slice(0, 10);
  // date-times without "Z" are parsed by the server as LOCAL time, so build the string from local clock fields
const pad = (n) => String(n).padStart(2, "0");
const iso = (offsetMin) => { const t = new Date(Date.now() + offsetMin * 60000); return `${t.getFullYear()}-${pad(t.getMonth() + 1)}-${pad(t.getDate())}T${pad(t.getHours())}:${pad(t.getMinutes())}:${pad(t.getSeconds())}`; };
  for (const [id, code, exp, ok] of [["MFR-BV-07", "FRM-EXP-Y", d(-1), false], ["MFR-BV-08", "FRM-EXP-T", d(0), false], ["MFR-BV-09", "FRM-EXP-N", d(1), true], ["MFR-BV-10", "FRM-EXP-M1", iso(-1), false], ["MFR-BV-11", "FRM-EXP-P1", iso(1), true]]) {
    await mk(code, "fixed", 10000, 0, exp); r = await apply(code, 100000, USER);
    rec(id, ok ? "chấp nhận" : "từ chối (hết hạn)", `expired_at=${exp}: ${fmt(r)}`, ok ? acceptCheck(r, "fixed", 10000, 100000) : r.status >= 400);
  }
  // ---- BVA: usage count (VIP100, max 2)
  await clearUsage();
  r = await apply("VIP100", 400000, USER); rec("MFR-BV-12", "chấp nhận (đã dùng 0)", fmt(r), acceptCheck(r, "fixed", 100000, 400000));
  await call("POST", "/coupon-usage", { coupon_id: VIP100 }, USER); r = await apply("VIP100", 400000, USER); rec("MFR-BV-13", "chấp nhận (đã dùng 1 = max-1)", fmt(r), acceptCheck(r, "fixed", 100000, 400000));
  await call("POST", "/coupon-usage", { coupon_id: VIP100 }, USER); r = await apply("VIP100", 400000, USER); rec("MFR-BV-14", "từ chối (đã dùng 2 = max)", fmt(r), r.status >= 400);
  await clearUsage();
  // ---- BVA: discount vs total
  await mk("FRM-FIX100K", "fixed", 100000, 0);
  for (const [id, total, finalMin] of [["MFR-BV-15", 99999], ["MFR-BV-16", 100000], ["MFR-BV-17", 100001]]) {
    r = await apply("FRM-FIX100K", total, USER); const exp = Math.max(0, total - 100000);
    rec(id, `final = ${exp} (không âm)`, `total ${total}: ${fmt(r)}`, r.status === 200 && r.data.final_amount === exp, r.data.final_amount < 0 ? "final âm" : "");
  }
  await mk("FRM-PCT100", "percent", 100, 0); r = await apply("FRM-PCT100", 1000, USER); rec("MFR-BV-18", "discount 1,000; final 0", fmt(r), r.status === 200 && r.data.discount_amount === 1000 && r.data.final_amount === 0, r.data.discount_amount < 0 ? "discount âm" : "");
  await mk("FRM-PCT10", "percent", 10, 0);
  r = await apply("FRM-PCT10", 9, USER); rec("MFR-BV-19", "discount 0 hoặc 1, final = total - discount ≥ 0", fmt(r), r.status === 200 && [0, 1].includes(r.data.discount_amount) && r.data.final_amount === 9 - r.data.discount_amount);
  r = await apply("FRM-PCT10", 10, USER); rec("MFR-BV-20", "discount 1; final 9", fmt(r), r.status === 200 && r.data.discount_amount === 1 && r.data.final_amount === 9, r.data.discount_amount < 0 ? "discount âm" : "");
  r = await apply("A".repeat(1000), 400000, USER); rec("MFR-BV-23", "từ chối, không lỗi server", fmt(r), r.status >= 400 && r.status < 500);

  // ---- cleanup of test data
  await run("DELETE FROM coupons WHERE code LIKE 'FRM-%'"); await run("DELETE FROM orders WHERE id > ?", [baseOrder]); await clearUsage();
  console.log("backend alive:", (await call("GET", "/products")).status);
  fs.writeFileSync(path.join(__dirname, "api_results.json"), JSON.stringify(results, null, 2));
  const p = results.filter((x) => x.result === "Pass").length;
  console.log(`\nTOTAL ${results.length}: Pass ${p}, Fail ${results.length - p}`);
  db.close();
}
main().catch((e) => { console.error(e); process.exit(1); });
