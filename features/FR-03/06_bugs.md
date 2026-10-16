# FR-03: Bug report

Môi trường chung: Windows 11, Node v22.20.0, Backend `http://localhost:3000`, Web `http://localhost:5173` (trình duyệt tích hợp Claude desktop, Chromium), dữ liệu seed gốc. Ngày phát hiện: 2026-10-16. Spec = `README.md` (SRS). Mức độ: Critical > Major > Minor.

Trạng thái GitHub Issues: **đã đăng** #1–#10 tại https://github.com/nhaajtdajt/eshop-hw02-domain-testing/issues (nhãn `bug`). Nội dung từng issue nằm trong `features/FR-03/issues/`.

| Bug | Tiêu đề | Mức độ | Test liên quan | Issue |
|---|---|---|---|---|
| BUG-01 | OTP được sinh ra chỉ có 4 chữ số thay vì 6 | Major | DT-01, BV-08 | #1 |
| BUG-02 | Form đặt lại mật khẩu từ chối mọi mật khẩu hợp lệ theo spec | Critical | DT-07, BV-10..BV-23 | #2 |
| BUG-03 | API reset-password chấp nhận mật khẩu rỗng/yếu (không validate phía server) | Major | DT-16..22, BV-09, BV-24, BV-25 | #3 |
| BUG-04 | Thiếu trường "Xác nhận mật khẩu mới" | Major | DT-23..25, BV-26..28 | #4 |
| BUG-05 | Thiếu Step Indicator "Bước x / 2" | Minor | DT-26, DT-27 | #5 |
| BUG-06 | Thiếu nút "Quay lại đăng nhập" | Minor | DT-28 | #6 |
| BUG-07 | Ô email dùng `type="text"` thay vì `type="email"` | Minor | DT-29 | #7 |
| BUG-08 | Trường bắt buộc không có ký hiệu `*` | Minor | DT-30 | #8 |
| BUG-09 | Lỗi hiển thị bằng `alert()`, không có vùng lỗi phía trên nút submit | Minor | DT-31 | #9 |
| BUG-10 | OTP không bao giờ hết hạn | Major | DT-15 | #10 |

---

### BUG-01: OTP được sinh ra chỉ có 4 chữ số thay vì 6
- **Feature:** FR-03 (Pool A) — **Mức độ:** Major
- **Test liên quan:** FR03-DT-01, FR03-BV-08
- **Các bước tái hiện:**
  1. Mở `http://localhost:5173/forgot-password`.
  2. Nhập `test@eshop.com`, bấm "Lấy mã OTP".
  3. Quan sát mã OTP hiển thị và nhãn ô nhập OTP ở bước 2.
- **Expected (SRS FR-03, README.md dòng 51; SEC-07, dòng 284):** OTP gồm **6 chữ số** ngẫu nhiên, tối thiểu 6 chữ số.
- **Actual:** OTP chỉ có **4 chữ số** (ví dụ `4543`, `7523`; 20 lần gọi API cho giá trị từ 1001 đến 9316, độ dài luôn 4). Nhãn ô nhập ghi "Mã OTP (4 số)". Chỉ có 9000 giá trị khả dĩ.
- **Bằng chứng:** `evidence/step2_reset_form_ui.jpg`, `evidence/api_results.json` (FR03-DT-01, FR03-BV-08). Vị trí code: `backend/server.js:72`, `frontend-web/src/pages/ForgotPassword.jsx:69`.

### BUG-02: Form đặt lại mật khẩu từ chối mọi mật khẩu hợp lệ theo spec
- **Feature:** FR-03 — **Mức độ:** Critical (người dùng không thể đặt lại mật khẩu bằng mật khẩu đúng chuẩn)
- **Test liên quan:** FR03-DT-07, FR03-BV-10..BV-23
- **Các bước tái hiện:**
  1. Mở `/forgot-password`, nhập `test@eshop.com`, bấm "Lấy mã OTP".
  2. Nhập đúng OTP vừa hiển thị và mật khẩu mới `Newpass1!` (đủ 8 ký tự, hoa, thường, số, ký tự đặc biệt `!`).
  3. Bấm "Đặt lại mật khẩu".
  4. Lặp lại với `Ab1!wxyz`, `Newpass1@`, … (mọi ký tự trong `@$!%*?&`).
