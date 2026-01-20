resource "google_compute_network" "vpc_network" {
  name = "nebulus-network"
}

resource "google_compute_firewall" "allow_nebulus" {
  name    = "allow-nebulus-services"
  network = google_compute_network.vpc_network.name

  allow {
    protocol = "tcp"
    ports    = ["22", "80", "443", "3000", "8000", "8001", "8002", "8888", "11435"]
  }

  source_ranges = var.source_ranges
}

resource "google_compute_instance" "vm_instance" {
  name         = var.instance_name
  machine_type = var.machine_type
  zone         = var.zone

  boot_disk {
    initialize_params {
      image = "debian-cloud/debian-12"
      size  = 50
    }
  }

  network_interface {
    network = google_compute_network.vpc_network.name
    access_config {
      // Ephemeral public IP
    }
  }

  metadata = {
    ssh-keys = "${var.ssh_user}:${file(var.ssh_pub_key_path)}"
  }

  tags = ["nebulus-server"]
}
