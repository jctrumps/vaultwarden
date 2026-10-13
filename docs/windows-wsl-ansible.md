# First deployment: Windows CMD, OpenTofu, WSL, SSH, Ansible

This is the canonical first-run procedure. The repository stays at `C:\projects\vaultwarden`; **OpenTofu runs natively in Windows CMD**, then Ansible runs in WSL Ubuntu from `/mnt/c/projects/vaultwarden/ansible`. Adjust the checkout path consistently if yours differs. Shell labels are part of the instructions.

Default target: Debian 13, 2 vCPU, 2 GiB RAM, 30 GiB disk, user `debian`. Ubuntu 24.04 LTS is supported by selecting its template and setting `vm_username` and inventory accordingly. The WSL distribution and VM OS are independent. All shown IPs are documentation-only; supply your reachable VM address.

## Phase A - Windows prerequisites and project SSH key

**Purpose:** prepare the control machine and one dedicated guest-access key. **Prerequisites:** Windows 11 or Windows 10 with WSL2 support, internet access, and administrator access for installing tools. Review [Proxmox prerequisites](prerequisites.md) before provisioning.

**WINDOWS CMD — install missing tools:**

```bat
winget install --id Git.Git --exact
winget install --id OpenTofu.Tofu --exact
```

Close/reopen CMD after installation. Windows OpenSSH Client must be installed through **Windows Settings → System → Optional features → Add an optional feature → OpenSSH Client** if `where ssh` fails. On Windows 10, Optional features is under Apps. Git and OpenTofu can also be installed using their official installers if WinGet is unavailable.

**WINDOWS CMD, opened as Administrator — install WSL if missing:**

```bat
wsl --install -d Ubuntu
wsl --update
wsl --list --verbose
```

Restart if requested, launch Ubuntu once, and create its Linux username and password. Return to CMD with `exit`. Use Ubuntu 24.04 or newer for the WSL control environment.

**WINDOWS CMD — verify and select the normal WSL distribution:**

```bat
where ssh
ssh -V
where tofu
tofu version
git --version
wsl --list --verbose
wsl --set-default Ubuntu
```

Use your actual Ubuntu distribution name if it is versioned. Expected: a Windows `tofu.exe` (OpenTofu 1.8+), working OpenSSH/Git, and Ubuntu listed as WSL version 2. Do not select `docker-desktop` as the development distribution. No Windows Docker installation is needed for deployment; Docker is installed on the VM.

Extract the supplied source ZIP to `C:\projects\vaultwarden`, or clone your chosen repository there with Git. You should have `opentofu`, `ansible`, `docker`, and `docs` directly under that directory, not an extra nested `vaultwarden` folder.

**WINDOWS CMD — generate the project key once:**

```bat
if not exist "%USERPROFILE%\.ssh" mkdir "%USERPROFILE%\.ssh"
ssh-keygen -t ed25519 -a 100 -f "%USERPROFILE%\.ssh\vault_01_ed25519" -C "vault-project-key"
dir "%USERPROFILE%\.ssh\vault_01_ed25519*"
type "%USERPROFILE%\.ssh\vault_01_ed25519.pub"
```

Choose a passphrase at the prompt. If this key already exists, reuse it rather than overwriting it. The `.pub` line goes into cloud-init via OpenTofu. `vault_01_ed25519` without `.pub` is the private key: keep it outside the checkout and never copy it to the server or commit it. Phase D copies this same private key to WSL; generating a different key there would not match cloud-init.

**Check/recovery:** two key files must exist, and the displayed public key must start with `ssh-ed25519`. Fix missing tools or PATH before continuing. For key recovery/rotation see [SSH keys](ssh-keys.md). **Next:** Phase B.

## Phase B - Provision using native Windows OpenTofu

**Purpose:** clone the dedicated VM and establish the IP/user handoff. **Prerequisites:** a tested cloud-init template, appropriate API-token privileges, reserved VM ID/address, storage, gateway and DNS from [prerequisites](prerequisites.md).

**WINDOWS CMD:**

```bat
cd /d "C:\projects\vaultwarden\opentofu"
if not exist terraform.tfvars copy terraform.tfvars.example terraform.tfvars
notepad terraform.tfvars
```

Replace every environment-specific example: endpoint, token, node/template, VM ID/name, datastore, bridge, IP/CIDR, gateway, DNS, and username. Set disk size at least as large as the template's disk. Paste the entire Phase A public-key line into `ssh_public_key`.

