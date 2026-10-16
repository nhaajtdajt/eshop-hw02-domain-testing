# FR-10: Thực thi test — kết quả

- **Ngày chạy:** 2026-10-16. **Môi trường:** Windows 11, Node v22.20.0, Backend `localhost:3000`, Web `localhost:5173`, Admin `localhost:5174` (trình duyệt tích hợp Claude desktop), dữ liệu seed gốc của repo.
- **Cách chạy:**
  - **API (60 kiểm tra: DT-01..43 và BV-01..17):** `evidence/run_api_tests.js` — gọi HTTP thật; DB chỉ dùng để xác minh trạng thái đơn đã lưu và xóa bảng `orders` trước nhóm BV ID (để ID là 1..3). Kết quả thô: `evidence/api_results.json`.
  - **UI (DT-44..54):** dùng `evidence/seed_ui_orders.js` tạo 5 đơn ở 5 trạng thái cho `test@eshop.com`; nạp token vào `localStorage` rồi thao tác trên trang thật (Web Admin tab Đơn hàng; Web `/profile`). `window.alert` được ghi lại để lấy nội dung. Kết quả thô: `evidence/ui_results.json`; ảnh: `admin_orders_ui_states.jpg`, `web_profile_orders_before.jpg`, `web_profile_cancel_shipping_after.jpg`.
- **Quy ước kết quả:** "từ chối" = HTTP ≥ 400 **và** trạng thái trong DB không đổi; "chấp nhận" = HTTP 200 **và** trạng thái đúng như đích.
- Lần chạy API đầu tiên có 8 test BV-01..08 báo Fail vì script quên gửi token Admin (401); đã sửa script và chạy lại toàn bộ — kết quả dưới đây là lần chạy sau.

## 1. Kết quả theo test case

