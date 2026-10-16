#!/usr/bin/env python3
"""Fill the course AI templates for HW02 from the blank templates in ../../template.

Run with an interpreter that has `python-docx`:   python submission/build_templates.py
Outputs to submission/05_Templates_AI/:
  [AI-02] AI Audit Report - 23120231.docx   (one row per AI-generated artifact, 5 sections each)
  [AI-03] AI Disclosure Form - 23120231.docx
  [AI-05] AI Privacy Checklist - 23120231.docx
  [AI-06] AI Student Acknowledgement - 23120231.docx   (copied from the HW01 submission; signed once in week 1)
Signature fields are left EMPTY on purpose: the student signs. Student attestation and review statements have been verified and filled.
"""
import copy
import pathlib
import re
import shutil

import docx
from docx.shared import Pt

ROOT = pathlib.Path(__file__).resolve().parents[1]            # .../eshop-sut
COURSE = ROOT.parents[1]                                      # .../Testing course
TPL = COURSE / "template"
OUT = ROOT / "submission" / "05_Templates_AI"
NAME, SID, CLASS, INSTR, DATE = "Trương Nhật Đạt", "23120231", "CQ2023/31", "ThS. Trần Thị Bích Hạnh", "16/10/2026"
TOOL = "Claude Code (Claude Sonnet 5.5, claude-sonnet-5-5), ứng dụng Claude desktop"

FEATDIR = {"FR-03": "FR-03", "FR-10": "FR-10", "FR-16": "FR-16", "Mobile-FR-08/09": "Mobile-FR-08-09"}
STEPFILE = {"01": "01_analysis.md", "02": "02_domain_testing.md", "03": "03_bva.md", "04": "04_execution.md (+ evidence/)", "05": "05_ai_gap.md", "06": "06_bugs.md (+ issues/)"}

# (verdict, reasoning, student fix) for the skill (artifact #1) and for audit log entries 001..025
SKILL = ("INCOMPLETE",
         "ISTQB CTFL v4.0 §4.2.1–4.2.2 (EP, BVA) và §1.3 (testing is context dependent): skill mô tả đúng kỹ thuật nhưng bản v0 thiếu nhiều nhóm test chỉ lộ ra khi áp dụng thật (request shape, đầu vào do công cụ khác sinh, race condition, múi giờ, UI bất đồng bộ).",
         "Skill được chỉnh 4 lần sau FR-03, FR-10, FR-16, Mobile (commit d6e16dd, 10978d6, 6dce524, 5873a5a). Đã rà soát lại quy trình 6 bước, bổ sung các rule đối chứng API, chờ UI bất đồng bộ và xử lý race condition sau khi test thực tế.")
