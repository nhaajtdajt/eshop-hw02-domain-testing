# FR-16: Import sản phẩm từ CSV — Phân tích

Phạm vi: Web Admin `http://localhost:5174` → tab **Sản phẩm** → khối "Import sản phẩm từ CSV" (chọn file, xem trước, nút Import) và API `POST /api/admin/import-products`. Việc đọc/parse file CSV được làm **ở client** (trình duyệt) rồi gửi lên API dưới dạng mảng JSON, nên có hai lớp cần test: **UI (file CSV thật)** và **API (mảng JSON)**.

## 1. Yêu cầu theo SRS (`README.md`)

> **FR-16** (dòng 200–211):
> - Admin có thể tải lên file CSV để import nhiều sản phẩm cùng lúc.
> - **Yêu cầu file CSV:** đuôi file phải là `.csv`; dòng đầu tiên là header `name,price,description,imageUrl,category_id`; hỗ trợ trường chứa dấu phẩy nếu được bọc trong dấu nháy kép (RFC 4180).
> - **Validation trước khi import:** `name` không được rỗng; `price` phải là số dương.
> - Nếu có lỗi ở bất kỳ dòng nào, toàn bộ import phải được **rollback** (giao dịch nguyên tử — all-or-nothing).
> - Hệ thống hiển thị báo cáo rõ ràng: bao nhiêu dòng thành công, bao nhiêu dòng lỗi và lý do.

Các yêu cầu liên quan ở mục khác:

> **FR-12** (dòng 176–179) và **SEC-03** (dòng 280): API Admin yêu cầu JWT hợp lệ **và** `role = 'admin'`.
> **FR-15** (dòng 191–198): ràng buộc sản phẩm — tên tối đa 255 ký tự, giá > 0, danh mục chọn từ danh sách có sẵn (thuộc feature khác; chỉ dùng làm tham chiếu cho `category_id`).
> **FR-21** (dòng 244–246): giao diện tiếng Việt; tiền dùng ký hiệu `₫`.

Điểm spec chưa định lượng/mơ hồ:
- "Báo cáo bao nhiêu dòng thành công, bao nhiêu dòng lỗi": khi rollback thì số dòng thành công = 0; vẫn phải có thông báo rõ rằng import **bị hủy** và liệt kê các dòng lỗi.
- "price phải là số dương": 0 và âm là không hợp lệ; số thập phân dương (ví dụ `0.5`) vẫn là số dương nên diễn giải là hợp lệ.
- Spec không quy định `category_id` phải tồn tại (FR-15 nói danh mục phải chọn từ danh sách) nên dùng làm test khám phá, không tính chắc chắn là bug.

## 2. Input / Điều kiện / Output

| Loại | Tên | Mô tả | Ràng buộc theo spec |
|---|---|---|---|
| Input | file | file tải lên | đuôi `.csv` |
| Input | header | dòng đầu | đúng `name,price,description,imageUrl,category_id` |
| Input | định dạng trường | dấu phẩy, nháy kép | RFC 4180 (trường có dấu phẩy được bọc `"..."`) |
| Input | `name` | tên SP của từng dòng | không rỗng |
| Input | `price` | giá của từng dòng | số dương |
| Input | `description`, `imageUrl`, `category_id` | các cột còn lại | spec không ràng buộc riêng |
| Input | số dòng dữ liệu | số bản ghi | ≥ 1 (file rỗng/chỉ header không có gì để import) |
| Input | vị trí dòng lỗi | đầu/giữa/cuối | một dòng lỗi → hủy toàn bộ |
| Precondition | tài khoản | Admin | token JWT, `role = admin` |
| Output | số sản phẩm trong DB | trước/sau | có lỗi → không thêm bản ghi nào |
| Output | báo cáo | thông báo trên UI | số dòng thành công/lỗi và lý do |

## 3. Spec vs Code (giả thuyết cần kiểm chứng)

Nguồn: `backend/server.js:198-241` (API), `frontend-admin/src/App.jsx:18-22,341-481` (UI).

