# FR-03: AI gap analysis

Ngữ cảnh: AI ở đây là Claude Code (Sonnet 5.5) chạy trong phiên làm việc này, được dẫn qua từng bước của skill `domain-testing-bva` (xem `audit/AI_AUDIT_LOG.md`). "Bỏ sót" nghĩa là: thứ có trong bộ test/bug **cuối cùng** nhưng **không** có trong bản thiết kế đầu tiên của AI ở Bước 1–3, hoặc là chỗ AI làm sai và phải sửa.

Nhóm nguyên nhân: `Prompt` (đầu vào/yêu cầu của mình chưa đủ) | `Giới hạn công cụ` | `Độ phức tạp feature`.

| # | Thứ AI bỏ sót / làm sai | Phát hiện bằng cách nào | Nhóm nguyên nhân | Giải thích | Cách khắc phục |
|---|---|---|---|---|---|
| G1 | **Test theo hình dạng request** (thiếu trường, `null`, kiểu object) cho `forgot-password`/`reset-password` | Khi chạy thật, nhận ra thiết kế chỉ có giá trị "hợp lệ/không hợp lệ" của từng ô, không có request lệch cấu trúc → thêm X-01..X-04 (không ra bug mới) | Prompt | Prompt Bước 2 yêu cầu chia lớp "theo từng input" nên AI chỉ nghĩ tới giá trị chuỗi người dùng gõ, không nghĩ tới client không phải trình duyệt | Thêm vào skill: sau khi chia lớp theo giá trị, luôn thêm nhóm "request shape" (thiếu/null/sai kiểu) cho mọi API |
| G2 | **Không giới hạn số lần đoán OTP** (300 lần đoán sai liên tiếp đều 400, không khóa/chậm lại) — kết hợp OTP chỉ có 4 chữ số (9000 giá trị) thì đoán ra trong vài giây | Nghĩ lại về SEC-07 ("đủ entropy") sau khi thấy OTP 4 số; chạy X-05 | Độ phức tạp feature | Đây là thuộc tính qua nhiều request, không phải miền của một input; phân hoạch/BVA tập trung vào một request nên khó nảy ra. AI chỉ dùng phần "tối thiểu 6 chữ số" của SEC-07 mà bỏ phần "đủ entropy" | Bổ sung bước "thuộc tính phi chức năng liên quan feature (SEC-xx)" vào skill; mục này thành quan sát chứ không tính bug vì SRS không yêu cầu rate limit cụ thể |
| G3 | **Chuẩn hóa email** (chữ hoa/thường, khoảng trắng đầu/cuối) | Nghĩ lại về lớp email; chạy X-06: `TEST@ESHOP.COM` → 404 (phân biệt hoa thường) | Prompt | SRS im lặng; AI mặc định "spec không nói thì không test" nên bỏ cả lớp. Với email, hoa/thường là biên thực tế của người dùng | Trong skill: khi spec im lặng về một lớp phổ biến, vẫn thiết kế test và ghi expected là "quan sát", không phải "bug" |
| G4 | **Lớp mật khẩu có khoảng trắng** | Ở Bước 1 AI đã thấy regex đòi `\s` nhưng không thêm lớp tương ứng; phải chạy `New pass1` ngoài kế hoạch mới xác nhận UI chỉ nhận mật khẩu có khoảng trắng | Prompt | Mình dặn "expected lấy từ spec, code chỉ gợi ý" nên AI không biến gợi ý trong code thành lớp test | Skill: gợi ý từ code ("Spec vs Code") phải được chuyển thành lớp test bổ sung (kiểm thử hộp đen dựa trên giả thuyết) |
| G5 | **Expected của DT-03 quá cụ thể** ("báo sai định dạng") trong khi API chỉ trả "User not found" | Khi đối chiếu kết quả, AI lúc đầu chấm Pass dù thông báo không phải về định dạng | Giới hạn công cụ | AI viết expected từ suy luận chứ không dựa vào chuỗi cụ thể nêu trong SRS; khi chấm lại dễ "dễ dãi" để khớp | Chỉ ghi expected ở mức hành vi mà SRS nêu (từ chối, không cấp OTP) và ghi riêng "chất lượng thông báo" thành quan sát |
| G6 | **Gộp nhiều nguyên nhân vào cùng nhóm test** — 14 test BV (BV-10..BV-23) cùng Fail vì **một** lỗi (regex UI) nên số test Fail (40) không phản ánh số lỗi (10) | Tổng hợp kết quả | Độ phức tạp feature | Hai lớp ràng buộc (UI + API) cùng áp lên một giá trị; một lỗi ở lớp UI làm "hợp lệ" thành Fail ở hàng loạt test | Báo cáo luôn có cột "Bug" để nhóm theo nguyên nhân gốc; không dùng số test Fail làm số bug |
| G7 | **Lỗi trong chính test script của AI**: (a) DT-06 báo Fail giả do trạng thái chung (user C của test hết hạn có `reset_token`); (b) DT-15 lần đầu chạy chỉ sau ~12 giây đã kết luận | Đọc kết quả bất thường, đối chiếu thời gian trong log | Giới hạn công cụ | AI không có cảm giác về thời gian thực và dễ bỏ qua tương tác giữa các test dùng chung DB | Skill: mỗi test dài (có chờ) dùng dữ liệu riêng; test phụ thuộc thời gian phải ghi thời điểm cấp và thời điểm dùng rồi tính số phút trước khi kết luận |

## Tóm tắt nguyên nhân
- **Prompt (3 mục: G1, G3, G4):** chủ yếu do cách mình đặt yêu cầu ở Bước 2 — "theo từng input" và "spec là oracle" — khiến AI bỏ qua các lớp ngoài spec hoặc ngoài giá trị người gõ.
- **Giới hạn công cụ (G5, G7):** AI dễ "dễ dãi" khi chấm kết quả và không tự theo dõi thời gian/trạng thái dùng chung.
- **Độ phức tạp feature (G2, G6):** thuộc tính xuyên nhiều request và nhiều lớp ràng buộc không nằm gọn trong một bảng lớp tương đương.

## Điều AI làm đúng (để đối chiếu)
- Bắt đúng ở Bước 1 các giả thuyết lớn: OTP 4 số, regex mật khẩu sai, thiếu trường xác nhận, thiếu Step Indicator, thiếu nút quay lại đăng nhập, `type="text"` cho email, không có thời hạn OTP. Tất cả được xác nhận khi chạy.
- Dự đoán sai/khẳng định thừa: H13 và H15 ("cần thử") hóa ra không có lỗi (X-01..X-04).
