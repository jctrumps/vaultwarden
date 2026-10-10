terraform {
  required_version = ">= 1.8.0"
  required_providers {
    proxmox = { source = "bpg/proxmox", version = "~> 0.86" }
  }
}
provider "proxmox" {
  endpoint  = var.proxmox_endpoint
  api_token = var.proxmox_api_token
  insecure  = false
  ssh { agent = true; username = var.proxmox_ssh_user }
}
resource "proxmox_virtual_environment_vm" "vault" {
  name      = var.vm_name
  node_name = var.node_name
  vm_id     = var.vm_id
  started   = true
  on_boot   = true
  agent { enabled = true }
  clone { vm_id = var.template_vm_id; full = true }
  cpu { cores = var.cpu_cores; type = "host" }
  memory { dedicated = var.memory_mb }
  disk { datastore_id = var.datastore_id; interface = "scsi0"; size = var.disk_gb }
  network_device { bridge = var.bridge; model = "virtio" }
  initialization {
    datastore_id = var.datastore_id
    user_account { username = var.vm_username; keys = [var.ssh_public_key] }
    ip_config { ipv4 { address = var.vm_ipv4_address; gateway = var.vm_ipv4_gateway } }
  }
}
output "vm_id" { value = proxmox_virtual_environment_vm.vault.vm_id }
output "vm_name" { value = proxmox_virtual_environment_vm.vault.name }
