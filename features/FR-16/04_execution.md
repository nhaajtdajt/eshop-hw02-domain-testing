# FR-16: Thực thi test — kết quả

- **Ngày chạy:** 2026-10-16. **Môi trường:** Windows 11, Node v22.20.0, Backend `localhost:3000`, Web Admin `localhost:5174` (trình duyệt tích hợp Claude desktop), dữ liệu seed gốc (5 sản phẩm ban đầu).
- **Cách chạy:**
  - **API (39 kiểm tra):** `evidence/run_api_tests.js` — `POST /api/admin/import-products` với mảng JSON; đếm số sản phẩm trong DB trước/sau, xóa bản ghi do test tạo. Kết quả thô: `evidence/api_results.json`, phản hồi lỗi 500: `evidence/dt39_response.txt`.
  - **UI (≈ 45 file CSV thật):** gán file vào `<input type="file">` của Web Admin (tab Sản phẩm), đọc bảng xem trước, bấm nút Import thật, đọc thông báo, đếm sản phẩm trong DB rồi xóa. Kết quả: `evidence/ui_results.json`; ảnh: `evidence/ui_partial_import_green_banner.jpg`, `evidence/ui_quoted_comma_preview.jpg`.
- **Quy ước:** "từ chối/không import" = **số sản phẩm trong DB không đổi**; "chấp nhận N" = DB tăng đúng N. Kết quả tổng là **Fail** nếu bất kỳ lớp đã chạy (UI hoặc API) lệch spec.
- **Chạy lại có chủ ý:** (1) lần chạy đầu của DT-02 trên UI bị loại vì bảng xem trước chưa kịp cập nhật nên import nhầm dữ liệu của test trước; chạy lại có chờ bảng xem trước khớp nội dung rồi mới bấm. (2) BV-18 lần đầu bị lỗi 413 (payload 131 KB) nên chưa kiểm được rollback 1000 dòng; chạy lại với dòng gọn (~80 KB).

## 1. Kết quả theo test case

