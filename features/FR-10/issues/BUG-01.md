API cho phép chuyển đơn đã hủy (`canceled`) sang `delivered`

- **Feature:** FR-10 (Pool B) — **Mức độ:** Major
- **Test liên quan:** FR10-DT-24, FR10-DT-43
- **Các bước tái hiện:**
  1. Đăng nhập Admin, lấy token. Đăng nhập User, tạo đơn bằng `POST /api/checkout` (`{"total_amount":100000,"shipping_address":"x"}`) → `orderId`.
  2. `PUT /api/admin/orders/<orderId>/status` với `{"status":"canceled"}` → 200.
  3. `PUT /api/admin/orders/<orderId>/status` với `{"status":"delivered"}`.
- **Expected (SRS FR-10, README.md dòng 160):** `canceled` là trạng thái kết thúc, không được chuyển sang trạng thái nào khác; chuyển không hợp lệ trả lỗi.
- **Actual:** HTTP **200** "Order status updated"; đơn từ `canceled` thành `delivered` (và được tính vào doanh thu Dashboard).
- **Bằng chứng:** [evidence/api_results.json](https://github.com/nhaajtdajt/eshop-hw02-domain-testing/blob/main/features/FR-10/evidence/api_results.json) (FR10-DT-24, FR10-DT-43). Code: `backend/server.js:550-551` (nhánh `if (currentStatus === "canceled" && status === "delivered") isValidTransition = true`).
