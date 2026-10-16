Tổng đơn đúng bằng ngưỡng tối thiểu bị từ chối (`>` thay vì `>=`)

- **Feature:** Mobile FR-09 (dùng chung backend) — **Mức độ:** Major
- **Test liên quan:** MFR-BV-02, MFR-BV-05
- **Các bước tái hiện:** Giỏ có tổng đúng 300,000 ₫ (sản phẩm giá 300,000 × 1), thanh toán, nhập `SAVE10`, bấm "Áp dụng" (hoặc `POST /api/apply-coupon` `{"code":"BIGBUY","total_amount":500000,"user_id":2}`).
- **Expected (SRS FR-09, dòng 118):** C3: tổng đơn **>=** `min_order_amount`; tổng 300,000 với `SAVE10` (min 300,000) phải được áp dụng.
- **Actual:** "Đơn hàng chưa đủ giá trị tối thiểu 300.000 ₫ để áp dụng mã này". Tương tự `BIGBUY` @500,000. Mã chỉ áp dụng được từ ngưỡng + 1 (300,001 / 500,001).
- **Bằng chứng:** [evidence/api_results.json](https://github.com/nhaajtdajt/eshop-hw02-domain-testing/blob/main/features/Mobile-FR-08-09/evidence/api_results.json) (MFR-BV-02, BV-05), [evidence/ui_results.json](https://github.com/nhaajtdajt/eshop-hw02-domain-testing/blob/main/features/Mobile-FR-08-09/evidence/ui_results.json) (BV-02). Code: `backend/server.js:379` (`total_amount > coupon.min_order_amount`).
