Import ~1000 dòng bị từ chối HTTP 413 do giới hạn body 100 KB, không có thông báo rõ ràng

- **Feature:** FR-16 — **Mức độ:** Minor
- **Test liên quan:** FR16-BV-04
- **Các bước tái hiện:** `POST /api/admin/import-products` (token Admin) với 1000 sản phẩm (mỗi sản phẩm có mô tả ngắn, tổng ~131 KB). Với file CSV tương đương trên Web Admin, request gửi đi là cùng payload.
- **Expected (SRS FR-16, dòng 202):** Admin có thể import nhiều sản phẩm cùng lúc; nếu có giới hạn thì phải báo rõ ràng.
- **Actual:** HTTP **413** với trang HTML mặc định; DB không đổi. Giao diện chỉ hiển thị thông báo kỹ thuật của axios ("Request failed with status code 413", suy ra từ `App.jsx:412-414`, chưa quan sát trực tiếp trên UI). Giới hạn 100 KB là mặc định của `body-parser`, server không cấu hình lại.
- **Bằng chứng:** [evidence/api_results.json](https://github.com/nhaajtdajt/eshop-hw02-domain-testing/blob/main/features/FR-16/evidence/api_results.json) (FR16-BV-04). Code: `backend/server.js:12` (`bodyParser.json()` không đặt `limit`).
