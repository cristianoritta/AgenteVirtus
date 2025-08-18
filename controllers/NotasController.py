from flask import render_template, request, jsonify, redirect, url_for, flash, send_file
from config import db
from models.models import Nota, CategoriaNota, VinculoNota, Usuario
from datetime import datetime
import controllers.IaController as IaController
import json
import re
import zipfile
import io
import os

class NotasController:
    
    @staticmethod
    def index():
        """Página principal do sistema de notas"""
        return render_template('notas/index.html')
    
    @staticmethod
    def ver_nota(id):
        """Página para visualizar uma nota específica"""
        return render_template('notas/index.html', nota_id=id)
    
    @staticmethod
    def api_listar_notas():
        """API para listar todas as notas"""
        try:
            # Parâmetros de filtro
            categoria_id = request.args.get('categoria_id', type=int)
            favoritas = request.args.get('favoritas', type=bool)
            arquivadas = request.args.get('arquivadas', type=bool)
            busca = request.args.get('busca', '')
            
            # Query base
            query = Nota.query
            
            # Aplicar filtros
            if categoria_id:
                query = query.filter(Nota.categoria_id == categoria_id)
            
            if favoritas is not None:
                query = query.filter(Nota.favorita == favoritas)
            
            if arquivadas is not None:
                query = query.filter(Nota.arquivada == arquivadas)
            
            if busca:
                query = query.filter(
                    db.or_(
                        Nota.titulo.ilike(f'%{busca}%'),
                        Nota.conteudo.ilike(f'%{busca}%'),
                        Nota.tags.ilike(f'%{busca}%')
                    )
                )
            
            # Ordenar por data de atualização
            notas = query.order_by(Nota.atualizada_em.desc()).all()
            
            return jsonify({
                'success': True,
                'notas': [nota.to_dict() for nota in notas]
            })
            
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @staticmethod
    def api_obter_nota():
        """API para obter uma nota específica"""
        try:
            nota_id = request.args.get('id', type=int)
            if not nota_id:
                return jsonify({'success': False, 'error': 'ID da nota é obrigatório'}), 400
            
            nota = Nota.query.get(nota_id)
            if not nota:
                return jsonify({'success': False, 'error': 'Nota não encontrada'}), 404
            
            # Buscar vínculos
            vinculos_origem = []
            for vinculo in nota.vinculos_origem:
                vinculos_origem.append({
                    'id': vinculo.id,
                    'nota_destino_id': vinculo.nota_destino_id,
                    'nota_destino_titulo': vinculo.nota_destino.titulo,
                    'tipo_vinculo': vinculo.tipo_vinculo,
                    'descricao': vinculo.descricao
                })
            
            vinculos_destino = []
            for vinculo in nota.vinculos_destino:
                vinculos_destino.append({
                    'id': vinculo.id,
                    'nota_origem_id': vinculo.nota_origem_id,
                    'nota_origem_titulo': vinculo.nota_origem.titulo,
                    'tipo_vinculo': vinculo.tipo_vinculo,
                    'descricao': vinculo.descricao
                })
            
            nota_dict = nota.to_dict()
            nota_dict['vinculos_origem'] = vinculos_origem
            nota_dict['vinculos_destino'] = vinculos_destino
            
            return jsonify({
                'success': True,
                'nota': nota_dict
            })
            
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @staticmethod
    def api_criar_nota():
        """API para criar uma nova nota"""
        try:
            data = request.get_json()
            
            if not data or not data.get('titulo') or not data.get('conteudo'):
                return jsonify({'success': False, 'error': 'Título e conteúdo são obrigatórios'}), 400
            
            # Criar nova nota
            nota = Nota(
                titulo=data['titulo'],
                conteudo=data['conteudo'],
                resumo=data.get('resumo'),
                tags=data.get('tags'),
                categoria_id=data.get('categoria_id'),
                usuario_id=1,  # TODO: Pegar do usuário logado
                favorita=data.get('favorita', False),
                arquivada=data.get('arquivada', False)
            )
            
            db.session.add(nota)
            db.session.commit()
            
            # Processar vínculos se fornecidos
            if data.get('vinculos'):
                NotasController._processar_vinculos(nota.id, data['vinculos'])
            
            return jsonify({
                'success': True,
                'nota': nota.to_dict(),
                'message': 'Nota criada com sucesso!'
            })
            
        except Exception as e:
            db.session.rollback()
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @staticmethod
    def api_atualizar_nota():
        """API para atualizar uma nota existente"""
        try:
            data = request.get_json()
            nota_id = data.get('id')
            
            if not nota_id:
                return jsonify({'success': False, 'error': 'ID da nota é obrigatório'}), 400
            
            nota = Nota.query.get(nota_id)
            if not nota:
                return jsonify({'success': False, 'error': 'Nota não encontrada'}), 404
            
            # Atualizar campos
            if 'titulo' in data:
                nota.titulo = data['titulo']
            if 'conteudo' in data:
                nota.conteudo = data['conteudo']
            if 'resumo' in data:
                nota.resumo = data['resumo']
            if 'tags' in data:
                nota.tags = data['tags']
            if 'categoria_id' in data:
                nota.categoria_id = data['categoria_id']
            if 'favorita' in data:
                nota.favorita = data['favorita']
            if 'arquivada' in data:
                nota.arquivada = data['arquivada']
            
            nota.atualizada_em = datetime.utcnow()
            
            # Processar vínculos se fornecidos
            if 'vinculos' in data:
                # Remover vínculos existentes
                VinculoNota.query.filter_by(nota_origem_id=nota_id).delete()
                # Adicionar novos vínculos
                NotasController._processar_vinculos(nota_id, data['vinculos'])
            
            db.session.commit()
            
            return jsonify({
                'success': True,
                'nota': nota.to_dict(),
                'message': 'Nota atualizada com sucesso!'
            })
            
        except Exception as e:
            db.session.rollback()
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @staticmethod
    def api_deletar_nota():
        """API para deletar uma nota"""
        try:
            data = request.get_json()
            nota_id = data.get('id')
            
            if not nota_id:
                return jsonify({'success': False, 'error': 'ID da nota é obrigatório'}), 400
            
            nota = Nota.query.get(nota_id)
            if not nota:
                return jsonify({'success': False, 'error': 'Nota não encontrada'}), 404
            
            db.session.delete(nota)
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': 'Nota deletada com sucesso!'
            })
            
        except Exception as e:
            db.session.rollback()
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @staticmethod
    def api_listar_categorias():
        """API para listar categorias"""
        try:
            categorias = CategoriaNota.query.order_by(CategoriaNota.nome).all()
            
            return jsonify({
                'success': True,
                'categorias': [{
                    'id': cat.id,
                    'nome': cat.nome,
                    'descricao': cat.descricao,
                    'cor': cat.cor,
                    'notas_count': len(cat.notas)
                } for cat in categorias]
            })
            
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @staticmethod
    def api_criar_categoria():
        """API para criar uma nova categoria"""
        try:
            data = request.get_json()
            
            if not data or not data.get('nome'):
                return jsonify({'success': False, 'error': 'Nome da categoria é obrigatório'}), 400
            
            nome = data['nome'].strip()
            if len(nome) < 2:
                return jsonify({'success': False, 'error': 'Nome da categoria deve ter pelo menos 2 caracteres'}), 400
            
            # Verificar se já existe uma categoria com este nome
            categoria_existente = CategoriaNota.query.filter(
                db.func.lower(CategoriaNota.nome) == nome.lower()
            ).first()
            
            if categoria_existente:
                return jsonify({'success': False, 'error': 'Já existe uma categoria com este nome'}), 400
            
            categoria = CategoriaNota(
                nome=nome,
                descricao=data.get('descricao', '').strip(),
                cor=data.get('cor', '#007bff'),
                usuario_id=1  # TODO: Pegar do usuário logado
            )
            
            db.session.add(categoria)
            db.session.commit()
            
            return jsonify({
                'success': True,
                'categoria': {
                    'id': categoria.id,
                    'nome': categoria.nome,
                    'descricao': categoria.descricao,
                    'cor': categoria.cor,
                    'notas_count': 0
                },
                'message': 'Categoria criada com sucesso!'
            })
            
        except Exception as e:
            db.session.rollback()
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @staticmethod
    def api_buscar_notas():
        """API para buscar notas por texto"""
        try:
            termo = request.args.get('q', '')
            if not termo:
                return jsonify({'success': False, 'error': 'Termo de busca é obrigatório'}), 400
            
            # Buscar por título, conteúdo ou tags
            notas = Nota.query.filter(
                db.or_(
                    Nota.titulo.ilike(f'%{termo}%'),
                    Nota.conteudo.ilike(f'%{termo}%'),
                    Nota.tags.ilike(f'%{termo}%')
                )
            ).order_by(Nota.atualizada_em.desc()).limit(10).all()
            
            return jsonify({
                'success': True,
                'notas': [nota.to_dict() for nota in notas]
            })
            
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @staticmethod
    def api_gerar_resumo():
        """API para gerar resumo automático da nota"""
        try:
            data = request.get_json()
            conteudo = data.get('conteudo', '')
            
            if not conteudo:
                return jsonify({'success': False, 'error': 'Conteúdo é obrigatório'}), 400
            
            # Gerar resumo com IA
            resultado = IaController.groq(f"Elabore um pequeno resumo, em duas ou três frases, da minha nota: \n\n {conteudo}", None, None)
            
            if hasattr(resultado[0], 'get_json'):
                resultado_data = resultado[0].get_json()
            else:
                resultado_data = resultado[0]
            
            return jsonify({
                'success': True,
                'resumo': resultado_data['resposta']
            })
            
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @staticmethod
    def _processar_vinculos(nota_id, vinculos_data):
        """Processa os vínculos de uma nota"""
        for vinculo_data in vinculos_data:
            nota_destino_id = vinculo_data.get('nota_destino_id')
            if nota_destino_id and nota_destino_id != nota_id:
                # Verificar se a nota destino existe
                nota_destino = Nota.query.get(nota_destino_id)
                if nota_destino:
                    # Verificar se o vínculo já existe para evitar duplicatas
                    vinculo_existente = VinculoNota.query.filter_by(
                        nota_origem_id=nota_id,
                        nota_destino_id=nota_destino_id
                    ).first()
                    
                    if not vinculo_existente:
                        vinculo = VinculoNota(
                            nota_origem_id=nota_id,
                            nota_destino_id=nota_destino_id,
                            tipo_vinculo=vinculo_data.get('tipo_vinculo', 'relacionada'),
                            descricao=vinculo_data.get('descricao')
                        )
                        db.session.add(vinculo)
    
    @staticmethod
    def api_estatisticas():
        """API para obter estatísticas das notas"""
        try:
            total_notas = Nota.query.count()
            notas_favoritas = Nota.query.filter_by(favorita=True).count()
            notas_arquivadas = Nota.query.filter_by(arquivada=True).count()
            total_categorias = CategoriaNota.query.count()
            total_vinculos = VinculoNota.query.count()
            
            # Notas por categoria
            categorias_stats = db.session.query(
                CategoriaNota.nome,
                db.func.count(Nota.id).label('count')
            ).outerjoin(Nota).group_by(CategoriaNota.id, CategoriaNota.nome).all()
            
            return jsonify({
                'success': True,
                'estatisticas': {
                    'total_notas': total_notas,
                    'notas_favoritas': notas_favoritas,
                    'notas_arquivadas': notas_arquivadas,
                    'total_categorias': total_categorias,
                    'total_vinculos': total_vinculos,
                    'categorias': [{'nome': cat.nome, 'count': cat.count} for cat in categorias_stats]
                }
            })
            
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @staticmethod
    def api_atualizar_categoria_nota(nota_id):
        """API para atualizar a categoria de uma nota"""
        try:
            data = request.get_json()
            categoria_id = data.get('categoria_id')
            
            # categoria_id pode ser None para remover a categoria
            if categoria_id is not None and categoria_id != '':
                # Verificar se a categoria existe
                categoria = CategoriaNota.query.get(categoria_id)
                if not categoria:
                    return jsonify({'success': False, 'error': 'Categoria não encontrada'}), 404
            
            nota = Nota.query.get(nota_id)
            if not nota:
                return jsonify({'success': False, 'error': 'Nota não encontrada'}), 404
            
            # Atualizar categoria
            nota.categoria_id = categoria_id if categoria_id and categoria_id != '' else None
            nota.atualizada_em = datetime.utcnow()
            
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': 'Categoria atualizada com sucesso!',
                'nota': nota.to_dict()
            })
            
        except Exception as e:
            db.session.rollback()
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

    @staticmethod
    def api_download_notas():
        """API para download de todas as notas em formato ZIP com JSON"""
        try:
            # Buscar todas as notas com suas categorias e vínculos
            notas = Nota.query.all()
            
            # Criar arquivo ZIP em memória
            zip_buffer = io.BytesIO()
            
            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                for nota in notas:
                    # Preparar dados da nota para JSON
                    nota_data = {
                        'id': nota.id,
                        'titulo': nota.titulo,
                        'conteudo': nota.conteudo,
                        'resumo': nota.resumo,
                        'tags': nota.tags,
                        'categoria_id': nota.categoria_id,
                        'categoria_nome': nota.categoria.nome if nota.categoria else None,
                        'categoria_cor': nota.categoria.cor if nota.categoria else None,
                        'favorita': nota.favorita,
                        'arquivada': nota.arquivada,
                        'criada_em': nota.criada_em.isoformat() if nota.criada_em else None,
                        'atualizada_em': nota.atualizada_em.isoformat() if nota.atualizada_em else None,
                        'usuario_id': nota.usuario_id
                    }
                    
                    # Adicionar vínculos
                    vinculos_origem = []
                    for vinculo in nota.vinculos_origem:
                        vinculos_origem.append({
                            'id': vinculo.id,
                            'nota_destino_id': vinculo.nota_destino_id,
                            'nota_destino_titulo': vinculo.nota_destino.titulo,
                            'tipo_vinculo': vinculo.tipo_vinculo,
                            'descricao': vinculo.descricao,
                            'criado_em': vinculo.criado_em.isoformat() if vinculo.criado_em else None
                        })
                    
                    vinculos_destino = []
                    for vinculo in nota.vinculos_destino:
                        vinculos_destino.append({
                            'id': vinculo.id,
                            'nota_origem_id': vinculo.nota_origem_id,
                            'nota_origem_titulo': vinculo.nota_origem.titulo,
                            'tipo_vinculo': vinculo.tipo_vinculo,
                            'descricao': vinculo.descricao,
                            'criado_em': vinculo.criado_em.isoformat() if vinculo.criado_em else None
                        })
                    
                    nota_data['vinculos_origem'] = vinculos_origem
                    nota_data['vinculos_destino'] = vinculos_destino
                    
                    # Criar nome do arquivo baseado no título da nota
                    # Remover caracteres inválidos para nome de arquivo
                    nome_arquivo = re.sub(r'[<>:"/\\|?*]', '_', nota.titulo)
                    nome_arquivo = nome_arquivo.strip()
                    if not nome_arquivo:
                        nome_arquivo = f"nota_{nota.id}"
                    
                    # Adicionar ao ZIP
                    zip_file.writestr(f"{nome_arquivo}.json", json.dumps(nota_data, indent=2, ensure_ascii=False))
            
            # Posicionar o buffer no início
            zip_buffer.seek(0)
            
            # Retornar o arquivo ZIP
            return send_file(
                zip_buffer,
                mimetype='application/zip',
                as_attachment=True,
                download_name=f'notas_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.zip'
            )
            
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
