from datetime import datetime
from config import db
from sqlalchemy.dialects.mysql import LONGTEXT
from flask import current_app
from docx import Document
from io import BytesIO

# Modelo de exemplo - Usuário
class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    telefone = db.Column(db.String(120), unique=False, nullable=True)
    api_key = db.Column(db.String(255), unique=True, nullable=True)
    modelo_chat = db.Column(db.String(255), nullable=True)
    modelo_voz = db.Column(db.String(255), nullable=True)
    modelo_visao = db.Column(db.String(255), nullable=True)
    endpoint = db.Column(db.String(255), nullable=True)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Usuario {self.nome}>'

# Modelo para APIs de IA
class ApiIa(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    api_key = db.Column(db.String(255), unique=True, nullable=True)
    modelo_chat = db.Column(db.String(255), nullable=True)
    modelo_voz = db.Column(db.String(255), nullable=True)
    modelo_visao = db.Column(db.String(255), nullable=True)
    endpoint = db.Column(db.String(255), nullable=True)
    ativo = db.Column(db.Boolean, default=True)


# Modelos para Agentes Inteligentes (IA)
class EquipeInteligente(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(200), nullable=False)
    descricao = db.Column(db.Text, nullable=True)
    processo = db.Column(db.String(50), nullable=False)
    memoria = db.Column(db.Integer, nullable=False, default=1) # 1 = ativo, 0 = inativo
    layout = db.Column(db.Text().with_variant(LONGTEXT, "mysql")) # JSON com nós e conexões
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)
    menu_ordem = db.Column(db.Integer, nullable=True)

    def __repr__(self):
        return f'<EquipeInteligente {self.nome}>'

class TemplateArquivo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    node_id = db.Column(db.Integer, nullable=False)
    equipe_id = db.Column(db.Integer, db.ForeignKey('equipe_inteligente.id'), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    data = db.Column(db.LargeBinary, nullable=False)
    mimetype = db.Column(db.String(255), nullable=False)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)
    
    equipe = db.relationship('EquipeInteligente', backref=db.backref('templates', lazy=True))
    
    def __repr__(self):
        return f'<TemplateArquivo {self.filename}>'

# Modelo para salvar execuções das equipes
class ExecucaoEquipe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    equipe_id = db.Column(db.Integer, db.ForeignKey('equipe_inteligente.id'), nullable=False)
    contexto = db.Column(db.Text, nullable=True)
    resposta = db.Column(db.Text, nullable=True)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)
    atualizado_em = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamento com EquipeInteligente
    equipe = db.relationship('EquipeInteligente', backref=db.backref('execucoes', lazy=True))
    
    def __repr__(self):
        return f'<ExecucaoEquipe {self.id} - Equipe {self.equipe_id}>'

# Modelo de Assistente
class Assistente(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(200), nullable=False)
    descricao = db.Column(db.Text, nullable=True)
    conhecimento = db.Column(db.Text, nullable=True)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)

# Sistema de Memória para Conversas
class Conversa(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    hash_conversa = db.Column(db.String(64), unique=True, nullable=False, index=True)
    titulo = db.Column(db.String(255), nullable=True)
    tipo_conversa = db.Column(db.String(50), nullable=False, default='chatbot')  # chatbot, transcricao, etc
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=True)
    ativa = db.Column(db.Boolean, default=True)
    criada_em = db.Column(db.DateTime, default=datetime.utcnow)
    atualizada_em = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    usuario = db.relationship('Usuario', backref=db.backref('conversas', lazy=True))
    mensagens = db.relationship('MensagemConversa', backref='conversa', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Conversa {self.hash_conversa}>'

class MensagemConversa(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    conversa_id = db.Column(db.Integer, db.ForeignKey('conversa.id'), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # user, assistant, system
    conteudo = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    ordem = db.Column(db.Integer, nullable=False)  # Para manter a ordem das mensagens
    
    def __repr__(self):
        return f'<MensagemConversa {self.role}: {self.conteudo[:50]}...>'

###########################################################################################
# SISTEMA DE NOTAS (Zettelkasten/Supernotes)
###########################################################################################

class CategoriaNota(db.Model):
    """Categorias para organizar as notas"""
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.Text, nullable=True)
    cor = db.Column(db.String(7), default='#007bff')  # Cor em hex
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=True)
    criada_em = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    usuario = db.relationship('Usuario', backref=db.backref('categorias_notas', lazy=True))
    notas = db.relationship('Nota', backref='categoria', lazy=True)
    
    def __repr__(self):
        return f'<CategoriaNota {self.nome}>'

class Nota(db.Model):
    """Modelo principal para as notas (inspirado no Supernotes)"""
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(200), nullable=False)
    conteudo = db.Column(db.Text, nullable=False)
    resumo = db.Column(db.Text, nullable=True)  # Resumo automático da nota
    tags = db.Column(db.String(500), nullable=True)  # Tags separadas por vírgula
    categoria_id = db.Column(db.Integer, db.ForeignKey('categoria_nota.id'), nullable=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=True)
    favorita = db.Column(db.Boolean, default=False)
    arquivada = db.Column(db.Boolean, default=False)
    criada_em = db.Column(db.DateTime, default=datetime.utcnow)
    atualizada_em = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    usuario = db.relationship('Usuario', backref=db.backref('notas', lazy=True))
    
    # Relacionamentos para vínculos
    vinculos_origem = db.relationship('VinculoNota', 
                                     foreign_keys='VinculoNota.nota_origem_id',
                                     backref='nota_origem', 
                                     lazy=True, 
                                     cascade='all, delete-orphan')
    
    vinculos_destino = db.relationship('VinculoNota', 
                                      foreign_keys='VinculoNota.nota_destino_id',
                                      backref='nota_destino', 
                                      lazy=True, 
                                      cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Nota {self.titulo}>'
    
    def to_dict(self):
        """Converte a nota para dicionário"""
        return {
            'id': self.id,
            'titulo': self.titulo,
            'conteudo': self.conteudo,
            'resumo': self.resumo,
            'tags': self.tags,
            'categoria_id': self.categoria_id,
            'categoria_nome': self.categoria.nome if self.categoria else None,
            'categoria_cor': self.categoria.cor if self.categoria else None,
            'favorita': self.favorita,
            'arquivada': self.arquivada,
            'criada_em': self.criada_em.isoformat() if self.criada_em else None,
            'atualizada_em': self.atualizada_em.isoformat() if self.atualizada_em else None,
            'vinculos_count': len(self.vinculos_origem) + len(self.vinculos_destino)
        }

class VinculoNota(db.Model):
    """Vínculos entre notas (backlinks)"""
    id = db.Column(db.Integer, primary_key=True)
    nota_origem_id = db.Column(db.Integer, db.ForeignKey('nota.id'), nullable=False)
    nota_destino_id = db.Column(db.Integer, db.ForeignKey('nota.id'), nullable=False)
    tipo_vinculo = db.Column(db.String(50), default='relacionada')  # relacionada, referencia, etc
    descricao = db.Column(db.String(200), nullable=True)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<VinculoNota {self.nota_origem_id} -> {self.nota_destino_id}>'

###########################################################################################
# SEED
###########################################################################################

def criar_usuario_inicial():
    usuario = Usuario(nome='Administrador', email='admin@admin.com', telefone='1234567890')
    if not usuario:
        db.session.add(usuario)
        db.session.commit()