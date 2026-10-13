variable "proxmox_endpoint" {
  type        = string
  description = "Proxmox API base URL, e.g. https://pve.example.com:8006/ (without /api2/json)."
  validation {
    condition     = can(regex("^https://[^/]+/?$", var.proxmox_endpoint))
    error_message = "Use an HTTPS base URL without an API path."
  }
}

variable "proxmox_api_token" {
  type        = string
  sensitive   = true
  description = "USER@REALM!TOKENID=SECRET; preferably set via TF_VAR_proxmox_api_token."
  validation {
    condition     = can(regex("^[^@[:space:]]+@[^![:space:]]+![^=[:space:]]+=[^[:space:]]+$", var.proxmox_api_token))
    error_message = "Use the complete USER@REALM!TOKENID=SECRET API token."
  }
}

variable "proxmox_insecure" {
  type        = bool
  default     = false
  description = "Skip Proxmox API TLS verification; prefer trusting the node's CA."
}

variable "proxmox_ssh_user" {
  type        = string
  default     = "root"
  description = "SSH user on the Proxmox node, not the guest VM."
}

variable "ssh_private_key_file" {
  type        = string
  default     = null
  description = "Optional local unencrypted Proxmox-node SSH key file. Null uses ssh-agent; guest SSH is configured in Ansible inventory."
  validation {
    condition     = var.ssh_private_key_file == null ? true : try(fileexists(pathexpand(var.ssh_private_key_file)), false)
    error_message = "ssh_private_key_file must be null or point to an existing local key file."
  }
}

variable "node_name" {
  type        = string
  description = "Target Proxmox node for the new VM; also the template node unless overridden."
}

variable "vm_id" {
  type = number
  validation {
    condition     = var.vm_id >= 100 && var.vm_id <= 999999999 && floor(var.vm_id) == var.vm_id
    error_message = "vm_id must be an integer between 100 and 999999999."
  }
}

variable "vm_name" {
  type = string
}

variable "template_vm_id" {
  type = number
  validation {
    condition     = var.template_vm_id >= 100 && var.template_vm_id <= 999999999 && floor(var.template_vm_id) == var.template_vm_id
    error_message = "template_vm_id must be an integer between 100 and 999999999."
  }
}

variable "datastore_id" {
  type        = string
  description = "Storage supporting VM disks and cloud-init, e.g. local-lvm."
}

variable "bridge" {
  type    = string
  default = "vmbr0"
}

variable "cpu_cores" {
  type    = number
  default = 2
  validation {
    condition     = var.cpu_cores >= 1 && floor(var.cpu_cores) == var.cpu_cores
    error_message = "cpu_cores must be a positive integer."
  }
}

variable "memory_mb" {
  type    = number
  default = 2048
  validation {
    condition     = var.memory_mb >= 512 && floor(var.memory_mb) == var.memory_mb
    error_message = "memory_mb must be an integer of at least 512 MiB."
  }
}

variable "disk_gb" {
  type        = number
  default     = 30
  description = "Disk size in GiB; must be at least the template's disk size."
  validation {
    condition     = var.disk_gb >= 1 && floor(var.disk_gb) == var.disk_gb
    error_message = "disk_gb must be a positive integer."
  }
}

variable "vm_ipv4_address" {
  type        = string
  description = "Static IPv4 CIDR, e.g. 192.0.2.50/24."
  validation {
    condition     = can(cidrnetmask(var.vm_ipv4_address))
    error_message = "vm_ipv4_address must be a valid IPv4 CIDR address."
  }
}

variable "vm_ipv4_gateway" {
  type = string
  validation {
    condition     = can(cidrnetmask("${var.vm_ipv4_gateway}/32"))
    error_message = "vm_ipv4_gateway must be an IPv4 address without a prefix."
  }
}

variable "vm_username" {
  type    = string
  default = "debian"
}

variable "vm_description" {
  type    = string
  default = "Vaultwarden managed by OpenTofu and Ansible"
}

variable "vm_tags" {
  type    = list(string)
  default = ["vaultwarden", "opentofu"]
}

variable "template_node_name" {
  type        = string
  default     = null
  description = "Source template node; null means node_name. Cross-node clones require compatible storage."
}

variable "cpu_type" {
  type    = string
  default = "host"
}

variable "disk_interface" {
  type        = string
  default     = "scsi0"
  description = "Must match the template system disk."
  validation {
    condition     = can(regex("^(scsi|sata|virtio)[0-9]+$", var.disk_interface))
    error_message = "Use a provider-supported disk interface such as scsi0."
  }
}

variable "cloud_init_datastore_id" {
  type        = string
  default     = null
  description = "Cloud-init disk storage; null uses datastore_id."
}

variable "guest_agent_enabled" {
  type    = bool
  default = true
}

variable "vm_started" {
  type    = bool
  default = true
}

variable "vm_on_boot" {
  type    = bool
  default = true
}

variable "boot_order" {
  type        = list(string)
  default     = []
  description = "Empty uses the provider/template boot selection; otherwise e.g. [scsi0]."
}

variable "dns_servers" {
  type        = list(string)
  default     = []
  description = "Guest DNS server IPs; empty inherits Proxmox/template DNS. Verify resolution before deploying."
  validation {
    condition     = alltrue([for server in var.dns_servers : can(cidrhost("${server}/32", 0))])
    error_message = "Each DNS server must be a valid IP address without a prefix."
  }
}

variable "dns_domain" {
  type        = string
  default     = null
  description = "Optional guest DNS search domain."
}

variable "ssh_public_key" {
  type        = string
  description = "Contents of the dedicated guest VM public key (not a file path)."
  validation {
    condition     = can(regex("^(ssh-ed25519|ssh-rsa|ecdsa-sha2-nistp[0-9]+) [A-Za-z0-9+/=]+( .*)?$", trimspace(var.ssh_public_key)))
    error_message = "Provide the full OpenSSH public key line from your .pub file."
  }
}
