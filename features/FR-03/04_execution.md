# FR-03: Thực thi test — kết quả

- **Ngày chạy:** 2026-10-16 (giờ máy: ~13:25–13:40, tương ứng 06:25–06:40 UTC trong log).
- **Môi trường:** Windows 11, Node v22.20.0, backend `localhost:3000`, web `localhost:5173` (Vite) trong trình duyệt tích hợp của Claude desktop; dữ liệu seed gốc của repo.
- **Cách chạy:**
  - **API:** `evidence/run_api_tests.js` (HTTP thật tới backend; chỉ dùng DB để reset/seed trạng thái và để kiểm chứng mật khẩu có đổi hay không). Kết quả thô: `evidence/api_results.json`.
  - **UI:** thao tác trên form `/forgot-password` bằng script trong trình duyệt (set giá trị input theo cách React nhận biết rồi bấm nút submit thật; `alert()` được ghi lại thay vì hiện hộp thoại). Kết quả UI được ghi trong bảng dưới. Ảnh: `evidence/step1_forgot_password_ui.jpg`, `evidence/step2_reset_form_ui.jpg`.
  - Với các test mật khẩu trên UI, dùng **OTP sai (`0000`)** để không làm đổi dữ liệu: nếu UI chấp nhận mật khẩu thì request được gửi và server trả "Mã OTP không đúng"; nếu UI từ chối thì xuất hiện thông báo "Mật khẩu quá yếu".
- **Quy ước kết quả tổng:** `Fail` nếu **bất kỳ** lớp đã chạy (UI hoặc API) lệch spec.

## 1. Kết quả theo test case

Ký hiệu: ✔ = đúng spec, ✘ = lệch spec, — = không áp dụng/không chạy.

### Domain Testing

| TC ID | UI | API | Kết quả | Actual tóm tắt | Bug |
|---|---|---|---|---|---|
| FR03-DT-01 | ✘ | ✘ | **Fail** | OTP sinh ra là **4 chữ số** (`4543`, `7523`...), nhãn "Mã OTP (4 số)" | BUG-01 |
| FR03-DT-02 | ✔ (HTML `required` chặn) | ✔ 404 | Pass | Không cấp OTP | |
| FR03-DT-03 | ✔ | ✔ 404 | Pass | Bị từ chối nhưng báo "User not found" (không nêu sai định dạng); ô email `type=text` nên không validate định dạng | BUG-07 (liên quan) |
| FR03-DT-04 | ✔ | ✔ 404 | Pass | "User not found" — lộ việc email chưa đăng ký (quan sát, không tính bug) | |
| FR03-DT-05 | ✔ | ✔ 404 | Pass | `"   "` bị coi như email không tồn tại | |
| FR03-DT-06 | ✔ | ✔ | Pass | Không lỗi server, không cấp OTP cho user nào | |
| FR03-DT-07 | ✘ | — | **Fail** | Với mật khẩu hợp lệ theo spec `Newpass1!` UI báo "Mật khẩu quá yếu" → không hoàn tất được. Chỉ hoàn tất được khi dùng mật khẩu **có khoảng trắng** (`New pass1`): đổi thành công, về `/login`, đăng nhập mật khẩu mới OK, mật khẩu cũ bị từ chối | BUG-02 |
| FR03-DT-08 | ✔ (`required`) | ✔ 400 | Pass | |
| FR03-DT-09 | ✔ | ✔ 400 | Pass | |
| FR03-DT-10 | ✔ | ✔ 400 | Pass | |
| FR03-DT-11 | ✔ | ✔ 400 | Pass | |
| FR03-DT-12 | ✔ | ✔ 400 | Pass | |
| FR03-DT-13 | — | ✔ 400 | Pass | OTP của B không đổi được mật khẩu A |
| FR03-DT-14 | — | ✔ | Pass | Lần 1 thành công (200); lần 2 bị từ chối (400), mật khẩu không đổi |
| FR03-DT-15 | — | (chờ) | (xem mục 3) | OTP hết hạn | |
| FR03-DT-16 | ✔ (`required`) | ✘ | **Fail** | API chấp nhận `newPassword = ""` (HTTP 200, mật khẩu bị đổi thành rỗng) | BUG-03 |
| FR03-DT-17 | ✔ | ✘ | **Fail** | API chấp nhận `Ab1!xyz` | BUG-03 |
| FR03-DT-18 | ✔ | ✘ | **Fail** | API chấp nhận `newpass1!` | BUG-03 |
| FR03-DT-19 | ✔ | ✘ | **Fail** | API chấp nhận `NEWPASS1!` | BUG-03 |
| FR03-DT-20 | ✔ | ✘ | **Fail** | API chấp nhận `Newpass!!` | BUG-03 |
| FR03-DT-21 | ✔ | ✘ | **Fail** | API chấp nhận `Newpass12` | BUG-03 |
| FR03-DT-22 | ✔ | ✘ | **Fail** | API chấp nhận `Newpass1#` (diễn giải chặt) | BUG-03 |
| FR03-DT-23 | ✘ | — | **Fail** | Không có trường Xác nhận mật khẩu; không thể test | BUG-04 |
| FR03-DT-24 | ✘ | — | **Fail** | Như trên | BUG-04 |
| FR03-DT-25 | ✘ | — | **Fail** | Như trên | BUG-04 |
| FR03-DT-26 | ✘ | — | **Fail** | Bước 1 không có "Bước 1 / 2" | BUG-05 |
| FR03-DT-27 | ✘ | — | **Fail** | Bước 2 không có "Bước 2 / 2" | BUG-05 |
| FR03-DT-28 | ✘ | — | **Fail** | Không có nút "Quay lại đăng nhập"; chỉ có "← Quay lại" (về bước 1) ở bước 2 | BUG-06 |
| FR03-DT-29 | ✘ | — | **Fail** | `input type="text"` | BUG-07 |
| FR03-DT-30 | ✘ | — | **Fail** | Nhãn không có `*` | BUG-08 |
| FR03-DT-31 | ✘ | — | **Fail** | Lỗi hiển thị bằng `alert()` của trình duyệt, không có vùng lỗi phía trên nút submit | BUG-09 |
| FR03-DT-32 | ✔ | — | Pass | Ô mật khẩu mới `type="password"` | |

