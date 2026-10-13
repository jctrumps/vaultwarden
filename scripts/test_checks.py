"""Regression checks for publishable-file scanning and configuration examples."""

import contextlib
import importlib.util
import io
from pathlib import Path
import re
import subprocess
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parent.parent
SPEC = importlib.util.spec_from_file_location("check_public", ROOT / "scripts/check-public.py")
SCANNER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(SCANNER)
BUILD_SPEC = importlib.util.spec_from_file_location("build_release", ROOT / "scripts/build-release.py")
BUILDER = importlib.util.module_from_spec(BUILD_SPEC)
BUILD_SPEC.loader.exec_module(BUILDER)


class PublicCheckTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        subprocess.run(["git", "init", "--quiet", str(self.root)], check=True)
        (self.root / ".gitignore").write_text((ROOT / ".gitignore").read_text())

    def write(self, name, text):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)

    def scan(self):
        output = io.StringIO()
        with patch.object(SCANNER, "ROOT", self.root), contextlib.redirect_stdout(output):
            result = SCANNER.main()
        return result, output.getvalue()

    def test_ignored_local_credentials_are_skipped(self):
        self.write("ansible/inventory/hosts.yml", "private inventory")
        self.write("opentofu/terraform.tfvars", 'proxmox_api_token = "' + "x" * 32 + '"')
        self.assertEqual(self.scan()[0], 0)

    def test_force_tracked_private_files_fail_without_showing_contents(self):
        for name in ["ansible/inventory/hosts.yml", "opentofu/custom.tfvars.json", "vm.tfstate.backup", "vault_01_ed25519", "ansible/vars.local.yml", "ansible/inventory/group_vars/vault.yml"]:
            self.write(name, "PRIVATE_CONTENT")
            subprocess.run(["git", "add", "-f", name], cwd=self.root, check=True)
        result, output = self.scan()
        self.assertEqual(result, 1)
        self.assertIn("ansible/inventory/hosts.yml", output)
        self.assertNotIn("PRIVATE_CONTENT", output)

    def test_untracked_secret_is_reported_without_showing_value(self):
        secret = "x" * 32
        self.write("accidental.txt", 'proxmox_api_token = "' + secret + '"')
        result, output = self.scan()
        self.assertEqual(result, 1)
        self.assertIn("accidental.txt:1", output)
        self.assertNotIn(secret, output)

    def test_examples_remain_publishable(self):
        for name in ["ansible/inventory/hosts.example.yml", "opentofu/terraform.tfvars.example", "docker/.env.example"]:
            self.write(name, (ROOT / name).read_text())
            result = subprocess.run(["git", "check-ignore", "--quiet", name], cwd=self.root)
            self.assertEqual(result.returncode, 1, name)
        self.assertEqual(self.scan()[0], 0)

    def test_deleted_tracked_file_does_not_crash(self):
        self.write("old.txt", "safe")
        subprocess.run(["git", "add", "old.txt"], cwd=self.root, check=True)
        (self.root / "old.txt").unlink()
        self.assertEqual(self.scan()[0], 0)

    def test_provider_lockfile_is_publishable(self):
        self.write("opentofu/.terraform.lock.hcl", "# Public provider checksums")
        result = subprocess.run(["git", "check-ignore", "--quiet", "opentofu/.terraform.lock.hcl"], cwd=self.root)
        self.assertEqual(result.returncode, 1)
        self.assertEqual(self.scan()[0], 0)

    def test_runtime_data_and_release_artifacts_are_ignored(self):
        for name in ["docker/data/config.json", "dist/vaultwarden-source.zip", "opentofu/vm.tfplan", "vault_01_ed25519"]:
            self.write(name, "private")
            result = subprocess.run(["git", "check-ignore", "--quiet", name], cwd=self.root)
            self.assertEqual(result.returncode, 0, name)


class ExampleTests(unittest.TestCase):
    def test_every_opentofu_variable_is_documented_in_example(self):
        declared = set(re.findall(r'variable\s+"([^"]+)"', (ROOT / "opentofu/variables.tf").read_text()))
        example = set(re.findall(r"^\s*(?:#\s*)?(\w+)\s*=", (ROOT / "opentofu/terraform.tfvars.example").read_text(), re.MULTILINE))
        self.assertEqual(declared, example)


class ReleaseTests(unittest.TestCase):
    setUp = PublicCheckTests.setUp
    write = PublicCheckTests.write

    def test_release_selection_excludes_private_working_files(self):
        public = {
            "README.md", "opentofu/main.tf", "opentofu/.terraform.lock.hcl",
            "docs/windows-wsl-ansible.md", "docs/daily-deployment.md",
            "docs/validation-report.md", "ansible/inventory/hosts.example.yml",
        }
        for name in public:
            self.write(name, "public source")
        for name in ["opentofu/terraform.tfvars", "opentofu/terraform.tfstate", "ansible/inventory/hosts.yml", "docker/.env", "docker/data/config.json", "vault_01_ed25519", "dist/old.zip"]:
            self.write(name, "private material")
        self.write("notes.txt", "unrelated local notes")
        with patch.object(BUILDER, "ROOT", self.root), patch.object(BUILDER.CHECK, "ROOT", self.root), contextlib.redirect_stdout(io.StringIO()):
            selected = set(BUILDER.source_files())
        self.assertEqual(selected, public | {".gitignore"})


if __name__ == "__main__":
    unittest.main()
