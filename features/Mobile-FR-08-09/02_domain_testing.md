# Mobile FR-08/09: Thanh toán và Mã giảm giá trên Mobile — Domain Testing

Oracle: SRS `README.md` (FR-08 dòng 102–108; FR-09 dòng 110–135; FR-20 dòng 235; FR-21 dòng 246; SEC-02 dòng 279). Chi tiết ở `01_analysis.md`.

Quy ước:
- Mã lớp: `EC-<nhóm>-V<n>` (hợp lệ), `EC-<nhóm>-I<n>` (không hợp lệ).
- Mỗi test không hợp lệ chỉ làm sai **một** điều kiện; các điều kiện khác hợp lệ (mã đang hoạt động, còn hạn, đủ ngưỡng, user còn lượt...).
- Số tiền kỳ vọng tính **bằng công thức SRS**: `percent`: `total × value / 100`; `fixed`: `value`; `final = total − discount`.
- Cột **Lớp chạy**: `UI` = ứng dụng Mobile chạy bằng Expo Web (`react-native-web`); `API` = HTTP trực tiếp `localhost:3000`.
- Dữ liệu chuẩn: user `test@eshop.com` / `Test1234!` (trừ khi nói khác); sản phẩm seed: *iPhone 15 Pro Max* 30,000,000 ₫; *Samsung Galaxy S24 Ultra* 28,000,000 ₫; *MacBook Pro M3* 45,000,000 ₫; *AirPods Pro 2* 6,000,000 ₫; *Keychron Q1* 4,000,000 ₫. Để có tổng đơn nhỏ (200,000–600,000) dùng sản phẩm tạo riêng qua API với giá phù hợp (ví dụ `FRM-100k` giá 100,000 ₫).
- Mã seed: `SAVE10` (percent 10, min 300,000, 1 lần), `BIGBUY` (fixed 50,000, min 500,000, 1 lần), `VIP100` (fixed 100,000, min 300,000, 2 lần), `EXPIRED` (percent 20, min 100,000, hết hạn 2020-01-01). Reset trạng thái dùng mã giữa các test bằng cách xóa `coupon_usage` của user.
- Giới hạn môi trường: không có thiết bị/emulator; `Alert.alert` không hiển thị trên bản web nên thông báo dạng Alert chỉ kiểm tra gián tiếp (chuyển màn hình, trạng thái giỏ/đơn).

## 1. Lớp tương đương

### 1.1 Điều kiện thanh toán (FR-08)
| Mã lớp | Loại | Mô tả |
|---|---|---|
| EC-auth-V1 | Hợp lệ | Đã đăng nhập (có token) |
| EC-auth-I1 | Không hợp lệ | Chưa đăng nhập (không token) |
| EC-cart-V1 | Hợp lệ | Giỏ có đúng 1 sản phẩm |
| EC-cart-V2 | Hợp lệ | Giỏ có nhiều sản phẩm |
| EC-cart-I1 | Không hợp lệ | Giỏ rỗng |
| EC-total-V1 | Hợp lệ | `total_amount` đúng bằng Σ đơn giá × số lượng |
| EC-total-I1 | Không hợp lệ | `total_amount` do client sửa (khác tổng thật) |
| EC-total-I2 | Không hợp lệ | Thiếu `total_amount` |
| EC-total-I3 | Không hợp lệ | `total_amount` âm |
| EC-total-I4 | Không hợp lệ | `total_amount` không phải số |

### 1.2 Mã giảm giá (FR-09, C1..C5)
| Mã lớp | Loại | Mô tả |
|---|---|---|
| EC-code-V1 | Hợp lệ | Mã tồn tại và đang hoạt động (C1) |
| EC-code-I1 | Không hợp lệ | Mã không tồn tại |
| EC-code-I2 | Không hợp lệ | Mã tồn tại nhưng `is_active = 0` |
| EC-code-I3 | Không hợp lệ | Rỗng |
| EC-code-I4 | Không hợp lệ | Chứa ký tự SQL/đặc biệt |
| EC-code-V2 | Hợp lệ (diễn giải) | Chữ thường hoặc có khoảng trắng thừa nhưng đúng mã |
| EC-exp-V1 | Hợp lệ | Còn hạn (C2) |
| EC-exp-I1 | Không hợp lệ | Hết hạn |
| EC-min-V1 | Hợp lệ | Tổng đơn ≥ ngưỡng (C3) |
| EC-min-I1 | Không hợp lệ | Tổng đơn < ngưỡng |
| EC-login-V1 | Hợp lệ | Có JWT hợp lệ (C4) |
| EC-login-I1 | Không hợp lệ | Không có JWT |
| EC-use-V1 | Hợp lệ | Số lần đã dùng < giới hạn (C5) |
| EC-use-I1 | Không hợp lệ | Đã dùng đủ giới hạn |