The API token format is `USER@REALM!TOKENID=SECRET`. The example assignment is commented: leave it commented to let OpenTofu request the value interactively, or fill it in **only in your ignored private tfvars using the editor**. Managed secret injection through `TF_VAR_proxmox_api_token` is also supported; tfvars takes precedence. Avoid typing credentials in CMD command arguments/history. Sensitive variables are redacted from normal plan output, but state and saved plans can contain secrets.

`proxmox_insecure=false` verifies API TLS; trust the Proxmox CA in Windows. Explicitly setting it to `true` skips that verification. `ssh_private_key_file` is for optional **Proxmox-node** SSH, not guest access; normal clone operations may not need node SSH. Leave `null` for the native Windows SSH agent, or supply a provider-supported unencrypted node-key file using a Windows forward-slash path. See [OpenTofu reference](opentofu.md).

**WINDOWS CMD — validate and review the plan:**

```bat
tofu init
tofu fmt -check
tofu validate
tofu plan -out=vm.tfplan
```

Expected: formatting/validation succeed and the plan creates the intended VM. If formatting fails, run `tofu fmt` locally and review the changes. If a plan unexpectedly replaces/deletes a VM, stop and investigate state, template and variables. Preserve `.terraform.lock.hcl` in version control; protect local state/plans and private tfvars with your Windows account permissions and encrypted backups.

**WINDOWS CMD — only after reviewing and approving the saved plan:**

```bat
tofu apply vm.tfplan
tofu output
tofu output -raw vm_ipv4_address
tofu output -raw vm_username
```

Applying a saved plan executes it without a second confirmation prompt. Run that command only when you approve its contents. The output IP is the configured static address, not proof that the VM is reachable. Record the address and username for Phases E/F. Inventory is **not** generated automatically.

**PROXMOX WEB INTERFACE → VM console:** confirm boot, then run these commands in the **REMOTE VM console**:

```bash
sudo cloud-init status --wait
ip -br address
ip route
getent hosts download.docker.com
sudo systemctl status ssh --no-pager
sudo systemctl status qemu-guest-agent --no-pager
sudo ssh-keygen -lf /etc/ssh/ssh_host_ed25519_key.pub
```

Record the ED25519 server fingerprint for Phase E. A template may have no console password. If the guest agent is running, an authorized administrator can instead open **PROXMOX WEB INTERFACE → node → Shell** and run `qm guest exec 2400 -- ssh-keygen -lf /etc/ssh/ssh_host_ed25519_key.pub`, replacing `2400` with the new VM ID. Check the successful command output for the fingerprint. If neither console nor agent access works, recover the template/VM through your trusted administration process before accepting an SSH prompt.

**Check/recovery:** cloud-init must finish, the chosen address/gateway and DNS must work, and SSH/guest agent must be running. Use [troubleshooting](troubleshooting.md) for token, template or network errors. Existing deployments must retain their original state; do not start an empty state against an existing VM. [OpenTofu lifecycle](opentofu.md) covers refresh and destructive cleanup. **Next:** Phase C.

## Phase C - Enter WSL directly from the Ansible directory

**Purpose:** keep this checkout as the Ansible working directory. **Prerequisites:** Ubuntu initialized in Phase A and the VM provisioned in Phase B.

**WINDOWS CMD:**

```bat
cd /d "C:\projects\vaultwarden\ansible"
wsl
```

**WSL / UBUNTU BASH:**

```bash
pwd
whoami
ls -la
ansible --version
```

Expected directory: `/mnt/c/projects/vaultwarden/ansible`. The Linux username need not match the Windows username. If necessary, run `cd /mnt/c/projects/vaultwarden/ansible`. If Ansible is not installed, install it **inside WSL**:

```bash
sudo apt update
sudo apt install -y ansible openssh-client curl nano git python3
ansible --version
```

**Check/recovery:** `ansible.cfg`, `requirements.yml`, `site.yml`, and `docker-only.yml` must be visible. Correct the directory or WSL distribution if they are missing. Ansible Core 2.16+ is recommended (Ubuntu 24.04 packages satisfy this). **Next:** Phase D.

## Phase D - Import the matching Windows private key into WSL

**Purpose:** give Linux OpenSSH a correctly permissioned copy of the existing key. **Prerequisites:** the Phase A key is still in the Windows profile; Windows interop is enabled in WSL.

**WSL / UBUNTU BASH:**

```bash
WIN_HOME="$(wslpath "$(cmd.exe /C 'echo %USERPROFILE%' | tr -d '\r')")"
echo "$WIN_HOME"
KEY_NAME="vault_01_ed25519"
install -d -m 700 "$HOME/.ssh"
ls -l "$WIN_HOME/.ssh/$KEY_NAME"
install -m 600 "$WIN_HOME/.ssh/$KEY_NAME" "$HOME/.ssh/$KEY_NAME"
ls -ld "$HOME/.ssh"
ls -l "$HOME/.ssh/$KEY_NAME"
eval "$(ssh-agent -s)"
ssh-add "$HOME/.ssh/$KEY_NAME"
ssh-add -l
```

