# Desafio Técnico Luiza Labs
## Visão Geral
Este projeto é uma aplicação web que fornece uma API para gerenciamento de clientes e lista de desejos com autenticação de usuários. Ele foi desenvolvido utilizando o framework Flask em Python e integração com banco de dados PostgreSQL.
## Funcionalidades Principais
1. Autenticação de Usuários: a API permite a criação de usuários, fazer login e autenticação.

2. Gerenciamento de Clientes: uma vez logados, os usuários podem adicionar, visualizar, atualizar e excluir clientes.

3. Lista de Desejos: os usuários podem adicionar produtos à sua lista de desejos, visualizar e detalhar os produtos, bem como remover produtos da mesma.

## Tecnologias Utilizadas
- Flask: Framework web utilizado para desenvolver a API.
- PostgreSQL: Banco de dados relacional utilizado para armazenar dados de clientes e lista de desejos.
- Flask SQLAlchemy: Extensão do Flask para integração com o PostgreSQL.
- Flask Marshmallow: Biblioteca utilizada para serialização/desserialização de objetos.
- Flask JWT Extended: Extensão do Flask para autenticação baseada em JWT (JSON Web Tokens).
- Requests: Biblioteca para fazer requisições HTTP para a API externa de produtos.
- Werkzeug: Utilizado para tratamento de exceções.

## Requisitos
- Python
- Docker
- PostgreSQL

## Instalação
- Clone este repositório do projeto.
- Na pasta raiz, suba o container para hospedar o banco de dados:

```docker-compose up```

- Uma vez aberto o projeto, faça a instalação das dependências:

``` pip install -r requirements.txt```
- Execute o arquivo model.py na pasta client para subir as tabelas no banco de dados.
- Execute o arquivo app.py para iniciar o servidor local.

## Utilização da API:
Este projeto segue o padrão RESTful. As rotas podem ser testadas localmente (http://localhost:5000/). Os endpoints são:

### /register: Rota para registrar novos usuários.

- Método: POST
- Parâmetros: "username" e "password" no corpo da requisição.

### /login: Rota para fazer login de usuários.

- Método: POST
- Parâmetros: "username" e "password" no corpo da requisição.
- Retorna: Token de acesso JWT.


### /clients: Rotas para gerenciamento de clientes.
Necessário Bearer Token para autenticação
- GET: Retorna todos os clientes.
- POST: Adiciona um novo cliente. Os parâmetros do corpo são: "name" e "email".


### /clients/{id_client}: Rotas para operações individuais de cliente.
Necessário Bearer Token para autenticação

- GET: Retorna os detalhes de um cliente específico.
- PUT: Atualiza os detalhes de um cliente. Parâmetros: "name" e "email".
- DELETE: Remove um cliente.

### /wish-list/{client_id}: Rotas para gerenciamento da lista de desejos de um cliente.
Necessário Bearer Token para autenticação
- GET: Retorna os produtos na lista de desejos de um cliente.
- POST: Adiciona um produto à lista de desejos de um cliente. Parâmetros: "product_id"

### /wish-list/{client_id}/{product_id}: Rotas para operações individuais na lista de desejos de um cliente.

- DELETE: Remove um produto da lista de desejos de um cliente.

## Observações Finais
Para fins de testes, os "produtc_id" podem ser obtidos através deste link: 
https://gist.github.com/Bgouveia/9e043a3eba439489a35e70d1b5ea08ec

