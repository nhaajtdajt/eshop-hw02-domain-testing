# FR-03: Quên & Đặt lại mật khẩu — Domain Testing

Oracle: SRS `README.md` (FR-03 dòng 46–60, FR-01 dòng 36–43, FR-22 dòng 250–256, SEC-07 dòng 284). Chi tiết ở `01_analysis.md`.

Quy ước:
- Mã lớp: `EC-<input>-V<n>` (hợp lệ), `EC-<input>-I<n>` (không hợp lệ).
- Mỗi test không hợp lệ chỉ chứa **một** lớp I; các input còn lại lấy giá trị hợp lệ "chuẩn" bên dưới, để khi fail biết đúng nguyên nhân.
- Cột **Lớp chạy**: `UI` = form web `/forgot-password`; `API` = gọi trực tiếp `localhost:3000`. Một số ràng buộc chỉ kiểm được ở một lớp (ví dụ trường Xác nhận mật khẩu chỉ có trên UI).

Dữ liệu chuẩn (giá trị hợp lệ mặc định):
- `email` = `test@eshop.com` (đã seed), `otp` = OTP vừa được cấp cho email đó, `newPassword` = `Newpass1!`, `confirmPassword` = `Newpass1!`.
- Dữ liệu sạch: chạy `node database.js` rồi `node server.js` trước nhóm test thay đổi mật khẩu.

## 1. Lớp tương đương

### 1.1 `email` (Bước 1)
| Mã lớp | Loại | Mô tả lớp | Ví dụ đại diện |
|---|---|---|---|
| EC-email-V1 | Hợp lệ | Email đúng định dạng và đã đăng ký | `test@eshop.com` |
| EC-email-I1 | Không hợp lệ | Rỗng | (trống) |
| EC-email-I2 | Không hợp lệ | Sai định dạng (thiếu `@` / thiếu miền) | `testeshop.com`, `test@` |
| EC-email-I3 | Không hợp lệ | Đúng định dạng nhưng chưa đăng ký | `nobody@eshop.com` |
| EC-email-I4 | Không hợp lệ | Chỉ gồm khoảng trắng | `"   "` |
| EC-email-I5 | Không hợp lệ | Chứa ký tự đặc biệt/SQL | `' OR '1'='1` |

### 1.2 `otp` (Bước 2)
| Mã lớp | Loại | Mô tả lớp | Ví dụ đại diện |
|---|---|---|---|
| EC-otp-V1 | Hợp lệ | Đúng 6 chữ số, là OTP đã cấp cho **chính email này**, còn hạn, chưa dùng | OTP vừa nhận |
| EC-otp-I1 | Không hợp lệ | Rỗng | (trống) |
| EC-otp-I2 | Không hợp lệ | Ít hơn 6 chữ số (chỉ gồm số) | `12345` |
| EC-otp-I3 | Không hợp lệ | Nhiều hơn 6 chữ số (chỉ gồm số) | `1234567` |
| EC-otp-I4 | Không hợp lệ | Đủ 6 ký tự nhưng có chữ cái/ký tự không phải số | `12a45!` |
| EC-otp-I5 | Không hợp lệ | Đủ 6 chữ số nhưng **sai giá trị** | OTP thật ± 1 |
| EC-otp-I6 | Không hợp lệ | OTP hợp lệ của **email khác** | OTP của user B dùng cho email A |
| EC-otp-I7 | Không hợp lệ | OTP **đã dùng** rồi (dùng lại lần 2) | OTP đã reset thành công |
| EC-otp-I8 | Không hợp lệ | OTP **hết hạn** (SEC-07) | OTP cấp từ lâu |