### BVA

| TC ID | UI | API | Kết quả | Actual tóm tắt | Bug |
|---|---|---|---|---|---|
| FR03-BV-01 | ✔ | ✔ | Pass | OTP rỗng bị từ chối | |
| FR03-BV-02 | ✔ | ✔ | Pass | 1 chữ số bị từ chối | |
| FR03-BV-03 | ✔ | ✔ | Pass | 5 chữ số bị từ chối | |
| FR03-BV-04 | — | ✔ | Pass | OTP seed `123456` được chấp nhận (logic `reset-password` khớp đúng 6 chữ số) | |
| FR03-BV-05 | ✔ | ✔ | Pass | 7 chữ số bị từ chối | |
| FR03-BV-06 | — | ✔ | Pass | `012345` được chấp nhận (số 0 đầu) | |
| FR03-BV-07 | — | ✔ | Pass | `12345` (mất số 0 đầu) bị từ chối | |
| FR03-BV-08 | — | ✘ | **Fail** | 20 OTP sinh ra đều dài 4; giá trị từ 1001 đến 9316 (không bao giờ có OTP bắt đầu bằng 0 hay đủ 6 chữ số) | BUG-01 |
| FR03-BV-09 | ✔ | ✘ | **Fail** | API chấp nhận mật khẩu 7 ký tự | BUG-03 |
| FR03-BV-10 | ✘ | ✔ | **Fail** | UI từ chối mật khẩu 8 ký tự hợp lệ; API chấp nhận | BUG-02 |
| FR03-BV-11 | ✘ | ✔ | **Fail** | UI từ chối 9 ký tự hợp lệ | BUG-02 |
| FR03-BV-12 | ✘ | ✔ | **Fail** | UI từ chối 256 ký tự hợp lệ; API chấp nhận | BUG-02 |
| FR03-BV-13 | ✘ | ✔ | **Fail** | UI từ chối (đúng 1 chữ hoa) | BUG-02 |
| FR03-BV-14 | ✘ | ✔ | **Fail** | UI từ chối (đúng 1 chữ thường) | BUG-02 |
| FR03-BV-15 | ✘ | ✔ | **Fail** | UI từ chối (đúng 1 chữ số) | BUG-02 |
| FR03-BV-16 | ✘ | ✔ | **Fail** | UI từ chối (đúng 1 ký tự đặc biệt) | BUG-02 |
| FR03-BV-17 | ✘ | ✔ | **Fail** | UI từ chối khi ký tự đặc biệt là `@` | BUG-02 |
| FR03-BV-18 | ✘ | ✔ | **Fail** | `$` | BUG-02 |
| FR03-BV-19 | ✘ | ✔ | **Fail** | `!` | BUG-02 |
| FR03-BV-20 | ✘ | ✔ | **Fail** | `%` | BUG-02 |
| FR03-BV-21 | ✘ | ✔ | **Fail** | `*` | BUG-02 |
| FR03-BV-22 | ✘ | ✔ | **Fail** | `?` | BUG-02 |
| FR03-BV-23 | ✘ | ✔ | **Fail** | `&` | BUG-02 |
| FR03-BV-24 | ✔ | ✘ | **Fail** | API chấp nhận `+` (diễn giải chặt) | BUG-03 |
| FR03-BV-25 | ✔ | ✘ | **Fail** | API chấp nhận `"` (diễn giải chặt) | BUG-03 |
| FR03-BV-26 | ✘ | — | **Fail** | Không có trường xác nhận | BUG-04 |
| FR03-BV-27 | ✘ | — | **Fail** | Như trên | BUG-04 |
| FR03-BV-28 | ✘ | — | **Fail** | Như trên | BUG-04 |

