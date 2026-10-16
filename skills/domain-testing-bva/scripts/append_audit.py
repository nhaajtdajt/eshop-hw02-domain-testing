#!/usr/bin/env python3
"""Append one AI interaction to the AI Audit Log (Markdown).

Usage:
  python append_audit.py --log audit/AI_AUDIT_LOG.md --tool "Claude Code (Sonnet 5.5)" \
      --feature FR-03 --step "02 Domain testing" \
      --prompt-file prompt.txt --output-file output.txt --review "Da sua: ..."

Prompt/output can also be passed inline with --prompt / --output.
The timestamp is taken from the local clock at call time.
"""
import argparse
import datetime
import pathlib
import sys


def read_text(inline, path):
    if inline is not None:
        return inline
    if path:
        return pathlib.Path(path).read_text(encoding="utf-8")
    return ""


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--log", required=True)
    p.add_argument("--tool", required=True)
    p.add_argument("--feature", required=True)
    p.add_argument("--step", required=True)
    p.add_argument("--prompt")
    p.add_argument("--prompt-file")
    p.add_argument("--output")
    p.add_argument("--output-file")
    p.add_argument("--review", required=True,
                   help="What you changed after reviewing the AI output (or why no change was needed)")
    a = p.parse_args()

    prompt = read_text(a.prompt, a.prompt_file).strip()
    output = read_text(a.output, a.output_file).strip()
    if not prompt or not output:
        sys.exit("Both prompt and output are required (use --prompt/--prompt-file and --output/--output-file).")

    log = pathlib.Path(a.log)
    log.parent.mkdir(parents=True, exist_ok=True)
    new_file = not log.exists()
    n = 1
    if not new_file:
        n = log.read_text(encoding="utf-8").count("\n## Entry ") + 1

    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = (
        f"\n## Entry {n:03d} — {a.feature} — {a.step}\n\n"
        f"- **AI tool:** {a.tool}\n"
        f"- **Date/time:** {now}\n"
        f"- **Human review / changes:** {a.review}\n\n"
        f"**Prompt**\n\n~~~text\n{prompt}\n~~~\n\n"
        f"**AI output**\n\n~~~text\n{output}\n~~~\n\n---\n"
    )
    with log.open("a", encoding="utf-8") as f:
        if new_file:
            f.write("# AI Audit Log\n\nI use AI tools for the following tasks.\n\n---\n")
        f.write(entry)
    print(f"Appended entry {n:03d} to {log}")


if __name__ == "__main__":
    main()
