# FR-03: Quên mật khẩu & Đặt lại mật khẩu (2 bước) — Phân tích

Phạm vi: Web (`/forgot-password`) và API (`POST /api/forgot-password`, `POST /api/reset-password`).
Màn hình quên mật khẩu trên Mobile không thuộc phạm vi FR-03 của bài này.

## 1. Yêu cầu theo SRS (`README.md`)

> **FR-03** (README.md dòng 46–60)
> Bước 1 — Lấy mã OTP:
> - Người dùng nhập địa chỉ Email đã đăng ký.
> - Hệ thống sinh mã OTP **6 chữ số ngẫu nhiên** và gửi qua Email (demo: hiển thị trực tiếp trên màn hình).
> - Giao diện phải hiển thị **chỉ báo bước (Step Indicator)** — ví dụ: "Bước 1 / 2".
> - Có nút **Quay lại đăng nhập**.
>
> Bước 2 — Đặt lại mật khẩu:
> - Người dùng nhập OTP, Mật khẩu mới, và **Xác nhận mật khẩu mới**.
> - Mật khẩu mới phải tuân thủ điều kiện như FR-01.
> - Hai trường mật khẩu phải khớp nhau.
> - OTP chỉ hợp lệ cho email đã yêu cầu, không thể dùng cho email khác.

Các yêu cầu liên quan ở mục khác:

> **FR-01** (dòng 36–43): mật khẩu tối thiểu 8 ký tự, ≥1 chữ hoa, ≥1 chữ thường, ≥1 chữ số, ≥1 ký tự đặc biệt trong `@ $ ! % * ? &`; email hợp lệ.
> **FR-22** (dòng 250–256): trường bắt buộc có `*`; Email dùng `type="email"`; Mật khẩu dùng `type="password"`; thông báo lỗi nằm **trên** nút submit; form ≥2 bước phải có Step Indicator.
> **SEC-07** (dòng 284): OTP tối thiểu 6 chữ số, **có thời hạn**, **vô hiệu hóa sau khi dùng**.
> **SEC-05** (dòng 282): truy vấn dùng parameterized query.

Điểm spec chưa định lượng: **thời hạn OTP** (SEC-07 chỉ nói "có thời hạn", không nêu số phút). Không thể tạo test biên thời gian chính xác; sẽ ghi là hạn chế và chỉ test "có hết hạn hay không" theo cách quan sát được.

## 2. Input / Điều kiện / Output

| Loại | Tên | Mô tả | Ràng buộc theo spec |
|---|---|---|---|
| Input (bước 1) | `email` | Email đã đăng ký | Đúng định dạng email; phải là email tồn tại trong hệ thống |
| Input (bước 2) | `otp` (`resetToken`) | Mã OTP | Đúng 6 chữ số; khớp OTP đã cấp cho **chính email đó** |
| Input (bước 2) | `newPassword` | Mật khẩu mới | Theo FR-01 (≥8 ký tự, hoa, thường, số, ký tự đặc biệt `@$!%*?&`) |
| Input (bước 2) | `confirmPassword` | Xác nhận mật khẩu mới | Phải bằng `newPassword` |
| Hành động | "Lấy mã OTP", "Đặt lại mật khẩu", "Quay lại đăng nhập" | | |
| Tiền đề | Tài khoản tồn tại (`test@eshop.com` / `Test1234!`) | | |
| Trạng thái | OTP đã cấp / đã dùng / hết hạn | | OTP hết hạn và đã dùng thì không dùng lại được (SEC-07) |
| Output | Thông báo, chuyển bước, đổi mật khẩu trong DB | | Bước 1: hiện OTP 6 số trên màn hình; bước 2 thành công: về `/login`, đăng nhập được bằng mật khẩu mới |
| Output UI | Step Indicator "Bước x / 2" | | Hiển thị ở cả 2 bước |

## 3. Spec vs Code (giả thuyết cần kiểm chứng)

Nguồn code: `backend/server.js:68-98`, `frontend-web/src/pages/ForgotPassword.jsx`, `frontend-web/src/pages/Login.jsx:50`.

