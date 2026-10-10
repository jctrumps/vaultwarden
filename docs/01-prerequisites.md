# 01 — Prerequisites and template checklist

1. Have an accessible Proxmox VE node and credentials for a **least-privilege** API token permitted to clone the chosen template, allocate a VM/disk and configure cloud-init. Create the token manually in Proxmox Datacenter → Permissions → API Tokens. Do not commit it. The Proxmox provider may additionally require node SSH access for some operations. See provider documentation for permissions.
2. Prepare Debian 12/13 or Ubuntu 24.04 cloud-init template; install `qemu-guest-agent`, enable its service, clean cloud-init machine state, make sure `openssh-server` exists and that SSH accepts public keys. Confirm its VM ID, storage pool, bridge and NIC naming.
3. Reserve a VM ID, static IP/CIDR and gateway; replace all documentation-only example values locally. Start with 2 vCPU, 2 GiB RAM and 20 GiB disk; adjust for usage.
4. Ensure outbound package, Docker registry and Bitwarden services connectivity; do not expose port 8080 publicly.
5. Workstation needs Git, OpenTofu, Ansible, SSH client; Windows users use WSL2 because native Ansible on Windows control nodes is unsupported.
6. Expect unattended VM creation to fail if template, cluster storage and provider permissions do not match. Review the OpenTofu plan carefully before approving.

**Cloud-init template compatibility:** this project expects the clone to preserve cloud-init support and `qemu-guest-agent`; check the template's initial boot and networking independently first.