### 1.3 `newPassword` (Bước 2) — theo FR-01
| Mã lớp | Loại | Mô tả lớp | Ví dụ đại diện |
|---|---|---|---|
| EC-pw-V1 | Hợp lệ | ≥8 ký tự, có hoa, thường, số và ký tự đặc biệt thuộc `@$!%*?&` | `Newpass1!` |
| EC-pw-I1 | Không hợp lệ | Rỗng | (trống) |
| EC-pw-I2 | Không hợp lệ | Dưới 8 ký tự (đủ 4 loại) | `Ab1!xyz` |
| EC-pw-I3 | Không hợp lệ | Thiếu chữ hoa | `newpass1!` |
| EC-pw-I4 | Không hợp lệ | Thiếu chữ thường | `NEWPASS1!` |
| EC-pw-I5 | Không hợp lệ | Thiếu chữ số | `Newpass!!` |
| EC-pw-I6 | Không hợp lệ | Thiếu ký tự đặc biệt | `Newpass12` |
| EC-pw-I7 | Không hợp lệ (diễn giải chặt) | Ký tự đặc biệt nằm **ngoài** tập `@$!%*?&` và không có ký tự nào trong tập | `Newpass1#` |

Ghi chú EC-pw-I7: FR-01 liệt kê tập `@ $ ! % * ? &`; diễn giải chặt là chỉ các ký tự này tính là "đặc biệt". Đây là điểm spec có thể hiểu hai cách, nên khi kết quả lệch sẽ ghi "theo diễn giải chặt", không tính ngay là bug chắc chắn.

### 1.4 `confirmPassword` (Bước 2)
| Mã lớp | Loại | Mô tả lớp | Ví dụ đại diện |
|---|---|---|---|
| EC-cf-V1 | Hợp lệ | Giống hệt `newPassword` | `Newpass1!` |
| EC-cf-I1 | Không hợp lệ | Khác `newPassword` hoàn toàn | `Other123!` |
| EC-cf-I2 | Không hợp lệ | Rỗng (khi `newPassword` có giá trị) | (trống) |
| EC-cf-I3 | Không hợp lệ | Chỉ khác hoa/thường (phân biệt chữ hoa thường) | `newpass1!` |

### 1.5 Yêu cầu giao diện của feature (GUI)
| Mã lớp | Mô tả |
|---|---|
| EC-gui-1 | Step Indicator "Bước 1 / 2" hiển thị ở bước 1 |
| EC-gui-2 | Step Indicator "Bước 2 / 2" hiển thị ở bước 2 |
| EC-gui-3 | Nút "Quay lại đăng nhập" có ở form |
| EC-gui-4 | Trường email dùng `type="email"` (FR-22) |
| EC-gui-5 | Trường bắt buộc có ký hiệu `*` (FR-22) |
| EC-gui-6 | Thông báo lỗi nằm **trên** nút submit (FR-22) |
| EC-gui-7 | Trường mật khẩu dùng `type="password"` (FR-22) |

## 2. Test case

Expected luôn theo **spec**. "Mật khẩu không đổi" nghĩa là đăng nhập bằng `Test1234!` vẫn thành công và mật khẩu mới không đăng nhập được.

### 2.1 Bước 1 — Lấy OTP
| TC ID | Lớp phủ | Tiền đề | Dữ liệu vào | Expected (theo spec) | Lớp chạy | Truy vết |
|---|---|---|---|---|---|---|
| FR03-DT-01 | EC-email-V1 | DB sạch | email = `test@eshop.com` | Sinh OTP **6 chữ số**, hiển thị trên màn hình, chuyển sang bước 2 | UI+API | FR-03 B1 |
| FR03-DT-02 | EC-email-I1 | — | email rỗng | Từ chối, báo lỗi, không sinh OTP, ở lại bước 1 | UI+API | FR-03 B1 |
| FR03-DT-03 | EC-email-I2 | — | `testeshop.com` | Từ chối vì sai định dạng, ở lại bước 1 | UI+API | FR-03 B1, FR-22 |
| FR03-DT-04 | EC-email-I3 | — | `nobody@eshop.com` | Từ chối, báo lỗi rõ ràng, không cấp OTP | UI+API | FR-03 B1 |
| FR03-DT-05 | EC-email-I4 | — | `"   "` (3 khoảng trắng) | Từ chối, báo lỗi, ở lại bước 1 | UI+API | FR-03 B1 |
| FR03-DT-06 | EC-email-I5 | — | `' OR '1'='1` | Từ chối như email không hợp lệ; không lỗi server, không cấp OTP cho user nào | API | SEC-05 |

