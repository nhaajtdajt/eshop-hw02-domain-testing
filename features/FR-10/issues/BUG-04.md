Trang Hồ sơ (Web) hiện nút "Hủy đơn" cho đơn đang giao

- **Feature:** FR-10 — **Mức độ:** Major (giao diện cho phép đúng thao tác bị cấm)
- **Test liên quan:** FR10-DT-51
- **Các bước tái hiện:**
  1. Đưa một đơn của `test@eshop.com` tới trạng thái `shipping` (qua Admin).
  2. Đăng nhập Web `http://localhost:5173` bằng `test@eshop.com`, mở `/profile`.
  3. Xem cột "Thao tác" của đơn "Đang giao" và bấm "Hủy đơn".
- **Expected (SRS FR-10, dòng 161; FR-20, dòng 236 cho Mobile cùng quy tắc):** Không hiển thị/không cho hủy khi `shipping`; chỉ hủy được ở `pending`/`confirmed`.
- **Actual:** Đơn "Đang giao" vẫn có nút "Hủy đơn"; bấm vào hiện "Hủy đơn thành công!" và đơn chuyển "Đã hủy" (kết hợp BUG-03). Các đơn `delivered`/`canceled` thì đúng là không có nút.
- **Bằng chứng:** ![evidence/web_profile_orders_before.jpg](https://raw.githubusercontent.com/nhaajtdajt/eshop-hw02-domain-testing/main/features/FR-10/evidence/web_profile_orders_before.jpg) (đơn #3 "Đang giao" có nút), ![evidence/web_profile_cancel_shipping_after.jpg](https://raw.githubusercontent.com/nhaajtdajt/eshop-hw02-domain-testing/main/features/FR-10/evidence/web_profile_cancel_shipping_after.jpg) (đơn #3 sau khi bấm: "Đã hủy"), [evidence/ui_results.json](https://github.com/nhaajtdajt/eshop-hw02-domain-testing/blob/main/features/FR-10/evidence/ui_results.json). Code: `frontend-web/src/pages/Profile.jsx:199-206` (điều kiện `status !== "delivered" && status !== "canceled"`).
