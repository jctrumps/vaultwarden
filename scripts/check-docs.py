#!/usr/bin/env python3
"""Check local Markdown link targets, anchors, and primary-shell conventions."""

from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parent.parent


def anchors(text):
    result = set()
    for heading in re.findall(r"^#+ (.+)$", text, re.MULTILINE):
        result.add(re.sub(r"[^\w\- ]", "", heading.lower()).replace(" ", "-"))
    return result


def main():
    failures = []
    files = [ROOT / "README.md", ROOT / "CONTRIBUTING.md", *sorted((ROOT / "docs").glob("*.md"))]
    for path in files:
        text = path.read_text(encoding="utf-8")
        for link in re.findall(r"\]\(([^)]+)\)", text):
            if "://" in link or link.startswith("mailto:"):
                continue
            target, _, anchor = link.partition("#")
            target_path = path.parent / target if target else path
            if not target_path.is_file():
                failures.append(f"{path.name}: missing {link}")
            elif anchor and anchor not in anchors(target_path.read_text(encoding="utf-8")):
                failures.append(f"{path.name}: missing anchor {link}")
        for block in re.findall(r"```bat\n(.*?)```", text, re.DOTALL):
            if re.search(r"\$env:|\$HOME|export |sudo |Set-Location|Copy-Item|chmod ", block):
                failures.append(f"{path.name}: non-CMD syntax in CMD block")
    for name in ["windows-wsl-ansible.md", "daily-deployment.md", "linux-deployment.md", "cloudflare-tunnel.md", "validation-report.md"]:
        if not (ROOT / "docs" / name).is_file():
            failures.append(f"Missing required guide: {name}")
    print("\n".join(failures) if failures else f"Documentation links and CMD conventions checked: {len(files)} files.")
    return int(bool(failures))


if __name__ == "__main__":
    sys.exit(main())
