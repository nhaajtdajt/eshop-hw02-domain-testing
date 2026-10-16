Không kiểm tra header và số trường của dòng

- **Feature:** FR-16 — **Mức độ:** Major
- **Test liên quan:** FR16-DT-12..DT-15, BV-05, BV-06
- **Các bước tái hiện:**
  1. Import file có header sai thứ tự `price,name,description,imageUrl,category_id`, hoặc thiếu cột `price`, thừa cột `sku`, hoặc viết hoa `Name,Price,...`.
  2. Import file có một dòng chỉ 4 trường, hoặc 6 trường.
- **Expected (SRS FR-16, dòng 205):** Dòng đầu phải là đúng `name,price,description,imageUrl,category_id`; file không đúng bị từ chối.
- **Actual:** Tất cả đều import thành công (DB tăng): header không được kiểm tra, cột thiếu cho giá trị rỗng/mặc định (`category_id` tự gán 1), cột thừa bị bỏ qua. Code còn chấp nhận các tên cột khác (`ten`, `gia`, `Name`, `Price`…).
- **Bằng chứng:** [evidence/ui_results.json](https://github.com/nhaajtdajt/eshop-hw02-domain-testing/blob/main/features/FR-16/evidence/ui_results.json) (DT-12..15, BV-05, BV-06). Code: `frontend-admin/src/App.jsx:368-402`.
