# Mobile FR-08/09: Thanh toán và Mã giảm giá trên Mobile — Phân tích

Phạm vi: màn hình **Giỏ hàng → Xác Nhận Đơn Hàng (checkout)** và khối **Mã Giảm Giá** của ứng dụng Mobile (`frontend-mobile/App.js`: `renderCart`, `renderCheckout`, `openCheckout`, `handleApplyCoupon`, `handleConfirmCheckout`), cùng các API mà nó gọi: `POST /api/apply-coupon`, `POST /api/checkout`, `POST /api/coupon-usage`.

Lưu ý ranh giới với thành viên khác: logic server của FR-08 (checkout) và FR-09 (coupon) cũng được test ở phiên bản Web bởi người khác, còn **giao diện và luồng Mobile** là phần của feature này. Bug ở backend dùng chung vẫn được báo kèm bằng chứng từ Mobile, có ghi chú "dùng chung với Web".

## 1. Yêu cầu theo SRS (`README.md`)

> **FR-08 — Thanh toán** (dòng 102–108):
> - Chỉ người dùng **đã đăng nhập** mới tiến hành thanh toán được.
> - **Tổng tiền thanh toán** được tính tự động từ giỏ hàng và không cho phép người dùng chỉnh sửa trực tiếp.
> - Giao diện hiển thị đầy đủ danh sách sản phẩm đặt mua.
> - Backend phải tự tính lại tổng tiền; không chấp nhận giá trị `total_amount` do client gửi lên.
> - Sau thanh toán thành công, giỏ hàng được xóa.
>
> **FR-09 — Mã giảm giá** (dòng 110–135): tại bước Checkout, nhập mã giảm giá; áp dụng khi **cả 5 điều kiện** thỏa mãn:
> | C1 | Mã tồn tại và `is_active = 1` | C2 | Còn hạn: ngày hiện tại trước `expired_at` | C3 | Tổng đơn **>=** `min_order_amount` | C4 | Đã đăng nhập (JWT hợp lệ) | C5 | Số lần đã dùng < `max_uses_per_user` |
> Công thức: `percent`: `discount_amount = total × discount_value / 100`; `fixed`: `discount_amount = discount_value`; `final_amount = total − discount_amount`.
> Mã mẫu: `SAVE10` (percent 10%, min 300,000, 1 lần/người), `BIGBUY` (fixed 50,000, min 500,000, 1 lần), `VIP100` (fixed 100,000, min 300,000, 2 lần), `EXPIRED` (percent 20%, min 100,000, hết hạn 2020-01-01).

Các yêu cầu liên quan ở mục khác:

> **FR-20** (dòng 235): Mobile có đầy đủ chức năng, trong đó có Thanh toán. **FR-21** (dòng 246): tiền luôn dùng ký hiệu `₫` với phân cách hàng nghìn. **SEC-02** (dòng 279): API có tính bảo mật phải yêu cầu JWT hợp lệ.

Điểm spec mơ hồ/chưa định lượng:
- Thứ tự thông báo lỗi khi vi phạm nhiều điều kiện (ví dụ mã hết hạn **và** chưa đủ ngưỡng) không được quy định; chỉ cần mã bị từ chối với lý do hợp lý.
- Hành vi khi `discount_amount > total` (mã cố định lớn hơn đơn): spec không nêu; giá trị cuối âm là bất hợp lý nên coi "tổng thanh toán không âm" là kỳ vọng hợp lý (ghi là diễn giải).
- Không nêu làm tròn khi giảm theo phần trăm.

## 2. Input / Điều kiện / Output

| Loại | Tên | Mô tả | Ràng buộc theo spec |
|---|---|---|---|
| Precondition | trạng thái đăng nhập | Đã/chưa đăng nhập | Chỉ người đã đăng nhập thanh toán (FR-08) và dùng mã (C4) |
| Precondition | giỏ hàng | danh sách sản phẩm, số lượng | tổng = Σ đơn giá × số lượng; hiển thị đủ sản phẩm |
| Input | mã giảm giá `code` | nhập ở ô "Nhập mã giảm giá..." | tồn tại, đang hoạt động (C1) |
| Input | tổng đơn `total_amount` | = tổng giỏ | `>= min_order_amount` (C3) |
| Input | ngày hiện tại so với `expired_at` | | trước `expired_at` (C2) |
| Input | số lần đã dùng của user | | `< max_uses_per_user` (C5) |
| Input | loại mã, giá trị | `percent` / `fixed` | công thức ở trên |
| Hành động | "Áp dụng", "Xác Nhận Thanh Toán" | | |
| Output | `discount_amount`, `final_amount`, thông báo | hiển thị "Tiết kiệm", "Thành tiền", "Tổng thanh toán" | tính đúng theo công thức |
| Output | đơn hàng được tạo | `status = pending`, `total_amount` do **backend** tính | không tin `total_amount` từ client |
| Output | giỏ hàng sau thanh toán | rỗng | |

## 3. Spec vs Code (giả thuyết cần kiểm chứng)

Nguồn: `frontend-mobile/App.js:16,75-77,342-420,590-757`; `backend/server.js:297-309` (checkout), `:363-441` (apply-coupon), `:444-454` (coupon-usage).

