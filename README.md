# Vaultwarden on Proxmox (OpenTofu + Ansible + Docker)

Public, reusable infrastructure starter. Creates a **dedicated Debian/Ubuntu cloud-init VM** on Proxmox with OpenTofu; installs Docker and deploys Vaultwarden with Ansible. The Cloudflare Tunnel is **manually created and managed outside this repository**.

> SECURITY: A password vault is critical infrastructure. This is a review-and-customize starter, **not a security certification or tested production deployment**. Inspect the IaC, rehearse backup restoration, and validate HTTPS, MFA, access and update procedures before storing real credentials.

## Architecture

`Windows PowerShell -> WSL2 Ubuntu (or native Linux) -> OpenTofu -> Proxmox VM -> Ansible -> Docker Compose -> localhost:8080`  
`Bitwarden clients -> HTTPS Cloudflare public hostname -> manually configured tunnel on the SAME VM -> http://127.0.0.1:8080`

No cloudflared installation, tunnel token, Cloudflare API key, DNS zone, hostname, real IP, SSH private key, or Proxmox connection values are included. Example IP addresses use the documentation-only TEST-NET ranges.

## Start here (do not skip steps)

1. [Prerequisites & VM template](docs/01-prerequisites.md)
2. [Windows PowerShell and WSL2](docs/02-windows-wsl.md) or [native Linux workstation](docs/03-linux.md)
3. [Unique SSH key generation](docs/04-ssh.md)
4. [OpenTofu VM provisioning](docs/05-proxmox-opentofu.md)
5. [Ansible / Docker deployment](docs/06-ansible-docker.md)
6. [Cloudflare Tunnel: manual setup ONLY](docs/07-cloudflare.md)
7. [First login & account restrictions](docs/08-first-run-security.md)
8. [Backup and restore](docs/09-backup-restore.md)
9. [Updates, troubleshooting and publishing](docs/10-operations.md)

## Repository layout

```text
infra/        OpenTofu Proxmox provider, cloud-init VM, example variables
ansible/      Docker installation and application role
inventory/    Example Ansible inventory
docker/      Compose and nonsecret environment templates
 docs/        Detailed runbooks
 scripts/     Public-content safety and static checks
 .github/     GitHub Actions static/security checks
```

## Version policy

The Compose examples pin a known version by default (not `latest`), while the Ansible role allows an `app_image_tag` override. Review the upstream release notes, then update the pin consciously. Provider constraints must likewise be reviewed before first use.

## Links

- [Proxmox provider](https://registry.terraform.io/providers/bpg/proxmox/latest/docs)
- [OpenTofu](https://opentofu.org/docs/)
- [Ansible](https://docs.ansible.com/)
- [Docker Engine](https://docs.docker.com/engine/install/)
- [Cloudflare Tunnel](https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/)
- [Vaultwarden upstream repository](https://github.com/dani-garcia/vaultwarden)

## Disclaimer

Independent infrastructure example; not affiliated with or endorsed by Bitwarden, Vaultwarden, Proxmox, or Cloudflare. MIT license covers this repository's original deployment code and documentation, not third-party applications.
