# 05 — Provision the VM with OpenTofu

Prerequisites: read 01–04; create least-privilege Proxmox token **outside Git**. Cloud-init VM template must be operational. In WSL/Linux terminal from repo root:

```bash
cp infra/terraform.tfvars.example infra/terraform.tfvars
nano infra/terraform.tfvars
```

Edit node, template ID, datastore, bridge, username, static IP/CIDR and gateway. Replace `ssh_public_key` with the entire line printed from your **dedicated** `.pub` file. Never commit terraform.tfvars. Export the token securely for this terminal session (the input is hidden):

```bash
read -rsp 'Proxmox API token (USER@REALM!TOKENID=SECRET): ' TF_VAR_proxmox_api_token; echo
export TF_VAR_proxmox_api_token
cd infra
tofu init
tofu fmt -check
tofu validate
tofu plan -out=vm.tfplan
tofu apply vm.tfplan
cd ..
unset TF_VAR_proxmox_api_token
```

> Token may enter the local shell environment and state; do not use this shell for untrusted processes. Keep state **local and protected** or configure a secure remote backend with locking and encryption for team use. State files and plans can include sensitive values and must NEVER be committed. Avoid showing secrets in CI logs.

On the Proxmox VM console confirm cloud-init applied IP and authorized keys. Test SSH with commands in 04. To remove a test VM: run `tofu plan -destroy` then `tofu destroy` from `infra/` after confirming you're targeting the correct VM. **Destruction erases vault data; first export/restore backups.**

Known variations: clones can require different disk interface, storage or initialization datastore depending on template. Change variables and provider schema only after consulting the provider version docs; validate before apply.