| # | Spec nói | Code làm | File:dòng | Trạng thái |
|---|---|---|---|---|
| H1 | OTP 6 chữ số | `Math.floor(1000 + Math.random()*9000)` → 4 chữ số (1000–9999) | server.js:72 | Chưa kiểm chứng |
| H2 | Nhãn UI nhất quán với spec | Nhãn "Mã OTP (4 số)" | ForgotPassword.jsx:69 | Chưa kiểm chứng |
| H3 | Mật khẩu mới theo FR-01 (có ký tự đặc biệt `@$!%*?&`) | Regex `(?=.*\s)` đòi khoảng trắng và `[A-Za-z\d\s]` cấm ký tự đặc biệt | ForgotPassword.jsx:26 | Chưa kiểm chứng |
| H4 | Có trường Xác nhận mật khẩu mới, hai trường khớp | Chỉ có 1 trường mật khẩu | ForgotPassword.jsx:78-87 | Chưa kiểm chứng |
| H5 | Step Indicator "Bước 1 / 2" | Không có | ForgotPassword.jsx | Chưa kiểm chứng |
| H6 | Nút "Quay lại đăng nhập" | Chỉ có nút "← Quay lại" (về bước 1); không có link về đăng nhập | ForgotPassword.jsx:93 | Chưa kiểm chứng |
| H7 | Email dùng `type="email"` (FR-22) | `type="text"` | ForgotPassword.jsx:50 | Chưa kiểm chứng |
| H8 | Trường bắt buộc có `*` (FR-22) | Nhãn không có `*` | ForgotPassword.jsx:48,69,79 | Chưa kiểm chứng |
| H9 | OTP có thời hạn (SEC-07) | Không lưu thời điểm tạo; không kiểm tra hết hạn | server.js:68-98 | Chưa kiểm chứng |
| H10 | OTP vô hiệu sau khi dùng | `reset_token = NULL` sau khi dùng — có vẻ đúng | server.js:90 | Chưa kiểm chứng |
| H11 | Mật khẩu mới theo FR-01 được kiểm tra | Backend `reset-password` không kiểm tra độ mạnh; chỉ UI (và UI sai, H3) | server.js:87-98 | Chưa kiểm chứng |
| H12 | OTP chỉ dùng cho email đã yêu cầu | SQL `WHERE email=? AND reset_token=?` → đúng ràng buộc theo email | server.js:90 | Chưa kiểm chứng |
| H13 | Validate đầu vào | `resetToken` rỗng/`null`/thiếu → `reset_token = NULL` khớp user có `reset_token IS NULL`? (`= NULL` luôn false trong SQL nên có thể an toàn) | server.js:90 | Cần thử |
| H14 | Không để lộ thông tin (khuyến nghị) | Email không tồn tại → 404 "User not found" (liệt kê được email) | server.js:71 | Quan sát |
| H15 | Email không hợp lệ thì báo lỗi rõ | Backend crash nếu `err` ở `forgot-password`? `if (!user)` xử lý; `err` bị bỏ qua ở `db.get` | server.js:70-71 | Cần thử |
| H16 | Thông báo lỗi phía trên nút submit (FR-22) | Bước 1 dùng `alert()`; bước 2 `alert()` | ForgotPassword.jsx:20,28,37 | Chưa kiểm chứng |
| H17 | OTP đủ entropy | Dùng `Math.random()` (không an toàn mật mã) | server.js:72 | Quan sát (SEC-07) |
| H18 | Sau khi đổi mật khẩu có thể đăng nhập bằng mật khẩu mới | Mật khẩu lưu plaintext (SEC-01 ngoài phạm vi, chỉ ghi chú) | server.js:90 | Ngoài phạm vi |

Ghi chú: H18 và H14 thuộc yêu cầu của feature khác/khuyến nghị; chỉ dùng để làm test thêm khi chạy, không gom vào số bug chính nếu spec FR-03 không nói.

## 4. Nhận xét ảnh hưởng thiết kế test

- Với H1, spec yêu cầu OTP **6** chữ số, hệ thống thật sinh **4**. Biên BVA lấy theo spec (5/6/7); khi thực thi sẽ kiểm tra thêm cả OTP 4 chữ số do hệ thống sinh ra để thấy sự lệch.
- Vì UI và API là hai lớp ràng buộc, mỗi test cần chỉ rõ chạy ở lớp nào: **UI** (web form) hay **API** (curl). Nhiều ràng buộc (xác nhận mật khẩu, độ mạnh mật khẩu mới) chỉ có hoặc không có ở một lớp.
- Dữ liệu sạch: chạy `node database.js` trước các test thay đổi mật khẩu để khôi phục `test@eshop.com` / `Test1234!`.