| # | Spec nói | Code làm | File:dòng | Trạng thái |
|---|---|---|---|---|
| H1 | Có lỗi ở bất kỳ dòng nào thì rollback toàn bộ | Mỗi dòng `INSERT` riêng, không có transaction; dòng lỗi chỉ bị bỏ qua, các dòng khác vẫn được thêm | server.js:209-232 | Chưa kiểm chứng |
| H2 | `price` phải là số dương | Backend không kiểm tra giá; UI lấy `row.price \|\| … \|\| 0` rồi gửi nguyên. Âm, 0, chữ đều được chèn | server.js:218-223; App.jsx:392 | Chưa kiểm chứng |
| H3 | Hỗ trợ trường có dấu phẩy bọc trong nháy kép (RFC 4180) | Parse bằng `line.split(",")` nên cắt sai trường có dấu phẩy | App.jsx:367-377 | Chưa kiểm chứng |
| H4 | Chỉ nhận file `.csv` | `<input type="file">` không có `accept`; code không kiểm tra tên file/đuôi | App.jsx:356-358 | Chưa kiểm chứng |
| H5 | Header phải đúng `name,price,description,imageUrl,category_id` | Không kiểm tra header; thiếu/sai cột chỉ cho giá trị rỗng; còn chấp nhận alias `ten`, `gia`, `Name`… | App.jsx:370-401 | Chưa kiểm chứng |
| H6 | Báo cáo rõ ràng số dòng thành công/lỗi + lý do | `message` chỉ ghi "x/y sản phẩm được thêm"; `errors[]` liệt kê lý do; HTTP luôn 200 kể cả khi có lỗi | server.js:234-240 | Chưa kiểm chứng |
| H7 | API Admin kiểm tra `role = admin` (FR-12, SEC-03) | `authenticateToken` chỉ xác thực token, không kiểm tra role | server.js:199 | Chưa kiểm chứng |
| H8 | `name` không rỗng | Có kiểm tra `!row.name` (đúng); nhưng tên toàn khoảng trắng bị UI `trim()` thành rỗng nên cũng bị chặn; API nhận `" "` truyền thẳng → `" "` là truthy nên **được chèn** | server.js:214; App.jsx:371 | Cần thử (UI đúng, API có thể sai) |
| H9 | `category_id` thuộc danh sách danh mục (FR-15) | Thiếu/không hợp lệ → mặc định `1`; không kiểm tra tồn tại | server.js:223; App.jsx:400-402 | Cần thử |
| H10 | File rỗng/chỉ header không import được | UI: không có dòng dữ liệu nên nút Import bị vô hiệu; API: mảng rỗng → 400 | App.jsx:418; server.js:202-204 | Có vẻ đúng, cần thử |
| H11 | Lỗi số dòng chính xác | `index + 2` (tính cả header); dòng trống giữa file thành dòng lỗi "Thiếu tên" | server.js:215; App.jsx:367-377 | Cần thử |
| H12 | File mẫu đúng header | Link "Tải file mẫu" tạo CSV đúng header | App.jsx:347-353 | Có vẻ đúng |
| H13 | Chống XSS khi hiển thị dữ liệu (SEC-04) | Bảng xem trước render `{v}` bằng React (an toàn); danh sách sản phẩm sau import thuộc FR-15 | App.jsx:446-450 | Ngoài phạm vi, chỉ ghi chú |

## 4. Nhận xét ảnh hưởng thiết kế test

- Miền đầu vào chia thành 3 tầng: **file** (đuôi, rỗng, header), **định dạng** (dấu phẩy/nháy kép, xuống dòng, BOM) và **nội dung từng dòng** (`name`, `price`, `category_id`). Mỗi test lỗi chỉ chứa một lỗi để biết nguyên nhân.
- Tính nguyên tử cần test theo **vị trí dòng lỗi** (đầu/giữa/cuối) và **số dòng lỗi** (1, nhiều, tất cả); tiêu chí kiểm tra là **số sản phẩm trong DB trước và sau** import, không chỉ thông báo.
- Parse CSV nằm ở client nên test về nháy kép, header, BOM, CRLF phải chạy trên **UI** với file thật; còn validate `name`/`price` và quyền phải chạy trên **API** (mảng JSON) để bắt lỗi thiếu validate phía server.
- Biên: số dòng dữ liệu (0, 1, nhiều), số trường mỗi dòng (n−1, n, n+1), giá (−1, 0, 1, …), độ dài tên (0, 1), vị trí dòng lỗi.
- Mỗi test phải dọn dữ liệu (xóa sản phẩm vừa chèn) để các test không ảnh hưởng nhau.
