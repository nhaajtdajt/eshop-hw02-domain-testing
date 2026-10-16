# Mobile FR-08/09: Thực thi test — kết quả

- **Ngày chạy:** 2026-10-16. **Môi trường:** Windows 11, Node v22.20.0, Backend `localhost:3000`; ứng dụng Mobile chạy bằng **Expo Web** (`react-native-web`, `http://localhost:8081`) trong trình duyệt tích hợp Claude desktop; dữ liệu seed gốc.
- **Hạn chế môi trường (quan trọng):**
  - Không có thiết bị thật/emulator Android hay iOS; kết quả UI từ bản web chạy **cùng mã nguồn `App.js`**, nhưng giao diện RN-web có thể khác máy thật (font, locale định dạng số).
  - `API_URL` trong `App.js` cứng là `http://192.168.10.13:3000/api` (không khớp IP máy test 192.168.1.225) nên **đổi tạm** sang `http://localhost:3000/api` để chạy; đã `git checkout` khôi phục sau khi test (không có thay đổi nào được commit cho `frontend-mobile`). Ba gói web (`react-dom`, `react-native-web`, `@expo/metro-runtime`) cài bằng `npm install --no-save` nên `package.json` không đổi.
  - `Alert.alert` không hiện trên web: thông báo dạng Alert được suy ra gián tiếp (chuyển màn hình, trạng thái giỏ/đơn).
- **Cách chạy:**
  - **API (47 kiểm tra):** `evidence/run_api_tests.js` — gọi HTTP thật; số tiền kỳ vọng tính bằng công thức SRS (không lấy số hệ thống trả); DB chỉ dùng để chuẩn bị/dọn dữ liệu. Kết quả thô: `evidence/api_results.json`.
  - **UI:** thao tác trên màn hình Mobile (gõ mã, bấm "Áp dụng", "Xác Nhận Thanh Toán"), bọc `fetch` để ghi lại body request, đọc số liệu đơn từ DB sau khi xác nhận. Kết quả: `evidence/ui_results.json`; ảnh: `evidence/mobile_checkout_save10_negative_discount.jpg`.
- **Quy ước:** kết quả tổng là **Fail** nếu bất kỳ lớp đã chạy (UI hoặc API) lệch spec.
- **Chạy lại có chủ ý:** BV-11 lần đầu báo Fail do script của tôi tạo `expired_at` bằng giờ UTC không có "Z" trong khi server hiểu là giờ địa phương (UTC+7); đã sửa để dùng giờ địa phương và chạy lại. Sau lần chạy API đầu, lần chạy UI đầu tiên của luồng giỏ nhiều món còn sót một sản phẩm cũ trong giỏ (script xóa giỏ sai) nên đã chạy lại luồng 2 món với giỏ sạch (BV-22).

## 1. Kết quả theo test case

