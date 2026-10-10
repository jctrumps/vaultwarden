# 03 — Native Linux workstation

Commands for Debian/Ubuntu-based workstations:

```bash
sudo apt update && sudo apt install -y git curl openssh-client ansible unzip
# Install OpenTofu from https://opentofu.org/docs/intro/install/
# Verify:
tofu version
ansible --version
mkdir -p ~/projects && cd ~/projects
git clone https://github.com/YOUR-USERNAME/REPOSITORY.git
cd REPOSITORY
```

On Fedora/Arch, use the native package manager and official OpenTofu installer. Continue with [SSH](04-ssh.md) and the deployment guides. Work as an ordinary local user; use sudo only for operations requiring privilege.
