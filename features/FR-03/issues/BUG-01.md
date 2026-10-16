OTP được sinh ra chỉ có 4 chữ số thay vì 6

- **Feature:** FR-03 (Pool A) — **Mức độ:** Major
- **Test liên quan:** FR03-DT-01, FR03-BV-08
- **Các bước tái hiện:**
  1. Mở `http://localhost:5173/forgot-password`.
  2. Nhập `test@eshop.com`, bấm "Lấy mã OTP".
  3. Quan sát mã OTP hiển thị và nhãn ô nhập OTP ở bước 2.
- **Expected (SRS FR-03, README.md dòng 51; SEC-07, dòng 284):** OTP gồm **6 chữ số** ngẫu nhiên, tối thiểu 6 chữ số.
- **Actual:** OTP chỉ có **4 chữ số** (ví dụ `4543`, `7523`; 20 lần gọi API cho giá trị từ 1001 đến 9316, độ dài luôn 4). Nhãn ô nhập ghi "Mã OTP (4 số)". Chỉ có 9000 giá trị khả dĩ.
- **Bằng chứng:** ![evidence/step2_reset_form_ui.jpg](https://raw.githubusercontent.com/nhaajtdajt/eshop-hw02-domain-testing/main/features/FR-03/evidence/step2_reset_form_ui.jpg), [evidence/api_results.json](https://github.com/nhaajtdajt/eshop-hw02-domain-testing/blob/main/features/FR-03/evidence/api_results.json) (FR03-DT-01, FR03-BV-08). Vị trí code: `backend/server.js:72`, `frontend-web/src/pages/ForgotPassword.jsx:69`.
