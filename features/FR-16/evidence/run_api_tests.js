// FR-16 API test runner: POST /api/admin/import-products with JSON arrays (the API layer of Domain Testing and BVA).
// Run:  node run_api_tests.js    (backend on :3000)
// Pass criterion for "rejected": the number of products in the DB does not change.
// The DB is used only to count products and to delete rows created by a test (id > baseline max id).
const path = require("path");
const fs = require("fs");
const sqlite3 = require(path.resolve(__dirname, "../../../backend/node_modules/sqlite3"));
const db = new sqlite3.Database(path.resolve(__dirname, "../../../backend/database.sqlite"));
const API = "http://localhost:3000/api";
const get = (sql, p = []) => new Promise((r, j) => db.get(sql, p, (e, row) => (e ? j(e) : r(row))));
const all = (sql, p = []) => new Promise((r, j) => db.all(sql, p, (e, rows) => (e ? j(e) : r(rows))));
const run = (sql, p = []) => new Promise((r, j) => db.run(sql, p, function (e) { e ? j(e) : r(this); }));
const count = async () => (await get("SELECT COUNT(*) c FROM products")).c;

async function post(body, token, raw) {
  const headers = { "Content-Type": "application/json" };
  if (token) headers.Authorization = "Bearer " + token;
  try {
    const res = await fetch(API + "/admin/import-products", { method: "POST", headers, body: raw ?? JSON.stringify(body) });
    const t = await res.text(); let data; try { data = JSON.parse(t); } catch { data = t.slice(0, 80); }
    return { status: res.status, data };
  } catch (e) { return { status: 0, data: String(e) }; }
}
const login = async (e, p) => (await (await fetch(API + "/login", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ email: e, password: p }) })).json()).token;
const row = (i, o = {}) => ({ name: `FR16-${i}`, price: 100000, description: `Mô tả sản phẩm test dòng ${i}`, imageUrl: "https://placehold.co/300", category_id: 1, ...o });
const rows = (n, f = () => ({})) => Array.from({ length: n }, (_, i) => row(i + 1, f(i + 1)));
const results = [];
const rec = (id, expected, actual, pass, note = "") => {
  results.push({ id, layer: "API", expected, actual, result: pass ? "Pass" : "Fail", note, at: new Date().toISOString() });
  console.log(`${pass ? "PASS" : "FAIL"} ${id} | ${actual}${note ? " | " + note : ""}`);
};
const short = (r) => `HTTP ${r.status} ${typeof r.data === "object" ? JSON.stringify(r.data).slice(0, 110) : r.data}`;

let ADMIN, USER, baseMax;
async function exec(body, token = ADMIN, raw) {
  const before = await count(); const r = await post(body, token, raw); const after = await count();
  const added = await all("SELECT id,name,price,category_id FROM products WHERE id > ?", [baseMax]);
  await run("DELETE FROM products WHERE id > ?", [baseMax]);
  return { r, delta: after - before, added };
}
// accept: expect delta == n, HTTP 200; reject: expect delta == 0
async function acceptCase(id, body, n, note = "") { const x = await exec(body); rec(id, `chấp nhận ${n} SP`, `${short(x.r)}; DB +${x.delta}`, x.r.status === 200 && x.delta === n, note); return x; }
async function rejectCase(id, body, note = "", token) { const x = await exec(body, token); rec(id, "từ chối, DB không đổi", `${short(x.r)}; DB +${x.delta}`, x.delta === 0, x.delta > 0 ? (note ? note + "; " : "") + `hệ thống đã thêm ${x.delta} SP` : note); return x; }

