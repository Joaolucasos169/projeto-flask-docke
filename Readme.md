# 📁 Flask File Explorer & Database Logger

## Visão Geral do Projeto

Este projeto é uma aplicação web simples desenvolvida em **Python com o framework Flask**, que serve a dois propósitos principais:

1.  **Explorador de Arquivos:** Permite a navegação interativa pelo sistema de arquivos do servidor (dentro do contêiner Docker).
2.  **Sistema de Logs Persistente:** Registra cada acesso do usuário (caminho acessado, IP) em um banco de dados **PostgreSQL** e exibe esse histórico em uma página de logs dedicada.

O projeto utiliza **Docker** e **Docker Compose** para garantir que o ambiente de desenvolvimento seja totalmente portátil e fácil de iniciar.

---

## 🚀 Tecnologias Utilizadas

| Categoria | Tecnologia | Função no Projeto |
| :--- | :--- | :--- |
| **Backend Core** | Python (3.11) + Flask | Framework principal para roteamento e lógica de aplicação. |
| **Persistência** | PostgreSQL | Banco de dados para armazenamento persistente dos logs. |
| **ORM** | Flask-SQLAlchemy | Mapeia classes Python para tabelas do PostgreSQL e gerencia o relacionamento 1:N com Sistemas Operacionais. |
| **Infraestrutura** | Docker & Docker Compose | Containerização e orquestração dos serviços (`web` e `db`). |
| **Gerenciamento DB** | Flask-Migrate (Alembic) | Gerencia a evolução do esquema do banco de dados (Migrations) sem perder dados. |
| **Frontend** | HTML, Jinja2, CSS, JavaScript | Interface do usuário e lógica de filtro de pesquisa em tempo real. |

---

## ⚙️ Arquitetura e Estrutura do Banco de Dados

### Estrutura dos Serviços

O `docker-compose.yml` orquestra dois serviços:

* **`web`**: O contêiner Python que executa o Flask (porta 5000).
* **`db`**: O contêiner PostgreSQL (porta 5432).

### Relacionamento de Dados (ORM)

O banco de dados possui um relacionamento **Um para Muitos (1:N)**:

1.  **`sistemas_operacionais` (Tabela 1):** Armazena o nome e a versão de cada SO de forma única (Chave Primária: `id`).
2.  **`log_acessos` (Tabela N):** Registra o acesso e usa uma **Chave Estrangeira (`so_id`)** que aponta para o SO correspondente.

---

## 🛠️ Como Rodar o Projeto

### Pré-requisitos

Você deve ter o seguinte instalado em seu sistema (preferencialmente no ambiente **WSL** para usuários Windows):

* **Docker Desktop** (com Docker Compose).
* **Python 3.x** e **Ambiente Virtual (`venv`)** (para gerenciamento local).

### Instruções

Siga os passos abaixo para iniciar o projeto e configurar o banco de dados pela primeira vez:

#### 1. Clonar e Instalar Dependências

```bash
# 1. Ative seu ambiente virtual (se estiver desenvolvendo localmente)
source venv/Scripts/activate

# 2. Instale as dependências localmente (para que o Flask-Migrate funcione)
pip install -r requirements.txt
```

### 3. Iniciar os Contêineres
```bash
docker-compose up
```

### 4. Inicializar e Aplicar as Migrations (OBRIGATÓRIO)
```bash
# 1. Inicializa o repositório de migrações
docker-compose exec web python -m flask db init

# 2. Cria o script de migração (se houver mudanças no models.py)
docker-compose exec web python -m flask db migrate -m "Criação inicial das tabelas LogAcesso e SistemasOperacionais"

# 3. Aplica as tabelas ao banco de dados PostgreSQL
docker-compose exec web python -m flask db upgrade
```

### Acesso à aplicação
- Acesse o Explorador de Arquivos: http://localhost:5000/
- Acesse a Página de Logs: http://localhost:5000/logs