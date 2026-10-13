output "vm_id" {
  value = proxmox_virtual_environment_vm.vault.vm_id
}

output "vm_name" {
  value = proxmox_virtual_environment_vm.vault.name
}

output "vm_ipv4_address" {
  description = "Configured guest IP for inventory; confirm reachability after cloud-init."
  value       = split("/", var.vm_ipv4_address)[0]
}

output "vm_username" {
  description = "Cloud-init login user for SSH and ansible_user."
  value       = var.vm_username
}

output "ssh_command" {
  description = "Run in WSL or native Linux after preparing the matching private key."
  value       = "ssh -o IdentitiesOnly=yes -i ~/.ssh/vault_01_ed25519 ${var.vm_username}@${split("/", var.vm_ipv4_address)[0]}"
}
