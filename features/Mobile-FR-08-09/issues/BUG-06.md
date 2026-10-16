`coupon-usage` ghi lượt dùng cho mã không tồn tại

- **Feature:** Mobile FR-09 (dùng chung backend) — **Mức độ:** Minor
- **Test liên quan:** MFR-DT-36
- **Các bước tái hiện:** Với token User, `POST /api/coupon-usage` `{"coupon_id":99999}`.
- **Expected:** Từ chối (4xx) vì mã không tồn tại; không ghi bản ghi.
- **Actual:** HTTP 200 "Usage recorded"; bản ghi mới trong `coupon_usage` với `coupon_id = 99999`.
- **Bằng chứng:** [evidence/api_results.json](https://github.com/nhaajtdajt/eshop-hw02-domain-testing/blob/main/features/Mobile-FR-08-09/evidence/api_results.json) (MFR-DT-36). Code: `backend/server.js:444-454`.
