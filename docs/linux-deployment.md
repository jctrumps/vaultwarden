# Native Linux deployment

This is the separate path for a native Debian/Ubuntu workstation; it has no WSL dependency. Prerequisites: [tested Proxmox template and connectivity](prerequisites.md), sudo on the workstation and VM, and a repository checkout at `~/projects/vaultwarden`.

## 1. Workstation tools - native Linux

On Debian 13 or Ubuntu 24.04+, in **NATIVE LINUX Bash**:

```bash
sudo apt update
sudo apt install -y git curl openssh-client ansible python3 nano
curl --proto '=https' --tlsv1.2 -fsSL https://get.opentofu.org/install-opentofu.sh -o /tmp/install-opentofu.sh
less /tmp/install-opentofu.sh
```

After reviewing the official installer, run it using its documented Debian installation method:

```bash
bash /tmp/install-opentofu.sh --install-method deb
tofu version
ansible --version
cd ~/projects/vaultwarden
```

Expected: native OpenTofu 1.8+ and Ansible Core 2.16+. See [official OpenTofu installation](https://opentofu.org/docs/intro/install/) if your workstation uses another distribution or the installer prerequisites fail.

## 2. Dedicated key and VM - native Linux

Generate once; reuse the existing project key if present:

```bash
install -d -m 700 "$HOME/.ssh"
ssh-keygen -t ed25519 -a 100 -f "$HOME/.ssh/vault_01_ed25519" -C "vault-project-key"
chmod 600 "$HOME/.ssh/vault_01_ed25519"
cat "$HOME/.ssh/vault_01_ed25519.pub"
eval "$(ssh-agent -s)"
ssh-add "$HOME/.ssh/vault_01_ed25519"
cd ~/projects/vaultwarden/opentofu
test -f terraform.tfvars || cp terraform.tfvars.example terraform.tfvars
chmod 600 terraform.tfvars
nano terraform.tfvars
```

Use your actual node/template/storage/network values and the full public-key line. Default user is `debian`; match your chosen cloud-init user. For the API token, leave its tfvars assignment commented and use interactive OpenTofu input, or export it without recording it in shell history:

```bash
read -rsp 'Proxmox API token: ' TF_VAR_proxmox_api_token; echo
export TF_VAR_proxmox_api_token
tofu init
tofu fmt -check
tofu validate
tofu plan -out=vm.tfplan
```

Only after reviewing and approving the plan:

```bash
tofu apply vm.tfplan
tofu output
unset TF_VAR_proxmox_api_token
```

Saved-plan apply has no second confirmation. Restrict permissions on state/plans and keep encrypted backups. See [OpenTofu reference](opentofu.md) for variables, refresh, state recovery and destruction (the `tofu` subcommands are the same; use this Linux working directory).

## 3. Trusted SSH and inventory - native Linux

Use the **PROXMOX WEB INTERFACE → REMOTE VM console** to verify `sudo cloud-init status --wait`, `ip -br address`, and `sudo ssh-keygen -lf /etc/ssh/ssh_host_ed25519_key.pub`.

Back in **NATIVE LINUX**, replace these values with OpenTofu's IP/user outputs:

```bash
VM_HOST=192.0.2.50
VM_USER=debian
ssh -o IdentitiesOnly=yes -i "$HOME/.ssh/vault_01_ed25519" "$VM_USER@$VM_HOST"
```

Compare the server fingerprint with the console before accepting. In the **REMOTE VM** SSH session, verify `python3 --version` and `sudo -v`, then `exit`. Fix SSH before running Ansible; use [troubleshooting](troubleshooting.md) for network/key/sudo errors.

**NATIVE LINUX:**

```bash
cd ~/projects/vaultwarden/ansible
export ANSIBLE_CONFIG="$PWD/ansible.cfg"
ansible-galaxy collection install -r requirements.yml
test -f inventory/hosts.yml || cp inventory/hosts.example.yml inventory/hosts.yml
chmod 600 inventory/hosts.yml
nano inventory/hosts.yml
ansible-inventory -i inventory/hosts.yml --graph
ansible vault -i inventory/hosts.yml -m ping
ansible-playbook -i inventory/hosts.yml --syntax-check docker-only.yml
ansible-playbook -i inventory/hosts.yml docker-only.yml --ask-become-pass
```

Inventory must use the same IP, guest user and Linux key path. Expected: `vault-vm` under `vault`, `pong`, then no failed/unreachable tasks. Omit `--ask-become-pass` if guest sudo is passwordless.

## 4. App configuration and deployment

Connect using the same SSH command. **REMOTE VM:**

```bash
sudo install -d -m 700 /opt/vaultwarden
sudo touch /opt/vaultwarden/.env
sudo chmod 600 /opt/vaultwarden/.env
sudo nano /opt/vaultwarden/.env
```

Fill from [`docker/.env.example`](../docker/.env.example), using your actual intended HTTPS `DOMAIN`, `SIGNUPS_ALLOWED=false`, and `INVITATIONS_ALLOWED=true`. Save and `exit` to the workstation.

**NATIVE LINUX, still in the checkout's `ansible/`:**

```bash
ansible-playbook -i inventory/hosts.yml --syntax-check site.yml
ansible-playbook -i inventory/hosts.yml site.yml --ask-become-pass
ssh -o IdentitiesOnly=yes -i "$HOME/.ssh/vault_01_ed25519" "$VM_USER@$VM_HOST"
```

In the **REMOTE VM**, run `sudo docker ps` and `curl -fsS http://127.0.0.1:8080/alive`. Verify port/mount/health using the remote commands in [Phase G](windows-wsl-ansible.md#phase-g---verify-locally-before-public-access); those commands execute on the guest and are independent of WSL. Rerun `site.yml` to check convergence, then proceed to [manual Cloudflare](cloudflare-tunnel.md), [first login](first-run.md), and [backup/restore](backup-restore.md).

For subsequent deployments: return to `~/projects/vaultwarden/ansible`, export the config, unlock the key in an agent, ping, and rerun the playbook. No Windows profile resolution or mounted Windows directory is involved.
