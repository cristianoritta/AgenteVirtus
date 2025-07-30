import hashlib
import uuid
from datetime import datetime
from models.models import Conversa, MensagemConversa
from config import db


class ConversaService:
    @staticmethod
    def gerar_hash_conversa():
        """Gera um hash único para identificar a conversa"""
        return hashlib.sha256(f"{uuid.uuid4()}{datetime.utcnow()}".encode()).hexdigest()
    
    @staticmethod
    def criar_conversa(tipo_conversa='chatbot', usuario_id=None, titulo=None):
        """Cria uma nova conversa"""
        hash_conversa = ConversaService.gerar_hash_conversa()
        
        conversa = Conversa(
            hash_conversa=hash_conversa,
            titulo=titulo or f"Conversa {datetime.utcnow().strftime('%d/%m/%Y %H:%M')}",
            tipo_conversa=tipo_conversa,
            usuario_id=usuario_id,
            ativa=True
        )
        
        db.session.add(conversa)
        db.session.commit()
        
        return conversa
    
    @staticmethod
    def buscar_conversa_por_hash(hash_conversa):
        """Busca uma conversa pelo hash"""
        return Conversa.query.filter_by(hash_conversa=hash_conversa, ativa=True).first()
    
    @staticmethod
    def buscar_conversa_por_id(conversa_id):
        """Busca uma conversa pelo ID"""
        return Conversa.query.filter_by(id=conversa_id, ativa=True).first()
    
    @staticmethod
    def adicionar_mensagem(conversa_id, role, conteudo):
        """Adiciona uma mensagem à conversa"""
        # Busca a última ordem para manter a sequência
        ultima_ordem = db.session.query(db.func.max(MensagemConversa.ordem)).filter_by(conversa_id=conversa_id).scalar()
        nova_ordem = (ultima_ordem or 0) + 1
        
        mensagem = MensagemConversa(
            conversa_id=conversa_id,
            role=role,
            conteudo=conteudo,
            ordem=nova_ordem
        )
        
        db.session.add(mensagem)
        
        # Atualiza a data de atualização da conversa
        conversa = Conversa.query.get(conversa_id)
        if conversa:
            conversa.atualizada_em = datetime.utcnow()
        
        db.session.commit()
        return mensagem
    
    @staticmethod
    def obter_historico_conversa(conversa_id, limit=None):
        """Obtém o histórico de mensagens de uma conversa"""
        query = MensagemConversa.query.filter_by(conversa_id=conversa_id).order_by(MensagemConversa.ordem)
        
        if limit:
            query = query.limit(limit)
        
        return query.all()
    
    @staticmethod
    def obter_mensagens_para_ia(conversa_id, limit=10):
        """Obtém as mensagens formatadas para envio à IA"""
        mensagens = ConversaService.obter_historico_conversa(conversa_id, limit)
        
        return [
            {
                "role": msg.role,
                "content": msg.conteudo
            }
            for msg in mensagens
        ]
    
    @staticmethod
    def listar_conversas_usuario(usuario_id, tipo_conversa=None, limit=20):
        """Lista as conversas de um usuário"""
        query = Conversa.query.filter_by(usuario_id=usuario_id, ativa=True)
        
        if tipo_conversa:
            query = query.filter_by(tipo_conversa=tipo_conversa)
        
        return query.order_by(Conversa.atualizada_em.desc()).limit(limit).all()
    
    @staticmethod
    def encerrar_conversa(conversa_id):
        """Marca uma conversa como inativa"""
        conversa = Conversa.query.get(conversa_id)
        if conversa:
            conversa.ativa = False
            db.session.commit()
            return True
        return False
    
    @staticmethod
    def atualizar_titulo_conversa(conversa_id, titulo):
        """Atualiza o título de uma conversa"""
        conversa = Conversa.query.get(conversa_id)
        if conversa:
            conversa.titulo = titulo
            db.session.commit()
            return True
        return False
    
    @staticmethod
    def deletar_conversa(conversa_id):
        """Deleta uma conversa e suas mensagens"""
        conversa = Conversa.query.get(conversa_id)
        if conversa:
            db.session.delete(conversa)
            db.session.commit()
            return True
        return False 