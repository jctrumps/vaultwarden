provider "proxmox" {
  endpoint  = var.proxmox_endpoint
  api_token = var.proxmox_api_token
  insecure  = var.proxmox_insecure

  ssh {
    agent       = var.ssh_private_key_file == null
    username    = var.proxmox_ssh_user
    private_key = var.ssh_private_key_file == null ? null : sensitive(file(pathexpand(var.ssh_private_key_file)))
  }
}