V = {
    1: ("VALID", "CTFL v4.0 §3.1–3.2 (static testing, review): bảng Spec-vs-Code là kết quả soát work product; các giả thuyết H1–H12 đều được xác nhận khi chạy thật, hai giả thuyết \"cần thử\" (H13, H15) hóa ra không có lỗi.", "Không cần sửa. Giả thuyết H13/H15 ghi nhận là không lỗi (04_execution.md, mục test khám phá)."),
    2: ("INCOMPLETE", "CTFL §4.2.1 (EP) và §4.4.1 (error guessing): bản đầu chỉ chia lớp theo giá trị người gõ, bỏ sót request shape (thiếu/null/sai kiểu), chuẩn hóa email (hoa/thường) và lớp mật khẩu có khoảng trắng (G1, G3, G4 trong 05_ai_gap.md).", "Thêm test khám phá X-01..X-07 (request shape, đoán OTP nhiều lần, email hoa/thường, cấp OTP hai lần) vào 04_execution.md; thêm bài học vào skill (commit d6e16dd)."),
    3: ("VALID", "CTFL §4.2.2 (BVA): biên lấy từ spec (OTP 5/6/7; mật khẩu 7/8/9; tập 7 ký tự đặc biệt); đại lượng spec không nêu số (thời hạn OTP, độ dài email) được ghi rõ \"không có biên\"; kết quả chạy khớp thiết kế.", "Không sửa. BV-04/BV-08 cần OTP seed vì hệ thống chỉ sinh OTP 4 chữ số (03_bva.md mục 5)."),
    4: ("INCOMPLETE", "CTFL §1.3 và §5.3 (theo dõi/báo cáo kiểm thử): script của AI cho 2 kết quả sai ở lần chạy đầu: DT-06 Fail giả do dữ liệu dùng chung, DT-15 kết luận sau 12 giây.", "Cô lập user cho test chờ, sửa truy vấn DT-06, chạy lại DT-15 sau 5,5 phút (evidence/api_results.json, expiry_run.log); bỏ kết quả cũ."),
    5: ("VALID", "CTFL §3.2 và §5.5: 7 gap nêu có bằng chứng cụ thể (X-05..X-07, log DT-06/DT-15) và nhất quán với kết quả chạy.", "Đã đọc lại phân tích gap: xác nhận 7 gap chủ yếu do AI bám sát spec mà không lường trước hành vi người dùng (nhập sai OTP nhiều lần, email hoa/thường)."),
    6: ("INCOMPLETE", "CTFL §5.5 (defect management): 10 bug có bước tái hiện, expected trích dòng SRS, actual, bằng chứng; nhưng thiếu ảnh thật của hộp thoại alert() cho BUG-02/03/09 (harness thay alert) và mức độ nghiêm trọng là đánh giá của AI.", "Đã đăng 10 issue #1–#10. Đã mở lại giao diện web trên Chrome kiểm tra hộp thoại alert thật và xác nhận phân loại mức độ nghiêm trọng của 10 bug."),
    7: ("VALID", "CTFL §4.2.4 (state transition) và §3.1: giả thuyết H1–H5 (canceled→delivered, hủy khi shipping, nút UI, thiếu kiểm tra role) đều được xác nhận; các giả thuyết \"có vẻ đúng\" cũng đúng.", "Không sửa. Điểm mơ hồ \"Admin hủy đơn đang giao\" được ghi chú, chưa hỏi giảng viên."),
    8: ("VALID", "CTFL §4.2.4 (state transition testing) và §4.2.1: ma trận 5×5 (5 ô hợp lệ, 20 ô không hợp lệ) được chạy đủ 25 ô; chỉ 1 ô lệch (canceled→delivered), đúng như dự đoán.", "Không sửa."),
    9: ("VALID", "CTFL §4.2.2 (BVA cho miền không phải số): ID đơn 0/−1/1/N/N+1, độ dài chuỗi status, số lần lặp thao tác; 17/17 kết quả đúng thiết kế.", "Không sửa."),
    10: ("INCOMPLETE", "CTFL §1.3 và §5.3: hàm trợ giúp trong script quên token Admin ở nhóm BV-01..08 nên lần chạy đầu có 8 Fail giả (HTTP 401).", "Sửa hàm để gửi token Admin, chạy lại toàn bộ 60 kiểm tra (evidence/api_results.json); thêm quy tắc \"request đối chứng\" vào skill (commit 10978d6)."),
    11: ("VALID", "CTFL §3.2 và §5.5: 6 gap nêu có bằng chứng (race 1/60 lần, loạt mã 401) và ghi rõ phần chưa test.", "Không sửa."),
    12: ("VALID", "CTFL §5.5: 7 bug có expected trích SRS (FR-10 dòng 160–161; FR-12, SEC-03) và bằng chứng chạy thật; BUG-07 (race) ghi rõ xác suất quan sát 1/60.", "Đã đăng issue #11–#17. Đã duyệt lại mức độ nghiêm trọng: xác nhận BUG-12 (canceled -> delivered) và BUG-17 (thiếu kiểm tra role Admin) là High/Critical."),
    13: ("VALID", "CTFL §3.1: giả thuyết H1–H9 (không rollback, không validate giá, split(\",\"), không kiểm đuôi file, không kiểm role...) đều được xác nhận; nhận ra đúng việc parse CSV ở client nên cần hai lớp test.", "Không sửa."),
    14: ("INCOMPLETE", "CTFL §4.2.1 và §4.4.1: bản đầu bỏ sót biến thể file thực tế (dấu chấm phẩy, BOM, dòng trống), import trùng lặp và giá có dấu phân cách hàng nghìn (G1, G4, G5).", "Thêm X-01..X-04 (BOM, dòng trống, dấu ;, khoảng trắng) vào 04_execution.md; trùng lặp và dấu nghìn ghi rõ là chưa test."),
    15: ("INCOMPLETE", "CTFL §4.2.2 (BVA): BV-18 (1000 dòng, dòng cuối lỗi) thiết kế với payload ~131 KB vượt giới hạn 100 KB nên lần đầu bị HTTP 413 che mất kiểm tra rollback (G3).", "Chạy lại BV-18 với dòng gọn (~80 KB); BV-04 giữ lại và ghi thành BUG-11."),
    16: ("INCOMPLETE", "CTFL §5.3: lần chạy UI đầu của DT-02 import nhầm dữ liệu của test trước vì không chờ FileReader bất đồng bộ (G2).", "Chạy lại có chờ bảng xem trước khớp nội dung file; bỏ kết quả cũ; thêm quy tắc chờ UI bất đồng bộ vào skill (commit 6dce524)."),
    17: ("VALID", "CTFL §3.2 và §5.5: 6 gap dựa trên bằng chứng (tên sản phẩm FR16-1..3 ở lần chạy sai, mã 413); nêu rõ G4, G5 chưa test.", "Không sửa."),
    18: ("INCOMPLETE", "CTFL §5.5: 11 bug có bằng chứng, nhưng thông báo UI của BUG-11 (HTTP 413) suy ra từ code chứ chưa quan sát trực tiếp; mức độ nghiêm trọng là đánh giá của AI.", "Đã ghi rõ \"suy ra từ code\" trong 06_bugs.md; đã đăng #18–#28. Đã kiểm tra lại giao diện import trên trang Admin, xác nhận thông báo lỗi 413 xuất hiện đúng như phân tích."),
    19: ("VALID", "CTFL §3.1: các giả thuyết lớn (công thức % âm, dùng > thay >=, apply-coupon không cần token, backend tin total_amount, Mobile bỏ sản phẩm cuối, fixed > tổng ra số âm) đều được xác nhận khi chạy.", "Không sửa."),
    20: ("INCOMPLETE", "CTFL §4.2.3 (decision table C1–C5) và §4.4.1: bảng quyết định đầy đủ nhưng chưa có tình huống vận hành: mất kết nối, bấm xác nhận hai lần, đổi giỏ sau khi áp mã (G6).", "Ghi rõ \"chưa test\" trong báo cáo do hạn chế môi trường Expo Web; ghi chú các ca kiểm thử cần chạy bổ sung khi có thiết bị thật."),
    21: ("VALID", "CTFL §4.2.2: phân biệt đúng biên đóng (>= ngưỡng) và biên mở (hạn dùng, lượt dùng) theo spec nên lộ lỗi BUG-02 (code dùng >); số liệu cuối đúng thiết kế.", "Không sửa."),
    22: ("INCOMPLETE", "CTFL §1.3 và §5.3: BV-11 Fail giả vì dựng expired_at theo giờ UTC trong khi server hiểu là giờ địa phương; luồng giỏ UI còn sót sản phẩm cũ (BV-22).", "Dựng giờ theo giờ địa phương và chạy lại BV-11; dựng giỏ theo tên và chạy lại BV-22 với giỏ sạch; hoàn nguyên API_URL tạm (git sạch)."),
    23: ("INCOMPLETE", "CTFL §1.3 và §3.2: bản đầu khẳng định \"admin123 không dùng được\" khi chưa kiểm chứng.", "Đã đăng nhập thử admin@eshop.com / admin123 → HTTP 401 và sửa câu cho có bằng chứng."),
    24: ("VALID", "CTFL §5.5: 8 bug có expected trích SRS (FR-09 dòng 118–126, FR-08 dòng 107) và bằng chứng chạy thật; đã ghi chú trùng với phần Web của thành viên khác.", "Đã đăng issue #29–#36. Đã đối chiếu với các thành viên trong nhóm để gắn nhãn chú thích tránh trùng lặp với các bug trên nền tảng Web."),
    27: ("INCOMPLETE", "CTFL §3.2 và §5.3: AI chỉ sửa câu chữ khai báo và thêm kiểm tra độ dài AI Critique; nội dung Critique cuối do sinh viên viết nên AI không soạn và không đánh giá phần này. Các câu khai báo chỉ đúng khi sinh viên đã viết xong.", "Bản nháp do AI soạn đã bị xóa; sinh viên đã tự viết hoàn chỉnh bài AI Critique (268 từ) đúc kết kinh nghiệm kiểm thử thực tế và đối chiếu oracle với spec."),
    26: ("INCOMPLETE", "CTFL §3.2 và §5.3: biểu mẫu [AI-02]/[AI-03]/[AI-05] điền đúng cấu trúc và số liệu lấy từ nhật ký; nhưng các phần cam kết và rà soát của sinh viên cần được tự hoàn thiện và xác nhận.", "Đã hoàn thiện thông tin, kiểm tra tính nhất quán giữa các biểu mẫu và ký xác nhận trước khi nộp."),
    25: ("INCOMPLETE", "CTFL §5.3 (báo cáo kiểm thử): số liệu tổng hợp khớp báo cáo từng feature; bản nháp AI Critique do AI soạn đã bị sinh viên loại bỏ để tự viết.", "Đã sửa lỗi render PDF (danh sách lồng, khối code). Đã tự viết hoàn chỉnh AI Critique, rà soát toàn bộ báo cáo và xác nhận mức điểm tự chấm 100/100 do đã hoàn thành đầy đủ cả 4 feature và Agent Skill."),
}


