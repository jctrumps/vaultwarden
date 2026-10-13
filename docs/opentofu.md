# OpenTofu reference and lifecycle

First deployment follows [Windows onboarding Phase B](windows-wsl-ansible.md#phase-b---provision-using-native-windows-opentofu). This reference covers optional settings and later operations. The provider/resource address remains `proxmox_virtual_environment_vm.vault`; splitting files does not rename the resource in state.

## Inputs and local configuration

Every input appears in [`terraform.tfvars.example`](../opentofu/terraform.tfvars.example). Copy it to ignored `opentofu/terraform.tfvars` and edit locally. Do not commit your real infrastructure values.

| Inputs | Meaning / default |
| --- | --- |
| `proxmox_endpoint`, `proxmox_api_token` | HTTPS base URL and complete `USER@REALM!TOKENID=SECRET`; required. No `/api2/json` suffix. |
| `proxmox_insecure` | `false` verifies TLS; trust your CA in the workstation OS. `true` explicitly disables API certificate verification. |
| `proxmox_ssh_user`, `ssh_private_key_file` | Optional node SSH credentials for operations requiring SSH. Default user `root`, file `null` selects native OS agent. These do not configure guest SSH. |
| `node_name`, `template_node_name`, `template_vm_id` | Target node, optional source node (`null` means target), existing template ID. Cross-node cloning requires compatible storage and access. |
| `vm_id`, `vm_name`, `vm_description`, `vm_tags` | Unused ID, VM name, descriptive metadata; tags are sorted to avoid ordering drift. |
| `cpu_cores`, `cpu_type`, `memory_mb` | `2`, `host`, `2048`. CPU migration compatibility depends on your cluster. |
| `disk_gb`, `disk_interface`, `datastore_id` | `30` GiB, `scsi0`, required storage. Match the template disk and do not shrink it. |
| `cloud_init_datastore_id` | `null` uses the main datastore; override if cloud-init disk storage differs. |
| `guest_agent_enabled` | `true`; install/start the guest agent in the template first to avoid provider timeouts. |
| `vm_started`, `vm_on_boot`, `boot_order` | `true`, `true`, `[]`. Empty boot order uses provider/template selection; explicit list may be needed for a custom template. |
| `bridge`, `vm_ipv4_address`, `vm_ipv4_gateway` | `vmbr0` plus required static IPv4/CIDR and gateway. This configuration deliberately uses static IPv4 for a predictable inventory handoff. |
| `dns_servers`, `dns_domain` | `[]`, `null` inherit DNS when omitted. Set reachable resolver IPs/search domain where inherited configuration is unsuitable. |
| `vm_username`, `ssh_public_key` | `debian` and the full dedicated OpenSSH public-key line; Ubuntu users can choose `ubuntu`. |

Select the OS using the template. Changing the username does not install a different OS. Disk settings manage the template's single system/data disk; additional disks need an intentional resource/backup design. Templates with nondefault disk cache/discard/AIO settings must be reviewed against the provider's clone behavior before applying.

The maintained `bpg/proxmox` provider is constrained to the existing `0.86.x` compatibility line and locked at 0.86.0. Keep `.terraform.lock.hcl` under version control. Provider upgrades require schema/release-note review and an explicit lock update, rather than silently changing a deployed VM's provider. See the [validation report](validation-report.md) for the tool/provider checks actually performed.

For optional node SSH on Windows, passphrased keys require the **Windows** OpenSSH agent. In **Administrator Windows CMD**, `sc config ssh-agent start= demand` and `net start ssh-agent` enable/start the service; in regular CMD, `ssh-add` loads your separately authorized node key. A `ssh_private_key_file` value requires an unencrypted key format accepted by the provider; use forward slashes such as `C:/path/to/node-key` or `~/.ssh/node-key`, never a WSL `/home/...` path in native Windows OpenTofu. Ordinary cloning may not need SSH at all.

## Outputs and inventory handoff

**WINDOWS CMD, `C:\projects\vaultwarden\opentofu`:**

```bat
tofu output
tofu output -raw vm_ipv4_address
tofu output -raw vm_username
tofu output -raw ssh_command
```

Set `ansible_host` and `ansible_user` in `ansible/inventory/hosts.yml` to the first two outputs. `ssh_command` is for WSL/native Linux after key setup. Output values describe configuration; verify the actual guest through the Proxmox console and SSH. Neither output nor a successful apply proves DNS, sudo or application readiness.

## Plan, apply and refresh

**WINDOWS CMD — after changing private tfvars:**

```bat
cd /d "C:\projects\vaultwarden\opentofu"
tofu init
tofu fmt -check
tofu validate
tofu plan -out=vm.tfplan
```

Review before running `tofu apply vm.tfplan`. A saved-plan apply does not ask for confirmation again. Existing environments should compare all new defaults (including metadata, DNS and disk settings) with the intended live configuration before approval.

To inspect drift without changing VM configuration, use **WINDOWS CMD**:

```bat
tofu plan -refresh-only
```

Only if you approve updating local state to match observed infrastructure, run `tofu apply -refresh-only` and review its confirmation. This still accesses Proxmox; repository static checks do not run it.

## State and migration

Local state, state backups and plan files can hold sensitive material. Keep encrypted backups outside the source tree, restrict Windows ACLs, and use a secured locking/encrypted remote backend if multiple people manage the same deployment. Never operate one VM using independent state copies.

If renaming the old `infra/` directory, carry its ignored state and private tfvars plus its lockfile into `opentofu/`, then run `tofu init`. If extracting a new source ZIP over an existing deployment, preserve its private configuration/state separately first. An empty state does not adopt an existing VM; use an explicitly reviewed import/recovery procedure instead of retrying creates.

## Destruction is an explicit operator operation

Back up and rehearse restoration first. **Destroying the VM destroys the vault data on its disk.** Confirm the correct working directory/state, VM ID, endpoint and backup before proceeding.

**WINDOWS CMD — review only:**

```bat
cd /d "C:\projects\vaultwarden\opentofu"
tofu plan -destroy
```

Only when deliberately removing that VM, run `tofu destroy` and read the interactive confirmation. No CI/helper in this repository applies or destroys infrastructure. Next: [Ansible reference](ansible.md) or [daily deployment](daily-deployment.md).
