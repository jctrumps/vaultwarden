# 09 — Backups and recovery exercise

**Warning:** Always protect vault backups as highly sensitive, even if vault contents are client-side encrypted. Backups include database, configuration, key material and attachments. Never commit them or place an unencrypted archive on shared cloud storage.

SQLite databases should not be naively copied while writing. The safe/simple starter procedure is a **brief maintenance outage**; plan an actual outage window:

```bash
ssh -i ~/.ssh/id_ed25519_vault_project ubuntu@192.0.2.50
cd /opt/vaultwarden
sudo docker compose down
# Save app directory (includes hidden files, DB, attachments and configuration):
sudo tar -C /opt -czf /root/vaultwarden-backup-$(date +%Y%m%d-%H%M%S).tar.gz vaultwarden
sudo docker compose up -d
sudo docker compose ps
```

Immediately encrypt the archive using a vetted encryption tool such as age/GPG and move encrypted output to a separately controlled offsite location. **Do not leave plaintext tar archives on the VM**; securely remove them according to your storage media policy. Set retention and automate only after thoroughly testing.

**Restore drill:** build an isolated VM with the same app image version; stop the container; restore the complete app tree to `/opt/vaultwarden` with owner/permissions checked; validate secrets and data; start the container; use a temporary DNS/hosts-based *HTTPS* test environment, log in to a test account and verify items, attachments and MFA recovery. Do not point two active servers at the same production vault or expose the restore clone publicly.

VM snapshots are supplemental, not sufficient. Document RPO/RTO, verify encrypted backup decryptability and rotate recovery credentials when a backup is lost.