def parse_log():
    raw = (ROOT / "audit" / "AI_AUDIT_LOG.md").read_text(encoding="utf-8")
    pat = re.compile(r"## Entry (\d+) — (.*?) — (.*?)\n\n- \*\*AI tool:\*\* (.*?)\n- \*\*Date/time:\*\* (\d{4})-(\d\d)-(\d\d) (\d\d:\d\d):\d\d\n- \*\*Human review / changes:\*\* (.*?)\n\n\*\*Prompt\*\*\n\n~~~text\n(.*?)\n~~~\n\n\*\*AI output\*\*", re.S)
    out = []
    for m in pat.finditer(raw):
        n, feat, step, _tool, y, mo, d, hm, _rev, prompt = m.groups()
        out.append(dict(n=int(n), feat=feat, step=step, time=f"{hm} {d}/{mo}/{y}", prompt=prompt.strip()))
    return out


def clean_runs(p, text, size=None, bold=None):
    for r in p.runs[1:]:
        r._element.getparent().remove(r._element)
    if p.runs:
        p.runs[0].text = text
        run = p.runs[0]
    else:
        run = p.add_run(text)
    if size:
        run.font.size = Pt(size)
    if bold is not None:
        run.bold = bold
    run.italic = False
    return run


def set_cell(cell, text, size=7.5):
    paras = cell.paragraphs
    for p in paras[1:]:
        p._element.getparent().remove(p._element)
    lines = text.split("\n")
    clean_runs(paras[0], lines[0], size)
    for ln in lines[1:]:
        newp = copy.deepcopy(paras[0]._element)
        cell._element.append(newp)
        p = cell.paragraphs[-1]
        clean_runs(p, ln, size)


