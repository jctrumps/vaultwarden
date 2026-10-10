# 06 — Deploy Docker and Vaultwarden using Ansible

The Ansible role installs Docker Engine and the Compose plugin via Docker's apt repository. Supported targets are Debian/Ubuntu with a working SSH/cloud-init user and sudo. The app's environment file is created **manually on the VM** so it is never copied into repository history.

Create inventory from the template and adjust your target IP/user/key:

```bash
cp inventory/hosts.example.yml inventory/hosts.yml
nano inventory/hosts.yml
# This file is ignored by Git.
```

**First install Docker only:** Ansible's app role intentionally stops if private settings are missing; this prevents an insecure/default deployment. You can run the Docker role with:

```bash
ansible -i inventory/hosts.yml vault -m ping
ansible-playbook -i inventory/hosts.yml ansible/docker-only.yml
```

On the guest, first install Docker manually or use a one-off playbook limited to Docker role:

```bash
ansible -i inventory/hosts.yml vault -b -m apt -a 'name=ca-certificates,curl,gnupg update_cache=yes state=present'
# Preferred automated bootstrap, following a verified target OS:
ansible-playbook -i inventory/hosts.yml ansible/docker-only.yml
```

Create the private environment file on the VM, preferably over SSH. This path isn't committed to Git:

```bash
ssh -i ~/.ssh/id_ed25519_vault_project ubuntu@192.0.2.50
sudo mkdir -p /opt/vaultwarden
sudo nano /opt/vaultwarden/.env
sudo chmod 600 /opt/vaultwarden/.env
exit
```

See `docker/.env.example` for exact names. Set DOMAIN to exact HTTPS public address, default SIGNUPS_ALLOWED=false, and only enable registration temporarily after Cloudflare HTTPS is working. Avoid enabling the /admin route unless necessary.

Then on control workstation:

```bash
ansible-playbook -i inventory/hosts.yml ansible/site.yml --syntax-check
ansible-playbook -i inventory/hosts.yml ansible/site.yml --ask-become-pass
ssh -i ~/.ssh/id_ed25519_vault_project ubuntu@192.0.2.50 'sudo docker ps'
```

If cloud-init sudo is passwordless omit `--ask-become-pass`. The service binds only to **127.0.0.1:8080 on the VM**; it is not reachable directly over a LAN or WAN. To test through SSH from your workstation run `ssh -L 8080:127.0.0.1:8080 ...` then `curl -I http://127.0.0.1:8080`; do not create vault accounts over insecure HTTP—first configure HTTPS tunnel.

Configure `app_image_tag` explicitly in the Ansible play invocation or role defaults when upgrading. Do not use the default `latest` in production; pin the intended upstream release. To inspect containers on guest: `cd /opt/vaultwarden && sudo docker compose ps && sudo docker compose logs --tail=100` (logs may contain sensitive metadata).
