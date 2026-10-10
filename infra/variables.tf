variable "proxmox_endpoint" { type = string; description = "Example https://pve.example.invalid:8006/" }
variable "proxmox_api_token" { type = string; sensitive = true }
variable "proxmox_ssh_user" { type = string; default = "root" }
variable "node_name" { type = string }
variable "vm_id" { type = number }
variable "vm_name" { type = string }
variable "template_vm_id" { type = number }
variable "datastore_id" { type = string }
variable "bridge" { type = string; default = "vmbr0" }
variable "cpu_cores" { type = number; default = 2 }
variable "memory_mb" { type = number; default = 2048 }
variable "disk_gb" { type = number; default = 20 }
variable "vm_ipv4_address" { type = string; description = "CIDR, e.g. 192.0.2.50/24" }
variable "vm_ipv4_gateway" { type = string }
variable "vm_username" { type = string; default = "ubuntu" }
variable "ssh_public_key" { type = string; description = "Contents of a dedicated public key" }
