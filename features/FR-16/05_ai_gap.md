# FR-16: AI gap analysis

Ngữ cảnh: AI là Claude Code (Sonnet 5.5) trong phiên này, dẫn qua từng bước của skill `domain-testing-bva` (xem `audit/AI_AUDIT_LOG.md`). "Bỏ sót" = có trong bộ test/bug cuối nhưng không có trong bản thiết kế đầu (Bước 1–3), hoặc AI làm sai và phải sửa. Đã áp dụng các bài học của FR-03 và FR-10 (request shape, quyền, UI/API, race), nên một số lỗ hổng cũ không lặp lại.

Nhóm nguyên nhân: `Prompt` | `Giới hạn công cụ` | `Độ phức tạp feature`.

| # | Thứ AI bỏ sót / làm sai | Phát hiện bằng cách nào | Nhóm nguyên nhân | Giải thích | Cách khắc phục |
|---|---|---|---|---|---|
| G1 | **Biến thể file thực tế**: dấu phân cách `;` (Excel tiếng Việt), BOM, dòng trống giữa file, giá trị có khoảng trắng đầu/cuối | Nghĩ lại về người dùng thật sau khi chạy xong; chạy X-01..X-04 | Prompt | Prompt Bước 2 gắn chặt với "RFC 4180" trong spec nên AI chỉ chia lớp theo những gì spec nêu; phần "đầu vào do công cụ khác sinh ra" (Excel, Notepad) không nằm trong spec nên bị bỏ qua. Dấu `;` đáng chú ý vì file CSV xuất từ Excel ở máy cài tiếng Việt thường dùng dấu này | Skill: với feature nhận file, thêm nhóm "file do công cụ phổ biến xuất ra" (BOM, dấu phân cách địa phương, xuống dòng, dòng trống, khoảng trắng) kể cả khi spec không nêu |
| G2 | **Kiểm tra bảng xem trước đã cập nhật chưa** trước khi bấm Import (harness của AI): lần chạy đầu DT-02 import nhầm dữ liệu của test trước | Tên sản phẩm trả về là `FR16-1..3` trong khi file chỉ có 1 dòng khác tên | Giới hạn công cụ | `FileReader` chạy bất đồng bộ; AI dùng thời gian chờ cố định (350 ms) thay vì chờ tới khi nội dung giao diện khớp file đã chọn | Skill: với UI bất đồng bộ, chờ điều kiện cụ thể (nội dung xem trước khớp) thay vì chờ cố định; kiểm tra dữ liệu thực tế sinh ra có khớp đầu vào |
| G3 | **Kích thước payload khi thiết kế BV-18**: dòng 1000 có mô tả dài làm tổng ~131 KB, vượt giới hạn 100 KB nên bị 413 và che mất việc kiểm tra rollback | Kết quả BV-18 "Pass" chỉ vì HTTP 413 (không có dòng nào được thêm) — nghi ngờ vì lý do không đúng | Độ phức tạp feature | Hai thuộc tính (kích thước body, rollback) tương tác; AI đã lường tới giới hạn body (BV-04) nhưng không tính độ dài dòng khi thiết kế BV-18 | Skill: khi một kết quả "Pass" của test từ chối có thể đến từ một lý do khác, kiểm tra **mã lỗi/nội dung phản hồi** có đúng lý do mong đợi không |
| G4 | **Trùng lặp**: import cùng một file hai lần, hoặc có hai dòng trùng tên trong một file | Rà phạm vi cuối bước | Prompt | Spec không nêu và AI áp dụng quy tắc "spec không nói thì không thiết kế" | Ghi nhận là chưa test; có thể bổ sung nếu giảng viên coi trùng lặp là lỗi |
| G5 | **Giá có dấu phân cách hàng nghìn** (`"100,000"` hoặc `100.000`) — định dạng quen thuộc với người dùng Việt | Rà phạm vi cuối bước | Prompt | Không có trong spec; trùng với lỗi parser nháy kép (BUG-03) nên khó tách riêng | Ghi nhận chưa test; liên quan BUG-02 và BUG-03 |
| G6 | **Kết quả Pass không đầy đủ**: DT-16 (không có header) "Pass" theo tiêu chí DB không đổi, nhưng giao diện hiện banner xanh "Import hoàn tất" | Đọc nội dung banner của từng test thay vì chỉ đọc số dòng được thêm | Giới hạn công cụ | Tiêu chí "DB không đổi" của AI chỉ đo kết quả dữ liệu, không đo thông điệp cho người dùng | Đã ghi thông điệp sai thành BUG-08; skill: với test từ chối, kiểm tra cả dữ liệu lẫn thông báo |

## Tóm tắt nguyên nhân
- **Prompt (G1, G4, G5):** AI bám sát spec và bỏ qua các tình huống thực tế quanh nó.
- **Giới hạn công cụ (G2, G6):** kiểm thử UI bất đồng bộ và tiêu chí chấm quá hẹp.
- **Độ phức tạp feature (G3):** tương tác giữa giới hạn kích thước request và tính nguyên tử.

## Điều AI làm đúng (để đối chiếu)
- Ở Bước 1, các giả thuyết lớn đều đúng: H1 không rollback, H2 không validate giá, H3 `split(",")` hỏng nháy kép, H4 không kiểm đuôi file, H5 không kiểm header, H7 thiếu kiểm tra role, H8 API nhận tên toàn khoảng trắng (khác UI).
- Dự đoán trước được giới hạn body 100 KB của `body-parser` (BV-04) từ hiểu biết về công cụ, và nó được xác nhận (HTTP 413).
- Các giả thuyết "có vẻ đúng" (H10 file rỗng/chỉ header, H11 số dòng báo cáo `index+2`, H12 file mẫu) đều đúng.