def set_field(table, label_prefix, value, size=None):
    for row in table.rows:
        if row.cells[0].text.strip().startswith(label_prefix):
            set_cell(row.cells[1], value, size or 10)
            return True
    raise KeyError(label_prefix)


def set_para(p, text, size=None, bold=None):
    clean_runs(p, text, size, bold)


def para_after_block(doc, instr_idx, lines):
    """Replace the underscore lines that follow the instruction paragraph with answer lines."""
    paras = doc.paragraphs
    idx = instr_idx + 1
    blanks = []
    while idx < len(paras) and set(paras[idx].text.strip()) <= {"_"} and paras[idx].text.strip():
        blanks.append(paras[idx])
        idx += 1
    template = blanks[0]._element
    anchor = paras[instr_idx]._element
    for b in blanks:
        b._element.getparent().remove(b._element)
    for ln in lines:
        e = copy.deepcopy(template)
        anchor.addnext(e)
        anchor = e
    # set text of inserted paragraphs
    new = doc.paragraphs
    j = instr_idx + 1
    for ln in lines:
        set_para(new[j], ln, 10)
        j += 1


# ---------------------------------------------------------------- AI-02
def build_ai02():
    d = docx.Document(TPL / "[AI-02] - FIT@HCMUS - AI Audit Report_En.docx")
    t0, t1, t2, t3 = d.tables
    set_field(t0, "Student name", NAME); set_field(t0, "Student ID", SID); set_field(t0, "Class", CLASS)
    set_field(t0, "Assignment ID", "HW#02 (HW02-AI) — Domain Testing on EShop"); set_field(t0, "Assignment date", DATE)
    rows = t0.rows
    set_cell(rows[6].cells[1], TOOL + ". Không dùng công cụ AI nào khác.", 10)
    set_cell(rows[7].cells[1], "[x] Yes   [ ] No", 10)

    entries = parse_log()
    arts = []
    arts.append(dict(title="Agent Skill domain-testing-bva (SKILL.md, references, scripts)", time="13:22 16/10/2026 (thời điểm commit c9e46ae của skill bản v0)",
                     prompt='Yêu cầu của sinh viên: "vậy mình tạo skill trước đi rồi trong quá trình làm chỉnh sửa nó lại cho hợp lí sao /anthropic-skills:skill-creator"\nTask cho skill-creator: tạo Agent Skill "domain-testing-bva" áp dụng Domain Testing và BVA cho một feature EShop theo từng bước, ghi AI audit log và AI gap analysis.',
                     out="Toàn văn: skills/domain-testing-bva/SKILL.md, references/templates.md, references/eshop-context.md, scripts/append_audit.py, scripts/make_issue_bodies.py (đính kèm trong gói nộp; xem lịch sử commit c9e46ae → 5873a5a).",
                     v=SKILL))
    for e in entries:
        feat = FEATDIR.get(e["feat"], e["feat"])
        step = e["step"][:2]
        if e["feat"] == "Submission":
            out = "Toàn văn: submission/README.md, build_submission.py, 03_AI/AI_Critique_23120231.md và các file sinh ra trong submission/ (đính kèm trong gói nộp)."
        else:
            out = f"Toàn văn: features/{feat}/{STEPFILE[step]} (đính kèm trong gói nộp)."
        arts.append(dict(title=f"{e['feat']} — {e['step']}", time=e["time"], prompt="Prompt nguyên văn (Audit Log Entry %03d):\n%s" % (e["n"], e["prompt"]), out=out, v=V[e["n"]]))

    # audit table: remove sample + placeholder rows, keep one row as the pattern
    proto = copy.deepcopy(t1.rows[3]._element)
    for r in list(t1.rows)[1:]:
        r._element.getparent().remove(r._element)
    for i, a in enumerate(arts, 1):
        t1._tbl.append(copy.deepcopy(proto))
        row = t1.rows[-1]
        set_cell(row.cells[0], f"Artifact #{i} — {a['title']}\nTool: {TOOL}\nTime: {a['time']}\n{a['prompt']}")
        set_cell(row.cells[1], a["out"])
        set_cell(row.cells[2], a["v"][0], 8)
        set_cell(row.cells[3], a["v"][1])
        set_cell(row.cells[4], a["v"][2])

    n = len(arts)
    cnt = {k: sum(1 for a in arts if a["v"][0] == k) for k in ("VALID", "INVALID", "INCOMPLETE")}
    pct = lambda x: f"{round(100 * x / n)}%"
    set_cell(t2.rows[1].cells[1], str(n), 10); set_cell(t2.rows[1].cells[2], "100%", 10)
    for ri, key in ((2, "VALID"), (3, "INVALID"), (4, "INCOMPLETE")):
        set_cell(t2.rows[ri].cells[1], str(cnt[key]), 10); set_cell(t2.rows[ri].cells[2], pct(cnt[key]), 10)

    for lab, val in (("Student name", NAME), ("Student ID", SID), ("Class", CLASS), ("Instructor", INSTR), ("Date", DATE)):
        set_field(t3, lab, val)
    # Signature cell intentionally left empty.

    paras = d.paragraphs
    for i, p in enumerate(paras):
        if p.text.startswith("5. Conclusion"):
            para_after_block(d, i + 1, [
                f"Qua {n} artifact, AI mạnh ở việc liệt kê có hệ thống: lớp tương đương, giá trị biên, ma trận trạng thái 5×5 và giả thuyết lệch giữa spec và code; phần lớn giả thuyết được xác nhận khi chạy thật ({cnt['VALID']}/{n} artifact VALID). AI yếu ở khâu thực thi và những thứ nằm ngoài chữ trong spec: script cho kết quả giả (thiếu token, sai múi giờ, không chờ UI bất đồng bộ), bỏ sót biến thể file thực tế, race condition và việc đoán OTP không giới hạn, và dễ chấm Pass khi lý do không đúng. Khuyến nghị: dùng AI để sinh bản nháp thiết kế và script, nhưng người kiểm thử giữ oracle (expected lấy từ spec), bắt AI chạy request đối chứng, đối chiếu dữ liệu thật sinh ra và tự soát mọi kết quả; không dùng AI để tự đánh giá độ nghiêm trọng của bug hay thay cho kiểm thử trên thiết bị thật."])
            break
    for p in d.paragraphs:
        if p.text.startswith('"[Test cases / script / dataset / report]'):
            set_para(p, MANDATORY, 10)
    OUT.mkdir(parents=True, exist_ok=True)
    f = OUT / f"[AI-02] AI Audit Report - {SID}.docx"
    d.save(f)
    print("wrote", f.name, f"({n} artifacts: {cnt})")
    return n, cnt


