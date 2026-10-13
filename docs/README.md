# Documentation index

## Start here

1. [Canonical Windows CMD → OpenTofu → WSL → Ansible onboarding](windows-wsl-ansible.md)
2. [Manual Cloudflare Tunnel](cloudflare-tunnel.md), after internal health works
3. [First login and account restrictions](first-run.md)
4. [Backup and restore exercise](backup-restore.md)
5. [Daily deployment quick reference](daily-deployment.md)

Native Linux operators use [Linux deployment](linux-deployment.md) instead of the Windows onboarding guide.

## References and maintenance

- [Architecture and boundaries](architecture.md)
- [Prerequisites and template checklist](prerequisites.md)
- [SSH key handling and rotation](ssh-keys.md)
- [OpenTofu inputs, outputs and lifecycle](opentofu.md)
- [Ansible variables and secret handling](ansible.md)
- [Updates, logs and rollback](operations.md)
- [Troubleshooting by symptom](troubleshooting.md)
- [Public release and ZIP packaging](public-release.md)
- [Local validation report](validation-report.md)

The former numbered runbooks have been consolidated into these files. Inventory remains `ansible/inventory/hosts.yml`; no `.ini` inventory is created. The primary key remains `vault_01_ed25519`.
