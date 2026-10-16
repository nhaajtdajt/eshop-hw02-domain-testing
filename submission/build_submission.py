#!/usr/bin/env python3
"""Build the HW02 submission package from the per-feature documents.

Run with an interpreter that has the `markdown` package (and Microsoft Edge/Chrome installed for PDF):
    python submission/build_submission.py [--no-pdf] [--no-zip] [--grade 082]

Outputs (inside submission/):
  01_BaoCao_chinh/BaoCao_HW02_23120231.md/.pdf  main report (Domain Testing + BVA + results + AI gap)
  02_BugReport/BugReport_HW02_23120231.md/.pdf  bug report with screenshots
  03_AI/AI_Audit_Report_23120231.md/.pdf        AI audit report (+ copy of the raw log)
  03_AI/AI_Critique_23120231.pdf                PDF of the hand-written critique
  04_Git_log/git_commit_log.txt                 git commit log
and, unless --no-zip, ../../23120231_HW02_AI_DomainTesting_<grade>.zip next to the repository folder.
Everything is generated from files in features/, audit/ and skills/, so re-run after editing them.
"""
import argparse
import datetime
import pathlib
import re
import shutil
import subprocess
import sys
import zipfile

import markdown

SID = "23120231"
ROOT = pathlib.Path(__file__).resolve().parents[1]          # .../eshop-sut
SUB = ROOT / "submission"
FEATURES = [
    ("FR-03", "FR-03 Quên & đặt lại mật khẩu (Pool A)", "FR-03"),
    ("FR-10", "FR-10 Máy trạng thái đơn hàng (Pool B)", "FR-10"),
    ("FR-16", "FR-16 Import sản phẩm từ CSV (Pool C)", "FR-16"),
    ("Mobile-FR-08-09", "Mobile FR-08/09 Thanh toán & mã giảm giá trên Mobile (Pool D)", "Mobile-FR-08-09"),
]
STATS = {  # feature dir -> (designed, executed, pass, fail, bugs)
    "FR-03": (60, 60, 20, 40, 10),
    "FR-10": (71, 71, 64, 7, 7),
    "FR-16": (62, 62, 28, 34, 11),
    "Mobile-FR-08-09": (63, 63, 42, 21, 8),
}


def read(p):
    return pathlib.Path(p).read_text(encoding="utf-8")


def demote(md, n):
    """Add n '#' to every heading outside fenced code blocks."""
    out, fence = [], False
    for line in md.splitlines():
        if re.match(r"^\s*(```|~~~)", line):
            fence = not fence
        if not fence and re.match(r"^#{1,6}\s", line):
            line = "#" * n + line
        out.append(line)
    return "\n".join(out)




def inline_indented_fences(md):
    """Fenced blocks nested in list items (indented) are not parsed by Python-Markdown: turn them into <pre> blocks."""
    import html
    lines, out, i = md.splitlines(), [], 0
    while i < len(lines):
        m = re.match(r"^(\s+)(```|~~~)\S*\s*$", lines[i])
        if m:
            indent, j, body = m.group(1), i + 1, []
            while j < len(lines) and not re.match(r"^\s*(```|~~~)\s*$", lines[j]):
                body.append(lines[j].strip() if lines[j].strip() else "")
                j += 1
            txt = html.escape("\n".join(body)).replace("*", "&#42;").replace("_", "&#95;").replace("`", "&#96;")
            out.append(f"{indent}<pre>{txt}</pre>")
            i = j + 1
            continue
        out.append(lines[i])
        i += 1
    return "\n".join(out)


LIST_RE = re.compile(r"^(\s*(?:>\s*)*)([-*+]|\d+[.)])\s+")


def fix_lists(md):
    """Python-Markdown needs a blank line before a list; insert one (keeping any blockquote prefix) outside code fences."""
    md = inline_indented_fences(md)
    out, fence = [], False
    for line in md.splitlines():
        if re.match(r"^\s*(```|~~~)", line):
            fence = not fence
        # sources use 2-space nesting; Python-Markdown needs 4 spaces for nested lists
        mi = re.match(r"^( +)([-*+]|\d+[.)])\s", line)
        if not fence and mi:
            line = mi.group(1) * 2 + line[len(mi.group(1)):]
        m = LIST_RE.match(line)
        if not fence and m and out:
            prev = out[-1]
            prev_is_blank = not prev.strip().lstrip(">").strip()
            prefix = re.match(r"^(\s*(?:>\s*)*)", line).group(1)
            prev_prefix = re.match(r"^(\s*(?:>\s*)*)", prev).group(1)
            starts_list = not LIST_RE.match(prev) and not prev.startswith("    ") and not prev.lstrip().startswith("|")
            dedent = bool(LIST_RE.match(prev)) and len(prev_prefix) > len(prefix)  # back to an outer list level
            if not prev_is_blank and (starts_list or dedent):
                out.append(prefix.rstrip() if prefix.strip() else "")
        out.append(line)
    return "\n".join(out)


