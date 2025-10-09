from . import db  # Importa a instância de SQLAlchemy que está em app/__init__.py
from datetime import datetime

class LogAcesso(db.Model):
    __tablename__ = 'log_acessos'
    
    id = db.Column(db.Integer, primary_key=True)
    caminho_acessado = db.Column(db.String(500), nullable=False)
    ip_usuario = db.Column(db.String(50))
    data_acesso = db.Column(db.DateTime, default=datetime.utcnow)
    so_id = db.Column(db.Integer, db.ForeignKey('sistemas_operacionais.id'), nullable=False)
    def __repr__(self):
        return f'<LogAcesso {self.data_acesso} - {self.caminho_acessado}>'
class SistemaOperacional(db.Model):
    __tablename__ = 'sistemas_operacionais'
    
    id = db.Column(db.Integer, primary_key=True)
    nome_so = db.Column(db.String(100), nullable=False)
    versao_so = db.Column(db.String(50), nullable=False)   
    logs = db.relationship('LogAcesso', backref='sistema_operacional', lazy=True)
    __table_args__ = (db.UniqueConstraint('nome_so', 'versao_so', name='_nome_versao_uc'),)
    
    def __repr__(self):
        return f'<SistemaOperacional {self.nome_so} {self.versao_so}>'