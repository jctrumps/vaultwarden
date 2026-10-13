# Vaultwarden on Proxmox

Provision a dedicated cloud-init VM with **OpenTofu in Windows CMD**, then deploy Vaultwarden with **Ansible in WSL Ubuntu** and Docker Compose. Vaultwarden is a self-hosted password-vault server compatible with Bitwarden clients. Cloudflare Tunnel and public DNS are configured manually.

**Start with [the Windows CMD → WSL deployment runbook](docs/windows-wsl-ansible.md).** It covers tools, one project SSH key, VM provisioning, inventory handoff, SSH verification, Ansible deployment, and health checks in order.

## Architecture and supported platforms

```text
Windows CMD + native OpenTofu -> Proxmox VE -> Debian 13 / Ubuntu 24.04 VM
Windows CMD: cd ansible, wsl -> WSL Ubuntu + SSH + Ansible -> Docker Compose
  Vaultwarden + persistent SQLite/attachments at /opt/vaultwarden/data
  VM 127.0.0.1:8080 -> container port 80
  Manually installed same-VM cloudflared -> public HTTPS hostname
```

Default guest: **Debian 13, 2 vCPU, 2 GiB RAM, 30 GiB disk**. Ubuntu 24.04 LTS is supported through a matching cloud-init template and username. Use WSL Ubuntu 24.04+ as the Windows control environment. A [separate native Linux guide](docs/linux-deployment.md) covers Linux workstations. See [architecture](docs/architecture.md).

## Prerequisites and Git-safe setup

You need a tested Proxmox cloud-init template with SSH, Python 3, sudo and running guest agent; a scoped API token; reserved VM ID/IP; suitable storage, bridge, gateway and DNS; and the workstation tools listed in [prerequisites](docs/prerequisites.md).

Provide real values only in ignored `opentofu/terraform.tfvars` and `ansible/inventory/hosts.yml`. Keep the private SSH key in the workstation's `.ssh` directory and the runtime `.env` on the VM. State/plans, runtime data, private inventories and release artifacts are ignored; the provider lockfile is preserved. Examples use documentation-only IPs and `example.com`.

## Start here, in order

1. [Windows CMD → native OpenTofu → WSL → Ansible first deployment](docs/windows-wsl-ansible.md), or [native Linux deployment](docs/linux-deployment.md).
2. [Verify the internal service and persistent mounts](docs/windows-wsl-ansible.md#phase-g---verify-locally-before-public-access).
3. [Configure Cloudflare Tunnel manually](docs/cloudflare-tunnel.md).
4. [Create the first account and restrict registration](docs/first-run.md).
5. [Back up and rehearse restoration](docs/backup-restore.md).

Then use [daily deployment](docs/daily-deployment.md), [operations/upgrades](docs/operations.md), and [troubleshooting](docs/troubleshooting.md). The [documentation index](docs/README.md) links all references, including OpenTofu inputs and Ansible variables.

## Quick reference after setup

**WINDOWS CMD:**

```bat
cd /d "C:\projects\vaultwarden\ansible"
wsl
```

**WSL / UBUNTU BASH**, from the mounted `ansible/` directory with the project key loaded in a Linux SSH agent:

```bash
export ANSIBLE_CONFIG="$PWD/ansible.cfg"
ansible vault -i inventory/hosts.yml -m ping
ansible-playbook -i inventory/hosts.yml site.yml --ask-become-pass
```

Omit `--ask-become-pass` for passwordless guest sudo. This project uses **`hosts.yml`, not `hosts.ini`**. The [daily reference](docs/daily-deployment.md) includes agent loading and status inspection; first-time operators must complete onboarding first.

## Verification and maintenance

- Local source checks: [contribution commands](CONTRIBUTING.md) and [actual validation report](docs/validation-report.md). Static validation is not a live deployment test.
- **REMOTE VM:** `sudo docker ps` and `curl -fsS http://127.0.0.1:8080/alive` check container/origin health. Verify loopback binding and the `/data` mount as described in onboarding.
- Verify public HTTPS and client sync after manual tunnel setup. Follow the pinned-version [upgrade/rollback process](docs/operations.md) and encrypted [backup/restore procedure](docs/backup-restore.md).
- Before sharing source or a ZIP, follow [public release](docs/public-release.md). The release helper selects source files instead of archiving the working directory recursively.

## Layout

```text
opentofu/          VM, provider, validated inputs, outputs, public provider lockfile
ansible/           Config, YAML inventory example, requirements, playbooks and roles
docker/            Single Compose definition and environment example
docs/              Canonical onboarding, daily deployment, references and report
scripts/           Public-content checks, doc checks, regression tests and ZIP builder
.github/workflows/ Static validation only
```

## Security and licensing

A password vault is critical infrastructure. Review the code, template, TLS/SSH trust, access controls and recovery procedure before storing real credentials. Keep registration disabled outside intentional onboarding; protect accounts with MFA. The local HTTP origin is not intended for direct public exposure. This repository is a reviewable deployment starter, not a production security certification.

Contributions: [CONTRIBUTING.md](CONTRIBUTING.md). Original IaC/documentation: [MIT license](LICENSE). Vaultwarden and other third-party software retain their own licenses. This project is independent of Bitwarden, Vaultwarden, Proxmox and Cloudflare.

References: [Vaultwarden](https://github.com/dani-garcia/vaultwarden), [OpenTofu](https://opentofu.org/docs/), [Proxmox provider](https://registry.terraform.io/providers/bpg/proxmox/0.86.0/docs), [Ansible](https://docs.ansible.com/), [Docker](https://docs.docker.com/engine/install/).
