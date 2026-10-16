API import không kiểm tra quyền Admin

- **Feature:** FR-16 (liên quan FR-12) — **Mức độ:** Critical
- **Test liên quan:** FR16-DT-35
- **Các bước tái hiện:**
  1. Đăng nhập `test@eshop.com` (User thường) lấy token.
  2. `POST /api/admin/import-products` với header `Authorization: Bearer <token user>` và `{"products":[{"name":"FR16-1","price":100000,"category_id":1}]}`.
- **Expected (SRS FR-12, dòng 176–179; SEC-03, dòng 280):** Từ chối (403) vì token không có `role = admin`.
- **Actual:** HTTP 200, sản phẩm được thêm. `authenticateToken` chỉ kiểm tra token hợp lệ.
- **Bằng chứng:** [evidence/api_results.json](https://github.com/nhaajtdajt/eshop-hw02-domain-testing/blob/main/features/FR-16/evidence/api_results.json) (FR16-DT-35). Code: `backend/server.js:199`.