### Domain Testing
| TC ID | Lớp chạy | Kết quả | Actual tóm tắt | Bug |
|---|---|---|---|---|
| MFR-DT-01 | UI | Pass | Khách bấm "Tiến hành thanh toán" → mở màn hình đăng nhập | |
| MFR-DT-02 | API | Pass | `POST /api/checkout` không token → 401 | |
| MFR-DT-03 | UI | Pass | Màn thanh toán liệt kê "FRM-400k x 1 — 400,000 ₫" | |
| MFR-DT-04 | UI | Pass | Giỏ 3 SP: liệt kê đủ 3 dòng với thành tiền | |
| MFR-DT-05 | UI | Pass | Ô tổng tiền `readOnly` | |
| MFR-DT-06 | UI | Pass | Giỏ rỗng: "Giỏ hàng của bạn đang trống", không có nút thanh toán | |
| MFR-DT-07 | API | **Fail** | `total_amount = 1` kèm `items` 30,000,000 ₫: HTTP 200, đơn lưu tổng **1** | BUG-03 |
| MFR-DT-08 | UI | Pass | Thanh toán không mã: "Thanh toán thành công!", giỏ về 0, đơn `pending` tổng 300,000 ₫ khớp | |
| MFR-DT-09 | UI+API | **Fail** | `SAVE10` @400,000: `discount_amount = -3,600,000`, `final_amount = 4,000,000`; UI hiện "Tiết kiệm: -3,600,000 ₫", "Tổng thanh toán: 4,000,000 ₫" (ảnh `mobile_checkout_save10_negative_discount.jpg`) | BUG-01 |
| MFR-DT-10 | UI+API | Pass | `BIGBUY` @600,000: 50,000 / 550,000 | |
| MFR-DT-11 | UI+API | Pass | `VIP100` @400,000: 100,000 / 300,000 | |
| MFR-DT-12 | UI+API | Pass | `NOPE` bị từ chối (404, thông báo hiển thị) | |
| MFR-DT-13 | UI+API | Pass | Mã `is_active = 0` bị từ chối | |
| MFR-DT-14 | UI | Pass | Mã rỗng: bấm "Áp dụng" không gửi request nào | |
| MFR-DT-15 | UI | Pass | `save10` được chấp nhận (UI đổi sang chữ hoa) — nhưng tính tiền vẫn sai do BUG-01 | |
| MFR-DT-16 | UI | Pass | `  SAVE10  ` được chấp nhận (UI cắt khoảng trắng) | |
| MFR-DT-17 | API | Pass | Chuỗi SQL bị từ chối như mã không tồn tại, không lỗi server | |
| MFR-DT-18 | UI+API | Pass | `EXPIRED` @400,000: "Mã giảm giá đã hết hạn" | |
| MFR-DT-19 | API | Pass | `EXPIRED` @50,000: từ chối nhưng báo "chưa đủ giá trị tối thiểu" (không báo hết hạn; thứ tự không quy định) | |
| MFR-DT-20 | UI+API | Pass | `SAVE10` @200,000: từ chối vì ngưỡng 300,000 | |
| MFR-DT-21 | UI+API | Pass | `BIGBUY` @400,000: từ chối vì ngưỡng 500,000 | |
| MFR-DT-22 | API | **Fail** | `apply-coupon` **không token**: HTTP 200 áp dụng thành công (C4 yêu cầu đăng nhập) | BUG-04 |
| MFR-DT-23 | UI+API | Pass | `SAVE10` lần 2: "Bạn đã sử dụng mã này 1 lần (đã đạt giới hạn)" | |
| MFR-DT-24 | API | **Fail** | Bỏ `user_id` khỏi request: HTTP 200, qua mặt kiểm tra lượt dùng (C5) | BUG-04 |
| MFR-DT-25 | API | **Fail** | `SAVE10` @333,333: `discount_amount = -2,999,997` | BUG-01 |
| MFR-DT-26 | API | **Fail** | Mã `fixed` 1,000,000 @100,000: `final_amount = -900,000` | BUG-05 |
| MFR-DT-27 | UI | **Fail** | Ô "Tổng tiền thanh toán (VND)" hiện `400000` không có `₫`, không phân cách hàng nghìn (FR-21); khi áp `SAVE10` các số "Tiết kiệm/Thành tiền" sai (BUG-01) | BUG-08, BUG-01 |
| MFR-DT-28 | UI | Pass | Sửa ô mã sau khi áp: kết quả cũ biến mất, "Tổng thanh toán" về 400,000 ₫ | |
| MFR-DT-29 | UI | Pass | Mã sai rồi mã đúng: lỗi cũ biến mất, hiện kết quả mới | |
| MFR-DT-30 | UI | **Fail** | Áp `SAVE10` (tổng 400,000) rồi xác nhận: request `total_amount = 4,000,000`, đơn #75 lưu **4,000,000** (đúng ra 360,000); giỏ rỗng, `coupon_usage` +1 | BUG-01, BUG-03 |
| MFR-DT-31 | UI | **Fail** | Giỏ 3 SP hiển thị đủ 3 nhưng request `items` chỉ có 2 (mất sản phẩm cuối) | BUG-07 |
| MFR-DT-32 | API | **Fail** | `checkout` thiếu `total_amount`: HTTP 200, tạo đơn rác | BUG-03 |
| MFR-DT-33 | API | **Fail** | `total_amount = -100`: HTTP 200, tạo đơn | BUG-03 |
| MFR-DT-34 | API | **Fail** | `total_amount = "abc"`: HTTP 200, tạo đơn | BUG-03 |
| MFR-DT-35 | API | Pass | `coupon-usage` không token → 401 | |
| MFR-DT-36 | API | **Fail** | `coupon_id = 99999` (không tồn tại): HTTP 200, ghi bản ghi `coupon_usage` | BUG-06 |
| MFR-DT-37 | API | Pass | Thiếu `code` → 400 | |
| MFR-DT-38 | API | Pass | Thiếu `total_amount` → 400 | |
| MFR-DT-39 | API | Pass | `total_amount` âm → 400 | |
| MFR-DT-40 | API | Pass | `total_amount = "abc"` → 400 | |

