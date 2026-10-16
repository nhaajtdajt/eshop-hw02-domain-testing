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