def strip_title(md):
    """Drop the first H1 line (the feature title) because the report adds its own heading."""
    lines = md.splitlines()
    if lines and lines[0].startswith("# "):
        lines = lines[1:]
    return "\n".join(lines).strip()


def ai_audit_numbers():
    """Verdict counts for the AI artifacts, taken from build_templates.py so both documents stay consistent."""
    sys.path.insert(0, str(SUB))
    import build_templates as bt
    verdicts = [bt.SKILL[0]] + [bt.V[i][0] for i in sorted(bt.V)]
    return len(verdicts), {k: verdicts.count(k) for k in ("VALID", "INVALID", "INCOMPLETE")}


def critique_words():
    parts = read(SUB / "03_AI" / f"AI_Critique_{SID}.md").split("\n", 2)
    body = parts[2] if len(parts) > 2 else ""
    return len(re.findall(r"\S+", body))


# ---------------------------------------------------------------- main report
def build_report():
    t = []
    t.append(f"""# BÁO CÁO CHÍNH — HW02 Domain Testing on EShop

**Sinh viên:** MSSV {SID} (Thành viên 4) — **Môn:** Kiểm thử phần mềm, FIT@HCMUS — **Ngày:** {datetime.date.today().isoformat()}
**SUT:** EShop (`https://github.com/ttbhanh/eshop-sut`) — **Repo làm việc:** https://github.com/nhaajtdajt/eshop-hw02-domain-testing

Báo cáo này gồm **báo cáo Domain Testing** (mục 4) và **báo cáo Boundary Value Analysis** (mục 5) cho bốn feature được giao, kèm kết quả thực thi (mục 6) và phân tích AI gap (mục 7). Bug report có screenshot ở file riêng `02_BugReport/`; AI Audit Report (mục 10), AI Critique (mục 11) và Mandatory Disclosure (mục 12) nằm cuối báo cáo, các biểu mẫu AI đã điền ở `05_Templates_AI/`.

## 1. Phạm vi và môi trường

| Pool | Feature | Lý do chọn / phạm vi |
|---|---|---|
| A | FR-03 Quên & đặt lại mật khẩu | Form 2 bước, OTP, mật khẩu mới; UI web và API |
| B | FR-10 Máy trạng thái đơn hàng | Ma trận trạng thái 5×5; API Admin, hủy đơn của User, UI Admin và Web |
| C | FR-16 Import sản phẩm từ CSV | Parse CSV ở client, API import, tính nguyên tử |
| D | Mobile FR-08/09 Thanh toán & mã giảm giá | Màn thanh toán Mobile, 5 điều kiện mã giảm giá, công thức tính tiền |

Môi trường: Windows 11, Node v22.20.0; Backend `localhost:3000`, Web `5173`, Admin `5174`; Mobile chạy bằng Expo Web (`react-native-web`). **Không có thiết bị thật/emulator.** Dữ liệu seed gốc của repo; mỗi nhóm test có bước reset/dọn dữ liệu.

## 2. Phương pháp (áp dụng cho mọi feature)

Mỗi feature đi qua 6 bước và mỗi bước là **một commit riêng** (xem `04_Git_log/git_commit_log.txt`); mỗi lần dùng AI đều được ghi vào AI Audit Log kèm phần người review đã sửa.

1. **Phân tích:** trích yêu cầu từ SRS (`README.md`), liệt kê input/điều kiện/output, rồi đối chiếu code để lập bảng giả thuyết "Spec vs Code". **Spec là oracle**, code chỉ để biết chỗ nào dễ sai.
2. **Domain Testing:** chia miền từng input thành lớp tương đương hợp lệ/không hợp lệ (mã `EC-…`). Mỗi test hợp lệ phủ nhiều lớp; **mỗi test không hợp lệ chỉ chứa đúng một lỗi**. Có bảng truy vết lớp → test. Với state machine, miền là cặp (trạng thái hiện tại × đích) nên test đủ 25 ô; với coupon dùng bảng quyết định C1..C5.
3. **Boundary Value Analysis:** xác định đại lượng có thứ tự theo spec, nêu biên đóng/mở (`>=` hay `>`), thiết kế 3 giá trị biên−1/biên/biên+1 và cực trị; đại lượng spec không nêu số thì ghi rõ "không có biên" thay vì tự bịa.
4. **Thực thi:** script API lặp lại được (HTTP thật, đếm dữ liệu trước/sau) và thao tác UI thật bằng trình duyệt; kết quả tổng là Fail nếu bất kỳ lớp UI/API lệch spec.
5. **AI gap analysis:** so bản thiết kế đầu của AI với bộ test/bug cuối, phân loại nguyên nhân (Prompt / Giới hạn công cụ / Độ phức tạp feature).
6. **Bug report:** gom các test Fail theo nguyên nhân gốc, mỗi bug có bước tái hiện, expected (trích dòng SRS), actual và bằng chứng; đăng lên GitHub Issues.

**Cách dùng AI có kỷ luật:** mỗi bước một prompt riêng (liệt kê input → chia lớp → ghép test → biên → thực thi → gap → bug), không dùng một prompt chung kiểu "sinh test và tìm bug". Quy trình được đóng gói thành Agent Skill `skills/domain-testing-bva/` và được chỉnh lại sau mỗi feature (xem bảng "Nhật ký cải tiến skill" trong `SKILL.md`).

## 3. Tổng hợp kết quả

| Feature | Test thiết kế | Đã chạy | Pass | Fail | Bug gốc |
|---|:---:|:---:|:---:|:---:|:---:|""")
    tot = [0, 0, 0, 0, 0]
    for d, name, _ in FEATURES:
        a = STATS[d]
        tot = [x + y for x, y in zip(tot, a)]
        t.append(f"| {name} | {a[0]} | {a[1]} | {a[2]} | {a[3]} | {a[4]} |")
    t.append(f"| **Tổng** | **{tot[0]}** | **{tot[1]}** | **{tot[2]}** | **{tot[3]}** | **{tot[4]}** |")
    t.append("""
Nhiều test Fail cùng một nguyên nhân gốc nên số bug nhỏ hơn số test Fail. Phát hiện nổi bật:
- **FR-03:** OTP chỉ 4 chữ số (spec: 6); regex form đặt lại mật khẩu từ chối mọi mật khẩu hợp lệ theo spec; thiếu ô xác nhận mật khẩu và Step Indicator; OTP không hết hạn.
- **FR-10:** `canceled → delivered` được phép; User hủy được đơn đang giao; API đổi trạng thái không kiểm tra role Admin; race condition làm đơn đã hủy bị xác nhận đè.
- **FR-16:** import không rollback; không validate giá; parse CSV hỏng trường có nháy kép; API import không kiểm tra role Admin.
- **Mobile FR-08/09:** mã giảm % cho tiền giảm âm (tổng đơn tăng lên 10 lần); đơn đúng bằng ngưỡng bị từ chối; backend tin `total_amount` của client; Mobile bỏ mất sản phẩm cuối của giỏ.
""")

    def section(num, title, files, shift):
        t.append(f"## {num}. {title}\n")
        for i, (d, name, _) in enumerate(FEATURES, 1):
            t.append(f"### {num}.{i} {name}\n")
            for f in files:
                p = ROOT / "features" / d / f
                t.append(demote(strip_title(read(p)), shift))
                t.append("")

    section(4, "Báo cáo Domain Testing", ["01_analysis.md", "02_domain_testing.md"], 3)
    section(5, "Báo cáo Boundary Value Analysis", ["03_bva.md"], 3)
    section(6, "Kết quả thực thi", ["04_execution.md"], 3)
    section(7, "AI gap analysis", ["05_ai_gap.md"], 3)
    t.append("""## 8. Bug report

Toàn bộ 36 bug được tổng hợp trong `02_BugReport/BugReport_HW02_23120231.pdf` (kèm screenshot) và đã đăng trên GitHub Issues: https://github.com/nhaajtdajt/eshop-hw02-domain-testing/issues

## 9. Hạn chế và trung thực

- Mobile chưa được thử trên thiết bị thật/emulator; kết quả UI Mobile đến từ Expo Web cùng mã nguồn `App.js`.
- Một số kết quả phụ thuộc diễn giải spec (Admin hủy đơn đang giao; `category_id` khi import; làm tròn khi giảm %). Các test này được gắn nhãn "diễn giải" và không coi là lỗi chắc chắn.
- Chưa test: import trùng lặp, giá có dấu phân cách hàng nghìn, mất kết nối/bấm hai lần ở thanh toán Mobile.
- Mức độ nghiêm trọng và nguyên nhân gap là đánh giá của AI, cần người kiểm thử xác nhận.
""")
    import build_templates as _bt
    mandatory = _bt.MANDATORY
    n_art, cnt = ai_audit_numbers()
    pc = lambda k: round(100 * cnt[k] / n_art)
    crit_parts = read(SUB / "03_AI" / f"AI_Critique_{SID}.md").split("\n", 2)
    crit_body = (crit_parts[2].strip() if len(crit_parts) > 2 else "") or "[AI Critique chưa được viết]"
    t.append(f"""## 10. AI Audit Report (tóm tắt)

Báo cáo đầy đủ theo mẫu 5 mục cho từng artifact: `05_Templates_AI/[AI-02] AI Audit Report - {SID}.docx` (và `03_AI/AI_Audit_Report_{SID}.md/.pdf`; nhật ký thô `audit/AI_AUDIT_LOG.md`). Tổng số artifact do AI sinh: **{n_art}** (Agent Skill và 25 sản phẩm theo từng bước của từng feature).

| Kết quả đánh giá | Số lượng | Tỉ lệ |
|---|:---:|:---:|
| VALID (đúng, dùng nguyên) | {cnt['VALID']} | {pc('VALID')}% |
| INVALID (sai, bị loại) | {cnt['INVALID']} | {pc('INVALID')}% |
| INCOMPLETE (dùng được sau khi sửa) | {cnt['INCOMPLETE']} | {pc('INCOMPLETE')}% |

**Khi nào nên / không nên dùng AI cho công việc này:** nên dùng AI để liệt kê có hệ thống lớp tương đương, giá trị biên, ma trận trạng thái và giả thuyết lệch giữa spec và code, cũng như viết bản nháp script và báo cáo. Không nên tin kết quả thực thi do script của AI khi chưa có request đối chứng và chưa đối chiếu dữ liệu thật; không nên để AI tự quyết expected (phải lấy từ spec), tự đánh giá mức độ nghiêm trọng của bug, hoặc thay cho kiểm thử trên thiết bị thật. Không artifact nào bị loại hẳn, nhưng một nửa chỉ dùng được sau khi sửa; các chỗ phải sửa nằm ở khâu thực thi và ở những tình huống nằm ngoài chữ trong spec.

## 11. AI Critique (200–300 từ)

{crit_body}

## 12. Mandatory Disclosure

{mandatory}
""")
    return "\n".join(t)


