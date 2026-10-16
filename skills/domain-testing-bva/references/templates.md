# Mẫu tài liệu cho skill domain-testing-bva

Dùng đúng các cột này để kết quả giữa các feature đồng nhất và dễ tổng hợp số liệu.

## 01_analysis.md

```markdown
# <FR-ID>: <Tên feature> — Phân tích

## 1. Yêu cầu theo SRS (trích nguyên văn)
> (trích dẫn, ghi rõ README.md mục/dòng)

## 2. Input / Điều kiện / Output
| Loại | Tên | Mô tả | Ràng buộc theo spec |
|---|---|---|---|
| Input | otp | mã xác thực | đúng 6 chữ số |
| Precondition | ... | | |
| Output | ... | | |

## 3. Spec vs Code (giả thuyết cần kiểm chứng)
| # | Spec nói | Code làm | File:dòng | Trạng thái |
|---|---|---|---|---|
| H1 | OTP 6 số | sinh 4 số | server.js:72 | chưa kiểm chứng |
```

## 02_domain_testing.md

```markdown
## Lớp tương đương
| Mã lớp | Input | Loại | Mô tả lớp | Ví dụ đại diện |
|---|---|---|---|---|
| EC-otp-V1 | otp | Hợp lệ | đúng 6 chữ số, khớp email | 123456 |
| EC-otp-I1 | otp | Không hợp lệ | 5 chữ số | 12345 |

## Test case
| TC ID | Lớp phủ | Điều kiện tiền đề | Dữ liệu vào | Expected (theo spec) | Truy vết |
|---|---|---|---|---|---|
| FR03-DT-01 | EC-email-V1, EC-otp-V1 | ... | ... | ... | README FR-03 |

## Truy vết lớp → test
| Mã lớp | Test phủ |
|---|---|
```

Quy ước: mỗi test không hợp lệ chỉ chứa **một** lớp I, input còn lại hợp lệ.

## 03_bva.md

```markdown
## Bảng biên
| Input | Miền theo spec | Biên | Đóng/Mở | Giá trị kiểm thử |
|---|---|---|---|---|
| độ dài OTP | = 6 | 6 | đóng | 5, 6, 7 |

## Test case
| TC ID | Input | Giá trị | Vị trí so với biên | Lớp | Expected (theo spec) |
|---|---|---|---|---|---|
| FR03-BV-01 | otp | 12345 | min-1 | EC-otp-I1 | báo lỗi |
```

## 04_execution.md

```markdown
| TC ID | Ngày giờ chạy | Môi trường (web/admin/mobile/API) | Actual | Kết quả | Evidence | Bug |
|---|---|---|---|---|---|---|
| FR03-DT-01 | 2026-10-17 09:30 | web | ... | Pass/Fail/Not executed | evidence/tc01.png | #3 |
```

Cuối file: tổng số thiết kế / đã chạy / pass / fail / chưa chạy.

## 05_ai_gap.md

```markdown
| # | Thứ AI bỏ sót (test case / bug) | Phát hiện bằng cách nào | Nhóm nguyên nhân | Giải thích | Cách khắc phục |
|---|---|---|---|---|---|
| G1 | Biên OTP 7 chữ số | review | Prompt | không nêu spec OTP là cố định 6 | thêm trích dẫn spec vào prompt |
```

Nhóm nguyên nhân: `Prompt` | `Giới hạn công cụ` | `Độ phức tạp feature`.

## 06_bugs.md và nội dung GitHub issue

```markdown
### BUG-<FR-ID>-01: <tiêu đề ngắn, nêu hiện tượng>
- **Issue:** #<số>
- **Feature:** <FR-ID>
- **Mức độ:** Critical | Major | Minor
- **Môi trường:** Web http://localhost:5173 / Chrome <ver> / Windows 11
- **Test case liên quan:** FR03-BV-01
- **Các bước tái hiện:**
  1. ...
- **Expected (SRS <mục>):** ...
- **Actual:** ...
- **Screenshot:** ![](evidence/bug01.png)
```

Lệnh tạo issue:
```bash
gh issue create --repo <owner>/<repo> --title "[FR-03] OTP chỉ có 4 chữ số" \
  --label bug --body-file features/FR-03/evidence/bug01_body.md
```

## Commit message
`<FR-ID>: step <N> - <tên bước>` với N: 1 phân tích, 2 domain testing, 3 BVA, 4 thực thi, 5 AI gap, 6 bug report.
