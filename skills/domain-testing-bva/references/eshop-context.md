# Ngữ cảnh SUT EShop (đọc ở Bước 0)

## Nguồn sự thật
- **SRS (oracle cho expected):** `README.md` ở thư mục gốc `eshop-sut`. Các mục: FR-01..FR-21.
- **API:** `api_specification.md`. Chú ý: tài liệu này có thể lệch SRS (ví dụ ví dụ OTP `123456`), SRS vẫn là chuẩn.
- **Code backend:** `backend/server.js` (Express + SQLite, `database.js` tạo và seed DB).
- **Web user:** `frontend-web/src/pages/*.jsx`. **Admin:** `frontend-admin/src/App.jsx`. **Mobile:** `frontend-mobile/App.js` (một file).

## Chạy hệ thống
| Thành phần | Lệnh (trong thư mục tương ứng) | URL |
|---|---|---|
| Backend | `node database.js` (reset + seed) rồi `node server.js` | http://localhost:3000 |
| Web | `npm run dev` | http://localhost:5173 |
| Admin | `npm run dev` | http://localhost:5174 |
| Mobile | `npx expo start` (hoặc `--web`) | cần `API_URL` trong App.js trỏ đúng backend |

`node database.js` **xóa và seed lại** dữ liệu; chạy trước mỗi lượt test cần dữ liệu sạch (ví dụ coupon đã dùng, trạng thái đơn).

## Tài khoản
- SRS ghi: Admin `admin@eshop.com` / `Admin123!`; User `test@eshop.com` / `Test1234!`.
- `setup_guide.md` ghi admin mật khẩu `admin123`. Thử cả hai, ghi lại cái nào đúng (có thể là một phát hiện).

## Coupon mẫu (SRS FR-09)
SAVE10 (percent 10%, min 300,000, 1 lần), BIGBUY (fixed 50,000, min 500,000, 1 lần), VIP100 (fixed 100,000, min 300,000, 2 lần), EXPIRED (percent 20%, hết hạn 2020-01-01).

## Gọi API nhanh (curl)
```bash
# đăng nhập lấy token
curl -s -X POST localhost:3000/api/login -H "Content-Type: application/json" \
  -d '{"email":"test@eshop.com","password":"Test1234!"}'
# gọi API có xác thực
curl -s localhost:3000/api/orders/my-orders -H "Authorization: Bearer <token>"
```
Trên Windows PowerShell dùng `curl.exe` và escape dấu nháy kép, hoặc gọi trong Git Bash.

## Lưu ý khi test
- Ràng buộc chỉ có ở UI (client-side) có thể bị bỏ qua khi gọi API trực tiếp: test cả hai lớp, vì đề tập trung validate dữ liệu.
- `backend/database.sqlite` nằm trong git và đổi mỗi lần chạy; đừng commit nó cùng bài.
- Hệ thống CỐ Ý chứa bug (UI, validation, bảo mật, logic nghiệp vụ). Bug thuộc feature của người khác trong nhóm thì ghi chú, đừng tính vào số bug của mình.
