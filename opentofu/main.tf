resource "proxmox_virtual_environment_vm" "vault" {
  name        = var.vm_name
  description = var.vm_description
  tags        = sort(var.vm_tags)
  node_name   = var.node_name
  vm_id       = var.vm_id
  started     = var.vm_started
  on_boot     = var.vm_on_boot
  boot_order  = var.boot_order

  agent {
    enabled = var.guest_agent_enabled
  }
  clone {
    vm_id        = var.template_vm_id
    node_name    = var.template_node_name
    datastore_id = var.datastore_id
    full         = true
  }
  cpu {
    cores = var.cpu_cores
    type  = var.cpu_type
  }
  memory {
    dedicated = var.memory_mb
  }
  disk {
    datastore_id = var.datastore_id
    interface    = var.disk_interface
    size         = var.disk_gb
  }
  network_device {
    bridge = var.bridge
    model  = "virtio"
  }
  initialization {
    datastore_id = coalesce(var.cloud_init_datastore_id, var.datastore_id)
    dynamic "dns" {
      for_each = length(var.dns_servers) > 0 || var.dns_domain != null ? [1] : []
      content {
        servers = var.dns_servers
        domain  = var.dns_domain
      }
    }
    user_account {
      username = var.vm_username
      keys     = [trimspace(var.ssh_public_key)]
    }
    ip_config {
      ipv4 {
        address = var.vm_ipv4_address
        gateway = var.vm_ipv4_gateway
      }
    }
  }

  lifecycle {
    precondition {
      condition     = var.vm_id != var.template_vm_id
      error_message = "vm_id must differ from template_vm_id."
    }
  }
}
