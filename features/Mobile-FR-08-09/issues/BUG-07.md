Mobile bỏ mất sản phẩm cuối của giỏ khi gửi yêu cầu thanh toán

- **Feature:** Mobile FR-08 — **Mức độ:** Major (dữ liệu đơn hàng thiếu sản phẩm; hiện chưa lộ ra vì backend không dùng `items`)
- **Test liên quan:** MFR-DT-31, MFR-BV-22
- **Các bước tái hiện:**
  1. Đăng nhập; thêm vào giỏ `FRM-100k` và `FRM-200k` (hoặc hai sản phẩm bất kỳ).
  2. Mở giỏ, "Tiến hành thanh toán": màn hình liệt kê đủ 2 sản phẩm.
  3. Bấm "Xác Nhận Thanh Toán" và quan sát body request `POST /api/checkout` (ví dụ bằng DevTools Network).
- **Expected (SRS FR-08, dòng 106):** Giao diện/đơn hàng chứa đầy đủ sản phẩm đặt mua; request gửi đủ mọi sản phẩm trong giỏ.
- **Actual:** `items` chỉ có `FRM-100k`; sản phẩm cuối (`FRM-200k`) bị bỏ. Giỏ 3 sản phẩm gửi 2 sản phẩm; giỏ 1 sản phẩm gửi đủ 1. Mã nguồn dùng `items: cart.length > 1 ? cart.slice(0, -1) : cart`.
- **Bằng chứng:** [evidence/ui_results.json](https://github.com/nhaajtdajt/eshop-hw02-domain-testing/blob/main/features/Mobile-FR-08-09/evidence/ui_results.json) (`BV-22_cart_with_2_items`, `DT-31_cart_with_3_items`). Code: `frontend-mobile/App.js:391`.
