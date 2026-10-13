# Backup and restore

Back up the entire `/opt/vaultwarden` directory: Compose, hidden `.env`, `data/db.sqlite3` and associated files, attachments, sends, keys and `config.json`. Treat backups as highly sensitive. Use encrypted offsite storage and keep its recovery key separately. VM snapshots are supplemental.

## Consistent backup during a maintenance outage

Prerequisites: healthy deployment, approved short outage, enough disk space, and `age` installed (`sudo apt install age` on the **REMOTE VM**). Have an independently stored age recipient public key; its decryption key must remain outside this VM. In trusted SSH, enter a root shell on the **REMOTE VM**:

```bash
sudo -i
cd /opt/vaultwarden
umask 077
read -rp 'Backup age recipient public key: ' AGE_RECIPIENT
BACKUP="/root/vaultwarden-$(date +%Y%m%d-%H%M%S).tar.gz.age"
```

Stop writes, stream directly into encryption, and restart even if backup fails. Execute this block in the same **REMOTE VM Bash root shell**:

```bash
(
  set -euo pipefail
  trap 'docker compose up -d --wait' EXIT
  docker compose stop
  tar -C /opt -czf - vaultwarden | age -r "$AGE_RECIPIENT" -o "$BACKUP"
)
docker compose ps
ls -lh "$BACKUP"
```

Any failed tar/encryption command makes the subshell fail; treat the resulting file as incomplete and do not count it as a backup. The EXIT trap attempts to restore service; check health explicitly. Move only successfully verified encrypted archives offsite using your private backup transport. The archive is root-only; use your established privileged transfer process. Test decryption and restoration before deleting the VM copy, and define retention/RPO/RTO appropriate to your vault.

## Restore rehearsal

Use an isolated VM with no production tunnel and the same Docker/Compose setup. Transfer an encrypted archive and an authorized decryption identity securely outside the Git tree. Do not restore over the only working production data copy.

**REMOTE RESTORE VM, root Bash shell:**

```bash
sudo -i
umask 077
read -rp 'Encrypted backup path: ' BACKUP
read -rp 'Decryption identity file path: ' AGE_IDENTITY
set -o pipefail
age -d -i "$AGE_IDENTITY" "$BACKUP" | tar -tzf -
```

The listing must contain only the expected `vaultwarden/` tree. It can expose private filenames; inspect locally. Stop an existing test container before extraction and preserve its old data in a separate recovery location. On a fresh restore VM with no `/opt/vaultwarden` tree:

```bash
age -d -i "$AGE_IDENTITY" "$BACKUP" | tar -xzf - -C /opt
chown root:root /opt/vaultwarden /opt/vaultwarden/.env
chmod 700 /opt/vaultwarden /opt/vaultwarden/data
chmod 600 /opt/vaultwarden/.env
cd /opt/vaultwarden
nano .env
docker compose config --quiet
docker compose up -d --wait
docker compose ps
curl -fsS http://127.0.0.1:8080/alive
```

In `.env`, retain the backed-up application tag and change `DOMAIN` to an isolated test HTTPS hostname; inspect any `data/config.json` override too. Use a separately controlled HTTPS test route to verify account login, items, attachments and MFA recovery. Disable production SMTP/integration delivery during the drill. Never point two active servers at the same vault data or expose the clone via the production hostname. Remove temporary decryption keys according to your recovery policy.

Record the backup timestamp, image tag, restore result and measured recovery time privately. Rollback after a failed upgrade uses the matching pre-upgrade backup and version, as described in [operations](operations.md).