`WIN_HOME` resolves the actual Windows profile; `$HOME` is the WSL Linux home. Expected permissions: `.ssh` is `drwx------` and the private key is `-rw-------`. Skip copying if the same correct key is already present in WSL. `install` replaces an existing destination, so confirm the source before using it to rotate keys.

Loading a key directly from `/mnt/c/Users/...` can produce `UNPROTECTED PRIVATE KEY FILE`: default Windows mount permissions may not honor Linux `chmod` semantics. Keep the Linux key in `$HOME/.ssh`. Passphrase entry at `ssh-add` is interactive; never put it in scripts or command arguments. Windows and Linux SSH agents are separate. A new agent session needs another `ssh-add`.

**Check/recovery:** `ssh-add -l` must list the project key. If Windows profile resolution fails, run `echo %USERPROFILE%` in CMD and convert that actual path using `wslpath` in Bash. See [SSH keys](ssh-keys.md) for fingerprint comparison. **Next:** Phase E.

## Phase E - Establish trusted SSH before Ansible

**Purpose:** verify the complete key/user/IP chain. **Prerequisites:** Phase B output values and trusted server fingerprint; Phase D key loaded.

**WSL / UBUNTU BASH — replace the example values with the OpenTofu outputs:**

```bash
VM_HOST=192.0.2.50
VM_USER=debian
ssh -o IdentitiesOnly=yes -i "$HOME/.ssh/$KEY_NAME" "$VM_USER@$VM_HOST"
```

Compare the initial ED25519 fingerprint with the one obtained from the VM console. If another host-key type is negotiated, inspect its corresponding `/etc/ssh/ssh_host_*_key.pub` in the trusted console. Accept only a matching fingerprint. WSL stores it in its own `~/.ssh/known_hosts`.

**REMOTE VM, inside that SSH session:**

```bash
whoami
python3 --version
sudo -v
sudo cloud-init status --wait
sudo systemctl is-active ssh
exit
```

`exit` returns to WSL. The guest user must have working sudo. Cloud-init images often use passwordless sudo with no password assigned; omit Ansible's `--ask-become-pass` in that case.

**Check/recovery:** do not continue until ordinary SSH works. `ssh -v -o IdentitiesOnly=yes -i "$HOME/.ssh/$KEY_NAME" "$VM_USER@$VM_HOST"` diagnoses identity selection; keep its output private. For IP/routing, DNS, firewall, username, public-key or fingerprint errors use the [troubleshooting table](troubleshooting.md). **Next:** Phase F.

## Phase F - Configure inventory and deploy with Ansible

**Purpose:** install Docker and deploy the app. **Prerequisites:** successful Phase E, intended public HTTPS hostname, and sudo access. All workstation commands below run in **WSL / UBUNTU BASH**, still in `/mnt/c/projects/vaultwarden/ansible`.

```bash
export ANSIBLE_CONFIG="$PWD/ansible.cfg"
ansible --version
ansible-galaxy collection install -r requirements.yml
test -f inventory/hosts.yml || cp inventory/hosts.example.yml inventory/hosts.yml
nano inventory/hosts.yml
```

Confirm `config file` points to this checkout's `ansible/ansible.cfg`. Windows-mounted directories may appear world-writable, causing Ansible to skip automatic discovery. Explicit `ANSIBLE_CONFIG` selects this **trusted, reviewed** project configuration; it does not make an untrusted directory safe. If you cannot establish trustworthy Windows ACLs for the checkout, use a clean reviewed copy in the native WSL filesystem, reinstall its local inventory, and set `ANSIBLE_CONFIG` there instead. Keys still belong in Linux `~/.ssh`.

Edit the existing YAML fields using the Phase B/E IP and username:

```yaml
all:
  children:
    vault:
      hosts:
        vault-vm:
          ansible_host: 192.0.2.50
          ansible_user: debian
          ansible_ssh_private_key_file: ~/.ssh/vault_01_ed25519
```

This file is ignored by Git. **The filename is `inventory/hosts.yml`, not `hosts.ini`.** `roles_path = roles` is already set in `ansible.cfg`.

