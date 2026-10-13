#!/usr/bin/env python3
"""Package reviewed source, never a recursive copy of the working directory."""

import argparse
import hashlib
import importlib.util
from pathlib import Path
import sys
import zipfile

ROOT = Path(__file__).resolve().parent.parent
SPEC = importlib.util.spec_from_file_location("check_public", ROOT / "scripts/check-public.py")
CHECK = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CHECK)
ROOT_FILES = {"README.md", "CONTRIBUTING.md", "LICENSE", ".gitignore", ".gitattributes", ".editorconfig"}


def allowed(name):
    path = Path(name)
    if name in ROOT_FILES:
        return True
    if path.parts[0] not in {"opentofu", "ansible", "docker", "docs", "scripts", ".github"}:
        return False
    return path.suffix in {".tf", ".hcl", ".yml", ".md", ".py", ".sh", ".cfg", ".example"}


def source_files():
    if CHECK.main():
        raise ValueError("Public-content check failed; refusing to package.")
    result = []
    for name in sorted(CHECK.candidates()):
        path = ROOT / name
        if path.is_symlink() or any(parent.is_symlink() for parent in path.parents if parent != ROOT.parent):
            raise ValueError(f"Refusing source symlink: {name}")
        if path.is_file() and allowed(name):
            result.append(name)
    required = {"opentofu/.terraform.lock.hcl", "docs/windows-wsl-ansible.md", "docs/daily-deployment.md", "docs/validation-report.md"}
    if not required.issubset(result):
        raise ValueError(f"Missing required release files: {sorted(required - set(result))}")
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "dist/vaultwarden-source.zip")
    args = parser.parse_args()
    names = source_files()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(args.output, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for name in names:
            archive.write(ROOT / name, f"vaultwarden/{name}")
    with zipfile.ZipFile(args.output) as archive:
        if archive.testzip() is not None:
            raise ValueError("ZIP integrity check failed.")
        expected = {f"vaultwarden/{name}" for name in names}
        if set(archive.namelist()) != expected:
            raise ValueError("ZIP file list differs from reviewed source selection.")
    digest = hashlib.sha256(args.output.read_bytes()).hexdigest()
    print(f"Created {args.output} ({len(names)} source files)")
    print(f"SHA256 {digest}")
    print("Included files:")
    print("\n".join(names))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (OSError, ValueError) as exc:
        sys.exit(str(exc))