### 1.3 Loại giảm giá và tính tiền
| Mã lớp | Loại | Mô tả |
|---|---|---|
| EC-type-V1 | Hợp lệ | `percent`, kết quả số nguyên (ví dụ 10% của 400,000) |
| EC-type-V2 | Hợp lệ | `percent`, kết quả có phần lẻ (10% của 333,333) |
| EC-type-V3 | Hợp lệ | `fixed`, nhỏ hơn tổng đơn |
| EC-type-I1 | Không hợp lệ (diễn giải) | `fixed` lớn hơn tổng đơn (tổng thanh toán không được âm) |

### 1.4 Hình dạng request áp mã
| Mã lớp | Loại | Mô tả |
|---|---|---|
| EC-body-I1 | Không hợp lệ | Thiếu `code` |
| EC-body-I2 | Không hợp lệ | Thiếu `total_amount` |
| EC-body-I3 | Không hợp lệ | `total_amount` âm |
| EC-body-I4 | Không hợp lệ | `total_amount` không phải số |
| EC-usage-I1 | Không hợp lệ | `coupon-usage` không token |
| EC-usage-I2 | Không hợp lệ | `coupon-usage` với `coupon_id` không tồn tại |

### 1.5 Giao diện Mobile
| Mã lớp | Mô tả |
|---|---|
| EC-ui-1 | Màn hình thanh toán liệt kê đầy đủ sản phẩm, số lượng, thành tiền |
| EC-ui-2 | Ô tổng tiền thanh toán không chỉnh sửa được |
| EC-ui-3 | Khối mã giảm giá: nút "Áp dụng" bị vô hiệu khi mã rỗng; lỗi/kết quả hiển thị đúng và tự xóa khi sửa mã |
| EC-ui-4 | Hiển thị tiền có `₫` và phân cách hàng nghìn; "Tổng thanh toán" cập nhật sau khi áp mã |
| EC-ui-5 | Luồng hoàn tất: đơn tạo đúng, giỏ được xóa, lượt dùng mã được ghi |

## 2. Test case

### 2.1 Thanh toán và đăng nhập (FR-08)
| TC ID | Lớp phủ | Dữ liệu / thao tác | Expected (theo spec) | Lớp chạy |
|---|---|---|---|---|
| MFR-DT-01 | EC-auth-I1 | Chưa đăng nhập, giỏ có 1 SP, bấm "Tiến hành thanh toán" | Không vào màn thanh toán; chuyển sang đăng nhập | UI |
| MFR-DT-02 | EC-auth-I1 | `POST /api/checkout` không token | 401, không tạo đơn | API |
| MFR-DT-03 | EC-auth-V1, EC-cart-V1, EC-ui-1 | Đăng nhập, giỏ 1 SP | Màn thanh toán liệt kê SP với số lượng, thành tiền; tổng = đơn giá × số lượng | UI |
| MFR-DT-04 | EC-cart-V2, EC-ui-1 | Giỏ 3 SP khác nhau | Liệt kê đủ 3 SP; tổng = Σ | UI |
| MFR-DT-05 | EC-ui-2 | Thử gõ vào ô "Tổng tiền thanh toán" | Không chỉnh sửa được | UI |
| MFR-DT-06 | EC-cart-I1 | Giỏ rỗng | Không có đường vào thanh toán; hiển thị thông báo giỏ trống | UI |
| MFR-DT-07 | EC-total-I1 | `POST /api/checkout` với `items` hợp lệ nhưng `total_amount = 1` | Backend tự tính lại; đơn có tổng = Σ giá × số lượng (không phải 1) hoặc bị từ chối | API |
| MFR-DT-08 | EC-ui-5 | Thanh toán thành công (không mã) | "Thanh toán thành công!"; giỏ rỗng; đơn `pending` trong lịch sử với đúng tổng | UI |

