Ô email dùng `type="text"` thay vì `type="email"`

- **Feature:** FR-03 — **Mức độ:** Minor
- **Test liên quan:** FR03-DT-29 (liên quan DT-03)
- **Các bước tái hiện:** Mở `/forgot-password`, kiểm tra thuộc tính `type` của ô email (DevTools) hoặc nhập `testeshop.com` rồi gửi.
- **Expected (SRS FR-22 dòng 253):** Trường Email dùng `type="email"` (validate định dạng HTML5).
- **Actual:** `type="text"`; chuỗi sai định dạng vẫn được gửi lên server (server trả "User not found").
- **Bằng chứng:** [evidence/ui_results.json](https://github.com/nhaajtdajt/eshop-hw02-domain-testing/blob/main/features/FR-03/evidence/ui_results.json) (`step1_dom`). Code: `ForgotPassword.jsx:50`.