| # | Spec nói | Code làm | File:dòng | Trạng thái |
|---|---|---|---|---|
| H1 | `percent`: `total × value / 100` | `Math.floor(total * (1 - discount_value))` → với `SAVE10` (value = 10) ra số **âm**; `final_amount` lớn hơn tổng | server.js:399-401, 419-421 | Chưa kiểm chứng |
| H2 | C3: tổng đơn **>=** `min_order_amount` | Dùng `>` → đúng bằng ngưỡng bị từ chối | server.js:379 | Chưa kiểm chứng |
| H3 | C4: phải đăng nhập (JWT) | `apply-coupon` không yêu cầu token; `user_id` do client gửi; bỏ trống `user_id` thì **bỏ qua** kiểm tra C5 | server.js:363-433 | Chưa kiểm chứng |
| H4 | C5: đã dùng < `max_uses_per_user` | Kiểm tra bằng `count >= max` (đúng) nhưng chỉ khi có `user_id`; lượt dùng chỉ ghi sau checkout bởi request riêng `/coupon-usage` | server.js:386-396, 444-454; App.js:399-408 | Cần thử |
| H5 | Backend tự tính lại tổng, không tin `total_amount` của client | `checkout` lưu thẳng `total_amount` từ body; không kiểm tra giỏ hàng/mã | server.js:297-309 | Chưa kiểm chứng |
| H6 | Hiển thị đầy đủ sản phẩm đặt mua | Gửi `items: cart.slice(0, -1)` khi giỏ có hơn 1 món → **bỏ mất món cuối** (backend hiện bỏ qua `items`) | App.js:391 | Cần thử (bắt request) |
| H7 | Chỉ người đã đăng nhập thanh toán | UI chặn ở `openCheckout`; API trả 401 nếu không token | App.js:343-347; server.js:297 | Có vẻ đúng, cần thử |
| H8 | Tổng tiền thanh toán không cho sửa | Ô "Tổng tiền thanh toán" `editable={false}`, hiển thị `cartTotal` | App.js:684-690 | Có vẻ đúng |
| H9 | Sau thanh toán giỏ hàng được xóa | `setCart([])`, xóa mã | App.js:410-414 | Có vẻ đúng, cần thử |
| H10 | Lý do hợp lý khi mã bị từ chối | Kiểm tra ngưỡng **trước** hạn dùng nên mã hết hạn + đơn nhỏ báo "chưa đủ giá trị tối thiểu" | server.js:379-384 | Cần thử |
| H11 | Tổng thanh toán không âm (diễn giải) | Mã `fixed` lớn hơn tổng cho `final_amount` âm | server.js:402-406 | Cần thử (tạo mã bằng API admin) |
| H12 | `Tổng thanh toán` hiển thị đúng | Ô trên cùng luôn là `cartTotal` (chưa giảm), dòng "Tổng thanh toán" mới là số sau giảm | App.js:684-741 | Có vẻ đúng |
| H13 | Địa chỉ giao hàng của đơn | Mobile không gửi `shipping_address` → đơn không có địa chỉ | App.js:390-394; server.js:299 | Quan sát |
| H14 | Cấu hình chạy được | `API_URL` cứng là `http://192.168.10.13:3000/api`, không khớp IP máy test (192.168.1.225) → app không kết nối nếu không sửa | App.js:16 | Quan sát môi trường |
| H15 | Số lượng trong giỏ đúng (FR-20) | Ô số lượng trong giỏ cộng thêm 1 (`parsed + 1`) khi gõ → sai tổng | App.js:615-623 | Ngoài phạm vi (FR-20 của thành viên khác), nhưng ảnh hưởng dữ liệu test nên tránh dùng ô này |
| H16 | Mã không phân biệt hoa/thường khi nhập | Client `toUpperCase()` rồi gửi; API so sánh chính xác | App.js:366 | Cần thử |

## 4. Nhận xét ảnh hưởng thiết kế test

- Miền đầu vào của coupon gồm 5 điều kiện C1..C5 độc lập: dùng bảng quyết định, mỗi test chỉ làm sai **một** điều kiện, các điều kiện khác đúng; thêm test mã hợp lệ cho từng loại `percent`/`fixed` và test tính tiền.
- Tính tiền kiểm tra bằng **công thức của spec**, không lấy số do hệ thống trả làm chuẩn.
- Biên: ngưỡng `min_order_amount` (−1, =, +1), hạn dùng (hôm qua/hôm nay/ngày mai), số lần dùng (`max−1`, `max`), số lượng/tổng giỏ, mã có khoảng trắng và chữ thường.
- Hai lớp thực thi: **UI Mobile** (chạy bằng Expo Web / `react-native-web`) và **API**. Giới hạn: không có thiết bị thật/emulator; hộp thoại `Alert.alert` không hiển thị trên bản web, nên các thông báo dạng `Alert` chỉ kiểm tra gián tiếp (chuyển màn hình, trạng thái giỏ/đơn).
- Dữ liệu tạo qua API trước mỗi test: user có token (đăng nhập), mã tùy chỉnh bằng `POST /api/admin/coupons` (API này không kiểm tra role nên dùng được để tạo mã hết hạn/ngưỡng khác).
