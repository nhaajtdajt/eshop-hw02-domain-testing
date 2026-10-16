Lỗi chuyển trạng thái không hợp lệ hiển thị tiếng Anh trên Web Admin

- **Feature:** FR-10 (liên quan FR-21) — **Mức độ:** Minor
- **Test liên quan:** FR10-DT-54
- **Các bước tái hiện:**
  1. Mở Web Admin, tab "Đơn hàng", để một đơn `pending` hiển thị (nút "Xác nhận").
  2. Trước khi bấm, xác nhận đơn đó bằng API (hoặc ở tab khác) để trạng thái đã đổi nhưng trang chưa tải lại.
  3. Bấm "Xác nhận" trên trang cũ.
- **Expected (SRS FR-10 dòng 162; FR-21 dòng 244):** Thông báo lỗi phù hợp, bằng tiếng Việt, dễ hiểu.
- **Actual:** Hộp thoại "Lỗi: Invalid state transition from confirmed to confirmed" — tiếng Anh, chứa tên trạng thái kỹ thuật.
- **Bằng chứng:** [evidence/ui_results.json](https://github.com/nhaajtdajt/eshop-hw02-domain-testing/blob/main/features/FR-10/evidence/ui_results.json) (`admin_ui_stale_action_DT54`). Code: `frontend-admin/src/App.jsx:90-91`, `backend/server.js:555`.
