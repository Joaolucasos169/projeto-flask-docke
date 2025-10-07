from . import db  # Importa a instância de SQLAlchemy que está em app/__init__.py
from datetime import datetime

class LogAcesso(db.Model):
    __tablename__ = 'log_acessos'
    
    id = db.Column(db.Integer, primary_key=True)
    caminho_acessado = db.Column(db.String(500), nullable=False)
    ip_usuario = db.Column(db.String(50))
    data_acesso = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<LogAcesso {self.data_acesso} - {self.caminho_acessado}>'