Lỗi hiển thị bằng `alert()`, không có vùng lỗi phía trên nút submit

- **Feature:** FR-03 — **Mức độ:** Minor
- **Test liên quan:** FR03-DT-31
- **Các bước tái hiện:** Nhập email chưa đăng ký (`nobody@eshop.com`) và bấm "Lấy mã OTP"; hoặc nhập mật khẩu yếu ở bước 2.
- **Expected (SRS FR-22 dòng 255):** Thông báo lỗi xuất hiện **trên** nút submit trong trang.
- **Actual:** Lỗi hiện qua hộp thoại `alert()` của trình duyệt ("Lỗi: User not found", "Mật khẩu quá yếu!…", "Mã OTP không đúng…"); không có vùng lỗi trong form.
- **Bằng chứng:** [evidence/ui_results.json](https://github.com/nhaajtdajt/eshop-hw02-domain-testing/blob/main/features/FR-03/evidence/ui_results.json) (`step1_cases`, `otp_cases_ui_result`). Code: `ForgotPassword.jsx:20,28,37`.
