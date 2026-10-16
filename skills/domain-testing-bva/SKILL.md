---
name: domain-testing-bva
description: Áp dụng Domain Testing (phân hoạch tương đương) và Boundary Value Analysis (BVA) cho một feature của hệ thống EShop theo đúng từng bước, dùng AI làm trợ lý có kỷ luật và ghi lại AI Audit Log, AI gap analysis, bug report, commit từng bước. Dùng skill này bất cứ khi nào người dùng nhắc tới domain testing, equivalence partitioning, lớp tương đương, boundary value, giá trị biên, thiết kế test case cho một FR (FR-01..FR-20, Mobile), bài HW02, hoặc muốn test một form/API/state machine có ràng buộc đầu vào, kể cả khi họ không nói rõ tên kỹ thuật.
---

# Domain Testing + BVA cho một feature EShop

Skill này đưa một feature (ví dụ FR-03, FR-10, FR-16, Mobile FR-08/09) đi qua đủ chuỗi: đọc spec → phân tích input → Domain Testing → BVA → chạy test → AI gap analysis → bug report. Mỗi bước là một commit riêng và một mục trong AI Audit Log, vì đề HW02 chấm cả quá trình dùng AI chứ không chỉ kết quả.

## Nguyên tắc nền (và lý do)

- **Spec là oracle, code không phải.** Kết quả mong đợi (expected) luôn lấy từ `README.md` (SRS) của SUT. Code chỉ giúp biết chỗ nào dễ sai. Nếu lấy expected từ code thì bug sẽ trở thành "đúng" và không bao giờ bị phát hiện.
- **Mỗi bước một prompt riêng.** Đề cấm kiểu "sinh test case và tìm bug". AI được dẫn qua từng bước kỹ thuật: liệt kê input → chia lớp → sinh test → biên. Làm vậy vừa đúng đề, vừa dễ review từng bước.
- **Người review, người chịu trách nhiệm.** Sau mỗi output của AI, đối chiếu với spec, sửa, và ghi lại *đã sửa gì*. Nộp output chưa review là không được chấp nhận, và ghi chú sửa chính là bằng chứng review.
- **Ghi lại ngay, không làm bù.** Audit log viết ngay sau mỗi lần dùng AI (dùng `scripts/append_audit.py`), vì làm bù cuối bài luôn thiếu và sai giờ.

## Thư mục làm việc cho mỗi feature

```
features/<FR-ID>/
  01_analysis.md        # spec trích dẫn, input/output, điều kiện, khác biệt spec vs code
  02_domain_testing.md  # bảng lớp tương đương + test case
  03_bva.md             # bảng biên + test case
  04_execution.md       # kết quả chạy, pass/fail, đường dẫn screenshot
  05_ai_gap.md          # AI bỏ sót gì, vì sao
  06_bugs.md            # bug report (đồng bộ với GitHub Issues)
  evidence/             # screenshot, file CSV test, response API
audit/AI_AUDIT_LOG.md   # dùng chung cho mọi feature
```

Tạo thư mục nếu chưa có. Mẫu từng file nằm ở `references/templates.md`; đọc nó trước khi viết file đầu tiên.

## Quy trình

### Bước 0 — Chuẩn bị ngữ cảnh
Đọc `references/eshop-context.md` (cổng, tài khoản, cách gọi API, vị trí spec). Chạy được backend và frontend liên quan trước khi bắt đầu, vì test case phải thực thi được.

