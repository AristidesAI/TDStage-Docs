#!/usr/bin/env python3
"""Catch the two ways a diagram can silently fail on this site.

Both of these produce a page that looks fine to a linter, builds without a
warning, and shows nothing where the diagram should be.

1. Jekyll runs Liquid over Markdown before Kramdown sees it, so `{{ ... }}`
   inside a fenced block is evaluated as a Liquid output tag and never reaches
   the browser. That is also Mermaid's hexagon node syntax, so writing a
   hexagon node deletes it.

2. Mermaid's `securityLevel: "strict"` turns off HTML labels, which makes every
   `<br/>` in a label a parse error and stops the whole diagram rendering.

Usage: python3 tools/check_diagrams.py
"""
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent


def main():
    problems = []

    for p in sorted(ROOT.rglob("*.md")):
        if ".git" in p.parts:
            continue
        text = p.read_text(encoding="utf-8")
        for block in re.findall(r"```mermaid\n(.*?)```", text, re.S):
            rel = p.relative_to(ROOT)
            if "{{" in block or "{%" in block:
                problems.append(f"{rel}: Liquid syntax inside a diagram. "
                                "Use [[...]] for a hexagon, not {{...}}.")
            for line in block.splitlines():
                if "[" in line and '"' not in line and re.search(r"\[[^\]]*[(<>]", line):
                    problems.append(f"{rel}: unquoted label with punctuation: {line.strip()}")

    cfg = ROOT / "_includes" / "mermaid_config.js"
    if cfg.exists():
        c = cfg.read_text(encoding="utf-8")
        if "//" in c:
            problems.append("_includes/mermaid_config.js: the include is inlined "
                            "onto one line, so a // comment deletes the config.")
        if "strict" in c and "htmlLabels" not in c:
            problems.append('_includes/mermaid_config.js: securityLevel "strict" '
                            "disables HTML labels, so every <br/> breaks a diagram.")

    if problems:
        print("\n".join("  " + x for x in problems))
        sys.exit(1)
    n = sum(len(re.findall(r"```mermaid", p.read_text(encoding='utf-8')))
            for p in ROOT.rglob("*.md") if ".git" not in p.parts)
    print(f"{n} diagrams, no known silent-failure patterns")


if __name__ == "__main__":
    main()
