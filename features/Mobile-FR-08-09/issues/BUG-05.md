Mã giảm cố định lớn hơn tổng đơn cho tổng thanh toán âm

- **Feature:** Mobile FR-09 (dùng chung backend) — **Mức độ:** Major (theo diễn giải: SRS không nêu, nhưng tổng thanh toán âm là bất hợp lý)
- **Test liên quan:** MFR-DT-26, MFR-BV-15
- **Các bước tái hiện:** Admin tạo mã `fixed` 100,000, min 0 (`POST /api/admin/coupons`); `POST /api/apply-coupon` với `total_amount = 99999`.
- **Expected (diễn giải theo FR-09, dòng 126):** `final_amount` không âm (tối đa giảm bằng tổng đơn, cho `final = 0`).
- **Actual:** `discount_amount = 100000`, `final_amount = -1` (với mã 1,000,000 @100,000: `final = -900,000`).
- **Bằng chứng:** [evidence/api_results.json](https://github.com/nhaajtdajt/eshop-hw02-domain-testing/blob/main/features/Mobile-FR-08-09/evidence/api_results.json) (MFR-DT-26, BV-15). Code: `backend/server.js:402-406`.