# ---------------------------------------------------------------- bug report
def build_bugs():
    t = [f"""# BUG REPORT — HW02 Domain Testing on EShop (MSSV {SID}, Thành viên 4)

Tổng cộng **36 bug** (FR-03: 10, FR-10: 7, FR-16: 11, Mobile FR-08/09: 8), đã đăng trên GitHub Issues: https://github.com/nhaajtdajt/eshop-hw02-domain-testing/issues (#1–#36, nhãn `bug`, tiền tố tên feature trong tiêu đề). Mỗi bug có bước tái hiện, expected (trích SRS), actual, bằng chứng; screenshot được nhúng bên dưới và đính kèm trong issue.
"""]
    n = 0
    for d, name, _ in FEATURES:
        n += 1
        md = read(ROOT / "features" / d / "06_bugs.md")
        md = strip_title(md)

        def img(m):
            rel = m.group(1)
            return f"![{rel}](../../features/{d}/evidence/{rel})\n\n"
        # embed screenshots mentioned as `evidence/xxx.jpg`
        md = re.sub(r"`evidence/([^`\s]+\.(?:jpg|jpeg|png))`", lambda m: f"`evidence/{m.group(1)}`\n\n![](../../features/{d}/evidence/{m.group(1)})\n", md)
        t.append(f"## {n}. {name}\n")
        t.append(demote(md, 2))
        t.append("")
    return "\n".join(t)


