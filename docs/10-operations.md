# 10 — Updates, troubleshooting, publication

## Upgrade process

Read the upstream release notes and compatibility warnings. Back up and verify restore first. Update the desired tag in `ansible/roles/vault_app/defaults/main.yml` **and/or** the Compose `APP_IMAGE_TAG` override; keep app file and Ansible copy aligned. On VM:

```bash
cd /opt/vaultwarden
sudo docker compose config --quiet
sudo docker compose pull
sudo docker compose up -d
sudo docker compose ps
sudo docker compose logs --tail=50
```

The upstream images may run database migrations. Rollback can require restoring a matching-version backup, not merely pulling the old image.

## Troubleshooting

- `ansible ping` fails: confirm VM IP, SSH user, SSH public key, host fingerprint, and guest network.
- Proxmox token 403: verify least-privilege permissions for VM clone, datastore, cloud-init and node access.
- `docker compose` fails: Docker Engine/Compose missing or malformed private env file; inspect `sudo docker compose config` **without pasting its potentially secret output publicly**.
- HTTP origin unavailable: inspect `sudo docker compose ps`, container logs and `curl -I http://127.0.0.1:8080` on the guest.
- Tunnel 502: check cloudflared running **on same VM** and origin service is exactly `http://127.0.0.1:8080`.
- Mobile clients fail: confirm TLS, custom-server URL, no incompatible Cloudflare Access challenge, and web vault sync.
- Disk full: assess attachment/data size and logs, expand filesystem safely; never delete SQLite WAL files manually.

## Publish to GitHub

```bash
bash scripts/check-public.sh
# Also run tofu fmt -check -recursive infra and tofu validate in infra after tofu init.
git init
git add .
git status --short
git diff --cached --stat
# Examine every staged file before pushing; review all content for personal/private data.
git commit -m "Initial public self-hosted vault deployment starter"
# Create an empty repo on GitHub first, then:
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/REPOSITORY.git
git push -u origin main
```

Do not run `git add -f` on ignored secret files. Scan full Git history with a dedicated secret scanner before publish. If a secret was exposed, revoke/rotate it; deleting the file alone does not eliminate exposure from Git history.
