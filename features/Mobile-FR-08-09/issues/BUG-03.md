Checkout lưu nguyên `total_amount` của client, không kiểm tra giá trị

- **Feature:** Mobile FR-08 (dùng chung backend với Web FR-08) — **Mức độ:** Critical
- **Test liên quan:** MFR-DT-07, DT-30, DT-32, DT-33, DT-34
- **Các bước tái hiện:**
  1. Đăng nhập lấy token User.
  2. `POST /api/checkout` với `{"items":[{"id":1,"name":"iPhone 15 Pro Max","price":30000000,"quantity":1}],"total_amount":1}`.
  3. Lặp lại với `total_amount` bị thiếu, `-100`, `"abc"`.
  4. Xem đơn trong `GET /api/orders/my-orders`.
- **Expected (SRS FR-08, dòng 107):** Backend tự tính lại tổng tiền; không chấp nhận `total_amount` do client gửi lên (đơn phải có tổng 30,000,000 hoặc bị từ chối).
- **Actual:** HTTP 200 "Checkout successful"; đơn lưu `total_amount = 1`. Với thiếu/âm/chuỗi cũng tạo đơn thành công (đơn rác). Ứng dụng Mobile gửi `total_amount` do client tính (kể cả số sai của BUG-01: đơn #75 lưu 4,000,000 thay vì 360,000).
- **Bằng chứng:** [evidence/api_results.json](https://github.com/nhaajtdajt/eshop-hw02-domain-testing/blob/main/features/Mobile-FR-08-09/evidence/api_results.json) (DT-07, DT-32..34), [evidence/ui_results.json](https://github.com/nhaajtdajt/eshop-hw02-domain-testing/blob/main/features/Mobile-FR-08-09/evidence/ui_results.json) (DT-30). Code: `backend/server.js:297-309`.
