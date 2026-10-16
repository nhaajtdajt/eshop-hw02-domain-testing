# FR-10: AI gap analysis

Ngữ cảnh: AI là Claude Code (Sonnet 5.5) trong phiên này, dẫn qua từng bước của skill `domain-testing-bva` (xem `audit/AI_AUDIT_LOG.md`). "Bỏ sót" = có trong bộ test/bug cuối nhưng không có trong bản thiết kế đầu (Bước 1–3), hoặc AI làm sai và phải sửa. Đây là phiên bản đã áp dụng các bài học của FR-03 (request shape, quyền, thuộc tính xuyên request), nên một số lỗ hổng cũ không lặp lại.

Nhóm nguyên nhân: `Prompt` | `Giới hạn công cụ` | `Độ phức tạp feature`.

| # | Thứ AI bỏ sót / làm sai | Phát hiện bằng cách nào | Nhóm nguyên nhân | Giải thích | Cách khắc phục |
|---|---|---|---|---|---|
| G1 | **Race condition** khi hai thao tác xung đột chạy đồng thời (Admin xác nhận × User hủy): đơn đã hủy bị "hồi sinh" thành `confirmed` | Sau khi chạy xong ma trận, nghĩ lại về tính bất biến "`canceled` là trạng thái cuối" và chạy X-01 (60 lần song song); 1/60 vi phạm | Độ phức tạp feature | Ma trận trạng thái × đích mô tả từng chuyển **tuần tự**. Lỗi chỉ lộ khi hai request xen kẽ, và xác suất thấp nên cũng không thấy ở test đơn lẻ | Thêm vào skill: với feature có trạng thái cuối/bất biến, thêm test đồng thời (chạy N lần) cho các cặp thao tác xung đột |
| G2 | **Khác biệt giữa UI và backend ở cùng một quy tắc** chỉ được phát hiện vì chạy riêng từng lớp: UI Web hiện nút hủy cho `shipping` (BUG-04) trong khi UI Admin ẩn đúng | Chạy thật UI từng màn hình | Prompt | Prompt Bước 2 yêu cầu nêu "Lớp chạy" cho mỗi test nhưng chưa yêu cầu **lặp quy tắc ở mọi giao diện có thể thao tác** (Admin, Web, Mobile). AI chỉ chắc chắn bao gồm cả hai nhờ đọc code Profile.jsx ở Bước 1 | Skill: khi một quy tắc có nhiều điểm thao tác (nhiều UI + API), lập bảng "điểm thao tác × trạng thái" trước khi viết test |
| G3 | **Phát hiện ngoài phạm vi** (FR-13 doanh thu nhân đôi, FR-11 xem đơn không cần token, FR-18 `innerHTML`) | Nhìn thấy khi chụp màn hình Dashboard và gọi `GET /api/orders/1` để dọn dữ liệu | Prompt | Bộ test chỉ thiết kế cho FR-10 nên không cố ý quan sát các feature lân cận; những thứ này lộ ra ngẫu nhiên. Có thể còn sót nhiều thứ tương tự | Skill: giữ mục "Quan sát ngoài phạm vi" và dành vài phút khám phá trên cùng màn hình; chuyển cho thành viên phụ trách feature đó thay vì tính vào bug của mình |
| G4 | **Diễn giải mơ hồ** "chỉ Admin mới có thể thao tác" khi `shipping`: AI chọn nghĩa chặt (Admin không được hủy) | Phân tích ở Bước 1; backend cũng từ chối `shipping → canceled` nên kết quả Pass không phân biệt được hai nghĩa | Giới hạn công cụ | AI không thể tự quyết ý định của đề; chọn một nghĩa rồi đối chiếu code dễ vô tình xác nhận nghĩa đó | Ghi rõ mơ hồ và đặt câu hỏi cho giảng viên/TA; DT-15 đã gắn nhãn "diễn giải chặt" |
| G5 | **Lỗi trong script test của AI**: BV-01..08 báo Fail giả (401) vì hàm trợ giúp quên gắn token Admin | Thấy 8 test cùng lỗi 401 ngay ở lần chạy đầu | Giới hạn công cụ | AI viết hàm riêng cho nhóm test mới và sao chép thiếu tham số xác thực; không có bước tự kiểm "request hợp lệ trước, rồi mới thử sai" | Skill: chạy một request hợp lệ làm "đối chứng" cho mỗi nhóm test trước khi tin kết quả Fail; nhiều test cùng một mã lỗi lạ (401) là dấu hiệu lỗi script |
| G6 | **Chưa test đường đi của Mobile** (Mobile FR-10 thuộc thành viên khác) và chưa test các hành động Admin khác (Admin hủy từ UI Admin tới trạng thái cuối) ngoài các nút có sẵn | Rà phạm vi cuối bước | Prompt | Phạm vi được cắt từ đầu; Admin UI chỉ được kiểm bằng việc đọc các nút chứ không bấm từng nút (đã bấm nút "Xác nhận" ở DT-54) | Có thể bấm thêm các nút còn lại nếu còn thời gian; ghi rõ trong README |

## Tóm tắt nguyên nhân
- **Độ phức tạp feature (G1):** lỗi nằm ở tương tác giữa các request, không nằm trong một ô của ma trận.
- **Prompt (G2, G3, G6):** cách đặt yêu cầu của mình chưa buộc AI duyệt hết các điểm thao tác và các màn hình lân cận.
- **Giới hạn công cụ (G4, G5):** AI không tự xác định ý đề khi spec mơ hồ, và tin kết quả script chưa đối chứng.

## Điều AI làm đúng (để đối chiếu)
- Ở Bước 1, AI đoán đúng 5/5 điểm lệch chính (H1 `canceled → delivered`, H2 nút Admin UI, H3 User hủy `shipping`, H4 nút Web hủy `shipping`, H5 thiếu kiểm tra role) và đều được xác nhận khi chạy.
- Các giả thuyết "có vẻ đúng" (H6, H8–H12: chủ đơn, trạng thái cuối `delivered`, giá trị `status` lạ, id không tồn tại) đều đúng; toàn bộ biên ID/chuỗi cho kết quả như dự đoán, và trong 25 ô ma trận chỉ có đúng 1 ô lệch (`canceled → delivered`).
- Ma trận 5×5 cho thấy giá trị rõ nhất của Domain Testing với state machine: mỗi bug gắn với một ô cụ thể (`canceled → delivered`) hay một cặp (vai trò × trạng thái).
