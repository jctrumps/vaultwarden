# Ansible configuration reference

Use [canonical onboarding](windows-wsl-ansible.md) for the complete command sequence. Run Ansible in **WSL / UBUNTU BASH** from `/mnt/c/projects/vaultwarden/ansible`, or in **NATIVE LINUX** from the checkout's `ansible/` directory.

| File | Role |
| --- | --- |
| `ansible.cfg` | Default `inventory/hosts.yml`, `roles_path = roles`, verified SSH host keys. |
| `inventory/hosts.example.yml` | Public YAML inventory; copy to ignored `inventory/hosts.yml` and set actual IP/user/WSL key path. |
| `requirements.yml` | `community.docker` 4.x, providing the Compose v2 module. |
| `docker-only.yml` | Install Docker/dependencies before setting private app configuration. |
| `site.yml` | Docker role, application deployment and readiness checks. |
| `roles/docker_host/` | Supported-OS check, cloud-init wait, apt repository/packages, Docker service and optional maintenance updates. |
| `roles/vault_app/` | Directories, shared Compose source, protected `.env`, persistent overrides, Compose health and HTTP checks. |

## Configuration selection and prerequisites

**WSL / UBUNTU BASH or NATIVE LINUX, `ansible/`:**

```bash
export ANSIBLE_CONFIG="$PWD/ansible.cfg"
ansible --version
ansible-galaxy collection install -r requirements.yml
ansible-inventory -i inventory/hosts.yml --graph
```

Select only a reviewed config in a trusted checkout. Explicit selection addresses `/mnt/c` automatic-discovery behavior, not underlying directory trust. Expect `config file` to reference this file and the graph to show `vault-vm` in `vault`. The guest must already have Python 3, sudo and working SSH; Ansible cannot bootstrap a missing remote Python using its normal modules.

## Variables

Set persistent, environment-specific overrides under `vault.vars` or the host in your ignored inventory. Values passed with `-e` override inventory for that invocation only. Examples:

```yaml
all:
  children:
    vault:
      vars:
        app_image_tag: "1.35.4"
        app_port: 8080
      hosts:
        vault-vm:
          ansible_host: 192.0.2.50
          ansible_user: debian
          ansible_ssh_private_key_file: ~/.ssh/vault_01_ed25519
```

| Variable | Default / behavior |
| --- | --- |
| `app_dir` | `/opt/vaultwarden`; absolute guest path, root-owned, mode `0700`. Changing it does not migrate existing data. |
| `app_image_tag` | `1.35.4`; pinned Vaultwarden release tag. |
| `app_bind_ip` | `127.0.0.1`; IPv4 guest bind address. Keep loopback for a same-VM tunnel. |
| `app_port` | `8080`; published guest port mapped to container port 80. |
| `docker_host_upgrade_packages` | `false`; set `true` explicitly during a maintenance window to apply safe apt upgrades. Reboots remain manual. |

The app role writes `APP_IMAGE_TAG`, `APP_BIND_IP` and `APP_PORT` into the guest `.env` so manual Compose commands use the same settings. Future Ansible runs reassert inventory/default values; keep deliberate overrides in inventory. Docker is installed with `state: present`; apt maintenance is a separate explicit choice.

## Runtime secrets

Create `/opt/vaultwarden/.env` **on the VM** using an editor over trusted SSH, as documented in [Phase F](windows-wsl-ansible.md#phase-f---configure-inventory-and-deploy-with-ansible). Start from [`docker/.env.example`](../docker/.env.example) and supply the actual HTTPS `DOMAIN`. Optional SMTP/admin secrets also belong there. The role enforces root ownership and `0600`, and does not copy secrets through the control machine. Secret-bearing tasks suppress log/diff output. A final nonsecret message reports the bind address and whether Compose changed.

No encrypted Ansible Vault file is required for this workflow, so no `--ask-vault-pass` is needed. Guest sudo may require `--ask-become-pass`; inventory private keys are independent of sudo passwords. Do not pass application secrets with `-e` on a command line.

## Reruns and failures

`site.yml` should converge with no needless container recreation. It waits for Compose health and `/alive`; failure leaves diagnostic state on the VM. Inspect `docker compose ps` and logs over SSH per [operations](operations.md). `--check` is a preview, not a first-deployment proof: required guest files/modules must exist, and health checks are skipped in check mode. Static syntax checks do not contact the host.

Next: [verification](windows-wsl-ansible.md#phase-g---verify-locally-before-public-access), [operations](operations.md), or [troubleshooting](troubleshooting.md).
