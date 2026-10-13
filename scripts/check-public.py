#!/usr/bin/env python3
"""Check publishable files without reading ignored local secrets or printing values."""

from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parent.parent
PRIVATE_PATH = re.compile(
    r"(^|/)(settings\.env|\.env(?!\.example$)(?:\..*)?|"
    r".*\.tfvars(?:\.json)?|.*\.tfstate(?:\..*)?|.*\.(?:tfplan|plan)|"
    r"(?:id_rsa|id_ed25519)[^/]*|[^/]*_ed25519[^/]*|.*\.(?:pem|key|p12)|"
    r".*\.local\.ya?ml|inventory/(?![^/]+\.example\.yml$).+|"
    r"(?:data|backups|\.terraform)/.+)$"
)
SECRET = re.compile(
    r"BEGIN (?:OPENSSH|RSA|EC|DSA|ENCRYPTED) PRIVATE KEY|"
    r"^\s*(?:CF_TUNNEL_TOKEN|CLOUDFLARE_API_TOKEN|BW_INSTALLATION_KEY)\s*=\s*\S+|"
    r'^\s*proxmox_api_token\s*=\s*"[^" ]{18,}"',
    re.MULTILINE,
)


def git_files(*args):
    result = subprocess.run(
        ["git", "ls-files", "-z", *args], cwd=ROOT, check=True, capture_output=True
    )
    return set(result.stdout.decode("utf-8").rstrip("\0").split("\0")) - {""}


def candidates():
    return git_files("--cached") | git_files("--others", "--exclude-standard")


def main():
    try:
        names = candidates()
    except (OSError, subprocess.CalledProcessError):
        print("FAIL: run this check in a Git checkout with Git installed.")
        return 1

    failed = False
    for name in sorted(names):
        if PRIVATE_PATH.search(name):
            # Check tracked paths even if they have since been deleted locally.
            print(f"FAIL: potentially sensitive publishable file: {name}")
            failed = True
            continue
        path = ROOT / name
        if not path.is_file() or path.is_symlink():
            continue
        text = path.read_bytes().decode("utf-8", errors="replace")
        for match in SECRET.finditer(text):
            line = text.count("\n", 0, match.start()) + 1
            print(f"FAIL: potential embedded secret: {name}:{line} (value hidden)")
            failed = True
    if not failed:
        print("No obvious embedded secrets in publishable files; human review still required.")
    return int(failed)


if __name__ == "__main__":
    sys.exit(main())