# ---------------------------------------------------------------- audit report
def build_audit():
    n_art, cnt = ai_audit_numbers()
    raw = read(ROOT / "audit" / "AI_AUDIT_LOG.md")
    entries = re.findall(r"## Entry (\d+) — (.*?) — (.*?)\n\n- \*\*AI tool:\*\* (.*?)\n- \*\*Date/time:\*\* (.*?)\n", raw)
    rows = "\n".join(f"| {a} | {b} | {c} | {e} |" for a, b, c, _, e in entries)
    head = f"""# AI AUDIT REPORT — HW02 Domain Testing (MSSV {SID}, Thành viên 4)

**I use AI tools for the following tasks.**

| Mục | Nội dung |
|---|---|
| Công cụ AI | Claude Code (mô hình Sonnet 5.5, `claude-sonnet-5-5`) chạy trong ứng dụng Claude desktop |
| Công cụ khác | Không dùng ChatGPT/Gemini/Copilot/Cursor; không dùng công cụ sinh test (ví dụ Diffblue) |
| Nhiệm vụ dùng AI | Phân tích spec và code, chia lớp tương đương, phân tích biên, viết script chạy test, chạy thử UI/API, tổng hợp kết quả, viết báo cáo/bug report/AI gap, tạo và chỉnh Agent Skill |
| Số lần ghi nhận | {len(entries)} mục (mỗi bước của mỗi feature một mục) |
| Người review | Sinh viên đối chiếu mọi kết quả với SRS và bằng chứng chạy thật; ô "Human review / changes" của từng mục ghi phần đã sửa |
| Tỉ lệ chính xác của AI | {n_art} artifact: VALID {cnt['VALID']} ({round(100*cnt['VALID']/n_art)}%), INVALID {cnt['INVALID']} (0%), INCOMPLETE {cnt['INCOMPLETE']} ({round(100*cnt['INCOMPLETE']/n_art)}%) — theo mẫu 5 mục trong `05_Templates_AI/[AI-02] AI Audit Report - 23120231.docx` |

## Cách ghi nhật ký
Mỗi mục gồm: tên công cụ, ngày giờ (từ đồng hồ máy khi ghi), prompt, output, phần người review đã chỉnh. Nhật ký được ghi ngay sau mỗi bước bằng `skills/domain-testing-bva/scripts/append_audit.py`. Vì AI chạy ngay trong phiên làm việc, "prompt" của mỗi bước gồm yêu cầu gốc của sinh viên và prompt bước theo skill; "output" là tóm tắt tài liệu/kết quả AI tạo ra (toàn văn nằm trong các file `features/*/0x_*.md`).

## Tóm tắt các mục

| # | Feature | Bước | Ngày giờ |
|---|---|---|---|
{rows}

## Phụ lục: toàn bộ nhật ký (nguyên văn `audit/AI_AUDIT_LOG.md`)
"""
    return head + "\n" + demote(raw.split("---", 1)[1] if "---" in raw else raw, 1)


