# Architecture

```text
Windows CMD + native OpenTofu -> Proxmox API -> dedicated cloud-init VM
Windows CMD: cd ansible, wsl -> WSL Ubuntu -> SSH/Ansible -> that VM
  Debian 13 (default) or Ubuntu 24.04 LTS
    Docker Engine + Compose
      Vaultwarden -> SQLite, attachments and keys in /opt/vaultwarden/data
      VM loopback 127.0.0.1:8080 -> container port 80
    Manually installed cloudflared host service
      HTTPS public hostname -> http://127.0.0.1:8080
```

OpenTofu manages one full clone from an existing template. Ansible manages Docker installation, app files and startup. The guest OS comes from the selected template, not the username. Defaults are 2 CPU cores, 2048 MiB RAM and a 30 GiB system disk. Disk capacity includes application data; attachments may require more. 1 GiB can work for small deployments but has less maintenance headroom.

The single Compose source is `docker/compose.yml`. Vaultwarden uses its embedded SQLite database, so no separate database service or published database port is needed. The bind mount `./data:/data` is relative to the deployed Compose directory, normally `/opt/vaultwarden`.

Cloudflare resources and credentials are not managed by IaC. A connector on another machine cannot reach this VM's loopback address. See [manual routing](cloudflare-tunnel.md).

This repository's MIT license applies to original deployment code and docs, not Vaultwarden or other upstream applications. Static checks are not proof of production readiness; see [validation report](validation-report.md). Next: [prerequisites](prerequisites.md) and [canonical onboarding](windows-wsl-ansible.md).