```bash
ansible-inventory -i inventory/hosts.yml --list
ansible-inventory -i inventory/hosts.yml --graph
ansible vault -i inventory/hosts.yml --private-key "$HOME/.ssh/$KEY_NAME" -m ping
ansible-playbook -i inventory/hosts.yml --private-key "$HOME/.ssh/$KEY_NAME" --syntax-check docker-only.yml
ansible-playbook -i inventory/hosts.yml --private-key "$HOME/.ssh/$KEY_NAME" docker-only.yml --ask-become-pass
```

Expected: a `vault` group with `vault-vm`, then `SUCCESS` / `"ping": "pong"`. Ansible ping tests SSH and remote Python, not ICMP. A syntax check alone does not prove inventory or connectivity is correct. At `BECOME password`, use the **VM user's sudo password**, not the Windows/WSL password or key passphrase. Omit `--ask-become-pass` for passwordless sudo.

The application environment is intentionally managed **only on the VM**, a documented local-secret alternative to Ansible Vault. No `--ask-vault-pass` is required. Open SSH again from WSL:

```bash
ssh -o IdentitiesOnly=yes -i "$HOME/.ssh/$KEY_NAME" "$VM_USER@$VM_HOST"
```

**REMOTE VM:**

```bash
sudo install -d -m 700 /opt/vaultwarden
sudo touch /opt/vaultwarden/.env
sudo chmod 600 /opt/vaultwarden/.env
sudo nano /opt/vaultwarden/.env
```

Use [`docker/.env.example`](../docker/.env.example). At minimum, set your actual intended public HTTPS hostname and these registration settings:

```dotenv
DOMAIN=https://vault.example.com
SIGNUPS_ALLOWED=false
INVITATIONS_ALLOWED=true
```

Save, then `exit` to WSL. Keep `/admin` disabled unless needed; optional Argon2 token generation is explained in [first run](first-run.md). SMTP is required for mail-based workflows and is configured privately in this file.

**WSL / UBUNTU BASH:**

```bash
ansible-playbook -i inventory/hosts.yml --private-key "$HOME/.ssh/$KEY_NAME" --syntax-check site.yml
ansible-playbook -i inventory/hosts.yml --private-key "$HOME/.ssh/$KEY_NAME" site.yml --ask-become-pass
```

**Check/recovery:** recap should have `unreachable=0` and `failed=0`; Compose waits for container health and the role verifies `/alive`. `no hosts matched` is a failed setup even if Ansible exits without an error. Missing `.env` means finish the remote configuration step. Collection/role/sudo errors are covered in [troubleshooting](troubleshooting.md). **Next:** Phase G.

## Phase G - Verify locally before public access

**Purpose:** establish actual runtime readiness and persistence. **Prerequisites:** successful playbook recap; an SSH session to the VM opened as in Phase E.

**REMOTE VM:**

```bash
sudo systemctl is-active docker
sudo docker compose version
sudo -i
cd /opt/vaultwarden
docker compose config --quiet
docker compose ps
docker compose port vaultwarden 80
docker inspect "$(docker compose ps -q vaultwarden)" --format '{{json .Mounts}}'
docker inspect "$(docker compose ps -q vaultwarden)" --format '{{json .State.Health}}'
curl -fsS http://127.0.0.1:8080/alive
docker compose logs --tail=50
exit
exit
```

The first `exit` leaves the root shell; the second leaves SSH. Expected: Docker active, Vaultwarden healthy, published port **`127.0.0.1:8080`**, and `/opt/vaultwarden/data` mounted at `/data`. An HTTP 200 from `/alive` confirms internal health. Logs and container inspection can contain private metadata; inspect locally. Adjust the path/port only if you intentionally configured overrides.

**WSL / UBUNTU BASH — rerun to check convergence:**

```bash
ansible-playbook -i inventory/hosts.yml site.yml --ask-become-pass
```

Expected: no unnecessary container recreation or configuration changes. Package-cache refreshes can legitimately report changes; investigate repeated Compose changes. Runtime idempotence must be verified on your actual VM, not inferred from syntax checks.

**Check/recovery:** inspect Compose status/logs, disk space and `.env` if health fails. Resolve local health/port problems before adding Cloudflare. **Next:** [manual Cloudflare Tunnel](cloudflare-tunnel.md), then [first login](first-run.md) and [backup/restore](backup-restore.md).

## Phase H - Troubleshooting and subsequent deployments

**Purpose:** recover without guessing shell, path, inventory or identity. **Prerequisites:** identify which phase failed. Use the [symptom → cause → diagnostic → fix table](troubleshooting.md), then repeat that phase's check before advancing. Never disable host-key verification to bypass a failure.

For everyday use, follow [daily deployment](daily-deployment.md). For native Linux without WSL, use [Linux deployment](linux-deployment.md). Repository validation results and untested runtime assumptions are recorded in [validation report](validation-report.md).
