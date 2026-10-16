Parse CSV bằng `split(",")` làm hỏng trường có nháy kép/dấu phẩy

- **Feature:** FR-16 — **Mức độ:** Major (dữ liệu bị lưu sai, tên và giá lệch cột)
- **Test liên quan:** FR16-DT-02, DT-03, DT-43
- **Các bước tái hiện:**
  1. File `quoted.csv`:
     ```
     name,price,description,imageUrl,category_id
     "FR16-Áo, size M",100000,Mo ta,https://placehold.co/300,1
     ```
  2. Chọn file trên Web Admin, xem bảng "Xem trước", rồi bấm Import.
  3. Mở danh sách sản phẩm và xem bản ghi vừa thêm.
  4. Lặp lại với tên `"FR16-Màn hình 27"" IPS"`.
- **Expected (SRS FR-16, dòng 206):** Hỗ trợ trường chứa dấu phẩy nếu được bọc trong dấu nháy kép (RFC 4180); nháy kép được escape bằng `""`.
- **Actual:** Dòng bị cắt tại dấu phẩy trong nháy kép nên các cột lệch: `name = "FR16-Áo` (còn dấu `"`), `price = size M"`, `description = 100000`. Với `""` thì tên lưu còn nguyên `"FR16-Màn hình 27"" IPS"`. Nháy kép không đóng cũng được chấp nhận.
- **Bằng chứng:** ![evidence/ui_quoted_comma_preview.jpg](https://raw.githubusercontent.com/nhaajtdajt/eshop-hw02-domain-testing/main/features/FR-16/evidence/ui_quoted_comma_preview.jpg), [evidence/ui_results.json](https://github.com/nhaajtdajt/eshop-hw02-domain-testing/blob/main/features/FR-16/evidence/ui_results.json). Code: `frontend-admin/src/App.jsx:367-377` (`line.split(",")`).
