# Contributing

Use focused changes with matching docs. Follow the primary CMD → native OpenTofu → WSL workflow; keep `docs/windows-wsl-ansible.md` canonical. Do not include credentials, actual inventory, hostnames, state, keys or unredacted logs. Original contributions are covered by [LICENSE](LICENSE); upstream applications keep their own licenses.

## Local source checks

Run against a clean clone/extracted source ZIP to avoid including local private configuration in recursive checks. Initialize extracted source with `git init` so ignore-aware checks work. Python 3, Git and native OpenTofu must be installed in Windows.

**WINDOWS CMD, repository root:**

```bat
python scripts/check-public.py
python scripts/check-docs.py
python -m unittest discover -s scripts -p "test_*.py"
tofu fmt -check -recursive opentofu
tofu fmt -check - < opentofu\terraform.tfvars.example
tofu -chdir=opentofu init -backend=false -input=false -lockfile=readonly
tofu -chdir=opentofu validate
```

**WSL / UBUNTU BASH**, after starting WSL from the checkout's `ansible/` directory:

```bash
export ANSIBLE_CONFIG="$PWD/ansible.cfg"
ansible-galaxy collection install -r requirements.yml
ansible-inventory -i inventory/hosts.example.yml --graph
ansible-playbook -i inventory/hosts.example.yml docker-only.yml --syntax-check
ansible-playbook -i inventory/hosts.example.yml site.yml --syntax-check
```

If ansible-lint is installed, run `ansible-lint --profile basic site.yml docker-only.yml` in the same directory. See CI for the validation dependency versions. On native Linux, run the same source checks with `python3` and native `tofu`, then the same Ansible commands from `ansible/`.

If Docker Compose 2.30+ is available on the validation machine, run this from the **repository root in WINDOWS CMD, WSL Bash or NATIVE LINUX**:

```text
docker compose --env-file docker/.env.example -f docker/compose.yml config --no-env-resolution --quiet
```

This parses configuration without the private runtime `.env` and starts no containers. Review Bash snippets with `bash -n`, Windows CMD syntax with the correct shell conventions, and all guide links using `check-docs.py`. Never validate changes by applying to a production VM.

Build a clean archive with `python scripts/build-release.py` (or `python3` on Linux), following [public release](docs/public-release.md). Update the [validation report](docs/validation-report.md) with checks actually performed and any limitations. For a vulnerability, use a private reporting channel such as enabled GitHub security advisories; do not include credentials or sensitive exploit details in public issues.