- **Expected (SRS FR-03 dòng 58 + FR-01 dòng 39):** Mật khẩu đáp ứng FR-01 được chấp nhận và đổi mật khẩu thành công.
- **Actual:** Hiện hộp thoại "Mật khẩu quá yếu! Phải dài tối thiểu 8 ký tự, gồm chữ hoa, chữ thường, số và KÝ TỰ ĐẶC BIỆT." với **mọi** mật khẩu hợp lệ. Regex phía client `/^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*\s)[A-Za-z\d\s]{8,}$/` đòi có khoảng trắng và chỉ cho phép `A-Za-z`, số, khoảng trắng nên cấm mọi ký tự đặc biệt. Chỉ mật khẩu **có khoảng trắng** mới qua (ví dụ `New pass1`), mâu thuẫn với chính thông báo lỗi.
- **Bằng chứng:** `evidence/ui_results.json` (mục `password_cases_ui_result`). Vị trí code: `frontend-web/src/pages/ForgotPassword.jsx:26`.

### BUG-03: API reset-password chấp nhận mật khẩu rỗng/yếu (không validate phía server)
- **Feature:** FR-03 — **Mức độ:** Major (bypass ràng buộc bằng cách gọi API trực tiếp)
- **Test liên quan:** FR03-DT-16..DT-22, FR03-BV-09, BV-24, BV-25
- **Các bước tái hiện:**
  1. `curl -X POST localhost:3000/api/forgot-password -H "Content-Type: application/json" -d '{"email":"test@eshop.com"}'` → lấy `resetToken`.
  2. `curl -X POST localhost:3000/api/reset-password -H "Content-Type: application/json" -d '{"email":"test@eshop.com","resetToken":"<token>","newPassword":""}'`.
  3. Thử với `newPassword` = `Ab1!xyz`, `newpass1!`, `NEWPASS1!`, `Newpass!!`, `Newpass12`, `Newpass1#`.
- **Expected (SRS FR-03 dòng 58; FR-01 dòng 39):** Từ chối (HTTP 4xx), mật khẩu không đổi, vì mật khẩu mới phải tuân thủ FR-01.
- **Actual:** HTTP **200** "Password reset successfully"; mật khẩu bị đổi thành giá trị rỗng/yếu. Backend không kiểm tra độ mạnh.
- **Bằng chứng:** `evidence/api_results.json` (FR03-DT-16..22, BV-09, BV-24, BV-25). Vị trí code: `backend/server.js:87-98`.

### BUG-04: Thiếu trường "Xác nhận mật khẩu mới"
- **Feature:** FR-03 — **Mức độ:** Major
- **Test liên quan:** FR03-DT-23..DT-25, FR03-BV-26..BV-28
- **Các bước tái hiện:** Mở `/forgot-password`, lấy OTP, quan sát form bước 2.
- **Expected (SRS FR-03 dòng 57, 59):** Có trường "Xác nhận mật khẩu mới"; hai trường mật khẩu phải khớp nhau.
- **Actual:** Chỉ có một ô "Mật khẩu mới" (và ô OTP). Không có xác nhận → người dùng gõ nhầm mật khẩu vẫn đổi được, không kiểm tra khớp.
- **Bằng chứng:** `evidence/step2_reset_form_ui.jpg`. Code: `ForgotPassword.jsx:63-96`.

### BUG-05: Thiếu Step Indicator "Bước x / 2"
- **Feature:** FR-03 — **Mức độ:** Minor
- **Test liên quan:** FR03-DT-26, FR03-DT-27
- **Các bước tái hiện:** Mở `/forgot-password` (bước 1), sau đó lấy OTP (bước 2); quan sát tiêu đề/form.
- **Expected (SRS FR-03 dòng 52; FR-22 dòng 256):** Hiển thị chỉ báo bước, ví dụ "Bước 1 / 2", "Bước 2 / 2".
- **Actual:** Không có chỉ báo bước ở cả hai bước.
- **Bằng chứng:** `evidence/step1_forgot_password_ui.jpg`, `evidence/step2_reset_form_ui.jpg`.

### BUG-06: Thiếu nút "Quay lại đăng nhập"
- **Feature:** FR-03 — **Mức độ:** Minor
- **Test liên quan:** FR03-DT-28
- **Các bước tái hiện:** Mở `/forgot-password`; tìm nút quay về đăng nhập ở bước 1 và bước 2.
- **Expected (SRS FR-03 dòng 53):** Có nút "Quay lại đăng nhập".
- **Actual:** Bước 1 không có nút nào ngoài "Lấy mã OTP". Bước 2 chỉ có "← Quay lại" (trở về bước 1, không về đăng nhập), và nút này cùng màu xanh lá với nút chính.
- **Bằng chứng:** `evidence/step1_forgot_password_ui.jpg`, `evidence/step2_reset_form_ui.jpg`.

