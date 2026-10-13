# Operations, updates and rollback

Use [daily deployment](daily-deployment.md) for normal reruns. Application version changes and OS upgrades are maintenance operations: read upstream release notes, take an encrypted backup, and rehearse restoration first.

## Inspect running services

Open trusted SSH as described in onboarding. **REMOTE VM:**

```bash
sudo -i
cd /opt/vaultwarden
docker compose config --quiet
docker compose ps
docker compose port vaultwarden 80
docker compose logs --tail=100
curl -fsS http://127.0.0.1:8080/alive
df -h /opt/vaultwarden
```

Expected: healthy container, loopback port 8080 and HTTP 200. The directory is root-only, hence `sudo -i` before `cd`. Full `docker compose config` or `docker inspect` output may expose secrets; prefer `config --quiet` and focused inspection. Logs rotate at 10 MiB × 3 files per container. Use [troubleshooting](troubleshooting.md) if health fails.

## Application upgrade

1. Review [Vaultwarden releases](https://github.com/dani-garcia/vaultwarden/releases) and take a restorable [backup](backup-restore.md). Record the current image tag.
2. **WSL / UBUNTU BASH**, checkout `ansible/`: edit `inventory/hosts.yml` to set `app_image_tag` to the selected exact release under `vault.vars` or the host. Keep that change private. Do not use `latest`.
3. In the same shell:

```bash
export ANSIBLE_CONFIG="$PWD/ansible.cfg"
ansible-playbook -i inventory/hosts.yml site.yml --ask-become-pass
```

Omit the sudo flag for passwordless guest sudo. A new image tag is pulled if absent; Compose recreates as needed and waits for health. Verify HTTPS, client sync, MFA and attachments, then rerun for convergence. To refresh a deliberately reused tag, perform a reviewed `docker compose pull` on the guest before `docker compose up -d --wait`; immutable version tags are preferred.

For a manual update in a **REMOTE VM root shell**, edit `APP_IMAGE_TAG` in `/opt/vaultwarden/.env`, then:

```bash
cd /opt/vaultwarden
docker compose config --quiet
docker compose pull
docker compose up -d --wait
docker compose ps
```

Synchronize the chosen tag with Ansible inventory or the next playbook run will reassert its configured version. When changing the **repository default**, align `ansible/roles/vault_app/defaults/main.yml`, `docker/compose.yml`, `docker/.env.example` and the hash-command documentation. This repository deliberately keeps its reviewed 1.35.4 pin; assess upstream fixes before your production use.

## Guest OS updates

**WSL / UBUNTU BASH or NATIVE LINUX, checkout `ansible/`, during a maintenance window:**

```bash
export ANSIBLE_CONFIG="$PWD/ansible.cfg"
ansible-playbook -i inventory/hosts.yml site.yml -e docker_host_upgrade_packages=true --ask-become-pass
```

The role runs safe apt upgrades and reports `/var/run/reboot-required`; it does not reboot automatically. In a **REMOTE VM** session, use `sudo reboot` when scheduled, reconnect, then verify Docker health, `/alive` and cloudflared. Normal daily runs leave this upgrade option off. Distribution-release upgrades need a separate migration plan.

## Rollback

Vaultwarden can migrate SQLite on startup. An older image may not understand the new schema. Stop the upgraded service, restore the matching **pre-upgrade full backup** in an isolated verification environment, set the old tag in `.env` and inventory, and only cut back after validating login/items/attachments/MFA. Merely changing the tag is not a guaranteed rollback. Never attach two instances to the same data directory. See [restore procedure](backup-restore.md).
