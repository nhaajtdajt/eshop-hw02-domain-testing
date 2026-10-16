Ô "Tổng tiền thanh toán" hiển thị số thô, không có `₫` và phân cách hàng nghìn

- **Feature:** Mobile FR-08 (liên quan FR-21) — **Mức độ:** Minor
- **Test liên quan:** MFR-DT-27
- **Các bước tái hiện:** Thêm sản phẩm 400,000 ₫, vào màn "Xác Nhận Đơn Hàng", xem ô "Tổng tiền thanh toán (VND)".
- **Expected (SRS FR-21, dòng 246):** Luôn dùng ký hiệu `₫` với định dạng phân cách hàng nghìn.
- **Actual:** Ô hiển thị `400000`; các dòng khác ("Tổng thanh toán: 400,000 ₫") đúng định dạng.
- **Bằng chứng:** ![evidence/mobile_checkout_save10_negative_discount.jpg](https://raw.githubusercontent.com/nhaajtdajt/eshop-hw02-domain-testing/main/features/Mobile-FR-08-09/evidence/mobile_checkout_save10_negative_discount.jpg), [evidence/ui_results.json](https://github.com/nhaajtdajt/eshop-hw02-domain-testing/blob/main/features/Mobile-FR-08-09/evidence/ui_results.json). Code: `frontend-mobile/App.js:684-690` (`value={String(cartTotal)}`).
