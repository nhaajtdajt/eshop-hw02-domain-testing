# FR-03: Quên & Đặt lại mật khẩu — Boundary Value Analysis

Oracle: SRS `README.md` (FR-03 dòng 46–60, FR-01 dòng 36–43, SEC-07 dòng 284). Nhập từ `02_domain_testing.md`.
Kỹ thuật: 3 giá trị tại mỗi biên (biên−1, biên, biên+1), có thêm giá trị cực trị khi hữu ích.

## 1. Chọn input có thứ tự và biên theo spec

| Input / đại lượng | Miền theo spec | Biên | Đóng/Mở | Giá trị kiểm thử | Nguồn |
|---|---|---|---|---|---|
| Độ dài OTP (người dùng nhập) | đúng 6 chữ số | 6 | đóng (`= 6`) | 0, 1, **5**, **6**, **7** | FR-03 dòng 51; SEC-07 |
| Giá trị OTP có số 0 đầu | 000000–999999 | 000000 | đóng | `012345` (nhận), `12345` (mất số 0, từ chối) | FR-03 dòng 51 (6 chữ số ngẫu nhiên) |
| Độ dài OTP do hệ thống **sinh** | đúng 6 chữ số | 6 | đóng | mọi OTP sinh ra đều dài 6 | FR-03 dòng 51 |
| Độ dài mật khẩu mới | ≥ 8 (không nêu tối đa) | 8 | đóng (`>= 8`) | **7**, **8**, **9**, 256 | FR-01 dòng 39 |
| Số chữ hoa | ≥ 1 | 1 | đóng | 0 (đã có ở DT-18), **1** | FR-01 dòng 39 |
| Số chữ thường | ≥ 1 | 1 | đóng | 0 (DT-19), **1** | FR-01 dòng 39 |
| Số chữ số | ≥ 1 | 1 | đóng | 0 (DT-20), **1** | FR-01 dòng 39 |
| Số ký tự đặc biệt | ≥ 1, thuộc `@ $ ! % * ? &` | 1 | đóng | 0 (DT-21), **1** | FR-01 dòng 39 |
| Thành viên của tập ký tự đặc biệt | 7 ký tự | từng phần tử; hàng xóm ngoài tập | — | mỗi ký tự trong tập (7); ngoài tập sát về mã ASCII: `"`(0x22), `#`(0x23, DT-22), `+`(0x2B) | FR-01 dòng 39 |
| Độ dài `confirmPassword` so với `newPassword` | bằng nhau | n | đóng | n−1, n, n+1 (và n + khoảng trắng) | FR-03 dòng 59 |
| Số lần dùng OTP | tối đa 1 lần | 1 | mở (`< 1` lần đã dùng) | lần 1 nhận, lần 2 từ chối (xem DT-07, DT-14) | SEC-07 |
| Thời hạn OTP | "có thời hạn", không có số | — | — | **Không có biên số học → không thiết kế BVA thời gian** | SEC-07 |
| Độ dài email | không nêu tối thiểu/tối đa | — | — | **Không có biên theo spec** (email chỉ có lớp định dạng, đã ở Domain Testing) | FR-01 dòng 38 |

Ghi chú: mật khẩu mới ≥ 8 nhưng spec không có tối đa → BV-12 (256 ký tự) là kiểm tra cực trị khám phá, expected "chấp nhận" vì không có giới hạn.

## 2. Test case BVA

Điều kiện chung: nhóm OTP (BV-01..08) dùng API trực tiếp vì UI không cho đặt trước OTP 6 số; **tiền đề seed**: đặt `reset_token` của `test@eshop.com` bằng script `evidence/seed_otp.js` (sẽ tạo ở Bước 4) rồi gọi `POST /api/reset-password`. Mỗi lần OTP bị dùng hoặc mật khẩu đổi thì chạy lại `node database.js` + seed để trở về trạng thái đầu. Nhóm mật khẩu (BV-09..25) chạy cả UI và API với OTP hợp lệ.

### 2.1 Độ dài OTP (tại bước đặt lại; token seed `123456` trừ khi nói khác)
| TC ID | Input | Giá trị | Vị trí so với biên | Lớp | Expected (theo spec) |
|---|---|---|---|---|---|
| FR03-BV-01 | otp | `` (0 chữ số) | cực trị thấp | EC-otp-I1 | Từ chối, mật khẩu không đổi |
| FR03-BV-02 | otp | `1` (1 chữ số) | cực trị thấp | EC-otp-I2 | Từ chối, mật khẩu không đổi |
| FR03-BV-03 | otp | `12345` (5) | biên−1 | EC-otp-I2 | Từ chối, mật khẩu không đổi |
| FR03-BV-04 | otp | `123456` (6) | **biên** | EC-otp-V1 | Chấp nhận, đổi mật khẩu thành công |
| FR03-BV-05 | otp | `1234567` (7) | biên+1 | EC-otp-I3 | Từ chối, mật khẩu không đổi |
| FR03-BV-06 | otp | token seed `012345`, nhập `012345` | biên giá trị (số 0 đầu) | EC-otp-V1 | Chấp nhận (6 chữ số, số 0 đầu hợp lệ) |
| FR03-BV-07 | otp | token seed `012345`, nhập `12345` | số 0 đầu bị mất | EC-otp-I2 | Từ chối (khác OTP đã cấp) |
| FR03-BV-08 | otp | gọi `forgot-password` 20 lần, lấy `resetToken` | độ dài OTP sinh ra | EC-otp-V1 | Cả 20 mã đều đúng 6 chữ số (000000–999999) |

