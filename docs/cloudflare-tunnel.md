# Manual Cloudflare Tunnel

**Prerequisite:** Vaultwarden is healthy inside the VM (`curl -fsS http://127.0.0.1:8080/alive` returns HTTP 200). Complete local verification before diagnosing public access. OpenTofu/Ansible do not create Cloudflare resources, tokens, DNS, Access policies or connector configuration.

## Dashboard and connector setup

1. **CLOUDFLARE DASHBOARD:** ensure your domain uses Cloudflare DNS. Choose a public hostname, illustrated here as `vault.example.com`.
2. **CLOUDFLARE DASHBOARD → Zero Trust → Networks → Tunnels:** create a Cloudflared tunnel and select the Linux connector installation instructions for Debian/Ubuntu.
3. **REMOTE VM, the same VM running Vaultwarden:** execute the dashboard's connector installation commands privately. They contain a tunnel token; do not put them in this repository, tfvars, Ansible inventory, shell recordings or a source ZIP. Follow Cloudflare's instructions for protecting/service-managing the connector.
4. **CLOUDFLARE DASHBOARD:** add a public hostname route for `vault.example.com`, service type **HTTP**, URL **`http://127.0.0.1:8080`**. The dashboard manages the required public DNS mapping. No router forwarding of port 8080 is needed.
5. **REMOTE VM:** edit `/opt/vaultwarden/.env` so `DOMAIN=https://vault.example.com` uses your actual public hostname. Recreate the container after a change (`sudo -i`, `cd /opt/vaultwarden`, `docker compose up -d --wait`).

Use a root hostname rather than a URL subpath: the repository's external `/alive` readiness check assumes a root-mounted application. The same HTTPS base URL belongs in all Bitwarden clients' self-hosted-server settings. Vaultwarden derives web links and relevant authentication URLs from `DOMAIN`; do not use the HTTP origin or VM IP as the public domain. Preserve WebSocket support for notifications and review any proxy/caching rules against the [Vaultwarden proxy guidance](https://github.com/dani-garcia/vaultwarden/wiki/Proxy-examples).

## Connector placement

The default port is bound to **VM loopback**. A connector installed on another host sees its own `127.0.0.1`, not this VM. Use the same-VM host service for this setup. A cloudflared container also has its own network namespace unless deliberately configured; the documented origin assumes a host service. A different-host design needs separately secured routing/reverse proxy/forwarding and an intentional bind/firewall change; simply changing the tunnel's origin to the VM IP will not reach a loopback-only port.

## Verification and Access

**REMOTE VM:**

```bash
sudo systemctl status cloudflared --no-pager
curl -fsS http://127.0.0.1:8080/alive
```

**WSL / UBUNTU BASH or NATIVE LINUX:**

```bash
curl -fsS https://vault.example.com/alive
```

Replace the example hostname. Expect successful HTTPS and a healthy origin, then open the web vault in a browser and test a Bitwarden client's self-hosted URL. Proceed to [first login](first-run.md) only after this works.

If enabling `/admin`, consider a manually configured Cloudflare Access policy restricted to that path and retain Vaultwarden's own strong admin token. A blanket interactive Access challenge across the vault API can break native clients, sync and notifications; test the intended client behavior before applying policies. Do not add unreviewed blanket bypass rules.

For a 502: verify local `/alive`, connector status, same-VM placement and the exact origin port. For HTTPS/DNS errors: check the dashboard route, DNS record and certificate. For client failures with a working browser: confirm `DOMAIN`, self-hosted URL, Access policy and WebSocket/proxy rules. Keep connector tokens and logs private. More diagnostics: [troubleshooting](troubleshooting.md).
