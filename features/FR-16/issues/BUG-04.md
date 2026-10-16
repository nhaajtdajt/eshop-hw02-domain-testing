Chấp nhận file không phải `.csv`

- **Feature:** FR-16 — **Mức độ:** Minor
- **Test liên quan:** FR16-DT-07, DT-08
- **Các bước tái hiện:** Đổi tên file CSV hợp lệ thành `products.txt` (hoặc `products.xlsx`) rồi chọn trong ô "Import sản phẩm từ CSV" và bấm Import.
- **Expected (SRS FR-16, dòng 204):** Đuôi file phải là `.csv`; file khác bị từ chối.
- **Actual:** File `.txt` và `.xlsx` vẫn được đọc và import (DB tăng). `<input type="file">` không có thuộc tính `accept` và code không kiểm tra tên file.
- **Bằng chứng:** [evidence/ui_results.json](https://github.com/nhaajtdajt/eshop-hw02-domain-testing/blob/main/features/FR-16/evidence/ui_results.json) (`file_input_accept_attribute: null`). Code: `frontend-admin/src/App.jsx:356-358`.