### Domain Testing
| TC ID | Lớp chạy | Kết quả | Actual tóm tắt | Bug |
|---|---|---|---|---|
| FR16-DT-01 | UI | Pass | 3 dòng hợp lệ → "Import hoàn tất: 3/3", DB +3 | |
| FR16-DT-02 | UI | **Fail** | Tên có dấu phẩy trong nháy kép bị cắt: lưu `name="FR16-Áo`, `price=size M"`, `description=100000` (ảnh `ui_quoted_comma_preview.jpg`) | BUG-03 |
| FR16-DT-03 | UI | **Fail** | `""` không được bỏ escape: tên lưu `"FR16-Màn hình 27"" IPS"` (còn nguyên nháy kép) | BUG-03 |
| FR16-DT-04 | UI | Pass | CRLF xử lý đúng, tên/giá không chứa `\r` | |
| FR16-DT-05 | UI | Pass | Tên tiếng Việt lưu đúng | |
| FR16-DT-06 | UI+API | Pass | Giá `0.5` được chấp nhận | |
| FR16-DT-07 | UI | **Fail** | File `.txt` vẫn import được (DB +2); ô chọn file không có `accept` | BUG-04 |
| FR16-DT-08 | UI | **Fail** | File `.xlsx` (nội dung CSV) vẫn import được (DB +2) | BUG-04 |
| FR16-DT-09 | UI | Pass | File rỗng → nút Import bị vô hiệu, DB không đổi | |
| FR16-DT-10 | UI | Pass | Chỉ header → nút vô hiệu | |
| FR16-DT-11 | UI | Pass | Chỉ khoảng trắng → nút vô hiệu | |
| FR16-DT-12 | UI | **Fail** | Header sai thứ tự vẫn import (DB +1), không kiểm tra header | BUG-05 |
| FR16-DT-13 | UI | **Fail** | Thiếu cột `price` vẫn import (DB +1) | BUG-05 |
| FR16-DT-14 | UI | **Fail** | Thừa cột `sku` vẫn import (DB +1) | BUG-05 |
| FR16-DT-15 | UI | **Fail** | Header `Name,Price,...` (sai hoa/thường) vẫn import (DB +1) | BUG-05 |
| FR16-DT-16 | UI | Pass | Không có header: dòng đầu bị coi là header, DB không đổi; nhưng hiện banner "✅ Import hoàn tất: 0/1" (xem BUG-08) | |
| FR16-DT-17 | UI+API | Pass | Tên rỗng bị từ chối ("Hàng 2: Thiếu tên sản phẩm"), DB không đổi | |
| FR16-DT-18 | UI+API | **Fail** | UI từ chối (đã `trim`), nhưng API nhận `name="   "` và **thêm** sản phẩm | BUG-06 |
| FR16-DT-19 | UI+API | **Fail** | Giá `-1` được thêm | BUG-02 |
| FR16-DT-20 | UI+API | **Fail** | Giá `0` được thêm | BUG-02 |
| FR16-DT-21 | UI+API | **Fail** | Giá `abc` được thêm | BUG-02 |
| FR16-DT-22 | UI+API | **Fail** | Giá rỗng được thêm (UI chuyển thành 0) | BUG-02 |
| FR16-DT-23 | UI+API | **Fail** | `category_id = 999` (không tồn tại) được thêm (diễn giải FR-15) | BUG-07 |
| FR16-DT-24 | UI+API | **Fail** | `category_id` rỗng được thêm, tự gán 1 (diễn giải FR-15) | BUG-07 |
| FR16-DT-25 | UI+API | **Fail** | 3 dòng, dòng 1 lỗi: DB +3 (không rollback) | BUG-01 (và BUG-02) |
| FR16-DT-26 | UI+API | **Fail** | Dòng 2 lỗi: DB +3 | BUG-01 (và BUG-02) |
| FR16-DT-27 | UI+API | **Fail** | Dòng 3 lỗi: DB +3 | BUG-01 (và BUG-02) |
| FR16-DT-28 | UI+API | **Fail** | 2/5 dòng lỗi: DB +5 | BUG-01 (và BUG-02) |
| FR16-DT-29 | UI+API | **Fail** | Cả 3 dòng lỗi: DB +3 | BUG-01 (và BUG-02) |
| FR16-DT-30 | UI+API | Pass | 5 dòng hợp lệ → DB +5 | |
| FR16-DT-31 | UI | Pass | Báo cáo thành công nêu "3/3 sản phẩm được thêm" | |
| FR16-DT-32 | UI | **Fail** | 3 dòng, dòng 2 thiếu tên: **2/3 được thêm** (dòng 1, 3 vẫn vào DB), banner xanh "✅ Import hoàn tất" + "Hàng 3: Thiếu tên sản phẩm"; không nêu số dòng lỗi và không nói import bị hủy (ảnh `ui_partial_import_green_banner.jpg`) | BUG-01, BUG-08 |
| FR16-DT-33 | API | **Fail** | Có dòng lỗi vẫn trả HTTP 200 "Import hoàn tất", DB +3 | BUG-01, BUG-08 |
| FR16-DT-34 | API | Pass | Không token → 401 | |
| FR16-DT-35 | API | **Fail** | **Token User thường** import được sản phẩm (HTTP 200, DB +1) | BUG-09 |
| FR16-DT-36 | API | Pass | Thiếu `products` → 400 "Không có dữ liệu để import" | |
| FR16-DT-37 | API | Pass | `products: []` → 400 | |
| FR16-DT-38 | API | Pass | `products: "abc"` → 400 | |
| FR16-DT-39 | API | **Fail** | `products: [null]` → HTTP **500**, trả trang HTML lỗi chứa stack trace và đường dẫn tuyệt đối tới `server.js:214`; server vẫn sống | BUG-10 |
| FR16-DT-40 | UI | Pass | Nút "Import 0 sản phẩm" bị vô hiệu khi chưa chọn file | |
| FR16-DT-41 | UI | Pass | Xem trước hiển thị đúng số dòng và 5 tên cột | |
| FR16-DT-42 | UI | Pass | File mẫu có header đúng, import được (DB +1) | |
| FR16-DT-43 | UI | **Fail** | Nháy kép không đóng: vẫn import, tên lưu `"FR16-Áo` (cắt tại dấu phẩy) | BUG-03 |

