# FR-10: Bug report

Môi trường chung: Windows 11, Node v22.20.0, Backend `http://localhost:3000`, Web `http://localhost:5173`, Web Admin `http://localhost:5174` (Chromium trong Claude desktop), dữ liệu seed gốc. Ngày phát hiện: 2026-10-16. Spec = `README.md` (SRS). Mức độ: Critical > Major > Minor.
Tài khoản dùng: User `test@eshop.com` / `Test1234!`, Admin `admin@eshop.com` / `Admin123!` (từ `database.js`).

Trạng thái GitHub Issues: **đã đăng** #11–#17 (tiêu đề có tiền tố `[FR-10]`, nhãn `bug`) tại https://github.com/nhaajtdajt/eshop-hw02-domain-testing/issues. Nội dung từng issue nằm trong `features/FR-10/issues/`.

| Bug | Tiêu đề | Mức độ | Test liên quan | Issue |
|---|---|---|---|---|
| BUG-01 | API cho phép chuyển đơn đã hủy (`canceled`) sang `delivered` | Major | DT-24, DT-43 | #11 |
| BUG-02 | Web Admin hiện nút "Đánh dấu Đã giao" cho đơn đã hủy | Minor | DT-48 | #12 |
| BUG-03 | API cho phép User hủy đơn đang giao (`shipping`) | Major | DT-28 | #13 |
| BUG-04 | Trang Hồ sơ (Web) hiện nút "Hủy đơn" cho đơn đang giao | Major | DT-51 | #14 |
| BUG-05 | API đổi trạng thái đơn không kiểm tra quyền Admin | Critical | DT-33 | #15 |
| BUG-06 | Lỗi chuyển trạng thái không hợp lệ hiển thị tiếng Anh trên Web Admin | Minor | DT-54 | #16 |
| BUG-07 | Race condition: đơn đã hủy có thể bị xác nhận đè lại | Minor | X-01 | #17 |

---

### BUG-01: API cho phép chuyển đơn đã hủy (`canceled`) sang `delivered`
- **Feature:** FR-10 (Pool B) — **Mức độ:** Major
- **Test liên quan:** FR10-DT-24, FR10-DT-43
- **Các bước tái hiện:**
  1. Đăng nhập Admin, lấy token. Đăng nhập User, tạo đơn bằng `POST /api/checkout` (`{"total_amount":100000,"shipping_address":"x"}`) → `orderId`.
  2. `PUT /api/admin/orders/<orderId>/status` với `{"status":"canceled"}` → 200.
  3. `PUT /api/admin/orders/<orderId>/status` với `{"status":"delivered"}`.
- **Expected (SRS FR-10, README.md dòng 160):** `canceled` là trạng thái kết thúc, không được chuyển sang trạng thái nào khác; chuyển không hợp lệ trả lỗi.
- **Actual:** HTTP **200** "Order status updated"; đơn từ `canceled` thành `delivered` (và được tính vào doanh thu Dashboard).
- **Bằng chứng:** `evidence/api_results.json` (FR10-DT-24, FR10-DT-43). Code: `backend/server.js:550-551` (nhánh `if (currentStatus === "canceled" && status === "delivered") isValidTransition = true`).

### BUG-02: Web Admin hiện nút "Đánh dấu Đã giao" cho đơn đã hủy
- **Feature:** FR-10 — **Mức độ:** Minor (giao diện mời thao tác sai, hệ quả là BUG-01)
- **Test liên quan:** FR10-DT-48
- **Các bước tái hiện:**
  1. Có một đơn đã hủy (ví dụ hủy đơn từ trang Hồ sơ hoặc từ Admin).
  2. Đăng nhập Web Admin `http://localhost:5174`, mở tab "Đơn hàng".
  3. Quan sát cột "Hành động" của đơn có trạng thái "Đã hủy".
