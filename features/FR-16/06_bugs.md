# FR-16: Bug report

Môi trường chung: Windows 11, Node v22.20.0, Backend `http://localhost:3000`, Web Admin `http://localhost:5174` (Chromium trong Claude desktop), dữ liệu seed gốc. Ngày phát hiện: 2026-10-16. Spec = `README.md` (SRS). Mức độ: Critical > Major > Minor.
Tài khoản: Admin `admin@eshop.com` / `Admin123!`, User `test@eshop.com` / `Test1234!` (từ `database.js`).
File CSV mẫu dùng trong các bước tái hiện có header `name,price,description,imageUrl,category_id`.

Trạng thái GitHub Issues: **đã đăng** #18–#28 (tiêu đề có tiền tố `[FR-16]`, nhãn `bug`) tại https://github.com/nhaajtdajt/eshop-hw02-domain-testing/issues. Nội dung từng issue nằm trong `features/FR-16/issues/`.

| Bug | Tiêu đề | Mức độ | Test liên quan | Issue |
|---|---|---|---|---|
| BUG-01 | Import không rollback: dòng hợp lệ vẫn được thêm khi file có dòng lỗi | Major | DT-25..29, DT-32, DT-33, BV-15..19 | #18 |
| BUG-02 | Không validate `price`: số âm, 0, chữ và rỗng đều được import | Major | DT-19..22 | #19 |
| BUG-03 | Parse CSV bằng `split(",")` làm hỏng trường có nháy kép/dấu phẩy | Major | DT-02, DT-03, DT-43 | #20 |
| BUG-04 | Chấp nhận file không phải `.csv` | Minor | DT-07, DT-08 | #21 |
| BUG-05 | Không kiểm tra header và số trường của dòng | Major | DT-12..15, BV-05, BV-06 | #22 |
| BUG-06 | API import nhận `name` toàn khoảng trắng | Minor | DT-18 | #23 |
| BUG-07 | Import bỏ qua ràng buộc danh mục và độ dài tên (FR-15) | Minor | DT-23, DT-24, BV-14 | #24 |
| BUG-08 | Báo cáo import gây hiểu nhầm: banner xanh "Import hoàn tất" dù có lỗi, API luôn trả HTTP 200 | Minor | DT-32, DT-33 (liên quan DT-16, 17) | #25 |
| BUG-09 | API import không kiểm tra quyền Admin | Critical | DT-35 | #26 |
| BUG-10 | Phần tử `null` trong `products` gây HTTP 500 lộ stack trace | Minor | DT-39 | #27 |
| BUG-11 | Import ~1000 dòng bị từ chối HTTP 413 do giới hạn body 100 KB, không có thông báo rõ ràng | Minor | BV-04 | #28 |

---

### BUG-01: Import không rollback: dòng hợp lệ vẫn được thêm khi file có dòng lỗi
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
- **Bằng chứng:** `evidence/ui_partial_import_green_banner.jpg`, `evidence/api_results.json`, `evidence/ui_results.json`. Code: `backend/server.js:206-232`.

### BUG-02: Không validate `price`: số âm, 0, chữ và rỗng đều được import
- **Feature:** FR-16 — **Mức độ:** Major
- **Test liên quan:** FR16-DT-19..DT-22
- **Các bước tái hiện:**
  1. File CSV một dòng dữ liệu có `price` lần lượt là `-1`, `0`, `abc` và để trống, ví dụ `FR16-1,-1,Mo ta,https://placehold.co/300,1`.
  2. Import trên Web Admin (hoặc `POST /api/admin/import-products` với `{"products":[{"name":"FR16-1","price":-1,"category_id":1}]}`).
  3. Kiểm tra danh sách sản phẩm.
- **Expected (SRS FR-16, dòng 208–209):** `price` phải là số dương; dòng sai bị từ chối (và theo rollback thì cả file không được import).
- **Actual:** Cả 4 trường hợp đều được thêm vào DB (`-1`, `0`, chữ `abc`; giá rỗng bị UI đổi thành 0). Backend chỉ kiểm tra `name`.
- **Bằng chứng:** `evidence/api_results.json` (FR16-DT-19..22), `evidence/ui_results.json`. Code: `backend/server.js:214-223`, `frontend-admin/src/App.jsx:392`.

