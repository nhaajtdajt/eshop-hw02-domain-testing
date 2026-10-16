API đổi trạng thái đơn không kiểm tra quyền Admin

- **Feature:** FR-10 (liên quan FR-12) — **Mức độ:** Critical (bất kỳ người dùng đăng nhập nào cũng điều khiển được vòng đời mọi đơn)
- **Test liên quan:** FR10-DT-33
- **Các bước tái hiện:**
  1. Đăng nhập User thường `test@eshop.com` lấy token (role `user`).
  2. `PUT /api/admin/orders/<orderId>/status` với header `Authorization: Bearer <token user>` và body `{"status":"confirmed"}` (đơn đang `pending`).
- **Expected (SRS FR-12, dòng 176–179; SEC-03, dòng 280; FR-10 "Admin xác nhận/giao hàng/hoàn tất"):** Từ chối (403) vì token không có `role = admin`; trạng thái đơn không đổi.
- **Actual:** HTTP **200** "Order status updated"; User thường xác nhận được đơn (và có thể giao/hoàn tất đơn của bất kỳ ai vì API không kiểm tra chủ đơn). Middleware `authenticateToken` chỉ kiểm tra token hợp lệ.
- **Bằng chứng:** [evidence/api_results.json](https://github.com/nhaajtdajt/eshop-hw02-domain-testing/blob/main/features/FR-10/evidence/api_results.json) (FR10-DT-33). Code: `backend/server.js:100-110`, `:525`.
