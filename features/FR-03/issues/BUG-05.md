Thiếu Step Indicator "Bước x / 2"

- **Feature:** FR-03 — **Mức độ:** Minor
- **Test liên quan:** FR03-DT-26, FR03-DT-27
- **Các bước tái hiện:** Mở `/forgot-password` (bước 1), sau đó lấy OTP (bước 2); quan sát tiêu đề/form.
- **Expected (SRS FR-03 dòng 52; FR-22 dòng 256):** Hiển thị chỉ báo bước, ví dụ "Bước 1 / 2", "Bước 2 / 2".
- **Actual:** Không có chỉ báo bước ở cả hai bước.
- **Bằng chứng:** ![evidence/step1_forgot_password_ui.jpg](https://raw.githubusercontent.com/nhaajtdajt/eshop-hw02-domain-testing/main/features/FR-03/evidence/step1_forgot_password_ui.jpg), ![evidence/step2_reset_form_ui.jpg](https://raw.githubusercontent.com/nhaajtdajt/eshop-hw02-domain-testing/main/features/FR-03/evidence/step2_reset_form_ui.jpg).