### BUG-03: Parse CSV bằng `split(",")` làm hỏng trường có nháy kép/dấu phẩy
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
- **Bằng chứng:** `evidence/ui_quoted_comma_preview.jpg`, `evidence/ui_results.json`. Code: `frontend-admin/src/App.jsx:367-377` (`line.split(",")`).

### BUG-04: Chấp nhận file không phải `.csv`
- **Feature:** FR-16 — **Mức độ:** Minor
- **Test liên quan:** FR16-DT-07, DT-08
- **Các bước tái hiện:** Đổi tên file CSV hợp lệ thành `products.txt` (hoặc `products.xlsx`) rồi chọn trong ô "Import sản phẩm từ CSV" và bấm Import.
- **Expected (SRS FR-16, dòng 204):** Đuôi file phải là `.csv`; file khác bị từ chối.
- **Actual:** File `.txt` và `.xlsx` vẫn được đọc và import (DB tăng). `<input type="file">` không có thuộc tính `accept` và code không kiểm tra tên file.
- **Bằng chứng:** `evidence/ui_results.json` (`file_input_accept_attribute: null`). Code: `frontend-admin/src/App.jsx:356-358`.

### BUG-05: Không kiểm tra header và số trường của dòng
- **Feature:** FR-16 — **Mức độ:** Major
- **Test liên quan:** FR16-DT-12..DT-15, BV-05, BV-06
- **Các bước tái hiện:**
  1. Import file có header sai thứ tự `price,name,description,imageUrl,category_id`, hoặc thiếu cột `price`, thừa cột `sku`, hoặc viết hoa `Name,Price,...`.
  2. Import file có một dòng chỉ 4 trường, hoặc 6 trường.
- **Expected (SRS FR-16, dòng 205):** Dòng đầu phải là đúng `name,price,description,imageUrl,category_id`; file không đúng bị từ chối.
- **Actual:** Tất cả đều import thành công (DB tăng): header không được kiểm tra, cột thiếu cho giá trị rỗng/mặc định (`category_id` tự gán 1), cột thừa bị bỏ qua. Code còn chấp nhận các tên cột khác (`ten`, `gia`, `Name`, `Price`…).
- **Bằng chứng:** `evidence/ui_results.json` (DT-12..15, BV-05, BV-06). Code: `frontend-admin/src/App.jsx:368-402`.

### BUG-06: API import nhận `name` toàn khoảng trắng
- **Feature:** FR-16 — **Mức độ:** Minor
- **Test liên quan:** FR16-DT-18
- **Các bước tái hiện:** `POST /api/admin/import-products` (token Admin) với `{"products":[{"name":"   ","price":100000,"category_id":1}]}`.
- **Expected (SRS FR-16, dòng 208):** `name` không được rỗng; tên chỉ gồm khoảng trắng không hợp lệ.
- **Actual:** HTTP 200, sản phẩm có tên `"   "` được thêm. (UI đã `trim()` trước khi gửi nên đã chặn; chỉ API bị lọt.)
- **Bằng chứng:** `evidence/api_results.json` (FR16-DT-18). Code: `backend/server.js:214`.

### BUG-07: Import bỏ qua ràng buộc danh mục và độ dài tên (FR-15)
- **Feature:** FR-16 (liên quan FR-15) — **Mức độ:** Minor (theo diễn giải: FR-16 không nêu rõ)
- **Test liên quan:** FR16-DT-23, DT-24, BV-14
- **Các bước tái hiện:** Import dòng có `category_id = 999` (không tồn tại), hoặc để trống `category_id`, hoặc `name` dài 256 ký tự.
- **Expected (SRS FR-15, dòng 195–197):** Tên tối đa 255 ký tự; danh mục phải chọn từ danh sách có sẵn.
- **Actual:** Cả ba đều được thêm: danh mục không tồn tại vẫn lưu `999`, danh mục rỗng được tự gán `1`, tên 256 ký tự được chấp nhận.
- **Bằng chứng:** `evidence/api_results.json` (FR16-DT-23, DT-24, BV-14). Code: `backend/server.js:223` (`row.category_id || 1`).