async function main() {
  ADMIN = await login("admin@eshop.com", "Admin123!"); USER = await login("test@eshop.com", "Test1234!");
  baseMax = (await get("SELECT COALESCE(MAX(id),0) m FROM products")).m;
  // DT-06 decimal price
  await acceptCase("FR16-DT-06", { products: [row(1, { price: 0.5 })] }, 1);
  // DT-17..24 single bad row
  await rejectCase("FR16-DT-17", { products: [row(1, { name: "" })] });
  await rejectCase("FR16-DT-18", { products: [row(1, { name: "   " })] });
  await rejectCase("FR16-DT-19", { products: [row(1, { price: -1 })] });
  await rejectCase("FR16-DT-20", { products: [row(1, { price: 0 })] });
  await rejectCase("FR16-DT-21", { products: [row(1, { price: "abc" })] });
  await rejectCase("FR16-DT-22", { products: [row(1, { price: "" })] });
  await rejectCase("FR16-DT-23", { products: [row(1, { category_id: 999 })] }, "diễn giải FR-15");
  await rejectCase("FR16-DT-24", { products: [row(1, { category_id: "" })] }, "diễn giải FR-15");
  // atomicity (bad = price -1)
  const bad = { price: -1 };
  await rejectCase("FR16-DT-25", { products: rows(3, (i) => (i === 1 ? bad : {})) });
  await rejectCase("FR16-DT-26", { products: rows(3, (i) => (i === 2 ? bad : {})) });
  await rejectCase("FR16-DT-27", { products: rows(3, (i) => (i === 3 ? bad : {})) });
  await rejectCase("FR16-DT-28", { products: rows(5, (i) => (i === 2 || i === 4 ? bad : {})) });
  await rejectCase("FR16-DT-29", { products: rows(3, () => bad) });
  await acceptCase("FR16-DT-30", { products: rows(5) }, 5);
  // DT-33 failure indication (one invalid row among three)
  { const x = await exec({ products: rows(3, (i) => (i === 2 ? bad : {})) });
    rec("FR16-DT-33", "phản hồi thất bại (4xx hoặc inserted=0), không có SP nào được thêm", `${short(x.r)}; DB +${x.delta}`, (x.r.status >= 400 || x.r.data?.inserted === 0) && x.delta === 0, x.r.status === 200 ? "trả HTTP 200 'Import hoàn tất' dù có dòng lỗi" : ""); }
  // auth and shape
  await rejectCase("FR16-DT-34", { products: rows(1) }, "", ""); // no token
  await rejectCase("FR16-DT-35", { products: rows(1) }, "thiếu kiểm tra role=admin", USER);
  for (const [id, body] of [["FR16-DT-36", {}], ["FR16-DT-37", { products: [] }], ["FR16-DT-38", { products: "abc" }], ["FR16-DT-39", { products: [null] }]]) {
    const x = await exec(body); rec(id, "400, server vẫn sống", `${short(x.r)}; DB +${x.delta}`, x.r.status === 400 && x.delta === 0);
  }
  { const r = await fetch(API + "/admin/import-products", { method: "POST", headers: { "Content-Type": "application/json", Authorization: "Bearer " + ADMIN }, body: JSON.stringify({ products: [null] }) });
    const t = (await r.text()).replace(/\s+/g, " "); fs.writeFileSync(path.join(__dirname, "dt39_response.txt"), `HTTP ${r.status}
` + t.slice(0, 600)); console.log("DT-39 body:", t.slice(0, 300)); }
  console.log("backend alive after DT-39:", (await fetch(API + "/products")).status);
  // BVA row counts
  await acceptCase("FR16-BV-01", { products: rows(1) }, 1);
  await acceptCase("FR16-BV-02", { products: rows(2) }, 2);
  await acceptCase("FR16-BV-03", { products: rows(100) }, 100);
  { const body = { products: rows(1000) }; const kb = (JSON.stringify(body).length / 1024).toFixed(0);
    const x = await exec(body); rec("FR16-BV-04", "chấp nhận 1000 SP (hoặc từ chối rõ ràng, DB không đổi)", `payload ~${kb} KB; ${short(x.r)}; DB +${x.delta}`, (x.r.status === 200 && x.delta === 1000) || (x.r.status >= 400 && x.delta === 0 && typeof x.r.data === "object" && x.r.data.error), x.r.status === 413 ? "bị giới hạn body 100 KB, thông báo không phải JSON lỗi rõ ràng" : ""); }
  // price boundaries
  await acceptCase("FR16-BV-07", { products: [row(1, { price: 1 })] }, 1);
  await acceptCase("FR16-BV-08", { products: [row(1, { price: 0.01 })] }, 1);
  { const x = await acceptCase("FR16-BV-09", { products: [row(1, { price: 2147483647 })] }, 1); const ok = x.added[0]?.price === 2147483647; if (!ok) console.log("  stored price:", x.added[0]?.price); }
  { const x = await acceptCase("FR16-BV-10", { products: [row(1, { price: 2147483648 })] }, 1); if (x.added[0]?.price !== 2147483648) console.log("  stored price:", x.added[0]?.price); }
  { const x = await exec({ products: [row(1, { price: 9223372036854775808 })] });
    rec("FR16-BV-11", "không lỗi server; lưu đúng hoặc từ chối rõ ràng", `${short(x.r)}; DB +${x.delta}; giá lưu=${x.added[0]?.price}`, x.r.status !== 0 && x.r.status < 500, "SRS không nêu giới hạn; ghi nhận giá lưu"); }
  // name length
  await acceptCase("FR16-BV-12", { products: [row(1, { name: "F" })] }, 1);
  await acceptCase("FR16-BV-13", { products: [row(1, { name: "F".repeat(255) })] }, 1);
  await rejectCase("FR16-BV-14", { products: [row(1, { name: "F".repeat(256) })] }, "diễn giải FR-15");
  // invalid row position
  await rejectCase("FR16-BV-15", { products: rows(1, () => bad) });
  await rejectCase("FR16-BV-16", { products: rows(2, (i) => (i === 2 ? bad : {})) });
  await rejectCase("FR16-BV-17", { products: rows(100, (i) => (i === 100 ? bad : {})) });
  { // compact rows (no description/imageUrl) keep the payload under the 100 KB body limit so atomicity can really be observed
    const compact = (i) => ({ name: `FR16-${i}`, price: i === 1000 ? -1 : 100000, description: "", imageUrl: "", category_id: 1 });
    const body = { products: Array.from({ length: 1000 }, (_, k) => compact(k + 1)) }; const kb = (JSON.stringify(body).length / 1024).toFixed(0);
    const x = await exec(body); rec("FR16-BV-18", "từ chối, DB không đổi (dòng 1000 lỗi, 999 dòng hợp lệ cũng không được lưu)", `payload ~${kb} KB; ${short(x.r)}; DB +${x.delta}`, x.delta === 0, x.delta > 0 ? `hệ thống đã thêm ${x.delta} SP` : ""); }
  // BV-19 row numbering: first data row has an empty name (the only defect the server detects)
  { const x = await exec({ products: rows(3, (i) => (i === 1 ? { name: "" } : {})) });
    const errs = x.r.data?.errors || []; const hasRow2 = errs.some((e) => /Hàng 2\b/.test(e));
    rec("FR16-BV-19", "báo lỗi dòng 2 và không thêm SP nào", `${short(x.r)}; DB +${x.delta}; errors=${JSON.stringify(errs)}`, hasRow2 && x.delta === 0, !hasRow2 ? "" : "báo đúng số dòng nhưng vẫn thêm các dòng hợp lệ (không rollback)"); }

  console.log("backend alive at end:", (await fetch(API + "/products")).status, "; products now:", await count());
  fs.writeFileSync(path.join(__dirname, "api_results.json"), JSON.stringify(results, null, 2));
  const p = results.filter((x) => x.result === "Pass").length;
  console.log(`\nTOTAL ${results.length}: Pass ${p}, Fail ${results.length - p}`);
  db.close();
}
main().catch((e) => { console.error(e); process.exit(1); });
