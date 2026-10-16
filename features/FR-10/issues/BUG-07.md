Race condition — đơn đã hủy có thể bị xác nhận đè lại

- **Feature:** FR-10 — **Mức độ:** Minor (vi phạm bất biến nhưng chỉ xảy ra khi hai thao tác trùng thời điểm; quan sát 1/60 lần)
- **Test liên quan:** X-01 (test khám phá)
- **Các bước tái hiện:**
  1. Tạo đơn `pending`.
  2. Gửi **đồng thời** (cùng lúc) `PUT /api/admin/orders/<id>/status {"status":"confirmed"}` (Admin) và `PUT /api/orders/<id>/cancel` (User chủ đơn). Lặp lại nhiều lần (script [evidence/race_test.js](https://github.com/nhaajtdajt/eshop-hw02-domain-testing/blob/main/features/FR-10/evidence/race_test.js) chạy 60 lần).
  3. Đọc trạng thái cuối.
- **Expected (SRS FR-10, dòng 160):** `canceled` là trạng thái kết thúc; sau khi bị hủy, không thể trở thành `confirmed`. Khi hai thao tác xung đột, một trong hai phải bị từ chối.
- **Actual:** Cả hai request đều trả 200 ở cả 60 lần; trạng thái cuối `canceled` 59 lần và `confirmed` **1 lần** (đơn đã hủy bị hồi sinh). Nguyên nhân: backend đọc trạng thái (`SELECT`) rồi ghi (`UPDATE ... WHERE id=?`) ở hai bước tách rời, không kiểm tra lại trạng thái cũ khi ghi.
- **Bằng chứng:** [evidence/race_result.json](https://github.com/nhaajtdajt/eshop-hw02-domain-testing/blob/main/features/FR-10/evidence/race_result.json), [evidence/race_test.js](https://github.com/nhaajtdajt/eshop-hw02-domain-testing/blob/main/features/FR-10/evidence/race_test.js). Code: `backend/server.js:321-342`, `:525-568`.
