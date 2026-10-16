#!/usr/bin/env python3
"""Split a feature's 06_bugs.md into one GitHub-issue body file per bug.

Usage:
  python make_issue_bodies.py --bugs features/FR-03/06_bugs.md --out features/FR-03/issues \
      --raw-base https://raw.githubusercontent.com/<owner>/<repo>/main/features/FR-03

Each '### BUG-xx: Title' section becomes issues/BUG-xx.md (first line = title, which the
create command reads with `head -1`). Paths like `evidence/foo.jpg` in the body are rewritten
to image links using --raw-base so screenshots render inside the issue (the files must be
pushed to the repo first). It only writes files; it never calls GitHub.

Create an issue afterwards (after the user has approved publishing):
  f=issues/BUG-01.md
  gh issue create --repo <owner>/<repo> --title "[FR-03] $(head -1 $f)" --label bug --body-file <(tail -n +3 $f)
"""
import argparse
import pathlib
import re


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--bugs", required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--raw-base", default="")
    a = p.parse_args()

    text = pathlib.Path(a.bugs).read_text(encoding="utf-8")
    out = pathlib.Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    sections = re.split(r"(?m)^### (?=BUG-)", text)[1:]
    for sec in sections:
        head, _, body = sec.partition("\n")
        m = re.match(r"(BUG-[\w-]+):\s*(.*)", head)
        if not m:
            continue
        bug_id, title = m.group(1), m.group(2).strip()
        body = body.split("\n---")[0].strip()  # stop at the horizontal rule after the last bug

        def to_link(mt):
            rel = mt.group(1)
            if rel.lower().endswith((".jpg", ".jpeg", ".png", ".gif")) and a.raw_base:
                return f"![{rel}]({a.raw_base.rstrip('/')}/{rel})"
            return f"`{rel}`" if not a.raw_base else f"[{rel}]({a.raw_base.rstrip('/').replace('raw.githubusercontent.com', 'github.com').replace('/main/', '/blob/main/')}/{rel})"

        body = re.sub(r"`(evidence/[^`\s]+)`", to_link, body)
        (out / f"{bug_id}.md").write_text(f"{title}\n\n{body}\n", encoding="utf-8")
        print(f"wrote {out / (bug_id + '.md')}")


if __name__ == "__main__":
    main()
