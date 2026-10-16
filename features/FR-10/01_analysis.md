# FR-10: Máy trạng thái đơn hàng (Order State Machine) — Phân tích

Phạm vi: API `PUT /api/admin/orders/:id/status` (Admin), `PUT /api/orders/:id/cancel` (User), cùng giao diện **Web Admin** (`:5174`, tab Đơn hàng) và **Web user** (`/profile`, danh sách đơn). Màn hình hủy đơn trên **Mobile** thuộc feature Mobile FR-10 của thành viên khác nên **không** nằm trong phạm vi; backend dùng chung nên phần API đã bao phủ.

## 1. Yêu cầu theo SRS (`README.md`)

> **FR-10** (dòng 141–162): Đơn hàng có **5 trạng thái** và phải tuân theo sơ đồ:
> - `pending` → `confirmed` [Admin xác nhận]; `confirmed` → `shipping` [Admin giao hàng]; `shipping` → `delivered` [Admin hoàn tất].
> - `pending` → `canceled` và `confirmed` → `canceled` [User/Admin hủy].
>
> **Ràng buộc trạng thái kết thúc:** `delivered` và `canceled` là trạng thái kết thúc — không được chuyển sang bất kỳ trạng thái nào khác. Khi đơn ở `shipping`, **User không được phép tự hủy** — chỉ Admin mới có thể thao tác. Mọi chuyển đổi không hợp lệ phải trả về lỗi với thông báo phù hợp.

Các yêu cầu liên quan ở mục khác:

> **FR-12** (dòng 176–179): mọi API `/api/admin/*` yêu cầu JWT hợp lệ **và** `role = 'admin'`. **SEC-03** (dòng 280): API Admin phải kiểm tra `role = 'admin'` trong token, không chỉ kiểm tra có token.
> **FR-18** (dòng 220–222): Admin chuyển trạng thái đơn theo đúng State Machine FR-10.
> **FR-21** (dòng 244): toàn bộ giao diện dùng tiếng Việt.
> **FR-20** (dòng 236): hủy đơn trên Mobile tuân theo FR-10 (thuộc feature khác).

Điểm mơ hồ của spec:
- "chỉ Admin mới có thể thao tác" khi đơn ở `shipping` — sơ đồ chỉ có mũi tên `shipping → delivered`, **không** có `shipping → canceled`. Diễn giải dùng ở đây: Admin chỉ được `shipping → delivered`, không được hủy. Nếu kết quả thực tế cho phép Admin hủy đơn đang giao, sẽ ghi là "theo diễn giải chặt".
- Spec không định nghĩa chuyển ngược (ví dụ `confirmed → pending`) nhưng sơ đồ không có mũi tên ngược → không hợp lệ.

## 2. Input / Điều kiện / Output

| Loại | Tên | Mô tả | Ràng buộc theo spec |
|---|---|---|---|
| Input | trạng thái hiện tại | `pending`, `confirmed`, `shipping`, `delivered`, `canceled` | 5 giá trị |
| Input | trạng thái đích (`status`) | body của `PUT /api/admin/orders/:id/status` | chỉ chuyển hợp lệ theo sơ đồ |
| Input | `id` đơn hàng | tham số đường dẫn | đơn phải tồn tại |
| Input | vai trò người gọi | không token / User thường / Admin | API Admin chỉ cho `admin`; hủy chỉ cho chủ đơn |
| Input | hành động User | nút "Hủy đơn" trên trang Profile (web) | chỉ khi `pending` hoặc `confirmed` |
| Precondition | đơn hàng được tạo bằng `POST /api/checkout` | trạng thái đầu `pending` | |
| Output | HTTP + JSON, trạng thái đơn trong DB, giao diện (nút hiển thị, thông báo lỗi) | | chuyển không hợp lệ → lỗi + trạng thái không đổi |

Nguồn dữ liệu khởi tạo: `POST /api/checkout` (token user) tạo đơn `pending`; đưa đơn về các trạng thái khác bằng chuỗi chuyển hợp lệ qua API Admin (token `admin@eshop.com` / `Admin123!`).

## 3. Spec vs Code (giả thuyết cần kiểm chứng)

Nguồn: `backend/server.js:100-110` (xác thực), `:311-342` (my-orders, hủy), `:525-568` (đổi trạng thái admin); `frontend-admin/src/App.jsx:85-92,805-870`; `frontend-web/src/pages/Profile.jsx:66-80,199-206`.