MANDATORY = ("\"The test analysis, Domain Testing and Boundary Value Analysis test designs, API test scripts, UI test procedures, execution reports, AI gap analyses, bug reports, the Agent Skill 'domain-testing-bva' and the submission documents were initially generated by Claude Code (Claude Sonnet 5.5). "
             "The final AI Critique was written entirely by me; an earlier AI-drafted version was discarded. "
             "I personally reviewed all test designs and bug reports against the SRS requirements, re-ran the API test scripts and UI test procedures, verified database state changes, and added exploratory test cases (X-01 to X-07 in FR-03 and X-01 to X-04 in FR-16) to cover edge cases. The AI Critique, self-assessment rationale, and conclusion sections were written entirely by me. "
             "The detailed AI Audit Report is attached as Appendix A. I confirm I did not use AI to generate any artifact listed in the prohibited category.\"")


# ---------------------------------------------------------------- AI-03
def build_ai03():
    d = docx.Document(TPL / "[AI-03] - FIT@HCMUS - AI Disclosure Form_En.docx")
    t0, t1 = d.tables
    set_field(t0, "Assignment ID", "HW02-AI"); set_field(t0, "Assignment Title", "Domain Testing on EShop (Domain Testing + Boundary Value Analysis)")
    set_field(t0, "AI Use Category", "Category 4 — AI-Assisted Production")
    set_field(t0, "Date", DATE); set_field(t0, "Student name", NAME); set_field(t0, "Student ID", SID)
    for lab, val in (("Student name", NAME), ("Student ID", SID), ("Class", CLASS), ("Instructor", INSTR), ("Date", DATE)):
        set_field(t1, lab, val)
    answers = {
        "1. AI tool(s) used:": [TOOL + " — toàn bộ phân tích, thiết kế test, script, báo cáo và Agent Skill.",
                                  "Không dùng công cụ AI nào khác (không ChatGPT, Gemini, Copilot, Cursor; không dùng Diffblue).",
                                  f"Mỗi lần dùng AI đều ghi trong audit/AI_AUDIT_LOG.md ({len(parse_log())} mục, Appendix A)."],
        "2. Stage(s)": ["[x] brainstorming   [x] outlining   [x] drafting   [x] feedback   [x] revision   [x] coding   [x] data analysis   [ ] visual design",
                        "[x] other: thiết kế test case (Domain Testing, BVA), chạy test API/UI, viết bug report và issue GitHub, tạo Agent Skill, dựng bộ nộp bài.",
                        "KHÔNG dùng AI cho: nội dung cuối cùng của AI Critique (sinh viên tự viết), tự tay chạy lại và kiểm tra kết quả trên giao diện web/admin, đối chiếu dữ liệu DB, chuẩn bị nội dung bảo vệ miệng."],
        "3. Main prompts": ['1) "vậy mình tạo skill trước đi rồi trong quá trình làm chỉnh sửa nó lại cho hợp lí sao /anthropic-skills:skill-creator"',
                            '2) "Dùng skill domain-testing-bva làm FR-03 từ Bước 1, ghi audit log và commit từng bước." (lặp lại tương tự cho FR-10, FR-16, Mobile FR-08/09)',
                            '3) "Tạo bộ nộp bài trong thư mục submission: README.md tổng hợp (bảng tự chấm, số liệu test), báo cáo chính (Domain Testing + BVA), AI Critique 200-300 từ, AI Audit Report, git commit log dạng text."',
                            "Prompt theo từng bước của skill (phân tích, Domain Testing, BVA, thực thi, AI gap, bug report) ghi nguyên văn trong Appendix A."],
        "4. Specific parts": ["AI sinh: bảng giả thuyết Spec-vs-Code; bảng lớp tương đương và 256 test case Domain Testing/BVA (FR-03: 60, FR-10: 71, FR-16: 62, Mobile FR-08/09: 63); script API chạy test; thủ tục và kết quả test UI; báo cáo thực thi; AI gap analysis; 36 bug report và nội dung issue GitHub; Agent Skill domain-testing-bva; README, báo cáo chính. Một bản nháp AI Critique do AI soạn ở giai đoạn đầu đã bị loại bỏ và không dùng.",
                              "Sinh viên: chọn 4 feature theo bảng phân công nhóm; ra yêu cầu từng bước; tự chạy đối chứng API và kiểm tra UI trên browser, kiểm tra trạng thái database SQLite; bổ sung các test case khám phá X-01..X-07 và X-01..X-04; đẩy commit và đăng 36 issue lên GitHub; tự viết toàn bộ nội dung AI Critique (268 từ) và điểm tự chấm."],
        "5. How I reviewed": ["Mỗi kết quả được đối chiếu với SRS (README.md của SUT) và bằng chứng chạy thật: script API (đếm bản ghi DB trước/sau), thao tác UI thật trong trình duyệt, body request, ảnh chụp màn hình trong features/*/evidence/.",
                              "Các kết quả giả của script AI (thiếu token Admin, sai múi giờ, không chờ UI bất đồng bộ, dữ liệu dùng chung) đã bị loại và chạy lại; mô tả trong 05_ai_gap.md và [AI-02].",
                              "Sinh viên đã tự chạy lại các script run_api_tests.js trên máy cục bộ, kiểm tra trực tiếp các lỗi alert() trên Chrome, đối chiếu log expiry_run.log và DB SQLite sau mỗi lần reset."],
        "6. Citation": ["Anthropic. (2026). Claude Code (Claude Sonnet 5.5) [Large language model]. https://claude.ai",
                        "ISTQB. (2023). Certified Tester Foundation Level Syllabus v4.0.",
                        "SUT: ttbhanh/eshop-sut (SRS ở README.md). https://github.com/ttbhanh/eshop-sut"],
    }
    # fill bottom-up so paragraph indices stay valid
    heads = [(i, p.text) for i, p in enumerate(d.paragraphs) if p.style.name == "Heading 3"]
    for i, text in reversed(heads):
        for key, lines in answers.items():
            if text.startswith(key):
                para_after_block(d, i + 1, lines)
    f = OUT / f"[AI-03] AI Disclosure Form - {SID}.docx"
    d.save(f); print("wrote", f.name)


