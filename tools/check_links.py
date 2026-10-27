#!/usr/bin/env python3
"""Check every internal link and image on the site actually resolves.

A broken link in documentation fails silently. Nothing warns, the build
succeeds, and the reader finds it at the moment they needed the page. This
site cross-links heavily between sections, and the pages are written by
several hands, so the links are exactly where a mistake survives.

Checks:
  - internal links like `page.html` or `../section/page.html` map to a real
    source file (`page.md`)
  - image sources exist on disk
  - heading anchors exist on the target page, because a link to a section
    that was renamed lands silently at the top instead

Usage: python3 tools/check_links.py
"""
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
LINK = re.compile(r"\[([^\]]*)\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
EXTERNAL = re.compile(r"^(https?:|mailto:|#)")


def slug(text):
    """just-the-docs/kramdown heading id: lowercase, punctuation dropped,
    spaces to hyphens."""
    t = text.strip().lower()
    t = re.sub(r"`|\*|_", "", t)
    t = re.sub(r"[^a-z0-9\s-]", "", t)
    # One hyphen per whitespace CHARACTER, not per run. Dropping punctuation
    # can leave two spaces where "(PoE / cable)" was, and kramdown turns those
    # into two hyphens. Collapsing them here reports working links as broken.
    return re.sub(r"\s", "-", t).strip("-")


def headings(md_path):
    out = set()
    for line in md_path.read_text(encoding="utf-8").splitlines():
        m = re.match(r"^#{1,6}\s+(.*)$", line)
        if m:
            out.add(slug(m.group(1)))
    return out


def main():
    pages = sorted(p for p in ROOT.rglob("*.md") if ".git" not in p.parts)
    heading_cache = {}
    problems = []
    links = images = 0

    for page in pages:
        rel = page.relative_to(ROOT)
        text = page.read_text(encoding="utf-8")
        # don't follow links inside fenced code blocks: they are examples
        text = re.sub(r"```.*?```", "", text, flags=re.S)

        for label, target in LINK.findall(text):
            is_img = f"![{label}]({target})" in page.read_text(encoding="utf-8")
            if EXTERNAL.match(target):
                continue
            path_part, _, anchor = target.partition("#")
            if not path_part:
                continue

            resolved = (page.parent / path_part).resolve()
            if is_img:
                images += 1
                if not resolved.exists():
                    problems.append(f"{rel}: image not found: {target}")
                continue

            links += 1
            # a .html link is served from the .md beside it
            src = resolved.with_suffix(".md") if resolved.suffix == ".html" else resolved
            if not src.exists():
                problems.append(f"{rel}: link target missing: {target}")
                continue
            if anchor:
                if src not in heading_cache:
                    heading_cache[src] = headings(src)
                if anchor not in heading_cache[src]:
                    problems.append(f"{rel}: no such heading: {target}")

    if problems:
        print("\n".join("  " + p for p in problems))
        print(f"\n{len(problems)} problem(s) across {len(pages)} pages")
        sys.exit(1)
    print(f"{links} internal links and {images} images across {len(pages)} pages, all resolve")


def demo():
    import tempfile
    d = pathlib.Path(tempfile.mkdtemp())
    (d / "a.md").write_text("# Title\n[ok](b.html)\n[bad](nope.html)\n", encoding="utf-8")
    (d / "b.md").write_text("# Other\n## A Section\n", encoding="utf-8")
    assert slug("## A Section") == "a-section", slug("## A Section")
    assert slug("`code` and punctuation!") == "code-and-punctuation"
    # the case that made this tool wrong before it was right
    assert slug("Prefer Ethernet (PoE / cable)") == "prefer-ethernet-poe--cable"
    assert "a-section" in headings(d / "b.md")
    print("self-check ok")


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        demo()
    else:
        main()