### Bước 1 — Phân tích feature (`01_analysis.md`)
1. Trích nguyên văn yêu cầu của feature từ SRS (`README.md`) và API spec. Ghi số dòng/mục để truy vết.
2. Liệt kê **input** (trường form, tham số API, file, hành động), **điều kiện tiền đề** (đã đăng nhập, role, trạng thái dữ liệu) và **output quan sát được** (thông báo, mã HTTP, thay đổi DB/UI).
3. Đọc code backend/frontend của feature, ghi bảng **"Spec vs Code"**: những chỗ code có vẻ lệch spec. Đây chỉ là *giả thuyết cần kiểm chứng*, chưa phải bug.
4. Rà các yêu cầu **liên quan ở mục khác** của SRS (GUI/form như FR-22, bảo mật như SEC-xx) và đưa vào phân tích. Thuộc tính bảo mật như "OTP đủ entropy, có thời hạn" cho ra các test nằm ngoài miền một input (hết hạn, đoán nhiều lần), nên cần nghĩ tới sớm.
5. Prompt AI (1 prompt): đưa trích dẫn spec, nhờ liệt kê input/điều kiện/output. Review, bổ sung cái AI thiếu.

### Bước 2 — Domain Testing (`02_domain_testing.md`)
1. Với mỗi input, chia miền thành **lớp tương đương hợp lệ (V) và không hợp lệ (I)**, đặt mã: `EC-<input>-V1`, `EC-<input>-I1`... Nghĩ về: rỗng/null, sai kiểu, sai định dạng, quá ngắn/dài, ký tự đặc biệt, khoảng trắng, trùng lặp, sai quyền, sai trạng thái.
2. Với feature theo trạng thái (state machine) thì "lớp" là cặp (trạng thái hiện tại × hành động × vai trò); lập bảng chuyển trạng thái đầy đủ rồi đánh dấu hợp lệ/không hợp lệ theo spec.
3. Với feature có nhiều điều kiện độc lập (ví dụ coupon C1..C5) lập bảng quyết định: mỗi điều kiện đúng/sai.
4. Sinh test case: mỗi test hợp lệ phủ nhiều lớp V cùng lúc; **mỗi test không hợp lệ chỉ chứa đúng một lớp I** và các input còn lại hợp lệ, để khi fail biết chắc nguyên nhân (nếu gộp nhiều lỗi, lỗi đầu tiên che các lỗi sau).
5. Có bảng truy vết: mọi lớp được ít nhất một test phủ.
6. Thêm hai nhóm hay bị bỏ sót (bài học từ FR-03):
   - **Request shape** với mọi API: thiếu trường, `null`, sai kiểu (object/số), chuỗi toàn khoảng trắng. Những thứ này không xuất hiện khi chỉ nghĩ "giá trị người dùng gõ".
   - **Lớp suy ra từ gợi ý trong code** (bảng Spec vs Code ở Bước 1): nếu code có dấu hiệu xử lý một lớp mà spec không nói (ví dụ regex đòi khoảng trắng, email phân biệt hoa/thường), vẫn thiết kế test và ghi expected là "quan sát", không phải "bug".
7. Mỗi test ghi **lớp chạy** (UI, API hoặc cả hai). Ràng buộc có thể chỉ có ở UI (client) hoặc chỉ ở API; thiếu ở API là lỗi riêng, vì client không phải đường duy nhất vào hệ thống.
8. Chỉ ghi expected ở mức hành vi mà spec nêu ("từ chối, không đổi dữ liệu"). Chất lượng thông báo lỗi ghi riêng thành quan sát, tránh chấm Pass cho thông báo không đúng loại rồi mới nhận ra expected quá cụ thể.
9. Prompt AI theo thứ tự: (a) chia lớp cho từng input, (b) gộp thành test case theo quy tắc trên. Review và ghi lại phần đã sửa.

