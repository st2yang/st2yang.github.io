#!/usr/bin/env python3
"""
Build script for the personal website.

Runs jemdoc, then applies post-processing for things jemdoc cannot emit:
HTML5 doctype, lang attribute, <main> landmark, <h1> for the page title,
nested-<p> unwrap, deprecated-attribute strip, and list coalescing.

Usage: ./build.py
"""

import os
import re
import subprocess
import sys

REPO = os.path.dirname(os.path.abspath(__file__))
HTML = os.path.join(REPO, "index.html")


def run_jemdoc():
    cmd = ["python3", "jemdoc.py", "-c", "site.conf", "index.jemdoc"]
    subprocess.run(cmd, cwd=REPO, check=True, stderr=subprocess.DEVNULL)


def post_process(s: str) -> str:
    # HTML5 doctype + lang attribute
    s = re.sub(
        r'<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1\.1//EN"\s*'
        r'"http://www\.w3\.org/TR/xhtml11/DTD/xhtml11\.dtd">\s*'
        r'<html xmlns="http://www\.w3\.org/1999/xhtml" xml:lang="en">',
        '<!DOCTYPE html>\n<html lang="en">',
        s, count=1, flags=re.S,
    )
    s = s.replace(
        '<meta http-equiv="Content-Type" content="text/html;charset=utf-8" />',
        '<meta charset="utf-8">',
    )

    # Unwrap invalid <p><h*></h*></p> and <p><p>...</p></p> (jemdoc auto-wraps
    # raw {{...}} blocks in <p>, which is invalid for block children).
    s = re.sub(r"<p>\s*(<h[1-6][^>]*>.*?</h[1-6]>)\s*</p>", r"\1", s, flags=re.S)
    s = re.sub(r"<p>\s*(<p[^>]*>.*?</p>)\s*</p>", r"\1", s, flags=re.S)

    # Strip deprecated attributes jemdoc emits
    s = re.sub(r'(width|height)="(\d+)px"', r'\1="\2"', s)
    s = s.replace('<td align="left">', '<td>')

    # Semantic upgrades
    s = s.replace('<h3>Yang Yang</h3>', '<h1>Yang Yang</h1>', 1)
    s = s.replace('<div id="layout-content">', '<main id="layout-content">', 1)
    s = s.replace('</div>\n<script', '</main>\n<script', 1)
    s = s.replace('</div>\n</body>', '</main>\n</body>', 1)
    s = s.replace('<table class="imgtable">',
                  '<table class="imgtable" role="presentation">')

    # Icon links: <a> already has aria-label, so nested <img> should be decorative.
    for label in ('Google Scholar', 'GitHub', 'LinkedIn'):
        s = s.replace(f' alt="{label}">', ' alt="">')

    # Performance hints on images
    s = s.replace(
        '<img src="assets/images/portrait.jpg" alt="Photo of Yang Yang"',
        '<img src="assets/images/portrait.jpg" alt="Portrait of Yang Yang" '
        'fetchpriority="high" decoding="async"',
    )
    s = re.sub(
        r'(<img src="assets/icon/[^"]+\.png")',
        r'\1 width="32" decoding="async"',
        s,
    )

    # Semantic email strikethrough
    s = s.replace('<del>yang5276 [at] umn.edu</del>',
                  '<s>yang5276 [at] umn.edu</s>')

    # Coalesce adjacent <ul>...</ul><ul>...</ul> into a single list. jemdoc
    # opens a new <ul> after each blank line between bullets, so each
    # publication becomes its own single-item list. Merging restores list
    # semantics for screen readers and SEO.
    s = re.sub(r'</ul>\s*<ul>', '', s)

    return s


def main():
    run_jemdoc()
    with open(HTML, "r") as f:
        s = f.read()
    with open(HTML, "w") as f:
        f.write(post_process(s))
    print("Built index.html")


if __name__ == "__main__":
    sys.exit(main())
