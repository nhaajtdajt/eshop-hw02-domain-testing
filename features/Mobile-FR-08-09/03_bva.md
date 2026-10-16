# Mobile FR-08/09: Thanh toán và Mã giảm giá trên Mobile — Boundary Value Analysis

Oracle: SRS `README.md` (FR-08 dòng 102–108; FR-09 dòng 110–135). Nhập từ `02_domain_testing.md`.
Kỹ thuật: 3 giá trị tại mỗi biên (biên−1, biên, biên+1); nêu rõ biên đóng/mở.

## 1. Chọn đại lượng có thứ tự và biên theo spec

| Đại lượng | Miền theo spec | Biên | Đóng/Mở | Giá trị kiểm thử | Nguồn |
|---|---|---|---|---|---|
| Tổng đơn so với `min_order_amount` (C3) | Tổng ≥ ngưỡng | ngưỡng của mã (`SAVE10` 300,000; `BIGBUY` 500,000) | **đóng** (`>=`) | ngưỡng−1, ngưỡng, ngưỡng+1 | FR-09 dòng 118 |
| Ngày hiện tại so với `expired_at` (C2) | hiện tại **trước** `expired_at` | `expired_at` | **mở** (`<`) | hôm qua, hôm nay, ngày mai (kiểu ngày); now−1 phút, now+1 phút (kiểu ngày giờ) | FR-09 dòng 117 |
| Số lần đã dùng so với `max_uses_per_user` (C5) | đã dùng **<** giới hạn | `max` | mở (`<`) | `max−1`, `max` (và 0); `VIP100` có max = 2 | FR-09 dòng 120 |
| Tổng đơn so với giá trị giảm cố định D | `final = total − D` | tổng = D | — | D−1, D, D+1 (tổng thanh toán không âm: diễn giải) | FR-09 dòng 125–126 |
| Giảm theo phần trăm | `total × value / 100` | value = 100 (giảm hết) | đóng | 100% | FR-09 dòng 124 |
| Phần thập phân của giảm % | số nguyên tiền | tổng = 9, 10 với 10% | — | 9 (0.9), 10 (1.0) | FR-09 dòng 124 |
| Số sản phẩm trong giỏ (điều kiện `cart.length > 1` trong code) | hiển thị/gửi đầy đủ sản phẩm | 1 và 2 | — | 1, 2 (và 3 ở DT-31) | FR-08 dòng 106 |
| Độ dài mã giảm giá | spec không nêu | — | — | 1000 ký tự (cực trị, kiểm tra chịu lỗi) | — |

Ghi chú: các mã `SAVE10` và `BIGBUY` có ngưỡng khác nhau nên mỗi mã có đủ bộ 3 giá trị. Các mã có hạn/giảm cố định/phần trăm đặc biệt được tạo bằng `POST /api/admin/coupons` (API này không kiểm tra role nên dùng được để chuẩn bị dữ liệu).

## 2. Test case BVA

Điều kiện chung: user `test@eshop.com` đã đăng nhập; `coupon_usage` của user được xóa trước mỗi test (trừ khi nói khác); tổng đơn truyền cho `POST /api/apply-coupon` đúng bằng giá trị nêu, và nhóm test UI dùng sản phẩm tạo riêng để có tổng đúng.

### 2.1 Ngưỡng đơn tối thiểu (C3, đóng)
| TC ID | Mã | Tổng đơn | Vị trí so với biên | Expected (theo spec) | Lớp chạy |
|---|---|---|---|---|---|
| MFR-BV-01 | `SAVE10` | 299,999 | ngưỡng−1 | Từ chối (chưa đủ ngưỡng) | UI+API |
| MFR-BV-02 | `SAVE10` | 300,000 | **ngưỡng** | Chấp nhận: discount 30,000; final 270,000 | UI+API |
| MFR-BV-03 | `SAVE10` | 300,001 | ngưỡng+1 | Chấp nhận: discount ≈ 30,000; final ≈ 270,001 | API |
| MFR-BV-04 | `BIGBUY` | 499,999 | ngưỡng−1 | Từ chối | API |
| MFR-BV-05 | `BIGBUY` | 500,000 | **ngưỡng** | Chấp nhận: discount 50,000; final 450,000 | API |
| MFR-BV-06 | `BIGBUY` | 500,001 | ngưỡng+1 | Chấp nhận: discount 50,000; final 450,001 | API |