# ---------------------------------------------------------------- git log
def build_gitlog():
    out = subprocess.run(["git", "log", "--pretty=format:%h | %ad | %an | %s", "--date=iso"], cwd=ROOT, capture_output=True, text=True, encoding="utf-8").stdout
    head = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT, capture_output=True, text=True).stdout.strip()
    n = len(out.splitlines())
    hdr = (f"# Git commit log — HW02 Domain Testing (MSSV {SID})\n# Repo: https://github.com/nhaajtdajt/eshop-hw02-domain-testing\n"
           f"# Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} at HEAD {head} ({n} commits)\n"
           f"# Format: <hash> | <date> | <author> | <message>   (mỗi bước kiểm thử của mỗi feature có một commit: '<FR-ID>: step N - ...')\n\n")
    return hdr + out + "\n"


# ---------------------------------------------------------------- PDF
CSS = """
body{font-family:'Segoe UI',Arial,sans-serif;font-size:10.5pt;line-height:1.45;margin:0 8px;color:#111}
h1{font-size:20pt;border-bottom:2px solid #444;padding-bottom:4px} h2{font-size:15pt;border-bottom:1px solid #aaa;margin-top:26px}
h3{font-size:12.5pt;margin-top:20px} h4{font-size:11.5pt} h5,h6{font-size:10.5pt}
table{border-collapse:collapse;width:100%;margin:8px 0;font-size:9pt;page-break-inside:auto}
th,td{border:1px solid #888;padding:3px 5px;vertical-align:top} th{background:#e9e9e9}
tr{page-break-inside:avoid} code{background:#f2f2f2;padding:0 2px;font-family:Consolas,monospace;font-size:9pt}
pre{background:#f6f6f6;border:1px solid #ddd;padding:6px;white-space:pre-wrap;font-size:8.5pt} pre code{background:none}
img{max-width:70%;border:1px solid #bbb;margin:4px 0;display:block} blockquote{border-left:3px solid #aaa;margin-left:0;padding-left:10px;color:#333}
"""