### 2.2 Mã giảm giá hợp lệ và loại mã
| TC ID | Lớp phủ | Dữ liệu | Expected (theo spec) | Lớp chạy |
|---|---|---|---|---|
| MFR-DT-09 | EC-code-V1, EC-type-V1 | `SAVE10`, tổng 400,000 | discount 40,000; final 360,000 | UI+API |
| MFR-DT-10 | EC-code-V1, EC-type-V3 | `BIGBUY`, tổng 600,000 | discount 50,000; final 550,000 | UI+API |
| MFR-DT-11 | EC-code-V1, EC-type-V3 | `VIP100`, tổng 400,000 | discount 100,000; final 300,000 | UI+API |

### 2.3 Mã không hợp lệ (C1)
| TC ID | Lớp phủ | Dữ liệu | Expected (theo spec) | Lớp chạy |
|---|---|---|---|---|
| MFR-DT-12 | EC-code-I1 | `NOPE`, tổng 400,000 | Từ chối với lý do; tổng không đổi | UI+API |
| MFR-DT-13 | EC-code-I2 | mã tồn tại nhưng `is_active = 0` | Từ chối; tổng không đổi | UI+API |
| MFR-DT-14 | EC-code-I3 | để trống | Nút "Áp dụng" vô hiệu / không gửi request | UI |
| MFR-DT-15 | EC-code-V2 | `save10` (chữ thường) | Chấp nhận như `SAVE10` (diễn giải: nhập chữ thường vẫn dùng được) | UI |
| MFR-DT-16 | EC-code-V2 | `  SAVE10  ` | Chấp nhận (bỏ khoảng trắng thừa) | UI |
| MFR-DT-17 | EC-code-I4 | `' OR '1'='1` | Từ chối như mã không tồn tại; không lỗi server | API |

### 2.4 Điều kiện C2–C5
| TC ID | Lớp phủ | Dữ liệu | Expected (theo spec) | Lớp chạy |
|---|---|---|---|---|
| MFR-DT-18 | EC-exp-I1 | `EXPIRED`, tổng 200,000 (≥ min 100,000) | Từ chối vì hết hạn | UI+API |
| MFR-DT-19 | EC-exp-I1, EC-min-I1 | `EXPIRED`, tổng 50,000 (< min) | Từ chối (lý do hợp lý; thứ tự báo lỗi không quy định) | API |
| MFR-DT-20 | EC-min-I1 | `SAVE10`, tổng 200,000 (< 300,000) | Từ chối vì chưa đủ ngưỡng | UI+API |
| MFR-DT-21 | EC-min-I1 | `BIGBUY`, tổng 400,000 (< 500,000) | Từ chối vì chưa đủ ngưỡng | UI+API |
| MFR-DT-22 | EC-login-I1 | `SAVE10`, tổng 400,000, không token | Từ chối (C4: phải đăng nhập) | API |
| MFR-DT-23 | EC-use-I1 | User đã dùng `SAVE10` một lần (đã thanh toán), áp lại | Từ chối vì đã dùng hết lượt | UI+API |
| MFR-DT-24 | EC-use-I1, EC-login-I1 | Như trên nhưng request **không** có `user_id` | Vẫn từ chối (C5 áp cho người dùng đã đăng nhập; không thể né bằng cách bỏ `user_id`) | API |