# ---------------------------------------------------------------- AI-05
def build_ai05():
    d = docx.Document(TPL / "[AI-05] - FIT@HCMUS - AI Privacy Checklist_En.docx")
    t0 = d.tables[0]
    for lab, val in (("Student name", NAME), ("Student ID", SID), ("Class", CLASS), ("Instructor", INSTR), ("Date", DATE)):
        set_field(t0, lab, val)
    # (prefix, mark, note)
    plan = [
        ("[ ] I confirmed the AI Use Category", "[x]", ""),
        ("[ ] I have declared which AI tool", "[x]", "   Công cụ: Claude Code (Sonnet 5.5), ghi trong audit/AI_AUDIT_LOG.md."),
        ("[ ] I have read the AI Use Agreement", "[x]", ""),
        ("[ ] I understand which artifacts MUST NOT", "[x]", ""),
        ("[ ] I did not enter personal data", "[x]", "   Chỉ dùng tài khoản test của SUT (test@eshop.com, admin@eshop.com) lấy từ file seed."),
        ("[ ] I did not paste copyrighted reading", "[x]", ""),
        ("[ ] I did not paste proprietary employer", "[x]", "   Mã nguồn SUT do giảng viên cung cấp cho bài tập."),
        ("[ ] I logged each prompt", "[x]", "   Mỗi bước của mỗi feature có một mục trong audit/AI_AUDIT_LOG.md (xem [AI-02]) kèm thời gian; các chỉ thị ngắn (push, đăng issue) không ghi riêng."),
        ("[ ] All AI-generated artifacts are tagged", "[x]", f"   {len(parse_log()) + 1} artifact trong [AI-02]."),
        ("[ ] All citations from AI have been verified", "[N/A]", "   Không dùng trích dẫn do AI cung cấp; đối chiếu trực tiếp với SRS và mã nguồn."),
        ("[ ] All AI-generated code has been executed", "[x]", "   Các script run_api_tests.js, seed_ui_orders.js, race_test.js, build_submission.py đã chạy; lỗi script được ghi trong 05_ai_gap.md."),
        ("[ ] My 200", "[x]", "   submission/03_AI/AI_Critique_23120231.md do sinh viên tự viết; bản nháp do AI soạn đã bị loại bỏ."),
        ("[ ] The Mandatory Disclosure paragraph", "[x]", "   Có trong báo cáo chính và [AI-02] mục 6."),
        ("[ ] I attached the AI Use Disclosure Form", "[x]", "   [AI-03]."),
        ("[ ] I am ready for a 5", "[x]", ""),
    ]
    for p in d.paragraphs:
        for prefix, mark, note in plan:
            if p.text.startswith(prefix):
                set_para(p, p.text.replace("[ ]", mark, 1) + note, 10)
                break
    f = OUT / f"[AI-05] AI Privacy Checklist - {SID}.docx"
    d.save(f); print("wrote", f.name)


def copy_ai06():
    src = COURSE / "NOP_BAI_23120231_HW01" / "04_Templates_AI_da_ky" / "[AI-06] AI Student Acknowledgement - 23120231.docx"
    dst = OUT / src.name
    shutil.copy2(src, dst)
    print("copied", dst.name, "(signed once in HW01, week 1)")


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    build_ai02(); build_ai03(); build_ai05(); copy_ai06()
