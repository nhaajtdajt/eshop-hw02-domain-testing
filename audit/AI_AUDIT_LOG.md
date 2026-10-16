# AI Audit Log

I use AI tools for the following tasks.

---

## Entry 001 — FR-03 — 01 Analysis

- **AI tool:** Claude Code (Sonnet 5.5, claude-sonnet-5-5)
- **Date/time:** 2026-10-16 13:23:49
- **Human review / changes:** Đối chiếu từng giả thuyết với README.md và code thật (ForgotPassword.jsx, server.js). Đánh dấu H13/H15 là 'cần thử' vì chưa chắc; H14/H18 là ngoài phạm vi FR-03 nên chỉ ghi chú. Tất cả giả thuyết còn 'chưa kiểm chứng' cho tới Bước 4. (Người dùng chưa đọc lại bản phân tích này tại thời điểm ghi log.)

**Prompt**

~~~text
User instruction (verbatim, Vietnamese): "Dùng skill domain-testing-bva làm FR-03 từ Bước 1, ghi audit log và commit từng bước."
Step prompt per skill (Step 1 - Analysis): Given SRS README.md lines 46-60 (FR-03), 250-256 (FR-22), 284 (SEC-07), api_specification.md section 1.3-1.4, backend/server.js:68-98 and frontend-web/src/pages/ForgotPassword.jsx: (1) quote the spec requirements, (2) list inputs / preconditions / outputs, (3) build a "Spec vs Code" hypotheses table. Spec is the oracle, code is only used to locate suspected deviations.
~~~

**AI output**

~~~text
Produced features/FR-03/01_analysis.md: quoted spec for FR-03/FR-01/FR-22/SEC-07; input table (email, otp, newPassword, confirmPassword, state); 18 Spec-vs-Code hypotheses, main ones: H1 OTP is 4 digits (server.js:72) vs spec 6; H3 regex requires whitespace and forbids special chars (ForgotPassword.jsx:26); H4 no confirm-password field; H5 no step indicator; H6 no 'back to login'; H7 email input type=text; H9 no OTP expiry; H11 backend does not validate new password; H14 404 reveals unknown emails. Noted spec gap: OTP lifetime not quantified in SRS.
~~~

---

## Entry 002 — FR-03 — 02 Domain testing

- **AI tool:** Claude Code (Sonnet 5.5, claude-sonnet-5-5)
- **Date/time:** 2026-10-16 13:24:52
- **Human review / changes:** Đối chiếu từng expected với SRS: không lấy expected từ code (ví dụ OTP là 6 số theo spec chứ không phải 4 như code). Gắn nhãn EC-pw-I7 ('#') là diễn giải chặt vì FR-01 liệt kê tập ký tự. Thêm DT-13 (OTP của email khác), DT-14 (dùng lại OTP), DT-15 (hết hạn) vì SRS/SEC-07 nêu rõ. Gom GUI thành nhóm riêng vì FR-22 yêu cầu.

**Prompt**

~~~text
Step prompt per skill (Step 2 - Domain Testing), input = features/FR-03/01_analysis.md + SRS FR-03/FR-01/FR-22/SEC-07:
(a) For each input (email, otp, newPassword, confirmPassword) and for GUI requirements, partition the domain into valid and invalid equivalence classes with codes EC-<input>-V<n>/I<n>.
(b) Combine into test cases: valid tests cover many valid classes at once; every invalid test contains exactly ONE invalid class with all other inputs valid. Expected results come from the SRS, not from code. Mark whether each test runs on UI, API or both. Add a class->test traceability table.
~~~

**AI output**