### 2.5 Tính tiền và hiển thị
| TC ID | Lớp phủ | Dữ liệu | Expected (theo spec) | Lớp chạy |
|---|---|---|---|---|
| MFR-DT-25 | EC-type-V2 | `SAVE10`, tổng 333,333 | discount ≈ 33,333 (làm tròn xuống/nhất quán), final ≈ 300,000 | API |
| MFR-DT-26 | EC-type-I1 | mã `fixed` 1,000,000, min 0, tổng 100,000 | final không âm (0) | API |
| MFR-DT-27 | EC-ui-4 | Áp `SAVE10` ở tổng 400,000 | Ô "Tổng tiền thanh toán" giữ 400,000; "Tiết kiệm: 40,000 ₫"; "Thành tiền" và "Tổng thanh toán": 360,000 ₫; có `₫` và phân cách nghìn | UI |
| MFR-DT-28 | EC-ui-3 | Áp mã thành công rồi sửa ô mã | Kết quả mã cũ bị xóa; "Tổng thanh toán" quay về tổng gốc | UI |
| MFR-DT-29 | EC-ui-3 | Áp mã sai rồi nhập mã đúng | Lỗi cũ biến mất; hiển thị kết quả mã đúng | UI |

### 2.6 Luồng hoàn tất có mã
| TC ID | Lớp phủ | Dữ liệu | Expected (theo spec) | Lớp chạy |
|---|---|---|---|---|
| MFR-DT-30 | EC-ui-5 | Áp `SAVE10` (tổng 400,000) rồi "Xác Nhận Thanh Toán" | Đơn có tổng 360,000 (do backend tính); giỏ rỗng; lượt dùng mã được ghi (`coupon_usage` +1) | UI |
| MFR-DT-31 | EC-ui-1 | Giỏ 3 SP, bấm xác nhận, quan sát request gửi đi | Request chứa **đủ 3** sản phẩm của giỏ | UI |

### 2.7 Hình dạng request (API)
| TC ID | Lớp phủ | Dữ liệu | Expected (theo spec) | Lớp chạy |
|---|---|---|---|---|
| MFR-DT-32 | EC-total-I2 | `checkout` thiếu `total_amount` | 400, không tạo đơn | API |
| MFR-DT-33 | EC-total-I3 | `total_amount = -100` | 400, không tạo đơn | API |
| MFR-DT-34 | EC-total-I4 | `total_amount = "abc"` | 400, không tạo đơn | API |
| MFR-DT-35 | EC-usage-I1 | `coupon-usage` không token | 401 | API |
| MFR-DT-36 | EC-usage-I2 | `coupon-usage` với `coupon_id = 99999` | Từ chối (4xx), không ghi bản ghi | API |
| MFR-DT-37 | EC-body-I1 | `apply-coupon` thiếu `code` | 400 | API |
| MFR-DT-38 | EC-body-I2 | `apply-coupon` thiếu `total_amount` | 400, không trả `final_amount` bất thường | API |
| MFR-DT-39 | EC-body-I3 | `apply-coupon` `total_amount = -400000` | 400 | API |
| MFR-DT-40 | EC-body-I4 | `apply-coupon` `total_amount = "abc"` | 400 | API |

## 3. Truy vết lớp → test
| Nhóm lớp | Test phủ |
|---|---|
| EC-auth | DT-01, DT-02, DT-03 |
| EC-cart | DT-03, DT-04, DT-06 |
| EC-total | DT-07, DT-32..DT-34 |
| EC-code | DT-09..DT-11, DT-12..DT-17 |
| EC-exp, EC-min | DT-18..DT-21 |
| EC-login | DT-22, DT-24 |
| EC-use | DT-23, DT-24 |
| EC-type | DT-09..DT-11, DT-25, DT-26 |
| EC-body, EC-usage | DT-35..DT-40 |
| EC-ui-1..5 | DT-03, 04, 05, 27, 28, 29, 08, 30, 31 |

Tổng: **40** test case Domain Testing; mọi lớp đều có ít nhất một test.

## 4. Giới hạn và giả định
- Cách đọc "tổng đơn" để so ngưỡng: coi bằng `total_amount` của request (tổng giỏ trước giảm).
- DT-15, DT-16, DT-26 là diễn giải; nếu lệch ghi "theo diễn giải", không coi chắc chắn là bug.
- Không test trên thiết bị thật/emulator; kết quả UI từ bản Expo Web dùng cùng mã nguồn `App.js` (đổi tạm `API_URL` sang `localhost`).
- Hiển thị ký hiệu `₫` và phân cách nghìn phụ thuộc `toLocaleString()` của môi trường (locale trình duyệt); có thể khác trên máy thật.
