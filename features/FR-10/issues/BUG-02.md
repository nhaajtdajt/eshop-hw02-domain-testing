Web Admin hiện nút "Đánh dấu Đã giao" cho đơn đã hủy

- **Feature:** FR-10 — **Mức độ:** Minor (giao diện mời thao tác sai, hệ quả là BUG-01)
- **Test liên quan:** FR10-DT-48
- **Các bước tái hiện:**
  1. Có một đơn đã hủy (ví dụ hủy đơn từ trang Hồ sơ hoặc từ Admin).
  2. Đăng nhập Web Admin `http://localhost:5174`, mở tab "Đơn hàng".
  3. Quan sát cột "Hành động" của đơn có trạng thái "Đã hủy".
- **Expected (SRS FR-10, dòng 160; FR-18, dòng 221):** Đơn `canceled` là trạng thái kết thúc nên không có hành động chuyển trạng thái nào.
- **Actual:** Đơn "Đã hủy" có nút **"Đánh dấu Đã giao"**; bấm vào là chuyển được (xem BUG-01). Đơn "Đã giao" thì đúng là không có nút.
- **Bằng chứng:** ![evidence/admin_orders_ui_states.jpg](https://raw.githubusercontent.com/nhaajtdajt/eshop-hw02-domain-testing/main/features/FR-10/evidence/admin_orders_ui_states.jpg), [evidence/ui_results.json](https://github.com/nhaajtdajt/eshop-hw02-domain-testing/blob/main/features/FR-10/evidence/ui_results.json). Code: `frontend-admin/src/App.jsx:862-869`.
