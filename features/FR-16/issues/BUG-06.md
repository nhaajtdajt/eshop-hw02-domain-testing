API import nhận `name` toàn khoảng trắng

- **Feature:** FR-16 — **Mức độ:** Minor
- **Test liên quan:** FR16-DT-18
- **Các bước tái hiện:** `POST /api/admin/import-products` (token Admin) với `{"products":[{"name":"   ","price":100000,"category_id":1}]}`.
- **Expected (SRS FR-16, dòng 208):** `name` không được rỗng; tên chỉ gồm khoảng trắng không hợp lệ.
- **Actual:** HTTP 200, sản phẩm có tên `"   "` được thêm. (UI đã `trim()` trước khi gửi nên đã chặn; chỉ API bị lọt.)
- **Bằng chứng:** [evidence/api_results.json](https://github.com/nhaajtdajt/eshop-hw02-domain-testing/blob/main/features/FR-16/evidence/api_results.json) (FR16-DT-18). Code: `backend/server.js:214`.
