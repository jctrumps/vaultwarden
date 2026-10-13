# Daily deployment quick reference

Complete [first-time Windows onboarding](windows-wsl-ansible.md) first. This assumes a running VM, filled `inventory/hosts.yml`, WSL key/known-host entry, installed collections, and a private `.env` on the VM.

## Windows CMD

```bat
cd /d "C:\projects\vaultwarden\ansible"
wsl
```

## WSL Ubuntu Bash

```bash
pwd
# Expected: /mnt/c/projects/vaultwarden/ansible
export ANSIBLE_CONFIG="$PWD/ansible.cfg"
ansible --version
KEY_NAME="vault_01_ed25519"
```

If an agent with this key is not already available (`ssh-add -l`), load it:

```bash
eval "$(ssh-agent -s)"
ssh-add "$HOME/.ssh/$KEY_NAME"
```

Then deploy and inspect status:

```bash
ansible vault -i inventory/hosts.yml -m ping
ansible-playbook -i inventory/hosts.yml --syntax-check site.yml
ansible-playbook -i inventory/hosts.yml site.yml --ask-become-pass
ansible vault -i inventory/hosts.yml -b --ask-become-pass -m ansible.builtin.command -a 'docker ps'
```

Omit both `--ask-become-pass` flags for passwordless guest sudo. Inventory already selects the private key. Expected: `pong`, recap with `failed=0` / `unreachable=0`, and a healthy container. If `pwd` is wrong, use `cd /mnt/c/projects/vaultwarden/ansible` before exporting config. Reinstall collections with `ansible-galaxy collection install -r requirements.yml` only when requirements change.

For an application version update, first follow [operations](operations.md) and [backup/restore](backup-restore.md); a normal rerun keeps the pinned image. [Troubleshooting](troubleshooting.md) explains failed checks.

## Optional infrastructure changes - Windows CMD

Exit WSL with `exit`, then use native CMD:

```bat
cd /d "C:\projects\vaultwarden\opentofu"
notepad terraform.tfvars
tofu init
tofu fmt -check
tofu validate
tofu plan -out=vm.tfplan
```

Review the entire saved plan. Only if you approve its effects, execute:

```bat
tofu apply vm.tfplan
tofu output
```

This saved-plan apply does not ask again. Transfer any IP/user changes to `ansible/inventory/hosts.yml`. See [OpenTofu lifecycle](opentofu.md) before refresh, state migration or destruction.