### Domain Testing
| TC ID | Lớp chạy | Kết quả | Actual tóm tắt | Bug |
|---|---|---|---|---|
| FR10-DT-01 … DT-23 | API | Pass | Mọi ô ma trận đúng spec: 4 ô hợp lệ (pending→confirmed, pending→canceled, confirmed→shipping, confirmed→canceled) chấp nhận; các ô không hợp lệ trả 400 và không đổi | |
| FR10-DT-24 | API | **Fail** | `canceled → delivered`: HTTP 200, DB = `delivered` (spec: `canceled` là trạng thái cuối, phải từ chối) | BUG-01 |
| FR10-DT-25 | API | Pass | `canceled → canceled` bị từ chối | |
| FR10-DT-14 | API | Pass | `shipping → delivered` chấp nhận (nằm trong DT-01..23) | |
| FR10-DT-15 | API | Pass | `shipping → canceled` (Admin) bị từ chối — đúng theo diễn giải chặt | |
| FR10-DT-26 | API | Pass | User hủy đơn `pending` thành công | |
| FR10-DT-27 | API | Pass | User hủy đơn `confirmed` thành công | |
| FR10-DT-28 | API | **Fail** | User hủy đơn `shipping`: HTTP 200, DB = `canceled` (spec: User không được hủy khi `shipping`) | BUG-03 |
| FR10-DT-29 | API | Pass | Hủy đơn `delivered` bị từ chối ("Cannot cancel this order.") | |
| FR10-DT-30 | API | Pass | Hủy đơn `canceled` bị từ chối | |
| FR10-DT-31 | API | Pass | Admin API không token → 401, không đổi | |
| FR10-DT-32 | API | Pass | Hủy không token → 401, không đổi | |
| FR10-DT-33 | API | **Fail** | **Token của User thường** gọi `PUT /api/admin/orders/:id/status`: HTTP 200, đơn đổi sang `confirmed` (FR-12/SEC-03: phải kiểm tra `role=admin`) | BUG-05 |
| FR10-DT-34 | API | Pass | User B hủy đơn của User A → 404, đơn A không đổi | |
| FR10-DT-35 | API | Pass | Admin API với id không tồn tại → 404 | |
| FR10-DT-36 | API | Pass | Hủy với id không tồn tại → 404 | |
| FR10-DT-37 … DT-41 | API | Pass | `status` rỗng/`refunded`/`CONFIRMED`/`null`/`123` đều bị từ chối 400, đơn không đổi | |
| FR10-DT-42 | API | Pass | Chuỗi `pending→confirmed→shipping→delivered` thành công; sau `delivered` mọi chuyển tiếp bị từ chối | |
| FR10-DT-43 | API | **Fail** | Hủy bởi User thành công, nhưng sau đó `canceled → delivered` (Admin) cũng thành công: HTTP 200, DB = `delivered` | BUG-01 |
| FR10-DT-44 | UI-Admin | Pass | `pending`: nút "Xác nhận", "Hủy" | |
| FR10-DT-45 | UI-Admin | Pass | `confirmed`: nút "Giao hàng", "Hủy" | |
| FR10-DT-46 | UI-Admin | Pass | `shipping`: nút "Hoàn thành" | |
| FR10-DT-47 | UI-Admin | Pass | `delivered`: không có nút | |
| FR10-DT-48 | UI-Admin | **Fail** | `canceled`: vẫn có nút **"Đánh dấu Đã giao"** (spec: trạng thái cuối, không có hành động) | BUG-02 |
| FR10-DT-49 | UI-Web | Pass | Đơn `pending`: có nút "Hủy đơn" | |
| FR10-DT-50 | UI-Web | Pass | Đơn `confirmed`: có nút "Hủy đơn" | |
| FR10-DT-51 | UI-Web | **Fail** | Đơn `shipping`: vẫn có nút "Hủy đơn"; bấm vào thì hủy thành công ("Hủy đơn thành công!", đơn #3 từ "Đang giao" sang "Đã hủy") | BUG-04 (và BUG-03) |
| FR10-DT-52 | UI-Web | Pass | Đơn `delivered`: không có nút | |
| FR10-DT-53 | UI-Web | Pass | Đơn `canceled`: không có nút | |
| FR10-DT-54 | UI-Admin | **Fail** | Thao tác trên dữ liệu cũ: hiện `alert` "Lỗi: Invalid state transition from confirmed to confirmed" — **tiếng Anh**, lộ chi tiết kỹ thuật (FR-21 yêu cầu tiếng Việt) | BUG-06 |

### BVA
| TC ID | Lớp chạy | Kết quả | Actual tóm tắt | Bug |
|---|---|---|---|---|
| FR10-BV-01 | API | Pass | id `0` → 404, không đơn nào đổi | |
| FR10-BV-02 | API | Pass | id `-1` → 404 | |
| FR10-BV-03 | API | Pass | id `1` (nhỏ nhất) → 200, đơn 1 = confirmed | |
| FR10-BV-04 | API | Pass | id `3` (lớn nhất) → 200, đơn 3 = confirmed | |
| FR10-BV-05 | API | Pass | id `4` (N+1) → 404 | |
| FR10-BV-06 | API | Pass | id `abc` → 404, server sống | |
| FR10-BV-07 | API | Pass | id `1.5` → 404, không đơn nào đổi | |
| FR10-BV-08 | API | Pass | id `9223372036854775808` → 404 | |
| FR10-BV-09 | API | Pass | User hủy id `0` → 404 | |
| FR10-BV-10 | API | Pass | User hủy id N+1 → 404 | |
| FR10-BV-11 | API | Pass | 3 bước tiến thành công; bước 4 (`delivered → canceled`) bị từ chối | |
| FR10-BV-12 | API | Pass | Hủy lần 1 thành công; lần 2 bị từ chối | |
| FR10-BV-13 | API | Pass | `confirme` bị từ chối | |
| FR10-BV-14 | API | Pass | `confirmed` chấp nhận | |
| FR10-BV-15 | API | Pass | `confirmedd` bị từ chối | |
| FR10-BV-16 | API | Pass | ` confirmed` (khoảng trắng đầu) bị từ chối | |
| FR10-BV-17 | API | Pass | `confirmed ` (khoảng trắng cuối) bị từ chối | |

## 2. Quan sát thêm (không tính vào số bug của FR-10)
Phát hiện khi chạy, thuộc feature của thành viên khác trong nhóm; ghi lại để báo cho đúng người:
- **FR-13 (Dashboard):** doanh thu hiển thị **300,000 ₫** trong khi chỉ có một đơn `delivered` 150,000 ₫ (code nhân đôi `total_amount`, `App.jsx:218`). Ảnh: `evidence/observation_dashboard_revenue.jpg`.
- **FR-11 (Lịch sử đơn):** `GET /api/orders/1` **không cần token** vẫn trả đầy đủ thông tin đơn (HTTP 200) — ai cũng xem được đơn của người khác.
- **FR-18 (Quản lý đơn Admin):** địa chỉ giao hàng hiển thị bằng `dangerouslySetInnerHTML` (`App.jsx:799-804`), chưa kiểm chứng XSS vì ngoài phạm vi.
- Thông báo lỗi API cho chuyển không hợp lệ là tiếng Anh ("Invalid state transition from X to Y"); SRS chỉ yêu cầu "thông báo phù hợp", nên chỉ tính lỗi khi hiển thị thẳng trên UI (BUG-06).

## 3. Test khám phá thêm sau khi chạy (`added-after-run`)
| ID | Kịch bản | Kết quả |
|---|---|---|
| X-01 | 60 lần: tạo đơn `pending`, gửi **đồng thời** "Admin xác nhận" và "User hủy" (`evidence/race_test.js`) | Cả hai request đều trả 200 ở cả 60 lần. Trạng thái cuối: `canceled` 59 lần, **`confirmed` 1 lần** → có lúc đơn đã bị User hủy rồi bị Admin "xác nhận" đè lên (đơn hủy bị hồi sinh), vi phạm "`canceled` là trạng thái kết thúc". Nguyên nhân: kiểm tra trạng thái (`SELECT`) và cập nhật (`UPDATE`) là hai bước riêng, `UPDATE` không có điều kiện theo trạng thái cũ (`server.js:528-562`). Ghi nhận là **BUG-07** (xác suất thấp). Kết quả thô: `evidence/race_result.json`. |

## 4. Thống kê FR-10

| Hạng mục | Số lượng |
|---|---|
| Test case thiết kế | **71** (54 Domain Testing + 17 BVA) |
| Đã thực thi | 71 |
| Pass | 64 (DT: 47, BV: 17) |
| Fail | 7 (DT: 7, BV: 0) |
| Chưa thực thi | 0 |
| Bug phân biệt (nguyên nhân gốc) | **7** (BUG-01 … BUG-07, xem `06_bugs.md`) |
| Test khám phá thêm | 1 (X-01) — phát hiện BUG-07 |