### 2.2 Bước 2 — Đặt lại mật khẩu (happy path)
| TC ID | Lớp phủ | Tiền đề | Dữ liệu vào | Expected (theo spec) | Lớp chạy | Truy vết |
|---|---|---|---|---|---|---|
| FR03-DT-07 | EC-email-V1, EC-otp-V1, EC-pw-V1, EC-cf-V1 | Đã có OTP của `test@eshop.com` | otp thật, `Newpass1!`, `Newpass1!` | Đổi mật khẩu thành công, về `/login`; đăng nhập `Newpass1!` OK, `Test1234!` bị từ chối; OTP bị vô hiệu | UI | FR-03 B2, SEC-07 |

### 2.3 Bước 2 — OTP không hợp lệ (mật khẩu còn lại hợp lệ)
| TC ID | Lớp phủ | Tiền đề | Dữ liệu vào | Expected (theo spec) | Lớp chạy | Truy vết |
|---|---|---|---|---|---|---|
| FR03-DT-08 | EC-otp-I1 | Đã có OTP | otp rỗng | Từ chối, mật khẩu không đổi | UI+API | FR-03 B2 |
| FR03-DT-09 | EC-otp-I2 | Đã có OTP | `12345` | Từ chối, mật khẩu không đổi | UI+API | FR-03 B2 |
| FR03-DT-10 | EC-otp-I3 | Đã có OTP | `1234567` | Từ chối, mật khẩu không đổi | UI+API | FR-03 B2 |
| FR03-DT-11 | EC-otp-I4 | Đã có OTP | `12a45!` | Từ chối, mật khẩu không đổi | UI+API | FR-03 B2 |
| FR03-DT-12 | EC-otp-I5 | Đã có OTP = X | OTP khác X (6 số) | Từ chối, mật khẩu không đổi | UI+API | FR-03 B2 |
| FR03-DT-13 | EC-otp-I6 | Tạo user B; lấy OTP của B | email = A, otp = OTP của B | Từ chối: OTP chỉ hợp lệ cho email đã yêu cầu; mật khẩu A không đổi | API | FR-03 B2 |
| FR03-DT-14 | EC-otp-I7 | Vừa reset thành công bằng OTP X | Dùng lại OTP X lần 2 | Từ chối: OTP vô hiệu sau khi dùng | UI+API | SEC-07 |
| FR03-DT-15 | EC-otp-I8 | Có OTP cấp từ lâu | Dùng OTP sau thời gian dài | Từ chối: OTP có thời hạn (thời hạn không định lượng trong SRS) | API | SEC-07 |

### 2.4 Bước 2 — Mật khẩu mới không hợp lệ (OTP hợp lệ)
| TC ID | Lớp phủ | Tiền đề | Dữ liệu vào | Expected (theo spec) | Lớp chạy | Truy vết |
|---|---|---|---|---|---|---|
| FR03-DT-16 | EC-pw-I1 | Đã có OTP | newPassword rỗng | Từ chối, mật khẩu không đổi | UI+API | FR-03 B2 |
| FR03-DT-17 | EC-pw-I2 | Đã có OTP | `Ab1!xyz` | Từ chối (<8 ký tự), mật khẩu không đổi | UI+API | FR-01 |
| FR03-DT-18 | EC-pw-I3 | Đã có OTP | `newpass1!` | Từ chối (thiếu hoa) | UI+API | FR-01 |
| FR03-DT-19 | EC-pw-I4 | Đã có OTP | `NEWPASS1!` | Từ chối (thiếu thường) | UI+API | FR-01 |
| FR03-DT-20 | EC-pw-I5 | Đã có OTP | `Newpass!!` | Từ chối (thiếu số) | UI+API | FR-01 |
| FR03-DT-21 | EC-pw-I6 | Đã có OTP | `Newpass12` | Từ chối (thiếu ký tự đặc biệt) | UI+API | FR-01 |
| FR03-DT-22 | EC-pw-I7 | Đã có OTP | `Newpass1#` | Từ chối (diễn giải chặt: `#` không thuộc `@$!%*?&`) | UI+API | FR-01 |