### BVA
| TC ID | Lớp chạy | Kết quả | Actual tóm tắt | Bug |
|---|---|---|---|---|
| MFR-BV-01 | UI+API | Pass | `SAVE10` @299,999: từ chối | |
| MFR-BV-02 | UI+API | **Fail** | `SAVE10` @**300,000** (= ngưỡng): bị từ chối "chưa đủ giá trị tối thiểu 300.000 ₫" | BUG-02 |
| MFR-BV-03 | API | **Fail** | `SAVE10` @300,001: `discount_amount = -2,700,009` | BUG-01 |
| MFR-BV-04 | API | Pass | `BIGBUY` @499,999: từ chối | |
| MFR-BV-05 | API | **Fail** | `BIGBUY` @**500,000**: bị từ chối | BUG-02 |
| MFR-BV-06 | API | Pass | `BIGBUY` @500,001: 50,000 / 450,001 | |
| MFR-BV-07 | API | Pass | `expired_at` hôm qua: hết hạn | |
| MFR-BV-08 | API | Pass | `expired_at` hôm nay (kiểu ngày): hết hạn | |
| MFR-BV-09 | API | Pass | `expired_at` ngày mai: chấp nhận | |
| MFR-BV-10 | API | Pass | now − 1 phút: hết hạn | |
| MFR-BV-11 | API | Pass | now + 1 phút (giờ địa phương): chấp nhận | |
| MFR-BV-12 | API | Pass | `VIP100` đã dùng 0 lần: chấp nhận | |
| MFR-BV-13 | API | Pass | `VIP100` đã dùng 1 lần (`max−1`): chấp nhận | |
| MFR-BV-14 | API | Pass | `VIP100` đã dùng 2 lần (`= max`): từ chối | |
| MFR-BV-15 | API | **Fail** | Mã `fixed` 100,000 @99,999: `final_amount = -1` | BUG-05 |
| MFR-BV-16 | API | Pass | @100,000: `final = 0` | |
| MFR-BV-17 | API | Pass | @100,001: `final = 1` | |
| MFR-BV-18 | API | **Fail** | Mã `percent` 100% @1,000: `discount = -99,000`, `final = 100,000` | BUG-01 |
| MFR-BV-19 | API | **Fail** | `percent` 10% @9: `discount = -81` | BUG-01 |
| MFR-BV-20 | API | **Fail** | `percent` 10% @10: `discount = -90`, `final = 100` | BUG-01 |
| MFR-BV-21 | UI | Pass | Giỏ 1 SP: request `items` có 1 SP | |
| MFR-BV-22 | UI | **Fail** | Giỏ đúng 2 SP (FRM-100k, FRM-200k): request `items` chỉ có FRM-100k | BUG-07 |
| MFR-BV-23 | API | Pass | Mã dài 1000 ký tự: 404, không lỗi server | |

## 2. Quan sát thêm (không tính vào số bug)
- Đơn tạo từ Mobile có `shipping_address = NULL` (Mobile không gửi địa chỉ); SRS FR-08 không yêu cầu địa chỉ nên chỉ ghi nhận (Web Admin hiển thị "Chưa cập nhật").
- Thông báo kiểm tra theo thứ tự "ngưỡng" trước "hết hạn": mã hết hạn kèm đơn nhỏ báo "chưa đủ giá trị tối thiểu" (DT-19); spec không quy định thứ tự.
- Ngoài phạm vi (thuộc feature khác): màn hình đăng nhập Mobile ghi nhãn "Username" nhưng placeholder "Email" và nút "Sign In" bằng tiếng Anh (FR-21/FR-02); ô số lượng trong giỏ cộng thêm 1 khi gõ (`App.js:615-623`, FR-20); nhãn "Tổng tạm tính" (FR-07/FR-20).
- Logic server của FR-08 và FR-09 cũng nằm ở Web của thành viên khác: bug BUG-01..06 là lỗi backend dùng chung, báo ở đây kèm bằng chứng từ Mobile.

## 3. Thống kê Mobile FR-08/09

| Hạng mục | Số lượng |
|---|---|
| Test case thiết kế | **63** (40 Domain Testing + 23 BVA) |
| Đã thực thi | 63 |
| Pass | 42 (DT: 27, BV: 15) |
| Fail | 21 (DT: 13, BV: 8) |
| Chưa thực thi | 0 |
| Bug phân biệt (nguyên nhân gốc) | **8** (BUG-01 … BUG-08, xem `06_bugs.md`) |

Một số test cùng Fail do một nguyên nhân gốc (ví dụ mọi kết quả giảm theo % đều do BUG-01), nên số bug nhỏ hơn số test Fail.
