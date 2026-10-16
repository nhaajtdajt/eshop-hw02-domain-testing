Phần tử `null` trong `products` gây HTTP 500 lộ stack trace

- **Feature:** FR-16 — **Mức độ:** Minor
- **Test liên quan:** FR16-DT-39
- **Các bước tái hiện:** `POST /api/admin/import-products` (token Admin) với `{"products":[null]}`.
- **Expected:** 400 với thông báo lỗi rõ ràng; không để lộ chi tiết nội bộ (liên quan SEC).
- **Actual:** HTTP 500, trả trang HTML lỗi có stack trace, nêu `TypeError: Cannot read properties of null (reading 'name')` và đường dẫn tuyệt đối `...\backend\server.js:214:14`.
- **Bằng chứng:** [evidence/dt39_response.txt](https://github.com/nhaajtdajt/eshop-hw02-domain-testing/blob/main/features/FR-16/evidence/dt39_response.txt). Code: `backend/server.js:213-216` (không kiểm tra từng phần tử).
