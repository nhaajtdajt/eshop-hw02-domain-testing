Trường bắt buộc không có ký hiệu `*`

- **Feature:** FR-03 — **Mức độ:** Minor
- **Test liên quan:** FR03-DT-30
- **Các bước tái hiện:** Mở `/forgot-password` và quan sát nhãn "Nhập Email của bạn", "Mã OTP", "Mật khẩu mới".
- **Expected (SRS FR-22 dòng 252):** Tất cả trường bắt buộc có `*` cạnh nhãn.
- **Actual:** Không nhãn nào có `*` (dù các ô đều `required`).
- **Bằng chứng:** ![evidence/step1_forgot_password_ui.jpg](https://raw.githubusercontent.com/nhaajtdajt/eshop-hw02-domain-testing/main/features/FR-03/evidence/step1_forgot_password_ui.jpg), ![evidence/step2_reset_form_ui.jpg](https://raw.githubusercontent.com/nhaajtdajt/eshop-hw02-domain-testing/main/features/FR-03/evidence/step2_reset_form_ui.jpg).
