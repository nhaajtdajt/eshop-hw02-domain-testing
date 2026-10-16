OTP không bao giờ hết hạn

- **Feature:** FR-03 — **Mức độ:** Major
- **Test liên quan:** FR03-DT-15
- **Các bước tái hiện:**
  1. Gọi `POST /api/forgot-password` cho một tài khoản, lưu `resetToken`.
  2. Chờ 5,5 phút (không yêu cầu OTP mới).
  3. Gọi `POST /api/reset-password` với OTP đó.
- **Expected (SRS SEC-07, dòng 284):** OTP có thời hạn; OTP hết hạn bị từ chối. (SRS không nêu số phút cụ thể.)
- **Actual:** HTTP 200, mật khẩu bị đổi. Code không lưu thời điểm tạo OTP và không kiểm tra hết hạn, nên OTP hợp lệ vô thời hạn cho tới khi bị dùng hoặc bị thay.
- **Bằng chứng:** [evidence/expiry_run.log](https://github.com/nhaajtdajt/eshop-hw02-domain-testing/blob/main/features/FR-03/evidence/expiry_run.log), [evidence/api_results_expiry.json](https://github.com/nhaajtdajt/eshop-hw02-domain-testing/blob/main/features/FR-03/evidence/api_results_expiry.json). Code: bảng `users` (`database.js:50-61`) không có cột hết hạn; `server.js:87-98`.
