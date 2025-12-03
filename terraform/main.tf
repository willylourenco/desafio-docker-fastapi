terraform {
  cloud {
    organization = "willy-devops-org" 
    
    workspaces {
      name = "desafio-docker-fastapi" 
    }
  }

  required_providers {
    digitalocean = {
      source  = "digitalocean/digitalocean"
      version = "~> 2.0"
    }
  }
}

# Configura o Provider com o Token (que virá de uma variável)
provider "digitalocean" {
  token = var.do_token
}

# 1. Recurso: Enviar sua chave SSH local para a DigitalOcean
resource "digitalocean_ssh_key" "minha_chave" {
  name       = "chave-terraform-fastapi"
  public_key = file("../chave_pem.pub") # Lê o arquivo que está na raiz do projeto
}

# 2. Recurso: O Servidor (Droplet)
resource "digitalocean_droplet" "servidor_app" {
  image    = "ubuntu-24-04-x64"
  name     = "droplet-fastapi-terraform"
  region   = "nyc1" # Ou a região que preferir
  size     = "s-1vcpu-512mb-10gb" # O mais barato ($4)
  
  # Adiciona a chave SSH que criamos acima para você poder acessar como root
  ssh_keys = [digitalocean_ssh_key.minha_chave.fingerprint]

  # --- CLOUD-INIT: O Script de Instalação Automática ---
  # Isso roda apenas uma vez, quando o servidor nasce.
  user_data = <<-EOF
    #!/bin/bash
    # Atualiza o sistema
    apt-get update
    
    # Instala o Docker
    curl -fsSL https://get.docker.com | sh
    
    # Instala o Docker Compose (Plugin)
    apt-get install -y docker-compose-plugin
    
    # Inicia o Docker
    systemctl start docker
    systemctl enable docker
  EOF
}