### Bước 3 — BVA (`03_bva.md`)
1. Chọn input có thứ tự (số, độ dài, số lượng, thời gian, ngưỡng tiền, số lần). Với mỗi miền ghi rõ min, max theo **spec**.
2. Dùng 3 giá trị tại mỗi biên: `biên-1, biên, biên+1` (tức min−1, min, min+1, max−1, max, max+1 khi áp dụng). Nêu rõ biên nào là đóng/mở (`>=` hay `>`), vì sai lệch `>` so với `>=` là lỗi biên kinh điển.
3. Biên "ẩn" hay bị bỏ sót: độ dài chuỗi (0, 1, max, max+1), số chữ số OTP, ngưỡng tiền `min_order_amount`, hạn dùng (ngày hết hạn, giây khóa), số lượt dùng `count < max`, số dòng CSV (0, 1, nhiều), giá trị âm/0/rất lớn.
4. Mỗi test BVA ghi: giá trị, lớp tương đương nó thuộc về, kết quả mong đợi theo spec.
5. Prompt AI: đưa bảng input + miền từ bước 2, nhờ liệt kê biên và test; review, đặc biệt kiểm tra AI có đoán sai biên (ví dụ lấy từ code thay vì spec).

### Bước 4 — Thực thi (`04_execution.md`)
- Chạy từng test trên hệ thống thật (UI hoặc gọi API bằng curl/Postman). Ghi: actual, Pass/Fail, ngày giờ, đường dẫn screenshot/log trong `evidence/`.
- Test chưa chạy được thì đánh dấu `Not executed` kèm lý do, đừng bỏ trống (README cần số liệu này).
- Test fail ở một chỗ thì suy ra lỗi mới, thêm test case phụ (ghi `added-after-run`) để khoanh vùng.
- **Viết script chạy API có thể lặp lại** (`evidence/run_*.js` hoặc tương đương): gọi HTTP thật, chỉ dùng DB để reset/seed trạng thái và để kiểm chứng dữ liệu có đổi hay không. Seed giá trị mà hệ thống không tự sinh được (ví dụ OTP 6 số khi hệ thống chỉ sinh 4 số) để vẫn kiểm được logic phía sau.
- **Chạy UI trong trình duyệt tích hợp**: gán giá trị input theo cách React nhận biết (`Object.getOwnPropertyDescriptor(HTMLInputElement.prototype,'value').set` rồi `dispatchEvent(new Event('input',{bubbles:true}))`), bấm nút submit thật, và thay `window.alert` bằng bộ ghi để lấy nội dung hộp thoại. Muốn thử validate phía client mà không đổi dữ liệu, dùng một giá trị phụ sai (ví dụ OTP sai) để server từ chối: nếu thấy lỗi của server nghĩa là validate client đã cho qua.
- **Cô lập trạng thái**: test dài (có chờ) dùng user/dữ liệu riêng mà các test khác không reset. Truy vấn kiểm chứng phải loại trừ dữ liệu của test khác (một lần DT-06 báo Fail giả vì lẫn token của test khác).
- **Test phụ thuộc thời gian**: ghi thời điểm cấp và thời điểm dùng, in ra số phút đã trôi qua *trước khi* kết luận. Một lần chạy sau ~12 giây đã bị kết luận sai, phải bỏ và chạy lại.
- **Kết quả theo lớp**: ghi riêng cột UI và API cho mỗi test; kết quả tổng là Fail nếu bất kỳ lớp nào lệch spec. Một lỗi ở lớp UI có thể làm hàng loạt test "hợp lệ" Fail, nên luôn có cột Bug để nhóm theo nguyên nhân gốc (FR-03: 40 test fail nhưng chỉ 10 bug).
- Screenshot công cụ trình duyệt nằm trong thư mục `tool-results` của phiên; copy vào `evidence/` ngay để commit được.

### Bước 5 — AI gap analysis (`05_ai_gap.md`)
So danh sách AI sinh ra ban đầu với danh sách cuối cùng sau review/chạy thật. Mỗi test case hoặc bug **AI bỏ sót**, ghi: nó là gì, nguyên nhân thuộc nhóm nào:
- **Prompt**: mình đưa thiếu ngữ cảnh/không nêu ràng buộc.
- **Giới hạn công cụ**: AI không thấy hành vi thật, bịa biên, sai kiểu dữ liệu.
- **Độ phức tạp của feature**: tương tác nhiều điều kiện, trạng thái, tác dụng phụ.
Và nêu cách đã khắc phục (prompt sửa lại thế nào). Đây là phần chứng minh mức G9.3 (Analyse), nên cụ thể quan trọng hơn dài.

