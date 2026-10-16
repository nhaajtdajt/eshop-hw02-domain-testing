Form đặt lại mật khẩu từ chối mọi mật khẩu hợp lệ theo spec

- **Feature:** FR-03 — **Mức độ:** Critical (người dùng không thể đặt lại mật khẩu bằng mật khẩu đúng chuẩn)
- **Test liên quan:** FR03-DT-07, FR03-BV-10..BV-23
- **Các bước tái hiện:**
  1. Mở `/forgot-password`, nhập `test@eshop.com`, bấm "Lấy mã OTP".
  2. Nhập đúng OTP vừa hiển thị và mật khẩu mới `Newpass1!` (đủ 8 ký tự, hoa, thường, số, ký tự đặc biệt `!`).
  3. Bấm "Đặt lại mật khẩu".
  4. Lặp lại với `Ab1!wxyz`, `Newpass1@`, … (mọi ký tự trong `@$!%*?&`).
- **Expected (SRS FR-03 dòng 58 + FR-01 dòng 39):** Mật khẩu đáp ứng FR-01 được chấp nhận và đổi mật khẩu thành công.
- **Actual:** Hiện hộp thoại "Mật khẩu quá yếu! Phải dài tối thiểu 8 ký tự, gồm chữ hoa, chữ thường, số và KÝ TỰ ĐẶC BIỆT." với **mọi** mật khẩu hợp lệ. Regex phía client `/^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*\s)[A-Za-z\d\s]{8,}$/` đòi có khoảng trắng và chỉ cho phép `A-Za-z`, số, khoảng trắng nên cấm mọi ký tự đặc biệt. Chỉ mật khẩu **có khoảng trắng** mới qua (ví dụ `New pass1`), mâu thuẫn với chính thông báo lỗi.
- **Bằng chứng:** [evidence/ui_results.json](https://github.com/nhaajtdajt/eshop-hw02-domain-testing/blob/main/features/FR-03/evidence/ui_results.json) (mục `password_cases_ui_result`). Vị trí code: `frontend-web/src/pages/ForgotPassword.jsx:26`.
