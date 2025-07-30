from flask import render_template, request, jsonify
from services.ConversaService import ConversaService
from models.models import Conversa, MensagemConversa


class ConversaController:
    @staticmethod
    def listar_conversas():
        """Lista todas as conversas ativas"""
        try:
            # Por enquanto, lista todas as conversas (sem filtro de usuário)
            conversas = Conversa.query.filter_by(ativa=True).order_by(Conversa.atualizada_em.desc()).limit(50).all()
            
            conversas_data = []
            for conversa in conversas:
                conversas_data.append({
                    'id': conversa.id,
                    'hash_conversa': conversa.hash_conversa,
                    'titulo': conversa.titulo,
                    'tipo_conversa': conversa.tipo_conversa,
                    'criada_em': conversa.criada_em.strftime('%d/%m/%Y %H:%M'),
                    'atualizada_em': conversa.atualizada_em.strftime('%d/%m/%Y %H:%M'),
                    'total_mensagens': len(conversa.mensagens)
                })
            
            return jsonify({
                'status': 'success',
                'conversas': conversas_data
            })
            
        except Exception as e:
            return jsonify({
                'status': 'error',
                'message': f'Erro ao listar conversas: {str(e)}'
            }), 500
    
    @staticmethod
    def listar_conversas_sidebar():
        """Lista conversas de forma simplificada para a barra lateral"""
        try:
            # Lista apenas as conversas mais recentes para a sidebar
            conversas = Conversa.query.filter_by(ativa=True).order_by(Conversa.atualizada_em.desc()).limit(20).all()
            
            conversas_data = []
            for conversa in conversas:
                conversas_data.append({
                    'id': conversa.id,
                    'hash_conversa': conversa.hash_conversa,
                    'titulo': conversa.titulo,
                    'tipo_conversa': conversa.tipo_conversa,
                    'atualizada_em': conversa.atualizada_em.strftime('%d/%m/%Y %H:%M'),
                    'total_mensagens': len(conversa.mensagens)
                })
            
            return jsonify({
                'status': 'success',
                'conversas': conversas_data
            })
            
        except Exception as e:
            return jsonify({
                'status': 'error',
                'message': f'Erro ao listar conversas: {str(e)}'
            }), 500
    
    @staticmethod
    def obter_conversa():
        """Obtém uma conversa específica com suas mensagens"""
        try:
            conversa_id = request.args.get('conversa_id')
            hash_conversa = request.args.get('hash_conversa')
            
            if not conversa_id and not hash_conversa:
                return jsonify({
                    'status': 'error',
                    'message': 'ID da conversa ou hash é obrigatório'
                }), 400
            
            conversa = None
            if conversa_id:
                conversa = ConversaService.buscar_conversa_por_id(conversa_id)
            elif hash_conversa:
                conversa = ConversaService.buscar_conversa_por_hash(hash_conversa)
            
            if not conversa:
                return jsonify({
                    'status': 'error',
                    'message': 'Conversa não encontrada'
                }), 404
            
            # Obter mensagens da conversa
            mensagens = ConversaService.obter_historico_conversa(conversa.id)
            
            mensagens_data = []
            for msg in mensagens:
                mensagens_data.append({
                    'id': msg.id,
                    'role': msg.role,
                    'conteudo': msg.conteudo,
                    'timestamp': msg.timestamp.strftime('%d/%m/%Y %H:%M:%S'),
                    'ordem': msg.ordem
                })
            
            return jsonify({
                'status': 'success',
                'conversa': {
                    'id': conversa.id,
                    'hash_conversa': conversa.hash_conversa,
                    'titulo': conversa.titulo,
                    'tipo_conversa': conversa.tipo_conversa,
                    'criada_em': conversa.criada_em.strftime('%d/%m/%Y %H:%M'),
                    'atualizada_em': conversa.atualizada_em.strftime('%d/%m/%Y %H:%M')
                },
                'mensagens': mensagens_data
            })
            
        except Exception as e:
            return jsonify({
                'status': 'error',
                'message': f'Erro ao obter conversa: {str(e)}'
            }), 500
    
    @staticmethod
    def criar_conversa():
        """Cria uma nova conversa"""
        try:
            tipo_conversa = request.form.get('tipo_conversa', 'chatbot')
            titulo = request.form.get('titulo')
            
            conversa = ConversaService.criar_conversa(
                tipo_conversa=tipo_conversa,
                titulo=titulo
            )
            
            return jsonify({
                'status': 'success',
                'conversa': {
                    'id': conversa.id,
                    'hash_conversa': conversa.hash_conversa,
                    'titulo': conversa.titulo,
                    'tipo_conversa': conversa.tipo_conversa
                }
            })
            
        except Exception as e:
            return jsonify({
                'status': 'error',
                'message': f'Erro ao criar conversa: {str(e)}'
            }), 500
    
    @staticmethod
    def atualizar_titulo():
        """Atualiza o título de uma conversa"""
        try:
            conversa_id = request.form.get('conversa_id')
            titulo = request.form.get('titulo')
            
            if not conversa_id or not titulo:
                return jsonify({
                    'status': 'error',
                    'message': 'ID da conversa e título são obrigatórios'
                }), 400
            
            sucesso = ConversaService.atualizar_titulo_conversa(conversa_id, titulo)
            
            if sucesso:
                return jsonify({
                    'status': 'success',
                    'message': 'Título atualizado com sucesso'
                })
            else:
                return jsonify({
                    'status': 'error',
                    'message': 'Conversa não encontrada'
                }), 404
            
        except Exception as e:
            return jsonify({
                'status': 'error',
                'message': f'Erro ao atualizar título: {str(e)}'
            }), 500
    
    @staticmethod
    def encerrar_conversa():
        """Encerra uma conversa (marca como inativa)"""
        try:
            conversa_id = request.form.get('conversa_id')
            
            if not conversa_id:
                return jsonify({
                    'status': 'error',
                    'message': 'ID da conversa é obrigatório'
                }), 400
            
            sucesso = ConversaService.encerrar_conversa(conversa_id)
            
            if sucesso:
                return jsonify({
                    'status': 'success',
                    'message': 'Conversa encerrada com sucesso'
                })
            else:
                return jsonify({
                    'status': 'error',
                    'message': 'Conversa não encontrada'
                }), 404
            
        except Exception as e:
            return jsonify({
                'status': 'error',
                'message': f'Erro ao encerrar conversa: {str(e)}'
            }), 500
    
    @staticmethod
    def deletar_conversa():
        """Deleta uma conversa e suas mensagens"""
        try:
            conversa_id = request.form.get('conversa_id')
            if not conversa_id:
                return jsonify({
                    'status': 'error',
                    'message': 'ID da conversa é obrigatório'
                }), 400
            sucesso = ConversaService.deletar_conversa(conversa_id)
            if sucesso:
                return jsonify({
                    'status': 'success',
                    'message': 'Conversa deletada com sucesso'
                })
            else:
                return jsonify({
                    'status': 'error',
                    'message': 'Conversa não encontrada'
                }), 404
        except Exception as e:
            return jsonify({
                'status': 'error',
                'message': f'Erro ao deletar conversa: {str(e)}'
            }), 500 