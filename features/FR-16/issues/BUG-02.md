Không validate `price`: số âm, 0, chữ và rỗng đều được import

- **Feature:** FR-16 — **Mức độ:** Major
- **Test liên quan:** FR16-DT-19..DT-22
- **Các bước tái hiện:**
  1. File CSV một dòng dữ liệu có `price` lần lượt là `-1`, `0`, `abc` và để trống, ví dụ `FR16-1,-1,Mo ta,https://placehold.co/300,1`.
  2. Import trên Web Admin (hoặc `POST /api/admin/import-products` với `{"products":[{"name":"FR16-1","price":-1,"category_id":1}]}`).
  3. Kiểm tra danh sách sản phẩm.
- **Expected (SRS FR-16, dòng 208–209):** `price` phải là số dương; dòng sai bị từ chối (và theo rollback thì cả file không được import).
- **Actual:** Cả 4 trường hợp đều được thêm vào DB (`-1`, `0`, chữ `abc`; giá rỗng bị UI đổi thành 0). Backend chỉ kiểm tra `name`.
- **Bằng chứng:** [evidence/api_results.json](https://github.com/nhaajtdajt/eshop-hw02-domain-testing/blob/main/features/FR-16/evidence/api_results.json) (FR16-DT-19..22), [evidence/ui_results.json](https://github.com/nhaajtdajt/eshop-hw02-domain-testing/blob/main/features/FR-16/evidence/ui_results.json). Code: `backend/server.js:214-223`, `frontend-admin/src/App.jsx:392`.
