# Prerequisites and cloud-init template

## Proxmox web interface

Before running OpenTofu, record privately:

- API base HTTPS URL, target node, and optional distinct template node.
- API token with permission to clone the chosen template, allocate/configure/start the VM and allocate target storage. Review the [pinned provider documentation](https://registry.terraform.io/providers/bpg/proxmox/0.86.0/docs) for your Proxmox version's privileges. Token and user ACLs both matter when privilege separation is enabled.
- An unused VM ID, compatible datastore, bridge, static IPv4/CIDR, gateway and reachable DNS servers.
- A **Debian 13** (default) or **Ubuntu 24.04 LTS** cloud-init template. Match the template's actual disk interface and boot setup; the default is `scsi0` and the requested disk cannot be smaller than the template.

Prepare and test the template using your normal Proxmox template procedure before converting it to a template. The VM must contain `cloud-init`, `openssh-server`, `python3`, `sudo`, and `qemu-guest-agent`; the guest agent must start automatically. Clean cloud-init instance state before templating, and ensure clones generate unique machine identity and SSH host keys. Configure a working cloud-init administrative user with sudo and key-based SSH access. Verify that the template's network interface naming and disk expansion work on a test clone.

## Remote template or test-clone console

To diagnose an existing prepared template/test clone, execute in its **REMOTE VM console**:

```bash
command -v cloud-init python3 sudo
sudo systemctl status ssh --no-pager
sudo systemctl status qemu-guest-agent --no-pager
ip -br address
ip route
getent hosts download.docker.com
```

Install missing packages during your template build, not after converting an active production VM into a template. This project clones templates; it does not download/build the OS image for you.

## Workstation and connectivity

- Windows: native OpenSSH, Git, OpenTofu 1.8+, WSL2 Ubuntu 24.04+; Ansible runs inside WSL. Installation commands are in [Phase A](windows-wsl-ansible.md#phase-a---windows-prerequisites-and-project-ssh-key).
- Native Linux: [separate setup/deployment guide](linux-deployment.md).
- Workstation → Proxmox HTTPS API and workstation/WSL → guest TCP 22 must be reachable. Permit these through the relevant network/Proxmox/guest firewalls.
- Guest needs DNS, apt repositories and Docker registry access. The manually installed tunnel needs its documented outbound connectivity. Do not forward VM port 8080 from a router.
- Start with 2 vCPU, 2 GiB memory, 30 GiB disk; plan storage for attachments and encrypted offsite backups.

Next: [Windows onboarding](windows-wsl-ansible.md) or [Linux deployment](linux-deployment.md). Troubleshoot the template or network before retrying a failed clone; do not assume a partial apply produced a usable guest.