### 2.2 Độ dài mật khẩu mới (OTP hợp lệ; confirm = newPassword)
| TC ID | Input | Giá trị | Vị trí so với biên | Lớp | Expected (theo spec) |
|---|---|---|---|---|---|
| FR03-BV-09 | newPassword | `Ab1!xyz` (7) | biên−1 | EC-pw-I2 | Từ chối, mật khẩu không đổi |
| FR03-BV-10 | newPassword | `Ab1!wxyz` (8) | **biên** | EC-pw-V1 | Chấp nhận |
| FR03-BV-11 | newPassword | `Ab1!vwxyz` (9) | biên+1 | EC-pw-V1 | Chấp nhận |
| FR03-BV-12 | newPassword | `Aa1!` lặp để đủ 256 ký tự | cực trị cao (khám phá) | EC-pw-V1 | Chấp nhận (spec không nêu tối đa); không lỗi server |

### 2.3 Số lượng tối thiểu từng loại ký tự (độ dài ≥ 8)
| TC ID | Input | Giá trị | Vị trí so với biên | Lớp | Expected (theo spec) |
|---|---|---|---|---|---|
| FR03-BV-13 | newPassword | `newpass1!A` (đúng 1 chữ hoa) | biên (min=1) | EC-pw-V1 | Chấp nhận |
| FR03-BV-14 | newPassword | `NEWPASS1!a` (đúng 1 chữ thường) | biên | EC-pw-V1 | Chấp nhận |
| FR03-BV-15 | newPassword | `Newpass!1` (đúng 1 chữ số) | biên | EC-pw-V1 | Chấp nhận |
| FR03-BV-16 | newPassword | `Newpass12!` (đúng 1 ký tự đặc biệt) | biên | EC-pw-V1 | Chấp nhận |

(Giá trị biên−1 = 0 ký tự của từng loại đã có ở DT-18..DT-21.)

### 2.4 Thành viên tập ký tự đặc biệt
Mẫu: `Newpass1<X>` với `<X>` là ký tự đặc biệt duy nhất.
| TC ID | `<X>` | Vị trí | Lớp | Expected (theo spec) |
|---|---|---|---|---|
| FR03-BV-17 | `@` | trong tập | EC-pw-V1 | Chấp nhận |
| FR03-BV-18 | `$` | trong tập | EC-pw-V1 | Chấp nhận |
| FR03-BV-19 | `!` | trong tập | EC-pw-V1 | Chấp nhận |
| FR03-BV-20 | `%` | trong tập | EC-pw-V1 | Chấp nhận |
| FR03-BV-21 | `*` | trong tập | EC-pw-V1 | Chấp nhận |
| FR03-BV-22 | `?` | trong tập | EC-pw-V1 | Chấp nhận |
| FR03-BV-23 | `&` | trong tập | EC-pw-V1 | Chấp nhận |
| FR03-BV-24 | `+` | ngoài tập (hàng xóm ASCII) | EC-pw-I7 | Từ chối (diễn giải chặt) |
| FR03-BV-25 | `"` | ngoài tập (hàng xóm ASCII) | EC-pw-I7 | Từ chối (diễn giải chặt) |

### 2.5 Xác nhận mật khẩu (chỉ UI)
`newPassword` = `Newpass1!` (9 ký tự).
| TC ID | confirmPassword | Vị trí so với biên | Lớp | Expected (theo spec) |
|---|---|---|---|---|
| FR03-BV-26 | `Newpass1` (n−1) | biên−1 | EC-cf-I1 | Từ chối vì không khớp |
| FR03-BV-27 | `Newpass1!!` (n+1) | biên+1 | EC-cf-I1 | Từ chối vì không khớp |
| FR03-BV-28 | `Newpass1! ` (thêm khoảng trắng cuối) | biên+1 | EC-cf-I1 | Từ chối vì không khớp |

(Giá trị bằng nhau, n, đã có ở DT-07.)

## 3. Tham chiếu chéo với Domain Testing
Các giá trị biên đã nằm sẵn ở Domain Testing nên không lặp lại ở đây: DT-09/10 (OTP 5/7 chữ số, đại diện), DT-14 (lần dùng thứ 2 của OTP), DT-17 (mật khẩu 7 ký tự, đại diện), DT-18..21 (0 ký tự của từng loại), DT-22 (`#`).
BV-03/05 và DT-09/10 khác nhau ở chỗ: BV-03/05 dùng giá trị sát biên của OTP seed `123456` (là tiền tố/mở rộng của OTP thật), nên phát hiện được cả lỗi khớp tiền tố; DT-09/10 chỉ là đại diện cho lớp.

## 4. Thống kê
- **28** test case BVA (BV-01..BV-28).
- Cùng 32 test Domain Testing → **60** test case thiết kế cho FR-03 (một số có thể bị trùng kết quả khi thực thi, tính theo ID).

## 5. Giới hạn
- Hệ thống thực sinh OTP 4 chữ số nên BV-04, BV-08 không thể thành công trên luồng thật; BV-04 chạy bằng OTP **seed** để kiểm tra riêng logic `reset-password`, BV-08 kiểm tra riêng bộ sinh OTP.
- Không có biên thời gian OTP và không có biên độ dài email vì SRS không nêu số liệu.
