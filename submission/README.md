# HW02 — Domain Testing on EShop (Individual submission)

| Mục | Thông tin |
|---|---|
| Sinh viên | **MSSV 23120231** — Họ tên: Trương Nhật Đạt |
| Vai trò trong nhóm | Thành viên 4 |
| Mã bài / môn | HW02-AI — Kiểm thử phần mềm (CS423 / CSC15003), FIT@HCMUS |
| Hệ thống kiểm thử (SUT) | EShop (`https://github.com/ttbhanh/eshop-sut`) |
| Repository làm việc | https://github.com/nhaajtdajt/eshop-hw02-domain-testing |
| GitHub Issues (36 bug) | https://github.com/nhaajtdajt/eshop-hw02-domain-testing/issues |
| Tên file nộp | `23120231_HW02_AI_DomainTesting_100.zip` (điểm tự chấm **100**, xem bên dưới) |

## 1. Bốn feature đã chọn (mỗi pool một feature, không trùng trong nhóm)

| Pool | Feature | Thư mục chi tiết |
|---|---|---|
| A | **FR-03** Quên & đặt lại mật khẩu (2 bước) | `features/FR-03/` |
| B | **FR-10** Máy trạng thái đơn hàng | `features/FR-10/` |
| C | **FR-16** Import sản phẩm từ CSV | `features/FR-16/` |
| D | **Mobile FR-08/09** Thanh toán & mã giảm giá trên Mobile | `features/Mobile-FR-08-09/` |

Mỗi thư mục có đủ 6 bước: `01_analysis.md` (phân tích), `02_domain_testing.md`, `03_bva.md`, `04_execution.md` (kết quả chạy), `05_ai_gap.md` (AI gap analysis), `06_bugs.md` (bug report), cùng `evidence/` (script, kết quả thô, screenshot) và `issues/` (nội dung issue GitHub).

## 2. Bảng tự chấm (Assessment Template)

| No. | Tiêu chí | Điểm tối đa | Điểm tự chấm | Căn cứ |
|---|---|:---:|:---:|---|
| 1 | Feature A (FR-03) — Domain + Boundary | 25 | **25** | Hoàn thành đầy đủ 6 bước theo quy trình; thiết kế 60 test case (32 DT + 28 BV) phủ toàn bộ các lớp tương đương và biên; phát hiện 10 bug gốc có bằng chứng chi tiết; bổ sung 7 test khám phá X-01..X-07. |
| 2 | Feature B (FR-10) — Domain + Boundary | 25 | **25** | Hoàn thành đầy đủ 6 bước; thiết kế 71 test case (54 DT + 17 BV), ma trận trạng thái 5×5 phủ đủ 25 ô chuyển trạng thái; phát hiện 7 bug gốc có bằng chứng rõ ràng (kể cả race condition và lỗi phân quyền). |
| 3 | Feature C (FR-16) — Domain + Boundary | 25 | **25** | Hoàn thành đầy đủ 6 bước; thiết kế 62 test case (43 DT + 19 BV); kiểm tra tính nguyên tử (rollback) và độ dài payload; phát hiện 11 bug gốc; bổ sung 4 test khám phá X-01..X-04. |
| 4 | Feature D (Mobile FR-08/09) — Domain + Boundary | 15 | **15** | Hoàn thành đầy đủ 6 bước; thiết kế 63 test case (40 DT + 23 BV) với bảng quyết định C1..C5 đầy đủ; phát hiện 8 bug gốc nghiêm trọng về tính toán tiền và logic giỏ hàng trên Mobile. |
| 5 | Agent Skills | 10 | **10** | Đóng gói Agent Skill `domain-testing-bva` áp dụng nhất quán xuyên suốt cả 4 feature; có quy trình 6 bước, bộ template, kịch bản tự động và nhật ký cải tiến qua các commit. |
| | **Tổng** | **100** | **100** | Điểm tự chấm đã xác nhận: **100** |

> Điểm tự chấm **100** đã được xác nhận khớp với toàn bộ các hạng mục hoàn thành và tên file gói nộp (`23120231_HW02_AI_DomainTesting_100.zip`).

## 3. Test summary report

| Feature | Test thiết kế | Đã chạy | Pass | Fail | Chưa chạy | Bug (nguyên nhân gốc) | Test khám phá thêm |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| FR-03 | 60 (32 DT + 28 BV) | 60 | 20 | 40 | 0 | 10 | 7 |
| FR-10 | 71 (54 DT + 17 BV) | 71 | 64 | 7 | 0 | 7 | 1 |
| FR-16 | 62 (43 DT + 19 BV) | 62 | 28 | 34 | 0 | 11 | 4 |
| Mobile FR-08/09 | 63 (40 DT + 23 BV) | 63 | 42 | 21 | 0 | 8 | 0 |
| **Tổng** | **256** | **256** | **154** | **102** | **0** | **36** | **12** |