- **Expected (SRS FR-10, dòng 160; FR-18, dòng 221):** Đơn `canceled` là trạng thái kết thúc nên không có hành động chuyển trạng thái nào.
- **Actual:** Đơn "Đã hủy" có nút **"Đánh dấu Đã giao"**; bấm vào là chuyển được (xem BUG-01). Đơn "Đã giao" thì đúng là không có nút.
- **Bằng chứng:** `evidence/admin_orders_ui_states.jpg`, `evidence/ui_results.json`. Code: `frontend-admin/src/App.jsx:862-869`.

### BUG-03: API cho phép User hủy đơn đang giao (`shipping`)
- **Feature:** FR-10 — **Mức độ:** Major
- **Test liên quan:** FR10-DT-28
- **Các bước tái hiện:**
  1. User tạo đơn (`POST /api/checkout`), Admin chuyển lần lượt `confirmed` rồi `shipping`.
  2. Với token **User** (chủ đơn): `PUT /api/orders/<orderId>/cancel`.
- **Expected (SRS FR-10, dòng 161):** Khi đơn đã ở `shipping`, User không được phép tự hủy; chỉ Admin thao tác.
- **Actual:** HTTP **200** "Order canceled successfully"; đơn `shipping` thành `canceled`. Backend chỉ chặn `delivered` và `canceled`.
- **Bằng chứng:** `evidence/api_results.json` (FR10-DT-28). Code: `backend/server.js:329` (comment trong code cũng ghi "Lẽ ra phải là: if (order.status !== 'pending' && order.status !== 'confirmed')").

### BUG-04: Trang Hồ sơ (Web) hiện nút "Hủy đơn" cho đơn đang giao
- **Feature:** FR-10 — **Mức độ:** Major (giao diện cho phép đúng thao tác bị cấm)
- **Test liên quan:** FR10-DT-51
- **Các bước tái hiện:**
  1. Đưa một đơn của `test@eshop.com` tới trạng thái `shipping` (qua Admin).
  2. Đăng nhập Web `http://localhost:5173` bằng `test@eshop.com`, mở `/profile`.
  3. Xem cột "Thao tác" của đơn "Đang giao" và bấm "Hủy đơn".