### Bước 6 — Bug report (`06_bugs.md` + GitHub Issues)
- Mỗi bug dùng mẫu trong `references/templates.md`: tiêu đề, feature, mức độ, các bước tái hiện, expected (trích spec), actual, môi trường, screenshot.
- Sinh sẵn nội dung issue: `python skills/domain-testing-bva/scripts/make_issue_bodies.py --bugs features/<FR>/06_bugs.md --out features/<FR>/issues --raw-base https://raw.githubusercontent.com/<owner>/<repo>/main/features/<FR>` (ảnh trong `evidence/` được nhúng bằng đường dẫn raw nên cần push trước).
- **Đăng issue là hành động công khai: chỉ làm sau khi người dùng đồng ý.** Lệnh mẫu có trong docstring của script (`gh issue create ... --label bug`). `gh` không đính kèm ảnh trực tiếp, nên dùng đường dẫn raw hoặc kéo-thả ảnh trên giao diện web của issue.
- Mục "Quan sát" ở cuối `06_bugs.md` dành cho thứ spec không yêu cầu (ví dụ không giới hạn số lần đoán OTP); không tính vào số bug.
- Ghi số issue (#n) vào `06_bugs.md`.
- Một bug là bug khi có **expected từ spec** làm chứng. Nếu spec không nói, ghi là "quan sát/đề xuất", không gọi là lỗi.

### Bước 7 — Commit theo bước
Một commit mỗi bước, thông điệp dạng `<FR-ID>: step N - <tên bước>`, ví dụ `FR-03: step 2 - domain testing classes and cases`. Chỉ `git add` đúng thư mục `features/<FR-ID>/` và `audit/`, không `git add .`, vì `backend/database.sqlite` đổi mỗi lần chạy server. Cuối cùng xuất log: `git log --pretty=format:"%h | %ad | %s" --date=iso > git_commit_log.txt`.

### Bước 8 — Số liệu cho README
Sau mỗi feature, cập nhật số: test case thiết kế / đã chạy / pass / fail / chưa chạy / số bug. Tổng hợp qua các feature để điền README nộp bài.

## Audit log (dùng sau MỖI lần gọi AI)

```
python skills/domain-testing-bva/scripts/append_audit.py \
  --log audit/AI_AUDIT_LOG.md --tool "Claude Code (Sonnet 5.5)" \
  --feature FR-03 --step "02 Domain testing" \
  --prompt-file prompt.txt --output-file output.txt \
  --review "Đã sửa: OTP là 6 số theo spec, AI lấy 4 số từ code"
```

Mục `--review` bắt buộc điền: ghi *bạn đã chỉnh gì* (hoặc "không cần sửa" kèm lý do). Nếu đang ở trong Claude Code, ghi prompt và output thực tế của bước đó.

## Nhật ký cải tiến skill

Skill này được chỉnh dần khi làm các feature thật. Sau mỗi feature, thêm một dòng vào đây: điều gì không hiệu quả và đã sửa gì trong skill.

| Sau feature | Phát hiện | Đã chỉnh |
|---|---|---|
| FR-03 | Thiết kế đầu tiên bỏ sót request shape, lớp suy ra từ code, thuộc tính bảo mật (đoán OTP nhiều lần, hết hạn) | Thêm mục 4 ở Bước 1 và mục 6–8 ở Bước 2 |
| FR-03 | Script test có lỗi trạng thái dùng chung (DT-06) và kết luận hết hạn quá sớm (DT-15) | Thêm quy tắc cô lập trạng thái và test phụ thuộc thời gian ở Bước 4 |
| FR-03 | Số test Fail (40) lớn hơn nhiều số bug (10) vì hai lớp UI/API cùng ràng buộc | Thêm kết quả theo lớp và cột Bug ở Bước 4; thêm `make_issue_bodies.py` ở Bước 6 |
