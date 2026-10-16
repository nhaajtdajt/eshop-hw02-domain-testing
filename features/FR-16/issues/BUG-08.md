Báo cáo import gây hiểu nhầm: banner xanh "Import hoàn tất" dù có lỗi, API luôn trả HTTP 200

- **Feature:** FR-16 — **Mức độ:** Minor
- **Test liên quan:** FR16-DT-32, DT-33 (và các test DT-16, DT-17, X-03 có cùng banner)
- **Các bước tái hiện:** Import file có một dòng thiếu tên (xem BUG-01) hoặc file phân cách bằng `;`; quan sát vùng thông báo dưới ô chọn file.
- **Expected (SRS FR-16, dòng 211):** Báo cáo rõ ràng: bao nhiêu dòng thành công, bao nhiêu dòng lỗi và lý do; khi có lỗi, import bị hủy toàn bộ và báo rõ như vậy.
- **Actual:** Banner xanh "✅ Import hoàn tất: 2/3 sản phẩm được thêm" kèm danh sách lỗi; không nêu **số** dòng lỗi và không báo import bị hủy. Với file chỉ có lỗi vẫn hiện "✅ Import hoàn tất: 0/1". API luôn trả HTTP 200.
- **Bằng chứng:** ![evidence/ui_partial_import_green_banner.jpg](https://raw.githubusercontent.com/nhaajtdajt/eshop-hw02-domain-testing/main/features/FR-16/evidence/ui_partial_import_green_banner.jpg), [evidence/api_results.json](https://github.com/nhaajtdajt/eshop-hw02-domain-testing/blob/main/features/FR-16/evidence/api_results.json), [evidence/ui_exploratory.json](https://github.com/nhaajtdajt/eshop-hw02-domain-testing/blob/main/features/FR-16/evidence/ui_exploratory.json). Code: `backend/server.js:234-240`, `frontend-admin/src/App.jsx:459-480`.
