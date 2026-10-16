Áp mã không cần đăng nhập và bỏ `user_id` là qua mặt kiểm tra lượt dùng

- **Feature:** Mobile FR-09 (dùng chung backend) — **Mức độ:** Major
- **Test liên quan:** MFR-DT-22, MFR-DT-24
- **Các bước tái hiện:**
  1. `POST /api/apply-coupon` **không có** header `Authorization` với `{"code":"SAVE10","total_amount":400000}` → áp dụng thành công.
  2. Cho user đã dùng `SAVE10` một lần (đã thanh toán), gọi lại `apply-coupon` **không** gửi `user_id` (hoặc không token).
- **Expected (SRS FR-09, dòng 119–120; SEC-02, dòng 279):** C4: phải đăng nhập (JWT hợp lệ); C5: số lần đã dùng của user < `max_uses_per_user`.
- **Actual:** HTTP 200 trong cả hai trường hợp: endpoint không yêu cầu token; `user_id` do client tự gửi nên chỉ cần bỏ trường này là không còn bị kiểm tra lượt dùng.
- **Bằng chứng:** [evidence/api_results.json](https://github.com/nhaajtdajt/eshop-hw02-domain-testing/blob/main/features/Mobile-FR-08-09/evidence/api_results.json) (DT-22, DT-24). Code: `backend/server.js:363-433` (không có `authenticateToken`; kiểm tra lượt dùng chỉ khi `if (user_id)`).