### 2.5 Bước 2 — Xác nhận mật khẩu
| TC ID | Lớp phủ | Tiền đề | Dữ liệu vào | Expected (theo spec) | Lớp chạy | Truy vết |
|---|---|---|---|---|---|---|
| FR03-DT-23 | EC-cf-I1 | Đã có OTP | new=`Newpass1!`, confirm=`Other123!` | Từ chối vì hai trường không khớp, mật khẩu không đổi | UI | FR-03 B2 |
| FR03-DT-24 | EC-cf-I2 | Đã có OTP | new=`Newpass1!`, confirm rỗng | Từ chối, mật khẩu không đổi | UI | FR-03 B2 |
| FR03-DT-25 | EC-cf-I3 | Đã có OTP | new=`Newpass1!`, confirm=`newpass1!` | Từ chối (phân biệt hoa/thường) | UI | FR-03 B2 |

### 2.6 Giao diện (GUI)
| TC ID | Lớp phủ | Tiền đề | Thao tác | Expected (theo spec) | Lớp chạy | Truy vết |
|---|---|---|---|---|---|---|
| FR03-DT-26 | EC-gui-1 | Mở `/forgot-password` | Quan sát bước 1 | Có chỉ báo "Bước 1 / 2" | UI | FR-03, FR-22 |
| FR03-DT-27 | EC-gui-2 | Hoàn tất bước 1 | Quan sát bước 2 | Có chỉ báo "Bước 2 / 2" | UI | FR-03, FR-22 |
| FR03-DT-28 | EC-gui-3 | Mở trang | Tìm nút | Có nút "Quay lại đăng nhập" dẫn về `/login` | UI | FR-03 B1 |
| FR03-DT-29 | EC-gui-4 | Mở trang | Kiểm tra thuộc tính input email | `type="email"` | UI | FR-22 |
| FR03-DT-30 | EC-gui-5 | Cả 2 bước | Quan sát nhãn | Trường bắt buộc có `*` | UI | FR-22 |
| FR03-DT-31 | EC-gui-6 | Gây lỗi | Quan sát vị trí thông báo lỗi | Thông báo nằm trên nút submit | UI | FR-22 |
| FR03-DT-32 | EC-gui-7 | Bước 2 | Kiểm tra input mật khẩu mới | `type="password"` | UI | FR-22 |

## 3. Truy vết lớp → test

| Mã lớp | Test phủ |
|---|---|
| EC-email-V1 | DT-01, DT-07 |
| EC-email-I1 | DT-02 |
| EC-email-I2 | DT-03 |
| EC-email-I3 | DT-04 |
| EC-email-I4 | DT-05 |
| EC-email-I5 | DT-06 |
| EC-otp-V1 | DT-07 |
| EC-otp-I1..I8 | DT-08..DT-15 (theo thứ tự) |
| EC-pw-V1 | DT-07 |
| EC-pw-I1..I7 | DT-16..DT-22 (theo thứ tự) |
| EC-cf-V1 | DT-07 |
| EC-cf-I1..I3 | DT-23..DT-25 |
| EC-gui-1..7 | DT-26..DT-32 |

Tổng: **32** test case Domain Testing. Mọi lớp đều có ít nhất một test.

## 4. Giới hạn và giả định
- **Thời hạn OTP** không có số trong SRS (SEC-07 chỉ nói "có thời hạn"), nên DT-15 chỉ kiểm hành vi "có hết hạn hay không", không kiểm biên thời gian.
- DT-23..DT-25 chỉ chạy được trên UI; nếu UI không có trường xác nhận, kết quả là **Fail** (spec yêu cầu có trường) và các test này không thể thực thi đầy đủ.
- Kết quả của DT-22 phụ thuộc diễn giải "ký tự đặc biệt" (xem ghi chú ở 1.3).
- Test đổi mật khẩu thành công (DT-07) thay đổi dữ liệu; sau đó phải reset DB trước các test dùng `Test1234!`.
