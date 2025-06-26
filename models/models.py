from datetime import datetime
from config import db
from sqlalchemy.dialects.mysql import LONGTEXT
from flask import current_app

# Modelo de exemplo - Usuário
class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    telefone = db.Column(db.String(120), unique=False, nullable=True)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Usuario {self.nome}>'

# Modelos para Agentes Inteligentes (IA)
class EquipeInteligente(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(200), nullable=False)
    descricao = db.Column(db.Text, nullable=True)
    processo = db.Column(db.String(50), nullable=False) # 'sequential' ou 'hierarchical'
    layout = db.Column(db.Text().with_variant(LONGTEXT, "mysql")) # JSON com nós e conexões
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)
    
    menu_ordem = db.Column(db.Integer, nullable=True)

    def __repr__(self):
        return f'<EquipeInteligente {self.nome}>'

def criar_usuario_inicial():
    usuario = Usuario(nome='Administrador', email='admin@admin.com', telefone='1234567890')
    if not usuario:
        db.session.add(usuario)
        db.session.commit()