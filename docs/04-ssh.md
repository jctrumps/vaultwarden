# 04 — Dedicated SSH key for this project

Run these commands inside **WSL Ubuntu** or **native Linux**:

```bash
mkdir -p ~/.ssh && chmod 700 ~/.ssh
ssh-keygen -t ed25519 -a 100 -f ~/.ssh/id_ed25519_vault_project -C "vault-project-key"
chmod 600 ~/.ssh/id_ed25519_vault_project
chmod 644 ~/.ssh/id_ed25519_vault_project.pub
cat ~/.ssh/id_ed25519_vault_project.pub
```

Choose a strong passphrase and store it outside this repo. Only paste the `.pub` key into the private `infra/terraform.tfvars` file. **Never** share the private key. When the VM is created:

```bash
ssh -i ~/.ssh/id_ed25519_vault_project ubuntu@192.0.2.50
```

Replace `ubuntu` and `192.0.2.50` with your chosen user/IP. Confirm the new SSH host fingerprint against Proxmox VM console before accepting; avoid disabling host-key checks. For key rotation, add the replacement public key, validate login, then remove the old public key and update your inventory/variables. Different deployments should use different keys.
