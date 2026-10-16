Mã giảm theo % tính sai: tiền giảm âm, tổng thanh toán tăng

- **Feature:** Mobile FR-09 (dùng chung backend với Web FR-09) — **Mức độ:** Critical (mã giảm giá làm tăng giá đơn hàng lên 10 lần)
- **Test liên quan:** MFR-DT-09, DT-25, DT-27, DT-30; MFR-BV-03, BV-18, BV-19, BV-20
- **Các bước tái hiện:**
  1. Chạy ứng dụng Mobile, đăng nhập `test@eshop.com`, thêm một sản phẩm giá 400,000 ₫ vào giỏ, bấm "Tiến hành thanh toán".
  2. Nhập mã `SAVE10`, bấm "Áp dụng".
  3. (Tùy chọn) bấm "Xác Nhận Thanh Toán" rồi xem đơn trong lịch sử.
  - Cách gọi API: `POST /api/apply-coupon` với `{"code":"SAVE10","total_amount":400000,"user_id":2}`.
- **Expected (SRS FR-09, README.md dòng 124):** `percent`: `discount_amount = total × discount_value / 100` = 40,000; `final_amount` = 360,000.
- **Actual:** Màn hình hiện "Tiết kiệm: **-3,600,000 ₫**", "Thành tiền: **4,000,000 ₫**", "Tổng thanh toán: 4,000,000 ₫". API trả `discount_amount = -3600000`, `final_amount = 4000000`. Nếu xác nhận, đơn được lưu với tổng 4,000,000 ₫. Công thức trong code là `total × (1 − discount_value)` với `discount_value = 10`. Mã `percent` 100% cho `discount = -99,000` @1,000.
- **Bằng chứng:** ![evidence/mobile_checkout_save10_negative_discount.jpg](https://raw.githubusercontent.com/nhaajtdajt/eshop-hw02-domain-testing/main/features/Mobile-FR-08-09/evidence/mobile_checkout_save10_negative_discount.jpg), [evidence/api_results.json](https://github.com/nhaajtdajt/eshop-hw02-domain-testing/blob/main/features/Mobile-FR-08-09/evidence/api_results.json), [evidence/ui_results.json](https://github.com/nhaajtdajt/eshop-hw02-domain-testing/blob/main/features/Mobile-FR-08-09/evidence/ui_results.json). Code: `backend/server.js:399-401, 419-421`.
