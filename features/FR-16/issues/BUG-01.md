Import không rollback: dòng hợp lệ vẫn được thêm khi file có dòng lỗi

- **Feature:** FR-16 (Pool C) — **Mức độ:** Major
- **Test liên quan:** FR16-DT-25..DT-29, DT-32, DT-33, BV-15..BV-19
- **Các bước tái hiện:**
  1. Đăng nhập Web Admin `http://localhost:5174`, mở tab "Sản phẩm" (ghi số sản phẩm hiện có).
  2. Tạo file `partial.csv`:
     ```
     name,price,description,imageUrl,category_id
     FR16-1,100000,Mo ta,https://placehold.co/300,1
     ,100000,Mo ta,https://placehold.co/300,1
     FR16-3,100000,Mo ta,https://placehold.co/300,1
     ```
  3. Chọn file, bấm "Import 3 sản phẩm".
  4. Kiểm tra danh sách sản phẩm.
- **Expected (SRS FR-16, README.md dòng 210):** Có lỗi ở bất kỳ dòng nào thì toàn bộ import bị rollback (all-or-nothing); không sản phẩm nào được thêm.
- **Actual:** Dòng 1 và 3 được thêm; chỉ dòng 2 bị bỏ qua: "Import hoàn tất: 2/3 sản phẩm được thêm — Hàng 3: Thiếu tên sản phẩm". Cùng kết quả khi gọi API trực tiếp. Mỗi dòng được `INSERT` riêng, không có transaction.
- **Bằng chứng:** ![evidence/ui_partial_import_green_banner.jpg](https://raw.githubusercontent.com/nhaajtdajt/eshop-hw02-domain-testing/main/features/FR-16/evidence/ui_partial_import_green_banner.jpg), [evidence/api_results.json](https://github.com/nhaajtdajt/eshop-hw02-domain-testing/blob/main/features/FR-16/evidence/api_results.json), [evidence/ui_results.json](https://github.com/nhaajtdajt/eshop-hw02-domain-testing/blob/main/features/FR-16/evidence/ui_results.json). Code: `backend/server.js:206-232`.
