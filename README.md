# Desafio Docker: Ambiente Multi-Container com FastAPI e PostgreSQL

Este projeto implementa um ambiente de desenvolvimento completo utilizando Docker e Docker Compose, consistindo em uma API de CRUD (FastAPI em Python) conectada a um banco de dados PostgreSQL.

O objetivo deste desafio é consolidar o conhecimento sobre `Dockerfile`, `docker-compose.yml`, redes customizadas, volumes para persistência de dados e gerenciamento de variáveis de ambiente para configurações sensíveis.

## Stack de Tecnologia

* **API (Serviço `app`):** Python 3.11 com [FastAPI](https://fastapi.tiangolo.com/) e SQLAlchemy.
* **Banco de Dados (Serviço `db`):** [PostgreSQL 15-Alpine](https://hub.docker.com/_/postgres).
* **Orquestração:** Docker Compose.

---

## Requisitos Cumpridos

O projeto atende a todos os requisitos do desafio:

1.  **Dockerfile Multi-stage & Alpine:** O `Dockerfile` utiliza um primeiro estágio (`builder`) baseado em `python:3.11-alpine` para compilar as dependências com as ferramentas de *build* necessárias. O estágio final (`final`) usa a mesma base `alpine` leve, mas copia apenas os pacotes pré-compilados e o código-fonte, resultando em uma imagem final leve e segura.
2.  **Docker Compose (2 Serviços):** O arquivo `docker-compose.yml` define e orquestra os dois serviços (`app` e `db`).
3.  **Volumes (Persistência de Dados):** Um volume nomeado (`postgres_data`) é usado para persistir os dados do banco de dados PostgreSQL, garantindo que os dados não sejam perdidos ao recriar o container `db`.
4.  **Rede Customizada:** Uma rede `bridge` customizada (`backend_net`) é criada para isolar a comunicação entre a API e o banco de dados.
5.  **Variáveis de Ambiente:** Configurações sensíveis (usuário, senha e nome do banco) são gerenciadas através de um arquivo `.env` e injetadas nos containers pelo Docker Compose, evitando que senhas sejam expostas no código ou no `docker-compose.yml`.
6.  **Segurança do DB (Usuário não-root):** O banco de dados é configurado para criar um usuário (`app_user`) e um banco (`minha_api_db`) específicos para a aplicação, em vez de usar o superusuário `postgres`.
7.  **API com CRUD:** A aplicação FastAPI implementa endpoints de CRUD (Criar, Ler) para a entidade "Produto".

---

## Estrutura do Projeto

```
/DESAFIO-DOCKER-FASTAPI
│
├── .env                # (NÃO DEVE IR PARA O GIT) Armazena as variáveis de ambiente
├── docker-compose.yml  # Orquestra os serviços, volumes e rede
├── Dockerfile          # Define a construção da imagem da API
├── main.py             # Código-fonte da API FastAPI
├── requirements.txt    # Lista de dependências Python
└── README.md           # Esta documentação
```

---

## Como Executar o Projeto

### Pré-requisitos

* [Docker](https://www.docker.com/products/docker-desktop/) instalado e em execução.
* Docker Compose (geralmente incluído no Docker Desktop).

### 1. Configurar Variáveis de Ambiente

Antes de subir os containers, crie um arquivo chamado `.env` na raiz do projeto e defina as credenciais do banco de dados.

**Arquivo `.env`:**
```.env
# Credenciais para o banco de dados
DB_USER=app_user
DB_PASS=app_secret_pass_123
DB_NAME=minha_api_db
```

### 2. Construir Imagens e Subir os Containers

Precisa abrir o terminal na raiz do projeto e executar o comando seguinte:

```bash
docker compose up --build
```

* `up`: Inicia os containers, volumes e redes.
* `--build`: Força o Docker a construir a imagem da `app` usando o `Dockerfile` pela primeira vez.

Você verá os logs de ambos os containers. Espere até que os logs se estabilizem e você veja a seguinte mensagem do `fastapi_app`:

```log
fastapi_app  | INFO:     Uvicorn running on [http://0.0.0.0:8000](http://0.0.0.0:8000) (Press CTRL+C to quit)
```

### 3. Testar a Aplicação (CRUD)

Com os containers rodando, você pode testar a API. O FastAPI fornece uma interface de documentação interativa (Swagger UI) para isso.

1.  Abra seu navegador e acesse: **[http://localhost:8000/docs](http://localhost:8000/docs)**

2.  **CRIAR um produto (POST):**
    * Clique no endpoint `POST /produtos/`.
    * Clique em "Try it out".
    * Insira o seguinte JSON no "Request body":
      ```json
      {
        "nome": "Produto de Teste",
        "descricao": "Este é um teste"
      }
      ```
    * Clique em "Execute". Você deve receber uma resposta `Code: 200` com o produto criado.

3.  **LER os produtos (GET):**
    * Clique no endpoint `GET /produtos/`.
    * Clique em "Try it out" e depois em "Execute".
    * Você deve receber uma resposta `Code: 200` com uma lista contendo o produto que acabou de criar.

### 4. Testar a Persistência (Volume)

Para verificar se o volume está funcionando, vamos destruir os containers e subi-los novamente.

1.  No terminal, pare os containers pressionando `Ctrl + C`.
2.  Execute o comando para destruir os containers (mas não o volume):
    ```bash
    docker compose down
    ```
3.  Suba os containers novamente:
    ```bash
    docker compose up
    ```
4.  Após a API estar no ar, volte ao navegador em **[http://localhost:8000/docs](http://localhost:8000/docs)**.
5.  Execute o `GET /produtos/` (ler todos) novamente.

**Resultado:** O "Produto de Teste" que você criou anteriormente ainda estará na lista, provando que os dados foram persistidos pelo volume `postgres_data`.

### 5. Parar o Ambiente

Para parar e remover todos os containers, redes e volumes (opcionalmente), use:

```bash
# Apenas parar e remover containers/redes
docker compose down

# Parar E remover o volume de dados (apaga os dados do DB)
docker compose down -v
```