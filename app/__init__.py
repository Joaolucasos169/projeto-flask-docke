import os  
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# Cria uma instância da classe SQLAlchemy (o banco de dados)
db = SQLAlchemy()

def create_app():
    # Inicializa o Flask
    app = Flask(__name__)
    app.json.ensure_ascii = False
    
    # Define o caminho base do projeto (onde o app.py está)
    BASEDIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    
    # -------------------------------------------------------------
    # Configuração do PostgreSQL
    # -------------------------------------------------------------
    # As credenciais são lidas das variáveis de ambiente que o Docker Compose fornecerá.
    # Esta URL usa o nome do serviço 'db' (do docker-compose.yml) como o host.
    DATABASE_URL = os.environ.get('DATABASE_URL', 'postgresql://postgres:postgres@db:5432/postgres')
    
    app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
    # Desabilita o aviso do Flask-SQLAlchemy
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Inicializa o SQLAlchemy com o app Flask
    db.init_app(app)

    # -------------------------------------------------------------
    # Importa e Registra os Modelos e as Rotas
    # -------------------------------------------------------------
    from .routes import bp
    app.register_blueprint(bp)
    from .models import LogAcesso
    # Cria as tabelas do banco de dados (dentro do contexto da aplicação)
    # Isso é feito a primeira vez que a aplicação é executada no contêiner.
    with app.app_context():
        db.create_all()

    return app