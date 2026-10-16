Thiếu trường "Xác nhận mật khẩu mới"

- **Feature:** FR-03 — **Mức độ:** Major
- **Test liên quan:** FR03-DT-23..DT-25, FR03-BV-26..BV-28
- **Các bước tái hiện:** Mở `/forgot-password`, lấy OTP, quan sát form bước 2.
- **Expected (SRS FR-03 dòng 57, 59):** Có trường "Xác nhận mật khẩu mới"; hai trường mật khẩu phải khớp nhau.
- **Actual:** Chỉ có một ô "Mật khẩu mới" (và ô OTP). Không có xác nhận → người dùng gõ nhầm mật khẩu vẫn đổi được, không kiểm tra khớp.
- **Bằng chứng:** ![evidence/step2_reset_form_ui.jpg](https://raw.githubusercontent.com/nhaajtdajt/eshop-hw02-domain-testing/main/features/FR-03/evidence/step2_reset_form_ui.jpg). Code: `ForgotPassword.jsx:63-96`.
