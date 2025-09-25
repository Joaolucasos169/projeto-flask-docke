# Resumo Executivo do Projeto: Explorador de Arquivos e API Dockerizada

Este projeto consistiu na criação e empacotamento de uma aplicação **Flask** em um contêiner **Docker** único. O objetivo foi consolidar todas as funcionalidades desenvolvidas (listagem de diretórios, informações do sistema e rota de eco) em uma solução pronta para ser executada em qualquer ambiente com o Docker.

---

## 🎯 Objetivos e Entregas Chave

| Objetivo | Descrição | Status |
| :--- | :--- | :--- |
| **Explorador de Arquivos (`/`)** | Implementação de uma rota dinâmica para listar o conteúdo de diretórios e ler arquivos via navegador. | **Concluído** |
| **API de Informações (`/info`)** | Criação de uma rota `GET` que retorna dados do sistema operacional e memória em formato JSON. | **Concluído** |
| **Rota de Echo (`/echo`)** | Implementação de uma rota `POST` que recebe um JSON com a chave "msg" e retorna a mensagem de volta. | **Concluído** |
| **Dockerização** | Empacotamento completo da aplicação usando `Dockerfile` e orquestração via `docker-compose.yml`. | **Concluído** |
| **Melhoria Visual** | Adição de uma barra de pesquisa (filtro em tempo real com JavaScript) para melhorar a usabilidade da listagem de arquivos. | **Concluído** |

---

## 🛠️ Tecnologias e Ferramentas Utilizadas

* **Linguagem:** Python
* **Framework:** Flask
* **Contêiner:** Docker
* **Orquestração:** Docker Compose
* **Outras libs:** `os`, `platform`, `psutil`
* **Controle de Versão:** Git / GitHub

---

## ✅ Como Executar

A aplicação pode ser iniciada com um único comando na pasta raiz do projeto:

```bash
docker-compose up