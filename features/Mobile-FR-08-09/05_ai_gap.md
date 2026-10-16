# Mobile FR-08/09: AI gap analysis

Ngữ cảnh: AI là Claude Code (Sonnet 5.5) trong phiên này, dẫn qua từng bước của skill `domain-testing-bva` (xem `audit/AI_AUDIT_LOG.md`). "Bỏ sót" = có trong kết quả/bộ test cuối nhưng không có trong bản thiết kế đầu (Bước 1–3), hoặc AI làm sai và phải sửa. Đã áp dụng bài học của FR-03, FR-10, FR-16.

Nhóm nguyên nhân: `Prompt` | `Giới hạn công cụ` | `Độ phức tạp feature`.

| # | Thứ AI bỏ sót / làm sai | Phát hiện bằng cách nào | Nhóm nguyên nhân | Giải thích | Cách khắc phục |
|---|---|---|---|---|---|
| G1 | **Chưa kiểm tra có chạy được thành phần Mobile hay không trước khi thiết kế**: `API_URL` cứng là IP LAN `192.168.10.13` (không khớp máy test), thiếu gói web cho Expo (`react-dom`, `react-native-web`, `@expo/metro-runtime`) | Chỉ phát hiện lúc bắt đầu Bước 4 | Giới hạn công cụ | AI thiết kế test từ code trước, rồi mới dựng môi trường; không có bước "chạy thử thành phần" ở Bước 0 | Skill: Bước 0 phải ghi rõ cách chạy từng thành phần (kể cả sửa tạm cấu hình) và dò trước các điều kiện chặn (IP cứng, thiếu phụ thuộc) |
| G2 | **Thông báo dạng `Alert.alert` không quan sát được** trên bản web nên các nhánh lỗi (thanh toán thất bại, token hết hạn) không kiểm tra trực tiếp được | Khi bấm thử trên Expo Web | Giới hạn công cụ | Môi trường test (react-native-web) khác nền tảng thật; AI giả định mọi thông báo đều đọc được từ DOM | Ghi vào báo cáo là hạn chế; cần test lại trên emulator/thiết bị thật nếu có |
| G3 | **Các hành vi riêng của thiết bị thật**: bàn phím số (`keyboardType="numeric"`), xoay màn hình, màn hình nhỏ, chạm nhanh hai lần | Rà phạm vi cuối bước | Giới hạn công cụ | Không có thiết bị/emulator; đề tài nhấn mạnh "Mobile" nhưng môi trường chỉ cho phép web | Ghi rõ chưa test; nếu có emulator thì bổ sung test thao tác chạm nhanh (double tap "Xác Nhận Thanh Toán") và hiển thị trên màn hình nhỏ |
| G4 | **Lỗi múi giờ trong test hạn dùng**: BV-11 lần đầu Fail giả vì AI dựng `expired_at` bằng giờ UTC không có "Z" trong khi server hiểu là giờ địa phương | Kết quả "hết hạn" cho mã còn hạn 1 phút | Giới hạn công cụ | AI không nhận ra khác biệt cách `new Date()` diễn giải chuỗi ngày giờ không có múi giờ | Skill: test phụ thuộc thời gian phải dựng thời điểm theo cùng quy ước múi giờ của hệ thống, ghi múi giờ khi kết luận |
| G5 | **Dữ liệu sót giữa các test UI**: script xóa giỏ làm sai nên giỏ còn sản phẩm cũ; luồng "2 món" thực tế gửi 3 món | Tổng đơn (700,000 thay vì 300,000) và danh sách sản phẩm trên màn hình không khớp dự kiến | Giới hạn công cụ | AI không kiểm tra giỏ rỗng trước mỗi kịch bản và dùng chỉ số mảng thay vì tên sản phẩm | Đã sửa (dựng giỏ theo tên, kiểm tra nội dung giỏ trước khi thanh toán) và chạy lại BV-22 với giỏ sạch; skill đã có quy tắc đối chiếu dữ liệu sinh ra với đầu vào |
| G6 | **Các tình huống chưa thiết kế**: mất kết nối khi thanh toán/áp mã, nhấn "Xác Nhận Thanh Toán" hai lần liên tiếp (đơn trùng), thay đổi giỏ sau khi đã áp mã rồi quay lại | Rà phạm vi cuối bước | Prompt | Spec không nêu; AI bám vào C1..C5 và công thức nên bỏ qua các tình huống vận hành | Ghi nhận chưa test; có thể bổ sung nếu giảng viên cho phép mô phỏng mất kết nối |
| G7 | **Một nguyên nhân gốc làm hàng loạt test Fail**: công thức % sai khiến 8 test (DT-09, 25, 27, 30; BV-03, 18, 19, 20) cùng Fail; lỗi `>` làm BV-02, BV-05 Fail | Tổng hợp kết quả | Độ phức tạp feature | Hai lớp (UI và API) cùng chạy một công thức; thiết kế không tách được test "áp mã" và test "tính tiền" nên một lỗi lan ra nhiều test | Báo cáo có cột Bug nhóm theo nguyên nhân gốc (63 test → 8 bug) |
| G8 | **Lệch giữa spec và dữ liệu seed**: SRS ghi `Admin123!`, `setup_guide.md` ghi `admin123` (đã thử đăng nhập `admin@eshop.com` / `admin123` → 401 "Invalid email or password"; chỉ `Admin123!` đăng nhập được, khớp `database.js`) | Khi đăng nhập Admin để tạo mã | Prompt | Hai tài liệu chính thức mâu thuẫn; AI chọn theo SRS (đã kiểm chứng ở `database.js`) | Ghi nhận trong báo cáo là điểm tài liệu không nhất quán |

## Tóm tắt nguyên nhân
- **Giới hạn công cụ (G1–G5):** môi trường test Mobile không phải thiết bị thật, kèm lỗi script của AI (múi giờ, giỏ hàng).
- **Prompt (G6, G8):** chỉ thiết kế quanh điều kiện và công thức trong spec, bỏ qua tình huống vận hành và tài liệu mâu thuẫn.
- **Độ phức tạp feature (G7):** một lỗi trong công thức lan sang nhiều test.

## Điều AI làm đúng (để đối chiếu)
- Ở Bước 1 AI đoán đúng các lệch chính và đều được xác nhận khi chạy: H1 công thức % âm, H2 `>` thay `>=`, H3 `apply-coupon` không cần token/bỏ qua C5 khi thiếu `user_id`, H5 backend tin `total_amount`, H6 Mobile bỏ mất sản phẩm cuối, H11 `fixed` lớn hơn tổng ra số âm, H14 `API_URL` cứng.
- Dự đoán đúng điều kiện "ngưỡng kiểm tra trước hạn dùng" (H10) và hành vi `category` mặc định không liên quan feature này.
- Nhờ tính expected bằng công thức SRS (thay vì lấy số hệ thống trả) nên phát hiện ngay "Tiết kiệm: -3,600,000 ₫" thay vì coi đó là kết quả bình thường.
