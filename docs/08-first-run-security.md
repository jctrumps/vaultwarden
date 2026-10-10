# 08 — First login and hardening

1. Do not create accounts until public HTTPS and custom domain are working.
2. Vaultwarden starts with `SIGNUPS_ALLOWED=false`; temporarily change it to `true` in private `.env`, restart using `docker compose up -d --force-recreate`, create the initial user account over HTTPS, then revert to `false` and recreate again.
3. Set long unique master passwords and enable MFA for each user. Preserve MFA recovery codes in a safe offline location.
4. Test desktop/mobile Bitwarden clients using **self-hosted server** option and the exact HTTPS URL; validate sync across devices.
5. For family sharing, create an organization and collections and assign least privileges; verify subscription entitlements for official Lite.
6. Never rely only on a VM snapshot for backup. Make encrypted offsite copies and practice a full restore to a separate isolated test machine.
7. Disable app registration when onboarding is finished. Remove stale members promptly and review logs sparingly (may contain private metadata).
8. Protect SSH with key authentication and verified host keys; configure VM OS security updates and an appropriate firewall; block inbound access to Docker's local HTTP port.
9. Configure SMTP separately if you need email verification, emergency access or invitations. Don't assume these features work without mail configuration.

**Do not confuse master passwords, administrative tokens and installation keys.** Keep all separate, securely stored and never in screenshots/public support questions.
