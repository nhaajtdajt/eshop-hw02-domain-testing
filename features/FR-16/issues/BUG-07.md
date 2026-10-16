Import bỏ qua ràng buộc danh mục và độ dài tên (FR-15)

- **Feature:** FR-16 (liên quan FR-15) — **Mức độ:** Minor (theo diễn giải: FR-16 không nêu rõ)
- **Test liên quan:** FR16-DT-23, DT-24, BV-14
- **Các bước tái hiện:** Import dòng có `category_id = 999` (không tồn tại), hoặc để trống `category_id`, hoặc `name` dài 256 ký tự.
- **Expected (SRS FR-15, dòng 195–197):** Tên tối đa 255 ký tự; danh mục phải chọn từ danh sách có sẵn.
- **Actual:** Cả ba đều được thêm: danh mục không tồn tại vẫn lưu `999`, danh mục rỗng được tự gán `1`, tên 256 ký tự được chấp nhận.
- **Bằng chứng:** [evidence/api_results.json](https://github.com/nhaajtdajt/eshop-hw02-domain-testing/blob/main/features/FR-16/evidence/api_results.json) (FR16-DT-23, DT-24, BV-14). Code: `backend/server.js:223` (`row.category_id || 1`).