### 2.2 Hạn dùng (C2, mở: hiện tại phải trước `expired_at`)
Tạo mã `fixed` 10,000, min 0, với `expired_at` như sau; gọi `apply-coupon` với tổng 100,000.
| TC ID | `expired_at` | Vị trí so với biên | Expected (theo spec) | Lớp chạy |
|---|---|---|---|---|
| MFR-BV-07 | ngày hôm qua (kiểu ngày) | trước biên | Từ chối (hết hạn) | API |
| MFR-BV-08 | ngày hôm nay (kiểu ngày) | **biên** | Từ chối (hiện tại không "trước" `expired_at`) | API |
| MFR-BV-09 | ngày mai (kiểu ngày) | sau biên | Chấp nhận | API |
| MFR-BV-10 | giờ hiện tại − 1 phút (ISO ngày giờ) | biên−1 | Từ chối | API |
| MFR-BV-11 | giờ hiện tại + 1 phút (ISO ngày giờ) | biên+1 | Chấp nhận | API |

### 2.3 Số lần dùng (C5, mở: đã dùng < max)
`VIP100` có `max_uses_per_user = 2`; lượt dùng được ghi bằng `POST /api/coupon-usage` (token user). Tổng đơn 400,000.
| TC ID | Số lần đã dùng | Vị trí so với biên | Expected (theo spec) | Lớp chạy |
|---|---|---|---|---|
| MFR-BV-12 | 0 | dưới `max−1` | Chấp nhận | API |
| MFR-BV-13 | 1 | **`max−1`** | Chấp nhận | API |
| MFR-BV-14 | 2 | **`max`** | Từ chối (đã dùng đủ lượt) | API |

### 2.4 Giảm giá so với tổng đơn
Mã `fixed` D = 100,000, min 0 (`FRM-FIX100K`).
| TC ID | Tổng đơn | Vị trí so với biên | Expected (diễn giải: tổng thanh toán không âm) | Lớp chạy |
|---|---|---|---|---|
| MFR-BV-15 | 99,999 | D−1 | `final_amount ≥ 0` (tức 0) | API |
| MFR-BV-16 | 100,000 | **D** | `discount = 100,000`; `final = 0` | API |
| MFR-BV-17 | 100,001 | D+1 | `discount = 100,000`; `final = 1` | API |
| MFR-BV-18 | 1,000 (mã `percent` 100%, min 0) | giảm 100% | `discount = 1,000`; `final = 0` | API |
| MFR-BV-19 | 9 (mã `percent` 10%, min 0) | phần lẻ 0.9 | `discount` = 0 hoặc 1 nhất quán (spec không nêu làm tròn); `final = total − discount`, số nguyên, ≥ 0 | API |
| MFR-BV-20 | 10 (mã `percent` 10%, min 0) | phần lẻ 1.0 | `discount = 1`; `final = 9` | API |

### 2.5 Số sản phẩm trong giỏ và độ dài mã
| TC ID | Kịch bản | Vị trí so với biên | Expected (theo spec) | Lớp chạy |
|---|---|---|---|---|
| MFR-BV-21 | Giỏ 1 sản phẩm, xác nhận thanh toán; quan sát request | `cart.length = 1` | Request chứa đủ 1 sản phẩm | UI |
| MFR-BV-22 | Giỏ 2 sản phẩm, xác nhận thanh toán; quan sát request | `cart.length = 2` (n+1) | Request chứa đủ 2 sản phẩm | UI |
| MFR-BV-23 | Mã giảm giá dài 1000 ký tự | cực trị | Từ chối như mã không tồn tại; không lỗi server | API |

## 3. Tham chiếu chéo với Domain Testing
Các biên còn lại đã có ở `02_domain_testing.md`: tổng nhỏ hơn ngưỡng (DT-20, DT-21), mã hết hạn (DT-18, DT-19), mã đã dùng hết lượt (DT-23, DT-24), giỏ 3 sản phẩm (DT-31), `fixed` lớn hơn tổng (DT-26), `percent` có phần lẻ (DT-25).

## 4. Thống kê
- **23** test case BVA (BV-01..BV-23).
- Cùng 40 test Domain Testing → **63** test case thiết kế cho Mobile FR-08/09.

## 5. Giới hạn
- BV-07..BV-11: múi giờ; `expired_at` kiểu ngày bị `new Date()` phân tích theo UTC, nên "hôm nay" tính theo ngày UTC; ghi múi giờ máy test (UTC+7) khi kết luận.
- BV-15..BV-20 dựa trên diễn giải "tổng thanh toán không âm" và "làm tròn nhất quán"; nếu lệch ghi "theo diễn giải".
- BV-21, BV-22 chỉ khả thi trên UI (quan sát request gửi đi bằng cách bọc `fetch` trong trình duyệt).