### BVA
| TC ID | Lớp chạy | Kết quả | Actual tóm tắt | Bug |
|---|---|---|---|---|
| FR16-BV-01 | UI+API | Pass | 1 dòng → DB +1 | |
| FR16-BV-02 | UI+API | Pass | 2 dòng → DB +2 | |
| FR16-BV-03 | UI+API | Pass | 100 dòng → DB +100 | |
| FR16-BV-04 | API | **Fail** | 1000 dòng (payload ~131 KB) → HTTP **413** (trang HTML), DB +0: vượt giới hạn body 100 KB mặc định; UI sẽ chỉ hiện "Request failed with status code 413" (suy ra từ `App.jsx:412-414`) | BUG-11 |
| FR16-BV-05 | UI | **Fail** | Dòng 4 trường vẫn import (DB +1, `category_id` tự gán 1) | BUG-05 |
| FR16-BV-06 | UI | **Fail** | Dòng 6 trường vẫn import, trường thừa bị bỏ qua (DB +1) | BUG-05 |
| FR16-BV-07 | UI+API | Pass | Giá `1` chấp nhận | |
| FR16-BV-08 | UI+API | Pass | Giá `0.01` chấp nhận | |
| FR16-BV-09 | API | Pass | Giá `2147483647` lưu đúng | |
| FR16-BV-10 | API | Pass | Giá `2147483648` lưu đúng | |
| FR16-BV-11 | API | Pass | Giá `2⁶³`: không lỗi, lưu dạng số thực (ghi nhận) | |
| FR16-BV-12 | UI+API | Pass | Tên 1 ký tự chấp nhận | |
| FR16-BV-13 | UI+API | Pass | Tên 255 ký tự chấp nhận | |
| FR16-BV-14 | UI+API | **Fail** | Tên 256 ký tự được chấp nhận (diễn giải FR-15) | BUG-07 |
| FR16-BV-15 | UI+API | **Fail** | 1 dòng lỗi (giá −1): DB +1 | BUG-01, BUG-02 |
| FR16-BV-16 | UI+API | **Fail** | 2 dòng, dòng 2 lỗi: DB +2 | BUG-01, BUG-02 |
| FR16-BV-17 | UI+API | **Fail** | 100 dòng, dòng 100 lỗi: DB +100 | BUG-01, BUG-02 |
| FR16-BV-18 | API | **Fail** | 1000 dòng gọn, dòng 1000 lỗi: DB +1000 (không rollback) | BUG-01, BUG-02 |
| FR16-BV-19 | UI+API | **Fail** | Số dòng báo cáo **đúng** ("Hàng 2: Thiếu tên sản phẩm") nhưng 2/3 dòng vẫn được thêm | BUG-01 |

## 2. Quan sát thêm (không tính riêng thành bug)
- Số dòng lỗi trong báo cáo dùng `index + 2` (tính cả header) → đúng với số dòng trong file.
- Bảng xem trước hiển thị dữ liệu bằng React (không dùng `innerHTML`), không lộ XSS ở màn import (kiểm tra bằng đọc code, chưa chạy payload XSS).
- Sản phẩm có tên/giá hỏng do BUG-03 sẽ hiện trong danh sách sản phẩm; thuộc phạm vi FR-15 nếu xem xét hiển thị.
- Import cùng một file hai lần tạo bản ghi trùng (spec không nêu), không test thêm.

## 3. Thống kê FR-16

| Hạng mục | Số lượng |
|---|---|
| Test case thiết kế | **62** (43 Domain Testing + 19 BVA) |
| Đã thực thi | 62 |
| Pass | 28 (DT: 18, BV: 10) |
| Fail | 34 (DT: 25, BV: 9) |
| Chưa thực thi | 0 |
| Bug phân biệt (nguyên nhân gốc) | **11** (BUG-01 … BUG-11, xem `06_bugs.md`) |

Nhiều test cùng Fail do một nguyên nhân gốc (ví dụ các test rollback đều do BUG-01), nên số bug nhỏ hơn số test Fail.
