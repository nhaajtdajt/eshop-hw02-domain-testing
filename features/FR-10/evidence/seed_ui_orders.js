// Prepare 5 orders (ids 1..5) for user test@eshop.com in states pending/confirmed/shipping/delivered/canceled
// and print tokens for the browser UI checks. Usage: node seed_ui_orders.js
const path = require("path");
const sqlite3 = require(path.resolve(__dirname, "../../../backend/node_modules/sqlite3"));
const db = new sqlite3.Database(path.resolve(__dirname, "../../../backend/database.sqlite"));
const run = (s) => new Promise((r, j) => db.run(s, (e) => (e ? j(e) : r())));
const API = "http://localhost:3000/api";
const call = async (m, p, b, t) => (await fetch(API + p, { method: m, headers: { "Content-Type": "application/json", ...(t ? { Authorization: "Bearer " + t } : {}) }, body: b ? JSON.stringify(b) : undefined })).json();
(async () => {
  const admin = (await call("POST", "/login", { email: "admin@eshop.com", password: "Admin123!" })).token;
  const a = (await call("POST", "/login", { email: "test@eshop.com", password: "Test1234!" })).token;
  await run("DELETE FROM orders"); await run("DELETE FROM sqlite_sequence WHERE name='orders'");
  const paths = [[], ["confirmed"], ["confirmed", "shipping"], ["confirmed", "shipping", "delivered"], ["canceled"]];
  for (const p of paths) {
    const id = (await call("POST", "/checkout", { total_amount: 150000, shipping_address: "UI test" }, a)).orderId;
    for (const s of p) await call("PUT", `/admin/orders/${id}/status`, { status: s }, admin);
  }
  console.log(JSON.stringify({ admin, a }));
  db.close();
})();