## 2. Quan sát thêm (không tính vào số bug chính)
- OTP được trả thẳng trong response của `forgot-password` (đúng với môi trường demo của spec, nhưng không có bước gửi email).
- `forgot-password` trả 404 "User not found" cho email chưa đăng ký → có thể liệt kê email đã đăng ký.
- OTP sinh bằng `Math.random()` (không phải nguồn ngẫu nhiên an toàn mật mã).
- `reset-password` không kiểm tra thời hạn; mật khẩu lưu plaintext (ngoài phạm vi FR-03).

## 3. Test hết hạn OTP (FR03-DT-15)
- Cấp OTP cho một user riêng (`userc@eshop.com`, không bị các test khác reset), chờ **5,5 phút**, rồi gọi `reset-password`: **HTTP 200, mật khẩu bị đổi** → OTP vẫn dùng được → **Fail** (`BUG-10`).
- Hạn chế: SRS (SEC-07) chỉ nói "có thời hạn", không nêu số phút. Kết luận dựa trên cả quan sát (5,5 phút vẫn hợp lệ) lẫn code: bảng `users` chỉ có cột `reset_token`, không có thời điểm tạo/hết hạn, và `reset-password` không kiểm tra thời gian (`database.js:50-61`, `server.js:87-98`).
- Lần chạy đầu tiên của test này (sau ~12 giây) bị **loại bỏ** vì quá sớm, không đại diện cho "đã hết hạn" (xem `05_ai_gap.md`, bài học về kiểm tra tiền đề thời gian). Log: `evidence/expiry_run.log`.

## 4. Test khám phá thêm sau khi chạy (`added-after-run`)
Mục đích: khoanh vùng lỗi xử lý đầu vào của API. Không có bug mới.
| ID | Request | Kết quả |
|---|---|---|
| X-01 | `forgot-password` không có `email` | 404 "User not found", server vẫn sống |
| X-02 | `reset-password` không có `resetToken` | 400 "Invalid token or email" |
| X-03 | `resetToken` là object | 400, server vẫn sống |
| X-04 | `resetToken: null` | 400 |

## 5. Thống kê FR-03

| Hạng mục | Số lượng |
|---|---|
| Test case thiết kế | **60** (32 Domain Testing + 28 BVA) |
| Đã thực thi | 60 |
| Pass | 20 (DT: 13, BV: 7) |
| Fail | 40 (DT: 19, BV: 21) |
| Chưa thực thi | 0 |
| Bug phân biệt (nguyên nhân gốc) | **10** (BUG-01 … BUG-10, xem `06_bugs.md`) |
| Test khám phá thêm | 4 (X-01..X-04), không có bug |

Nhiều test Fail cùng một nguyên nhân gốc (ví dụ 14 test BV từ BV-10 đến BV-23 đều do BUG-02), nên số bug nhỏ hơn nhiều so với số test Fail.
