# Mobile FR-08/09: Bug report

Môi trường chung: Windows 11, Node v22.20.0, Backend `http://localhost:3000`, ứng dụng Mobile chạy bằng **Expo Web** (`react-native-web`, Chromium trong Claude desktop; `API_URL` đổi tạm sang `localhost`), dữ liệu seed gốc. Ngày phát hiện: 2026-10-16. Spec = `README.md` (SRS). Mức độ: Critical > Major > Minor. **Chưa kiểm tra trên thiết bị thật/emulator.**
Tài khoản: User `test@eshop.com` / `Test1234!`, Admin `admin@eshop.com` / `Admin123!`.
Mã seed: `SAVE10` (percent 10, min 300,000, 1 lần), `BIGBUY` (fixed 50,000, min 500,000), `VIP100` (fixed 100,000, min 300,000, 2 lần), `EXPIRED`.
Ghi chú: BUG-01..06 nằm ở backend dùng chung với Web (FR-08/FR-09 của thành viên khác); báo ở đây kèm bằng chứng từ màn hình Mobile. Nên đối chiếu để tránh báo trùng khi nhóm tổng hợp.

Trạng thái GitHub Issues: **đã đăng** #29–#36 (tiêu đề có tiền tố `[Mobile FR-08/09]`, nhãn `bug`) tại https://github.com/nhaajtdajt/eshop-hw02-domain-testing/issues. Nội dung từng issue nằm trong `features/Mobile-FR-08-09/issues/`.

| Bug | Tiêu đề | Mức độ | Test liên quan | Issue |
|---|---|---|---|---|
| BUG-01 | Mã giảm theo % tính sai: tiền giảm âm, tổng thanh toán tăng | Critical | DT-09, 25, 27, 30; BV-03, 18, 19, 20 | #29 |
| BUG-02 | Tổng đơn đúng bằng ngưỡng tối thiểu bị từ chối (`>` thay vì `>=`) | Major | BV-02, BV-05 | #30 |
| BUG-03 | Checkout lưu nguyên `total_amount` của client, không kiểm tra giá trị | Critical | DT-07, 30, 32, 33, 34 | #31 |
| BUG-04 | Áp mã không cần đăng nhập và bỏ `user_id` là qua mặt kiểm tra lượt dùng | Major | DT-22, DT-24 | #32 |
| BUG-05 | Mã giảm cố định lớn hơn tổng đơn cho tổng thanh toán âm | Major | DT-26, BV-15 | #33 |
| BUG-06 | `coupon-usage` ghi lượt dùng cho mã không tồn tại | Minor | DT-36 | #34 |
| BUG-07 | Mobile bỏ mất sản phẩm cuối của giỏ khi gửi yêu cầu thanh toán | Major | DT-31, BV-22 | #35 |
| BUG-08 | Ô "Tổng tiền thanh toán" hiển thị số thô, không có `₫` và phân cách hàng nghìn | Minor | DT-27 | #36 |

---

### BUG-01: Mã giảm theo % tính sai: tiền giảm âm, tổng thanh toán tăng
- **Feature:** Mobile FR-09 (dùng chung backend với Web FR-09) — **Mức độ:** Critical (mã giảm giá làm tăng giá đơn hàng lên 10 lần)
- **Test liên quan:** MFR-DT-09, DT-25, DT-27, DT-30; MFR-BV-03, BV-18, BV-19, BV-20
- **Các bước tái hiện:**
  1. Chạy ứng dụng Mobile, đăng nhập `test@eshop.com`, thêm một sản phẩm giá 400,000 ₫ vào giỏ, bấm "Tiến hành thanh toán".
  2. Nhập mã `SAVE10`, bấm "Áp dụng".
  3. (Tùy chọn) bấm "Xác Nhận Thanh Toán" rồi xem đơn trong lịch sử.
  - Cách gọi API: `POST /api/apply-coupon` với `{"code":"SAVE10","total_amount":400000,"user_id":2}`.
- **Expected (SRS FR-09, README.md dòng 124):** `percent`: `discount_amount = total × discount_value / 100` = 40,000; `final_amount` = 360,000.
- **Actual:** Màn hình hiện "Tiết kiệm: **-3,600,000 ₫**", "Thành tiền: **4,000,000 ₫**", "Tổng thanh toán: 4,000,000 ₫". API trả `discount_amount = -3600000`, `final_amount = 4000000`. Nếu xác nhận, đơn được lưu với tổng 4,000,000 ₫. Công thức trong code là `total × (1 − discount_value)` với `discount_value = 10`. Mã `percent` 100% cho `discount = -99,000` @1,000.
- **Bằng chứng:** `evidence/mobile_checkout_save10_negative_discount.jpg`, `evidence/api_results.json`, `evidence/ui_results.json`. Code: `backend/server.js:399-401, 419-421`.

