# 02 — Windows → WSL2 detailed walkthrough

Run the first commands in **Administrator PowerShell** (Start → type PowerShell → Run as administrator):

```powershell
wsl --install -d Ubuntu
wsl --update
wsl --list --verbose
```

Restart if prompted; launch **Ubuntu** from Start and set your Linux username/password. All remaining commands below run in the **Ubuntu WSL terminal**, not PowerShell:

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y git curl unzip gpg software-properties-common python3 python3-pip pipx openssh-client
sudo apt install -y ansible
# Install OpenTofu following the current official Debian/Ubuntu packages guide:
# https://opentofu.org/docs/intro/install/deb/
# For a quick verified alternative, use official release binaries/checksums.
# Confirm after installing OpenTofu:
tofu version
ansible --version
git --version
```

Clone **your fork/repository** inside the WSL Linux filesystem (faster and avoids Windows file-permission issues):

```bash
mkdir -p ~/projects && cd ~/projects
git clone https://github.com/YOUR-USERNAME/REPOSITORY.git
cd REPOSITORY
```

If reviewing an extracted ZIP instead, copy its folder into `~/projects` (e.g. from `/mnt/c/Users/YOUR_WINDOWS_USER/Downloads/REPOSITORY`). Use `pwd` and `ls -la` to check your working directory. Follow [SSH](04-ssh.md), [OpenTofu](05-proxmox-opentofu.md) and [Ansible](06-ansible-docker.md).

**Boundary reminder:** `C:\Users\...` paths belong to PowerShell; `/mnt/c/Users/...` is WSL's view. Generate and store private SSH keys in `~/.ssh` *inside WSL*, not the repo. `wsl --shutdown` from PowerShell stops WSL when needed.