def find_browser():
    for p in [r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe", r"C:\Program Files\Microsoft\Edge\Application\msedge.exe", r"C:\Program Files\Google\Chrome\Application\chrome.exe"]:
        if pathlib.Path(p).exists():
            return p
    return None


def to_pdf(md_path, title):
    md_path = pathlib.Path(md_path)
    html = markdown.markdown(fix_lists(read(md_path)), extensions=["tables", "fenced_code", "sane_lists"])
    html_path = md_path.with_suffix(".html")
    html_path.write_text(f"<!doctype html><html><head><meta charset='utf-8'><title>{title}</title><style>{CSS}</style></head><body>{html}</body></html>", encoding="utf-8")
    br = find_browser()
    if not br:
        print("  (no Edge/Chrome found, PDF skipped)")
        return
    pdf = md_path.with_suffix(".pdf")
    import tempfile
    prof = tempfile.mkdtemp(prefix="edge_pdf_")  # separate profile so an already-running browser is not reused
    try:
        subprocess.run([br, "--headless=new", "--disable-gpu", "--no-first-run", f"--user-data-dir={prof}", "--no-pdf-header-footer", f"--print-to-pdf={pdf}", html_path.as_uri()], check=True, capture_output=True, timeout=180)
    finally:
        shutil.rmtree(prof, ignore_errors=True)
    html_path.unlink()
    print("  PDF:", pdf.relative_to(ROOT), f"({pdf.stat().st_size // 1024} KB)")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-pdf", action="store_true")
    ap.add_argument("--no-zip", action="store_true")
    ap.add_argument("--grade", default="082")
    a = ap.parse_args()

    docs = {
        SUB / "01_BaoCao_chinh" / f"BaoCao_HW02_{SID}.md": (build_report(), "Báo cáo chính HW02"),
        SUB / "02_BugReport" / f"BugReport_HW02_{SID}.md": (build_bugs(), "Bug report HW02"),
        SUB / "03_AI" / f"AI_Audit_Report_{SID}.md": (build_audit(), "AI Audit Report HW02"),
    }
    for p, (md, _) in docs.items():
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(md, encoding="utf-8")
        print("wrote", p.relative_to(ROOT))
    gl = SUB / "04_Git_log" / "git_commit_log.txt"
    gl.parent.mkdir(parents=True, exist_ok=True)
    gl.write_text(build_gitlog(), encoding="utf-8")
    print("wrote", gl.relative_to(ROOT))

    if not a.no_pdf:
        for p, (_, title) in docs.items():
            to_pdf(p, title)
        to_pdf(SUB / "03_AI" / f"AI_Critique_{SID}.md", "AI Critique HW02")

    words = critique_words()
    if not (200 <= words <= 300):
        print(f"WARNING: AI Critique has {words} words (required 200-300); zip NOT created. Write it in submission/03_AI/AI_Critique_{SID}.md and re-run.")
        a.no_zip = True
    if not a.no_zip:
        zpath = ROOT.parent / f"{SID}_HW02_AI_DomainTesting_{a.grade}.zip"
        skip_dirs = {"node_modules", ".git", ".expo", "__pycache__"}
        with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
            z.write(SUB / "README.md", "README.md")
            for sub in ["01_BaoCao_chinh", "02_BugReport", "03_AI", "04_Git_log", "05_Templates_AI"]:
                for f in (SUB / sub).rglob("*"):
                    if f.is_file() and f.suffix != ".html":
                        z.write(f, f.relative_to(SUB).as_posix())
            for top in ["features", "skills", "audit"]:
                for f in (ROOT / top).rglob("*"):
                    if f.is_file() and not (set(f.parts) & skip_dirs):
                        z.write(f, f.relative_to(ROOT).as_posix())
        print("zip:", zpath, f"({zpath.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