### BUG-02: Tổng đơn đúng bằng ngưỡng tối thiểu bị từ chối (`>` thay vì `>=`)
- **Feature:** Mobile FR-09 (dùng chung backend) — **Mức độ:** Major
- **Test liên quan:** MFR-BV-02, MFR-BV-05
- **Các bước tái hiện:** Giỏ có tổng đúng 300,000 ₫ (sản phẩm giá 300,000 × 1), thanh toán, nhập `SAVE10`, bấm "Áp dụng" (hoặc `POST /api/apply-coupon` `{"code":"BIGBUY","total_amount":500000,"user_id":2}`).
- **Expected (SRS FR-09, dòng 118):** C3: tổng đơn **>=** `min_order_amount`; tổng 300,000 với `SAVE10` (min 300,000) phải được áp dụng.
- **Actual:** "Đơn hàng chưa đủ giá trị tối thiểu 300.000 ₫ để áp dụng mã này". Tương tự `BIGBUY` @500,000. Mã chỉ áp dụng được từ ngưỡng + 1 (300,001 / 500,001).
- **Bằng chứng:** `evidence/api_results.json` (MFR-BV-02, BV-05), `evidence/ui_results.json` (BV-02). Code: `backend/server.js:379` (`total_amount > coupon.min_order_amount`).

### BUG-03: Checkout lưu nguyên `total_amount` của client, không kiểm tra giá trị
- **Feature:** Mobile FR-08 (dùng chung backend với Web FR-08) — **Mức độ:** Critical
- **Test liên quan:** MFR-DT-07, DT-30, DT-32, DT-33, DT-34
- **Các bước tái hiện:**
  1. Đăng nhập lấy token User.
  2. `POST /api/checkout` với `{"items":[{"id":1,"name":"iPhone 15 Pro Max","price":30000000,"quantity":1}],"total_amount":1}`.
  3. Lặp lại với `total_amount` bị thiếu, `-100`, `"abc"`.
  4. Xem đơn trong `GET /api/orders/my-orders`.