~~~text
Produced features/FR-03/02_domain_testing.md: classes email(1 valid+5 invalid), otp(1+8: empty, <6, >6, non-digit, wrong value, other email's OTP, already used, expired), newPassword(1+7 following FR-01), confirmPassword(1+3), GUI(7). 32 test cases FR03-DT-01..32 with expected results from SRS, layer (UI/API), traceability table; limitations: OTP lifetime not quantified in SRS, confirm-password tests UI-only, '#' special char is an interpretation issue.
~~~

---

## Entry 003 — FR-03 — 03 BVA

- **AI tool:** Claude Code (Sonnet 5.5, claude-sonnet-5-5)
- **Date/time:** 2026-10-16 13:26:07
- **Human review / changes:** Biên lấy từ spec: OTP 5/6/7 (không phải 3/4/5 theo code). Đánh dấu rõ 'không có biên' cho thời hạn OTP và độ dài email thay vì tự bịa số. Thêm biên giá trị số 0 đầu và hàng xóm ASCII của tập ký tự đặc biệt (BV-24/25). BV-12 (256 ký tự) chỉ là khám phá vì spec không nêu tối đa. Chuyển OTP boundary sang API + token seed vì UI không đặt được OTP 6 số.

**Prompt**

~~~text
Step prompt per skill (Step 3 - BVA), input = features/FR-03/02_domain_testing.md + SRS FR-03/FR-01/SEC-07:
Identify every ordered input/quantity with a numeric or length boundary according to the SRS (not the code), state whether each boundary is closed or open (>= vs >), and design 3-value tests (boundary-1, boundary, boundary+1) plus useful extremes. Mark quantities where the SRS gives no number (OTP lifetime, email length) instead of inventing boundaries. Avoid duplicating Domain Testing cases; cross-reference them.
~~~

**AI output**

~~~text
Produced features/FR-03/03_bva.md: boundary table (OTP length 5/6/7 + extremes, leading-zero OTP, generated OTP length, password length 7/8/9/256, min count per character class, membership of the 7 special characters + ASCII neighbours '+' and '"', confirm-password n-1/n/n+1, OTP usage count). 28 test cases FR03-BV-01..28; cross-references to DT cases; 60 designed tests total for FR-03; limits: no numeric boundary for OTP lifetime/email length; OTP boundary tests need seeded token because real system issues 4-digit OTP.
~~~

---

## Entry 004 — FR-03 — 04 Execution

- **AI tool:** Claude Code (Sonnet 5.5, claude-sonnet-5-5)
- **Date/time:** 2026-10-16 13:33:59
- **Human review / changes:** Sửa 2 lỗi do chính test của mình: (1) DT-06 báo Fail giả vì user C (test hết hạn) có reset_token → loại user C khỏi truy vấn rồi chạy lại; (2) lần chạy DT-15 đầu tiên chỉ chờ ~12 giây nên Fail không có ý nghĩa → bỏ và chạy lại với 5,5 phút. Kết quả test mật khẩu trên UI dùng OTP sai để không làm đổi dữ liệu. Tất cả kết quả đã đối chiếu với spec, không dùng code làm expected.

**Prompt**

~~~text
Step prompt per skill (Step 4 - Execution): Execute the 60 designed FR-03 test cases on the real EShop. API layer: write a repeatable script (HTTP requests to localhost:3000, DB used only to reset/seed state and to verify whether the password changed). UI layer: drive the real /forgot-password form in the browser (real React handlers, alert() captured). Record per test: UI result, API result, overall Pass/Fail (Fail if any layer deviates from the SRS), actual behaviour, bug reference. Save evidence (script, raw JSON, screenshots) under features/FR-03/evidence.
~~~

**AI output**

~~~text
evidence/run_api_tests.js + api_results.json (45 API checks: 33 pass / 12 fail); UI harness run in browser; 04_execution.md with per-test table. Totals: 60 designed, 60 executed, 20 pass, 40 fail, 10 distinct bugs. Key actuals: OTP is 4 digits (e.g. 4543); UI password regex rejects every spec-valid password and only accepts one with a space; backend reset-password accepts empty/weak passwords; no confirm field, no step indicator, no 'back to login', email type=text, no '*', errors via alert(); OTP still valid after 5.5 min; 4 extra exploratory API checks found nothing new. The first expiry run (12 s after issuing) was discarded as invalid and rerun with a 5.5 minute wait.
~~~

---

## Entry 005 — FR-03 — 05 AI gap analysis

- **AI tool:** Claude Code (Sonnet 5.5, claude-sonnet-5-5)
- **Date/time:** 2026-10-16 13:35:46
- **Human review / changes:** Phân tích gap do cùng AI tự đánh giá nên có nguy cơ thiên vị; đã bám bằng chứng cụ thể (X-05..X-07, log DT-06/DT-15) thay vì nhận xét chung. Người dùng cần đọc lại và bổ sung/phản biện các nhóm nguyên nhân trước khi nộp.

**Prompt**

~~~text
Step prompt per skill (Step 5 - AI gap analysis): Compare the first-pass test design produced by the AI in steps 1-3 with the final set after execution. List every test case, bug or check that the AI missed or got wrong, how it was discovered, which cause group applies (Prompt / Tool limitation / Feature complexity), why, and how the skill or prompt should change. Be specific; also say what the AI got right.
~~~

**AI output**

~~~text
05_ai_gap.md with 7 gaps: G1 request-shape tests missing; G2 no OTP guess limiting (300 wrong guesses all 400); G3 email normalisation (case-sensitive); G4 password-with-whitespace class not derived from code hint; G5 over-specific expected for DT-03 and lenient grading; G6 many failing tests share one root cause (40 failing tests vs 10 bugs); G7 test-script errors (shared state false fail on DT-06; premature DT-15). Added exploratory X-05..X-07 to 04_execution.md. Lessons to feed back into the skill.
~~~

---

## Entry 006 — FR-03 — 06 Bug report

- **AI tool:** Claude Code (Sonnet 5.5, claude-sonnet-5-5)
- **Date/time:** 2026-10-16 13:36:49
- **Human review / changes:** Mức độ nghiêm trọng là đánh giá của AI, người dùng nên xác nhận lại (đặc biệt BUG-02 Critical vs Major). Chưa có screenshot của hộp thoại alert() vì harness thay alert bằng bộ ghi; bằng chứng cho BUG-02/03/09 là log JSON và code. Cần chụp lại bằng tay nếu muốn ảnh trước khi đăng issue.

**Prompt**

~~~text
Step prompt per skill (Step 6 - Bug report): Group the 40 failing FR-03 tests by root cause and write one bug per root cause using the template: title, feature, severity, steps to reproduce, expected (quote SRS line numbers), actual, evidence paths, code location. Keep observations that the SRS does not require (no rate limit, email enumeration, case sensitivity) out of the bug list. Generate one GitHub-issue body file per bug but do NOT publish them.
~~~

**AI output**

~~~text
06_bugs.md with 10 bugs: BUG-01 OTP 4 digits (Major); BUG-02 UI regex rejects all spec-valid passwords (Critical); BUG-03 backend accepts empty/weak passwords (Major); BUG-04 no confirm-password field (Major); BUG-05 no step indicator; BUG-06 no back-to-login; BUG-07 email type=text; BUG-08 no required asterisks; BUG-09 errors via alert(); BUG-10 OTP never expires (Major). Plus an observations list. Added scripts/make_issue_bodies.py to the skill and generated features/FR-03/issues/BUG-01..10.md. GitHub issues NOT created yet.
~~~

---

## Entry 007 — FR-10 — 01 Analysis

- **AI tool:** Claude Code (Sonnet 5.5, claude-sonnet-5-5)
- **Date/time:** 2026-10-16 13:58:59
- **Human review / changes:** Đối chiếu sơ đồ spec với code từng nhánh if (server.js:537-551). Ghi rõ điểm mơ hồ 'chỉ Admin mới có thể thao tác' ở shipping và chọn diễn giải chặt. Loại Mobile khỏi phạm vi vì là feature của thành viên khác. H14/H15 là ngoài phạm vi nên chỉ ghi chú. Mọi giả thuyết còn 'chưa kiểm chứng' đến Bước 4. (Người dùng chưa đọc lại tại thời điểm ghi log.)

**Prompt**

~~~text
User instruction (verbatim, Vietnamese): "Làm FR-10 (máy trạng thái đơn hàng) bằng skill domain-testing-bva từ Bước 1, ghi audit log và commit từng bước."
Step prompt per skill (Step 1 - Analysis): Given SRS README.md FR-10 (lines 141-162), FR-12, FR-18, FR-21, SEC-03, api_specification.md 4.6 and 6.2, backend/server.js:100-110, 311-349, 525-568, frontend-admin App.jsx order tab and frontend-web Profile.jsx cancel button: quote the spec, list inputs/preconditions/outputs, note ambiguities, and build a Spec vs Code hypotheses table. Spec is the oracle; code only locates suspected deviations.
~~~

**AI output**

~~~text
features/FR-10/01_analysis.md: spec quotes, ambiguity notes (admin cancel from shipping not in diagram), input/output table, 15 Spec-vs-Code hypotheses: H1 canceled->delivered allowed (server.js:550) and admin UI button for it (App.jsx:862); H3 user can cancel shipping orders (server.js:329); H4 web Profile shows cancel for shipping (Profile.jsx:200); H5 admin status API has no role check (SEC-03/FR-12); H7/H13 English error text shown in UI; H14/H15 are out-of-scope notes (FR-11/FR-18). Mobile cancel excluded (belongs to another member). Test design hints: 25-cell state matrix, boundary kinds for a non-numeric domain.
~~~

---
