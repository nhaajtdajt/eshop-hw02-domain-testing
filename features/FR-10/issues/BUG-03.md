API cho phép User hủy đơn đang giao (`shipping`)

- **Feature:** FR-10 — **Mức độ:** Major
- **Test liên quan:** FR10-DT-28
- **Các bước tái hiện:**
  1. User tạo đơn (`POST /api/checkout`), Admin chuyển lần lượt `confirmed` rồi `shipping`.
  2. Với token **User** (chủ đơn): `PUT /api/orders/<orderId>/cancel`.
- **Expected (SRS FR-10, dòng 161):** Khi đơn đã ở `shipping`, User không được phép tự hủy; chỉ Admin thao tác.
- **Actual:** HTTP **200** "Order canceled successfully"; đơn `shipping` thành `canceled`. Backend chỉ chặn `delivered` và `canceled`.
- **Bằng chứng:** [evidence/api_results.json](https://github.com/nhaajtdajt/eshop-hw02-domain-testing/blob/main/features/FR-10/evidence/api_results.json) (FR10-DT-28). Code: `backend/server.js:329` (comment trong code cũng ghi "Lẽ ra phải là: if (order.status !== 'pending' && order.status !== 'confirmed')").
