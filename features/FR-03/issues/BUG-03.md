API reset-password chấp nhận mật khẩu rỗng/yếu (không validate phía server)

- **Feature:** FR-03 — **Mức độ:** Major (bypass ràng buộc bằng cách gọi API trực tiếp)
- **Test liên quan:** FR03-DT-16..DT-22, FR03-BV-09, BV-24, BV-25
- **Các bước tái hiện:**
  1. `curl -X POST localhost:3000/api/forgot-password -H "Content-Type: application/json" -d '{"email":"test@eshop.com"}'` → lấy `resetToken`.
  2. `curl -X POST localhost:3000/api/reset-password -H "Content-Type: application/json" -d '{"email":"test@eshop.com","resetToken":"<token>","newPassword":""}'`.
  3. Thử với `newPassword` = `Ab1!xyz`, `newpass1!`, `NEWPASS1!`, `Newpass!!`, `Newpass12`, `Newpass1#`.
- **Expected (SRS FR-03 dòng 58; FR-01 dòng 39):** Từ chối (HTTP 4xx), mật khẩu không đổi, vì mật khẩu mới phải tuân thủ FR-01.
- **Actual:** HTTP **200** "Password reset successfully"; mật khẩu bị đổi thành giá trị rỗng/yếu. Backend không kiểm tra độ mạnh.
- **Bằng chứng:** [evidence/api_results.json](https://github.com/nhaajtdajt/eshop-hw02-domain-testing/blob/main/features/FR-03/evidence/api_results.json) (FR03-DT-16..22, BV-09, BV-24, BV-25). Vị trí code: `backend/server.js:87-98`.