### BUG-07: Ô email dùng `type="text"` thay vì `type="email"`
- **Feature:** FR-03 — **Mức độ:** Minor
- **Test liên quan:** FR03-DT-29 (liên quan DT-03)
- **Các bước tái hiện:** Mở `/forgot-password`, kiểm tra thuộc tính `type` của ô email (DevTools) hoặc nhập `testeshop.com` rồi gửi.
- **Expected (SRS FR-22 dòng 253):** Trường Email dùng `type="email"` (validate định dạng HTML5).
- **Actual:** `type="text"`; chuỗi sai định dạng vẫn được gửi lên server (server trả "User not found").
- **Bằng chứng:** `evidence/ui_results.json` (`step1_dom`). Code: `ForgotPassword.jsx:50`.

### BUG-08: Trường bắt buộc không có ký hiệu `*`
- **Feature:** FR-03 — **Mức độ:** Minor
- **Test liên quan:** FR03-DT-30
- **Các bước tái hiện:** Mở `/forgot-password` và quan sát nhãn "Nhập Email của bạn", "Mã OTP", "Mật khẩu mới".
- **Expected (SRS FR-22 dòng 252):** Tất cả trường bắt buộc có `*` cạnh nhãn.
- **Actual:** Không nhãn nào có `*` (dù các ô đều `required`).
- **Bằng chứng:** `evidence/step1_forgot_password_ui.jpg`, `evidence/step2_reset_form_ui.jpg`.

### BUG-09: Lỗi hiển thị bằng `alert()`, không có vùng lỗi phía trên nút submit
- **Feature:** FR-03 — **Mức độ:** Minor
- **Test liên quan:** FR03-DT-31
- **Các bước tái hiện:** Nhập email chưa đăng ký (`nobody@eshop.com`) và bấm "Lấy mã OTP"; hoặc nhập mật khẩu yếu ở bước 2.
- **Expected (SRS FR-22 dòng 255):** Thông báo lỗi xuất hiện **trên** nút submit trong trang.
- **Actual:** Lỗi hiện qua hộp thoại `alert()` của trình duyệt ("Lỗi: User not found", "Mật khẩu quá yếu!…", "Mã OTP không đúng…"); không có vùng lỗi trong form.
- **Bằng chứng:** `evidence/ui_results.json` (`step1_cases`, `otp_cases_ui_result`). Code: `ForgotPassword.jsx:20,28,37`.

### BUG-10: OTP không bao giờ hết hạn
- **Feature:** FR-03 — **Mức độ:** Major
- **Test liên quan:** FR03-DT-15
- **Các bước tái hiện:**
  1. Gọi `POST /api/forgot-password` cho một tài khoản, lưu `resetToken`.
  2. Chờ 5,5 phút (không yêu cầu OTP mới).
  3. Gọi `POST /api/reset-password` với OTP đó.
- **Expected (SRS SEC-07, dòng 284):** OTP có thời hạn; OTP hết hạn bị từ chối. (SRS không nêu số phút cụ thể.)
- **Actual:** HTTP 200, mật khẩu bị đổi. Code không lưu thời điểm tạo OTP và không kiểm tra hết hạn, nên OTP hợp lệ vô thời hạn cho tới khi bị dùng hoặc bị thay.
- **Bằng chứng:** `evidence/expiry_run.log`, `evidence/api_results_expiry.json`. Code: bảng `users` (`database.js:50-61`) không có cột hết hạn; `server.js:87-98`.

---

## Quan sát (không tính là bug của FR-03)
- Không giới hạn số lần đoán OTP: 300 lần đoán sai liên tiếp đều trả 400, không khóa (kết hợp BUG-01 → đoán OTP 4 chữ số trong vài giây). SRS không yêu cầu rate limit cụ thể nên ghi là quan sát.
- `forgot-password` trả 404 "User not found" → lộ email nào đã đăng ký.
- Email phân biệt hoa/thường (`TEST@ESHOP.COM` → 404); SRS không nêu.
- OTP sinh bằng `Math.random()`; mật khẩu lưu plaintext (thuộc SEC-01, ngoài FR-03).
