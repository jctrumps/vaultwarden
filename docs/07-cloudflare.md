# 07 — Manual Cloudflare Tunnel setup (NO secrets in this repository)

**No Cloudflare API resources or tunnel tokens are deployed by OpenTofu/Ansible.** Complete this separately in Cloudflare Zero Trust dashboard.

1. Confirm your domain is already in Cloudflare DNS. Choose a **new** hostname (for example `vault.example.com`); no real hostname is included in this project.
2. In Cloudflare Zero Trust → Networks → Tunnels, create a **Cloudflared** tunnel. Name it something descriptive. Choose **Linux / Debian/Ubuntu** for tunnel connector on **the SAME vault VM**.
3. Cloudflare presents connector install commands. Run these **privately on the vault VM**, following Cloudflare's current generated instructions. NEVER paste the connector token/credentials into git, terminal recordings, PRs, issue comments, Terraform variables or Ansible.
4. In the dashboard, create a public hostname mapping `vault.example.com` to service **HTTP** `http://127.0.0.1:8080` (localhost relative to the cloudflared service running on the SAME VM). No router port forwarding is required.
5. Verify `https://vault.example.com` shows your server login page. Confirm your DNS and HTTPS certificate are valid before enabling account creation.
6. Use the **same HTTPS hostname** in DOMAIN (including https://) and every Bitwarden client custom-server setting.

**Important:** Placing a blanket Cloudflare Access browser login page in front of the entire vault API can break native clients, syncing, and notifications. Restrict the admin endpoint separately when possible; do NOT casually create Access bypass rules without testing. Protect the application with its own strong MFA and rate limits. Keep the origin bound to localhost. Cloudflare tunnel connectivity is a transport mechanism, not a replacement for vault authentication.

If cloudflared runs on a **different VM**, `127.0.0.1` points at the wrong computer. You must design an authenticated private connection and carefully controlled internal origin before changing the binding; this repo documents same-VM only.