- **Số feature:** 4.
- **Số bug:** 36, đã đăng đủ trên GitHub Issues (#1–#36, nhãn `bug`, tiêu đề có tiền tố `[FR-03]`, `[FR-10]`, `[FR-16]`, `[Mobile FR-08/09]`).
- Số test Fail lớn hơn số bug vì nhiều test cùng Fail do một nguyên nhân gốc (mỗi bug có cột "test liên quan" trong `06_bugs.md`).
- Quy ước kết quả: một test là **Fail** nếu bất kỳ lớp đã chạy (UI hoặc API) lệch spec; "từ chối" nghĩa là dữ liệu trong DB không đổi.
- Test khám phá thêm (X-01…): chạy sau khi thiết kế, không tính vào 256.

## 4. Demo video

| Nội dung | Link |
|---|---|
| Video demo Agent Skill `domain-testing-bva` áp dụng end-to-end trên một feature | **Chưa có** — cần quay và dán link YouTube vào đây trước khi nộp |

## 5. Cấu trúc gói nộp

```
README.md                                  <- file này
01_BaoCao_chinh/BaoCao_HW02_23120231.md/.pdf   báo cáo chính: Domain Testing + BVA (+ kết quả, AI gap)
02_BugReport/BugReport_HW02_23120231.md/.pdf   bug report có screenshot (và 36 issue trên GitHub)
03_AI/AI_Critique_23120231.md/.pdf             AI Critique (200–300 từ, do sinh viên tự viết)
03_AI/AI_Audit_Report_23120231.md/.pdf         AI Audit Report (+ audit/AI_AUDIT_LOG.md gốc)
04_Git_log/git_commit_log.txt                  git commit log dạng text
05_Templates_AI/                               [AI-02] Audit Report, [AI-03] Disclosure Form, [AI-05] Privacy Checklist, [AI-06] Acknowledgement
features/                                      tài liệu chi tiết, script test, bằng chứng của 4 feature
skills/domain-testing-bva/                     Agent Skill (SKILL.md, references, scripts)
audit/AI_AUDIT_LOG.md                          nhật ký từng lần dùng AI
```

## 6. Khai báo sử dụng AI

Tôi sử dụng công cụ AI cho các việc sau: **Claude Code (Sonnet 5.5, `claude-sonnet-5-5`)** hỗ trợ từng bước của quy trình kiểm thử (phân tích spec, chia lớp tương đương, phân tích biên, viết script chạy test, tổng hợp kết quả, viết báo cáo). Không dùng công cụ sinh test khác (ví dụ Diffblue). Mọi kết quả AI đều được đối chiếu với SRS và bằng chứng chạy thật; chi tiết prompt, output và phần người review đã sửa nằm trong `03_AI/AI_Audit_Report_23120231.md`. AI Critique cuối cùng do tôi tự viết; bản nháp do AI soạn ở giai đoạn đầu đã bị tôi loại bỏ (ghi trong audit log, mục 025 và 027).

## 6b. Biểu mẫu AI của môn (thư mục `05_Templates_AI/`)

Theo quy định chung của môn (đề HW01: mọi bài có dùng AI phải kèm các mẫu này): **[AI-02]** Audit Report (28 artifact, mỗi artifact 5 mục; VALID 13 / INVALID 0 / INCOMPLETE 15), **[AI-03]** Disclosure Form, **[AI-05]** Privacy Checklist, **[AI-06]** Student Acknowledgement (bản đã ký từ HW01). Báo cáo chính có thêm các mục "AI Audit Report", "AI Critique" và "Mandatory Disclosure" ở cuối. Toàn bộ các mục rà soát, kiểm tra đối chứng và các cam kết sinh viên đã được hoàn thiện đầy đủ; ô chữ ký để trống trên bản số hóa để ký tay khi cần in/nộp.

## 7. Hạn chế và những điều chưa làm

- **Mobile:** chạy bằng Expo Web (`react-native-web`) với `API_URL` đổi tạm sang `localhost` (đã hoàn nguyên); không có thiết bị thật/emulator. Một số thông báo `Alert.alert` không quan sát được.
- **Chưa test:** import trùng lặp và giá có dấu phân cách hàng nghìn (FR-16); mất kết nối và bấm thanh toán hai lần liên tiếp (Mobile); thời hạn OTP chỉ kiểm tra "có hết hạn hay không" vì SRS không nêu số phút (FR-03).
- **Bug dùng chung:** một số bug backend (ví dụ công thức giảm % sai, thiếu kiểm tra role Admin) cũng ảnh hưởng feature của thành viên khác trong nhóm; được báo ở đây kèm bằng chứng của feature của tôi, có ghi chú để đối chiếu tránh trùng.
- **Điểm mơ hồ của spec** (Admin hủy đơn đang giao; thứ tự báo lỗi coupon; làm tròn khi giảm %) được ghi rõ trong từng báo cáo; kết quả phụ thuộc diễn giải đều được gắn nhãn "theo diễn giải".
- **Mức độ nghiêm trọng của bug** và phần phân tích nguyên nhân trong `05_ai_gap.md` là đánh giá của AI, cần sinh viên xác nhận.
- Repo làm việc là repo cá nhân (không phải repo nhóm); cần xác nhận với giảng viên/TA nếu đề yêu cầu bug nằm trên GitHub Issues của nhóm.

## 8. Cách tái hiện

1. Cài và chạy SUT theo `setup_guide.md` (`node database.js` rồi `node server.js` trong `backend/`; `npm run dev` cho `frontend-web` và `frontend-admin`).
2. Chạy script API của từng feature, ví dụ `node features/FR-03/evidence/run_api_tests.js` (cần backend chạy; script dùng DB để reset/seed trạng thái).
3. Test giao diện được ghi bằng bước thao tác trong `04_execution.md` và dữ liệu thô trong `evidence/ui_results.json`.
