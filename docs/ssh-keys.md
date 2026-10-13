# SSH key handling

The primary key is `vault_01_ed25519`. Generate it once in **WINDOWS CMD** following [Phase A](windows-wsl-ansible.md#phase-a---windows-prerequisites-and-project-ssh-key), place its `.pub` contents in OpenTofu `ssh_public_key`, and import its private half into WSL using [Phase D](windows-wsl-ansible.md#phase-d---import-the-matching-windows-private-key-into-wsl). Native Linux users generate it in their Linux home per [Linux deployment](linux-deployment.md).

| Location | Meaning |
| --- | --- |
| `%USERPROFILE%\.ssh\vault_01_ed25519` | Windows private key, outside Git. |
| `%USERPROFILE%\.ssh\vault_01_ed25519.pub` | Public key installed into the guest by cloud-init. |
| `$HOME/.ssh/vault_01_ed25519` inside WSL | Copy of that private key, directory `0700`, file `0600`. |
| `~/.ssh/authorized_keys` for the guest user | Authorized public keys; never store the client private key here. |
| WSL `~/.ssh/known_hosts` | Trusted server identities, separate from Windows known-hosts. |

## Confirm the key pair

**WINDOWS CMD:**

```bat
ssh-keygen -lf "%USERPROFILE%\.ssh\vault_01_ed25519.pub"
```

**WSL / UBUNTU BASH:**

```bash
ssh-keygen -y -f "$HOME/.ssh/vault_01_ed25519" | ssh-keygen -lf -
ssh-add -l
```

The public-key fingerprints should match. The first Bash command may ask for the private-key passphrase. This is a **client key** fingerprint; it differs from the **server host** fingerprint checked at first SSH login.

## Rotation or lost keys

Generate a new dedicated key with a new filename on the control workstation. In the existing trusted **REMOTE VM** session, edit `~/.ssh/authorized_keys` to add its public line, then validate a second SSH connection with the new key before removing the old public line. Update private tfvars `ssh_public_key`, inventory's key path, and the WSL key copy. Review the OpenTofu plan; changing cloud-init metadata alone is not guaranteed to rewrite an already initialized user's keys.

If no usable key remains, recover through the trusted Proxmox VM console using the template's recovery process. Never fix a host-key mismatch by disabling checking: confirm the new server fingerprint through the console before removing only the old target entry using `ssh-keygen -R "$VM_HOST"` in WSL.

Next: [SSH connectivity](windows-wsl-ansible.md#phase-e---establish-trusted-ssh-before-ansible) or [troubleshooting](troubleshooting.md).