- **Expected (SRS FR-08, dòng 107):** Backend tự tính lại tổng tiền; không chấp nhận `total_amount` do client gửi lên (đơn phải có tổng 30,000,000 hoặc bị từ chối).
- **Actual:** HTTP 200 "Checkout successful"; đơn lưu `total_amount = 1`. Với thiếu/âm/chuỗi cũng tạo đơn thành công (đơn rác). Ứng dụng Mobile gửi `total_amount` do client tính (kể cả số sai của BUG-01: đơn #75 lưu 4,000,000 thay vì 360,000).
- **Bằng chứng:** `evidence/api_results.json` (DT-07, DT-32..34), `evidence/ui_results.json` (DT-30). Code: `backend/server.js:297-309`.

### BUG-04: Áp mã không cần đăng nhập và bỏ `user_id` là qua mặt kiểm tra lượt dùng
- **Feature:** Mobile FR-09 (dùng chung backend) — **Mức độ:** Major
- **Test liên quan:** MFR-DT-22, MFR-DT-24
- **Các bước tái hiện:**
  1. `POST /api/apply-coupon` **không có** header `Authorization` với `{"code":"SAVE10","total_amount":400000}` → áp dụng thành công.
  2. Cho user đã dùng `SAVE10` một lần (đã thanh toán), gọi lại `apply-coupon` **không** gửi `user_id` (hoặc không token).
- **Expected (SRS FR-09, dòng 119–120; SEC-02, dòng 279):** C4: phải đăng nhập (JWT hợp lệ); C5: số lần đã dùng của user < `max_uses_per_user`.
- **Actual:** HTTP 200 trong cả hai trường hợp: endpoint không yêu cầu token; `user_id` do client tự gửi nên chỉ cần bỏ trường này là không còn bị kiểm tra lượt dùng.
- **Bằng chứng:** `evidence/api_results.json` (DT-22, DT-24). Code: `backend/server.js:363-433` (không có `authenticateToken`; kiểm tra lượt dùng chỉ khi `if (user_id)`).

### BUG-05: Mã giảm cố định lớn hơn tổng đơn cho tổng thanh toán âm
- **Feature:** Mobile FR-09 (dùng chung backend) — **Mức độ:** Major (theo diễn giải: SRS không nêu, nhưng tổng thanh toán âm là bất hợp lý)
- **Test liên quan:** MFR-DT-26, MFR-BV-15
- **Các bước tái hiện:** Admin tạo mã `fixed` 100,000, min 0 (`POST /api/admin/coupons`); `POST /api/apply-coupon` với `total_amount = 99999`.
- **Expected (diễn giải theo FR-09, dòng 126):** `final_amount` không âm (tối đa giảm bằng tổng đơn, cho `final = 0`).
- **Actual:** `discount_amount = 100000`, `final_amount = -1` (với mã 1,000,000 @100,000: `final = -900,000`).
- **Bằng chứng:** `evidence/api_results.json` (MFR-DT-26, BV-15). Code: `backend/server.js:402-406`.

### BUG-06: `coupon-usage` ghi lượt dùng cho mã không tồn tại
- **Feature:** Mobile FR-09 (dùng chung backend) — **Mức độ:** Minor
- **Test liên quan:** MFR-DT-36
- **Các bước tái hiện:** Với token User, `POST /api/coupon-usage` `{"coupon_id":99999}`.
- **Expected:** Từ chối (4xx) vì mã không tồn tại; không ghi bản ghi.
- **Actual:** HTTP 200 "Usage recorded"; bản ghi mới trong `coupon_usage` với `coupon_id = 99999`.
- **Bằng chứng:** `evidence/api_results.json` (MFR-DT-36). Code: `backend/server.js:444-454`.

### BUG-07: Mobile bỏ mất sản phẩm cuối của giỏ khi gửi yêu cầu thanh toán
- **Feature:** Mobile FR-08 — **Mức độ:** Major (dữ liệu đơn hàng thiếu sản phẩm; hiện chưa lộ ra vì backend không dùng `items`)
- **Test liên quan:** MFR-DT-31, MFR-BV-22
- **Các bước tái hiện:**
  1. Đăng nhập; thêm vào giỏ `FRM-100k` và `FRM-200k` (hoặc hai sản phẩm bất kỳ).
  2. Mở giỏ, "Tiến hành thanh toán": màn hình liệt kê đủ 2 sản phẩm.
  3. Bấm "Xác Nhận Thanh Toán" và quan sát body request `POST /api/checkout` (ví dụ bằng DevTools Network).
- **Expected (SRS FR-08, dòng 106):** Giao diện/đơn hàng chứa đầy đủ sản phẩm đặt mua; request gửi đủ mọi sản phẩm trong giỏ.
- **Actual:** `items` chỉ có `FRM-100k`; sản phẩm cuối (`FRM-200k`) bị bỏ. Giỏ 3 sản phẩm gửi 2 sản phẩm; giỏ 1 sản phẩm gửi đủ 1. Mã nguồn dùng `items: cart.length > 1 ? cart.slice(0, -1) : cart`.
- **Bằng chứng:** `evidence/ui_results.json` (`BV-22_cart_with_2_items`, `DT-31_cart_with_3_items`). Code: `frontend-mobile/App.js:391`.

### BUG-08: Ô "Tổng tiền thanh toán" hiển thị số thô, không có `₫` và phân cách hàng nghìn
- **Feature:** Mobile FR-08 (liên quan FR-21) — **Mức độ:** Minor
- **Test liên quan:** MFR-DT-27
- **Các bước tái hiện:** Thêm sản phẩm 400,000 ₫, vào màn "Xác Nhận Đơn Hàng", xem ô "Tổng tiền thanh toán (VND)".
- **Expected (SRS FR-21, dòng 246):** Luôn dùng ký hiệu `₫` với định dạng phân cách hàng nghìn.
- **Actual:** Ô hiển thị `400000`; các dòng khác ("Tổng thanh toán: 400,000 ₫") đúng định dạng.
- **Bằng chứng:** `evidence/mobile_checkout_save10_negative_discount.jpg`, `evidence/ui_results.json`. Code: `frontend-mobile/App.js:684-690` (`value={String(cartTotal)}`).

---

## Quan sát (không tính là bug của Mobile FR-08/09)
- Đơn tạo từ Mobile có `shipping_address = NULL` (Mobile không gửi địa chỉ); SRS không yêu cầu địa chỉ ở FR-08.
- Báo lỗi theo thứ tự "ngưỡng" trước "hết hạn" (mã hết hạn + đơn nhỏ báo "chưa đủ giá trị tối thiểu"); SRS không quy định thứ tự.
- `API_URL` trong `App.js` cứng là `http://192.168.10.13:3000/api`; phải sửa theo IP máy chủ khi chạy (SRS có ghi "IP LAN của máy chủ").
- Ngoài phạm vi, nên báo thành viên phụ trách: màn đăng nhập Mobile dùng nhãn "Username" (placeholder "Email") và nút "Sign In" tiếng Anh (FR-21/FR-02); ô số lượng trong giỏ cộng thêm 1 khi gõ (`App.js:615-623`, FR-20); nhãn "Tổng tạm tính" (FR-20).
- Chưa test: mất kết nối khi thanh toán, nhấn xác nhận thanh toán hai lần liên tiếp, thiết bị thật/emulator.
