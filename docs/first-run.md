# First login and account restrictions

Prerequisites: healthy internal application and working public HTTPS per [Cloudflare guide](cloudflare-tunnel.md). Registration starts disabled. Do not create vault accounts over plain HTTP.

## Create the initial account

**REMOTE VM, over trusted SSH:**

```bash
sudo -i
cd /opt/vaultwarden
nano .env
```

Temporarily set `SIGNUPS_ALLOWED=true`. Save, then execute in the same **REMOTE VM root shell**:

```bash
docker compose up -d --force-recreate --wait
```

**BROWSER:** visit your configured HTTPS domain and register the first account. Choose a strong unique master password. Then immediately set `SIGNUPS_ALLOWED=false` in the remote `.env` and run the same recreate command. Confirm unauthenticated registration is disabled.

Enable MFA for each account and preserve offline recovery codes. In Bitwarden desktop/mobile clients select the self-hosted server and the exact HTTPS domain; verify login and item sync between clients. For shared vaults use organizations/collections with appropriate member privileges. Configure SMTP privately in `.env` if email verification, invitations or emergency access are needed; these workflows should be tested, not assumed to work.

## Optional admin panel

The panel is disabled when `ADMIN_TOKEN` is absent. If needed, run in the **REMOTE VM**:

```bash
sudo docker run --rm -it ghcr.io/dani-garcia/vaultwarden:1.35.4 /vaultwarden hash
```

Supply a strong admin secret interactively. Put the generated Argon2 PHC string in the remote `.env` as a **single-quoted** value, matching the format in [`docker/.env.example`](../docker/.env.example). Single quoting prevents Compose from interpreting the `$` characters. Recreate the container and validate `/admin`. Keep the plaintext admin secret separate from user master passwords. Admin changes stored in `/data/config.json` can override environment settings; include that file in backups and inspect it if configuration seems ignored.

## Ready-for-use checks

Verify local port binding, client MFA/sync, disabled registration, functional mail workflows if enabled, and encrypted offsite backup restoration. Keep VM security updates and firewall policy maintained. Remove stale accounts promptly. [Back up and rehearse restore](backup-restore.md) before storing important credentials; snapshots alone are insufficient.