- **Expected (SRS FR-10, dòng 161; FR-20, dòng 236 cho Mobile cùng quy tắc):** Không hiển thị/không cho hủy khi `shipping`; chỉ hủy được ở `pending`/`confirmed`.
- **Actual:** Đơn "Đang giao" vẫn có nút "Hủy đơn"; bấm vào hiện "Hủy đơn thành công!" và đơn chuyển "Đã hủy" (kết hợp BUG-03). Các đơn `delivered`/`canceled` thì đúng là không có nút.
- **Bằng chứng:** `evidence/web_profile_orders_before.jpg` (đơn #3 "Đang giao" có nút), `evidence/web_profile_cancel_shipping_after.jpg` (đơn #3 sau khi bấm: "Đã hủy"), `evidence/ui_results.json`. Code: `frontend-web/src/pages/Profile.jsx:199-206` (điều kiện `status !== "delivered" && status !== "canceled"`).

### BUG-05: API đổi trạng thái đơn không kiểm tra quyền Admin
- **Feature:** FR-10 (liên quan FR-12) — **Mức độ:** Critical (bất kỳ người dùng đăng nhập nào cũng điều khiển được vòng đời mọi đơn)
- **Test liên quan:** FR10-DT-33
- **Các bước tái hiện:**
  1. Đăng nhập User thường `test@eshop.com` lấy token (role `user`).
  2. `PUT /api/admin/orders/<orderId>/status` với header `Authorization: Bearer <token user>` và body `{"status":"confirmed"}` (đơn đang `pending`).
- **Expected (SRS FR-12, dòng 176–179; SEC-03, dòng 280; FR-10 "Admin xác nhận/giao hàng/hoàn tất"):** Từ chối (403) vì token không có `role = admin`; trạng thái đơn không đổi.
- **Actual:** HTTP **200** "Order status updated"; User thường xác nhận được đơn (và có thể giao/hoàn tất đơn của bất kỳ ai vì API không kiểm tra chủ đơn). Middleware `authenticateToken` chỉ kiểm tra token hợp lệ.
- **Bằng chứng:** `evidence/api_results.json` (FR10-DT-33). Code: `backend/server.js:100-110`, `:525`.

### BUG-06: Lỗi chuyển trạng thái không hợp lệ hiển thị tiếng Anh trên Web Admin
- **Feature:** FR-10 (liên quan FR-21) — **Mức độ:** Minor
- **Test liên quan:** FR10-DT-54
- **Các bước tái hiện:**
  1. Mở Web Admin, tab "Đơn hàng", để một đơn `pending` hiển thị (nút "Xác nhận").
  2. Trước khi bấm, xác nhận đơn đó bằng API (hoặc ở tab khác) để trạng thái đã đổi nhưng trang chưa tải lại.
  3. Bấm "Xác nhận" trên trang cũ.
- **Expected (SRS FR-10 dòng 162; FR-21 dòng 244):** Thông báo lỗi phù hợp, bằng tiếng Việt, dễ hiểu.
- **Actual:** Hộp thoại "Lỗi: Invalid state transition from confirmed to confirmed" — tiếng Anh, chứa tên trạng thái kỹ thuật.
- **Bằng chứng:** `evidence/ui_results.json` (`admin_ui_stale_action_DT54`). Code: `frontend-admin/src/App.jsx:90-91`, `backend/server.js:555`.

### BUG-07: Race condition — đơn đã hủy có thể bị xác nhận đè lại
- **Feature:** FR-10 — **Mức độ:** Minor (vi phạm bất biến nhưng chỉ xảy ra khi hai thao tác trùng thời điểm; quan sát 1/60 lần)
- **Test liên quan:** X-01 (test khám phá)
- **Các bước tái hiện:**
  1. Tạo đơn `pending`.
  2. Gửi **đồng thời** (cùng lúc) `PUT /api/admin/orders/<id>/status {"status":"confirmed"}` (Admin) và `PUT /api/orders/<id>/cancel` (User chủ đơn). Lặp lại nhiều lần (script `evidence/race_test.js` chạy 60 lần).
  3. Đọc trạng thái cuối.
- **Expected (SRS FR-10, dòng 160):** `canceled` là trạng thái kết thúc; sau khi bị hủy, không thể trở thành `confirmed`. Khi hai thao tác xung đột, một trong hai phải bị từ chối.
- **Actual:** Cả hai request đều trả 200 ở cả 60 lần; trạng thái cuối `canceled` 59 lần và `confirmed` **1 lần** (đơn đã hủy bị hồi sinh). Nguyên nhân: backend đọc trạng thái (`SELECT`) rồi ghi (`UPDATE ... WHERE id=?`) ở hai bước tách rời, không kiểm tra lại trạng thái cũ khi ghi.
- **Bằng chứng:** `evidence/race_result.json`, `evidence/race_test.js`. Code: `backend/server.js:321-342`, `:525-568`.

---

## Quan sát ngoài phạm vi FR-10 (báo cho thành viên phụ trách; không tính vào số bug FR-10)
- **FR-13 (Dashboard):** "Tổng doanh thu (Delivered)" hiển thị 300,000 ₫ khi chỉ có một đơn đã giao 150,000 ₫ (nhân đôi, `frontend-admin/src/App.jsx:218`). Ảnh: `evidence/observation_dashboard_revenue.jpg`.
- **FR-11 (Lịch sử đơn hàng):** `GET /api/orders/:id` không yêu cầu token, trả thông tin đơn của bất kỳ ai (HTTP 200 khi gọi không token).
- **FR-18 (Quản lý đơn Admin):** địa chỉ giao hàng render bằng `dangerouslySetInnerHTML` (`App.jsx:799-804`); chưa kiểm chứng XSS.
- Thông báo lỗi của API cho chuyển không hợp lệ là tiếng Anh ("Invalid state transition from X to Y"); chỉ tính lỗi khi hiển thị thẳng trên UI (BUG-06).
