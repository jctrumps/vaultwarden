# Public release and source ZIP

Run this audit before publishing. A source archive must not contain your filled tfvars/inventory, state/plans, runtime `.env`, data, SSH keys, tunnel credentials or logs. Provider checksums in `.terraform.lock.hcl` are public and should be preserved.

## Review the checkout

**WINDOWS CMD, repository root:**

```bat
cd /d "C:\projects\vaultwarden"
git status --short
git diff --check
git diff
git check-ignore opentofu/terraform.tfvars ansible/inventory/hosts.yml
```

For a newly extracted ZIP, initialize a local repository first with `git init`. This does not publish anything. It lets the source-selection tools use Git ignore rules. Confirm private files are ignored and example files are present. Do not force-add ignored private files. `.gitignore` does not untrack already committed files: remove those from the index carefully, audit history and rotate exposed credentials.

## Validate and build the archive

Install Python 3 locally if needed using the official installer or `winget install --id Python.Python.3.13 --exact`, then reopen CMD. Follow [CONTRIBUTING](../CONTRIBUTING.md) for full checks.

**WINDOWS CMD, repository root:**

```bat
python scripts/check-public.py
python scripts/check-docs.py
python -m unittest discover -s scripts -p "test_*.py"
python scripts/build-release.py
```

Expected output: `dist/vaultwarden-source.zip`, an SHA-256 checksum and the exact included-file list. The ZIP has one top-level `vaultwarden/` directory. The builder uses tracked plus nonignored untracked source candidates, a supported-source-path filter, symlink rejection and the public-content check. Deleted source paths are omitted; `.git`, ignored files and runtime artifacts are not copied. It checks ZIP integrity after writing. Inspect the printed file list and extracted contents before sharing; heuristics cannot recognize every real hostname or credential.

In **WSL / UBUNTU BASH or NATIVE LINUX**, the same scripts run with `python3` from the repository root. Do not use a whole-directory ZIP command against a configured working tree.

## Staged review and history audit

After deliberately staging only reviewed source changes, use **WINDOWS CMD**:

```bat
git status --short
git diff --cached --stat
git diff --cached
```

Check every staged file for actual infrastructure details and credentials, including files that already existed in history. If [Gitleaks](https://github.com/gitleaks/gitleaks) is installed, run `gitleaks git .` for history and `gitleaks dir .` only against a **clean extracted source archive**, not a working tree containing intended private local configuration. Review findings privately. The bundled checker scans publishable current files, not Git history; successful scans reduce risk but do not prove secrets were never exposed.

Commit/push or create a GitHub repository only when you deliberately choose to publish. If a secret was exposed, revoke/rotate it and handle history cleanup; deleting the current file alone is insufficient. Keep infrastructure/state backups separate from the public source ZIP.