### BUG-08: Báo cáo import gây hiểu nhầm: banner xanh "Import hoàn tất" dù có lỗi, API luôn trả HTTP 200
- **Feature:** FR-16 — **Mức độ:** Minor
- **Test liên quan:** FR16-DT-32, DT-33 (và các test DT-16, DT-17, X-03 có cùng banner)
- **Các bước tái hiện:** Import file có một dòng thiếu tên (xem BUG-01) hoặc file phân cách bằng `;`; quan sát vùng thông báo dưới ô chọn file.
- **Expected (SRS FR-16, dòng 211):** Báo cáo rõ ràng: bao nhiêu dòng thành công, bao nhiêu dòng lỗi và lý do; khi có lỗi, import bị hủy toàn bộ và báo rõ như vậy.
- **Actual:** Banner xanh "✅ Import hoàn tất: 2/3 sản phẩm được thêm" kèm danh sách lỗi; không nêu **số** dòng lỗi và không báo import bị hủy. Với file chỉ có lỗi vẫn hiện "✅ Import hoàn tất: 0/1". API luôn trả HTTP 200.
- **Bằng chứng:** `evidence/ui_partial_import_green_banner.jpg`, `evidence/api_results.json`, `evidence/ui_exploratory.json`. Code: `backend/server.js:234-240`, `frontend-admin/src/App.jsx:459-480`.

### BUG-09: API import không kiểm tra quyền Admin
- **Feature:** FR-16 (liên quan FR-12) — **Mức độ:** Critical
- **Test liên quan:** FR16-DT-35
- **Các bước tái hiện:**
  1. Đăng nhập `test@eshop.com` (User thường) lấy token.
  2. `POST /api/admin/import-products` với header `Authorization: Bearer <token user>` và `{"products":[{"name":"FR16-1","price":100000,"category_id":1}]}`.
- **Expected (SRS FR-12, dòng 176–179; SEC-03, dòng 280):** Từ chối (403) vì token không có `role = admin`.
- **Actual:** HTTP 200, sản phẩm được thêm. `authenticateToken` chỉ kiểm tra token hợp lệ.
- **Bằng chứng:** `evidence/api_results.json` (FR16-DT-35). Code: `backend/server.js:199`.

### BUG-10: Phần tử `null` trong `products` gây HTTP 500 lộ stack trace
- **Feature:** FR-16 — **Mức độ:** Minor
- **Test liên quan:** FR16-DT-39
- **Các bước tái hiện:** `POST /api/admin/import-products` (token Admin) với `{"products":[null]}`.
- **Expected:** 400 với thông báo lỗi rõ ràng; không để lộ chi tiết nội bộ (liên quan SEC).
- **Actual:** HTTP 500, trả trang HTML lỗi có stack trace, nêu `TypeError: Cannot read properties of null (reading 'name')` và đường dẫn tuyệt đối `...\backend\server.js:214:14`.
- **Bằng chứng:** `evidence/dt39_response.txt`. Code: `backend/server.js:213-216` (không kiểm tra từng phần tử).

### BUG-11: Import ~1000 dòng bị từ chối HTTP 413 do giới hạn body 100 KB, không có thông báo rõ ràng
- **Feature:** FR-16 — **Mức độ:** Minor
- **Test liên quan:** FR16-BV-04
- **Các bước tái hiện:** `POST /api/admin/import-products` (token Admin) với 1000 sản phẩm (mỗi sản phẩm có mô tả ngắn, tổng ~131 KB). Với file CSV tương đương trên Web Admin, request gửi đi là cùng payload.
- **Expected (SRS FR-16, dòng 202):** Admin có thể import nhiều sản phẩm cùng lúc; nếu có giới hạn thì phải báo rõ ràng.
- **Actual:** HTTP **413** với trang HTML mặc định; DB không đổi. Giao diện chỉ hiển thị thông báo kỹ thuật của axios ("Request failed with status code 413", suy ra từ `App.jsx:412-414`, chưa quan sát trực tiếp trên UI). Giới hạn 100 KB là mặc định của `body-parser`, server không cấu hình lại.
- **Bằng chứng:** `evidence/api_results.json` (FR16-BV-04). Code: `backend/server.js:12` (`bodyParser.json()` không đặt `limit`).

---

## Quan sát (không tính là bug của FR-16)
- File CSV phân cách bằng `;` (kiểu Excel tiếng Việt) không được nhận diện (X-03); dòng trống giữa file bị tính là dòng lỗi (X-02); BOM và khoảng trắng hai đầu được xử lý đúng (X-01, X-04).
- Chưa test: import trùng lặp (cùng file hai lần, trùng tên trong file) và giá có dấu phân cách hàng nghìn (`100.000`/`"100,000"`).