| # | Spec nói | Code làm | File:dòng | Trạng thái |
|---|---|---|---|---|
| H1 | `canceled` là trạng thái cuối, không chuyển tiếp | Cho phép `canceled → delivered` | server.js:550-551 | Chưa kiểm chứng |
| H2 | UI không nên cho thao tác sai | Admin UI hiện nút "Đánh dấu Đã giao" ở đơn `canceled` | App.jsx:862-869 | Chưa kiểm chứng |
| H3 | User không được hủy khi `shipping` | Backend chỉ chặn `delivered` và `canceled` → User hủy được đơn `shipping` | server.js:329 (kèm comment "Lẽ ra phải là…") | Chưa kiểm chứng |
| H4 | Nút hủy chỉ khi `pending`/`confirmed` | Web Profile hiện nút "Hủy đơn" cho mọi trạng thái trừ `delivered`/`canceled` (gồm `shipping`) | Profile.jsx:199-206 | Chưa kiểm chứng |
| H5 | API Admin kiểm tra `role = 'admin'` (FR-12, SEC-03) | `authenticateToken` chỉ kiểm tra token hợp lệ, không kiểm tra role → User thường đổi được trạng thái mọi đơn | server.js:525 + :100-110 | Chưa kiểm chứng |
| H6 | Chủ đơn mới được hủy | Truy vấn `WHERE id=? AND user_id=?` → hủy đơn người khác trả 404 | server.js:321-327 | Có vẻ đúng, cần thử |
| H7 | Chuyển không hợp lệ trả lỗi "phù hợp" | Trả 400 `Invalid state transition from X to Y` (tiếng Anh) | server.js:553-557 | Chưa kiểm chứng; liên quan FR-21 |
| H8 | `delivered` là trạng thái cuối | Không có nhánh cho phép rời `delivered` → đúng | server.js:537-551 | Có vẻ đúng |
| H9 | Admin không hủy được đơn `shipping` (sơ đồ) | Không có nhánh `shipping → canceled` → bị từ chối (đúng với diễn giải chặt) | server.js:547 | Có vẻ đúng |
| H10 | Giá trị `status` không hợp lệ bị từ chối | `status` không khớp nhánh nào → `isValidTransition=false` → 400 | server.js:553 | Có vẻ đúng, cần thử |
| H11 | Chuyển cùng trạng thái (`pending→pending`) không hợp lệ | Không có nhánh → 400 | server.js:537-551 | Có vẻ đúng |
| H12 | Thao tác trên đơn không tồn tại báo lỗi | `SELECT` rỗng → 404 | server.js:532 | Có vẻ đúng |
| H13 | Thông báo lỗi UI bằng tiếng Việt (FR-21) | Admin UI hiện `"Lỗi: " + err.response.data.error` → lộ chuỗi tiếng Anh | App.jsx:90-91 | Chưa kiểm chứng |
| H14 | `GET /api/orders/:id` chỉ cho chủ đơn xem (FR-11) | Không có xác thực, ai cũng xem được | server.js:344-349 | Ngoài phạm vi FR-10 (thuộc FR-11) |
| H15 | Hiển thị an toàn (FR-18) | `dangerouslySetInnerHTML` cho địa chỉ giao hàng | App.jsx:799-804 | Ngoài phạm vi FR-10 (thuộc FR-18) |

H14, H15 chỉ ghi chú vì thuộc feature của thành viên khác, không đưa vào bug của FR-10.

## 4. Nhận xét ảnh hưởng thiết kế test

- Miền đầu vào chính là **cặp (trạng thái hiện tại × trạng thái đích)**: 5 × 5 = 25 ô; hợp lệ chỉ 5 ô. Mỗi ô là một lớp tương đương nên sẽ test đủ cả 25.
- "Biên" của state machine không phải số: gồm (a) ranh giới giữa trạng thái cho phép và không cho phép hủy trong chuỗi `pending < confirmed < shipping < delivered`, (b) ID đơn hàng (0, 1, lớn nhất, lớn nhất+1, không phải số), (c) chuỗi `status` sát giá trị hợp lệ (thiếu/thừa 1 ký tự, khoảng trắng), (d) số lần lặp một thao tác (hủy lần 1 và lần 2).
- Có hai lớp thực thi cho mỗi ràng buộc: **API** (backend) và **UI** (Web Admin, Web user). Backend phải chặn dù UI đã ẩn nút.
- Chuẩn bị dữ liệu: mỗi test tạo đơn mới bằng checkout rồi đưa tới trạng thái cần thiết bằng các chuyển hợp lệ, để các test độc lập nhau.
