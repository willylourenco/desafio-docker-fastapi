output "droplet_ip" {
  value       = digitalocean_droplet.servidor_app.ipv4_address
  description = "O IP Publico do servidor criado"
}