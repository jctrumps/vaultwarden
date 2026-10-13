# Validation report

## Scope

This alignment uses the supplied infrastructure-project generation standard: native Windows CMD OpenTofu, then WSL Ansible in the mounted checkout; one project key and YAML inventory; manual Cloudflare setup; source-only delivery.

Public README/layout conventions were reviewed for the `n8n-app`, `ai-paperclip`, and `bitwarden-lite` repositories. GitHub CLI was installed but unauthenticated, so the public pages/raw README files were retrieved over HTTPS instead. Compact `opentofu/`, `ansible/`, `docker/`, and detailed operator docs were retained; older conflicting workstation conventions were consolidated.

## Local checks executed

Validated on 2026-10-12 using Windows OpenTofu 1.12.0, Python 3.13, Docker Compose 5.1.2, and WSL Ubuntu with Python 3.12, Ansible Core 2.20.10, community.docker 4.8.9 and ansible-lint 26.10.0. A source-only export was used for recursive OpenTofu/YAML/Compose validation so local filled settings and existing state were excluded.

| Check | Result |
| --- | --- |
| `tofu fmt -check` for all source `.tf` files and example tfvars via standard input | Passed. |
| `tofu init -backend=false -input=false -lockfile=readonly` in clean export | Passed; installed the signed locked bpg/proxmox 0.86.0 provider without changing the lockfile. |
| `tofu validate` | Passed with the added VM, DNS, clone and boot inputs. Native Windows CMD execution of `tofu version` and `tofu validate` was also checked. |
| YAML parsing | Passed for 10 public YAML files, including playbooks/roles, examples, Compose and CI. |
| Ansible example inventory graph | Parsed `vault` group containing `vault-vm`. Only the example inventory was used. |
| `docker-only.yml` and `site.yml` syntax checks | Passed in WSL; no guest connections. |
| `ansible-lint --profile basic site.yml docker-only.yml` | Passed with zero lint findings. The existing public `app_*` variable names have scoped role-prefix exceptions to preserve inventory compatibility; internal registered values use role prefixes. |
| Compose example configuration | Passed without a private `.env`. Resolved loopback port 8080, `/data` bind mount and `/healthcheck.sh` were asserted. An empty DOMAIN was confirmed to fail configuration. |
| Documentation checks | 18 Markdown files checked for local links/anchors; CMD blocks checked for accidental Bash/PowerShell syntax. 43 Bash blocks passed `bash -n`; their deployment commands were not executed. |
| Regression suite | 9 tests passed: variable/example coverage, ignored-secret handling, forced-tracked private-file rejection, output redaction, publishable examples/lockfile, deleted paths, runtime-artifact exclusion and release source selection. |
| Public-content heuristic and Git whitespace checks | Passed. Private local files are excluded from scanning; secret values are not printed. |
| Source packaging | A 46-file source archive was built and integrity-checked; its file list includes the provider lockfile and required guides, and excludes filled tfvars/inventory, state/plans, keys, runtime data and Git internals. The final archive is rebuilt with this report. |

Windows CMD command blocks were reviewed for CMD syntax and path consistency; installation, SSH key creation and infrastructure mutation commands were not executed. The Bash backup/restore commands were syntax-checked only. The updated GitHub Actions workflow contains these static quality gates but has not been run on hosted GitHub during this review.

The public-content checker is heuristic and is not a full Git-history secrets audit. A dedicated history scan is still part of the operator's [publication review](public-release.md). OpenTofu's schema validation does not establish that a particular template, Proxmox version or API role is compatible at runtime.

## Operator-only verification

No live Proxmox API plan/apply, SSH login, Ansible deployment, Cloudflare change, container startup or restore drill is part of repository validation. Template compatibility, API privileges, actual cloud-init/DNS/SSH/sudo, image startup, runtime idempotence, public HTTPS/client behavior and full backup restoration require the operator's environment.

## Delivery and first use

The release helper creates `dist/vaultwarden-source.zip`, with a top-level `vaultwarden/` directory and prints its SHA-256. Start with [Windows CMD onboarding](windows-wsl-ansible.md), then use [daily deployment](daily-deployment.md).

Supply your API endpoint/token/TLS trust choice, node/template/storage/network details, unused VM ID, actual IP/gateway/DNS, guest username and matching public/private project key. Fill the ignored inventory manually using OpenTofu outputs. Create the remote `.env` with the real HTTPS domain and any optional SMTP/admin settings. Configure the tunnel manually only after local health works.
