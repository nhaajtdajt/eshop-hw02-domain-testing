// X-01 (added-after-run): concurrent conflicting transitions on the same pending order.
// Fire "pending->confirmed" and "pending->canceled" at the same time; spec invariant: a canceled order is final.
const path = require("path");
const sqlite3 = require(path.resolve(__dirname, "../../../backend/node_modules/sqlite3"));
const db = new sqlite3.Database(path.resolve(__dirname, "../../../backend/database.sqlite"));
const API = "http://localhost:3000/api";
const call = async (m, p, b, t) => { const r = await fetch(API + p, { method: m, headers: { "Content-Type": "application/json", ...(t ? { Authorization: "Bearer " + t } : {}) }, body: b ? JSON.stringify(b) : undefined }); return { status: r.status, data: await r.json().catch(() => ({})) }; };
const st = (id) => new Promise((r) => db.get("SELECT status FROM orders WHERE id=?", [id], (e, row) => r(row.status)));
(async () => {
  const admin = (await call("POST", "/login", { email: "admin@eshop.com", password: "Admin123!" })).data.token;
  const a = (await call("POST", "/login", { email: "test@eshop.com", password: "Test1234!" })).data.token;
  let bothOk = 0, final = {}, revived = 0; const N = 60;
  for (let i = 0; i < N; i++) {
    const id = (await call("POST", "/checkout", { total_amount: 1000, shipping_address: "race" }, a)).data.orderId;
    const [r1, r2] = await Promise.all([call("PUT", `/admin/orders/${id}/status`, { status: "confirmed" }, admin), call("PUT", `/orders/${id}/cancel`, {}, a)]);
    const s = await st(id); final[s] = (final[s] || 0) + 1;
    if (r1.status === 200 && r2.status === 200) bothOk++;
  }
  console.log(JSON.stringify({ pairs: N, bothRequestsReturned200: bothOk, finalStatusCounts: final }));
  db.close();
})();
