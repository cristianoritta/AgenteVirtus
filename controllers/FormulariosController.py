from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from models.models import Formulario, CampoFormulario, RegistroFormulario, Nota, db
from datetime import datetime
import json

formularios_bp = Blueprint('formularios', __name__)

@formularios_bp.route('/formularios')
def index():
    """Lista todos os formulários"""
    formularios = Formulario.query.order_by(Formulario.criado_em.desc()).all()
    return render_template('formularios/index.html', formularios=formularios)

@formularios_bp.route('/formularios/novo', methods=['GET', 'POST'])
def novo():
    """Cria um novo formulário"""
    if request.method == 'POST':
        try:
            dados = request.get_json()
            
            formulario = Formulario(
                nome=dados['nome'],
                descricao=dados.get('descricao', ''),
                ativo=dados.get('ativo', True)
            )
            
            db.session.add(formulario)
            db.session.commit()
            
            return jsonify({'success': True, 'id': formulario.id, 'message': 'Formulário criado com sucesso!'})
        except Exception as e:
            return jsonify({'success': False, 'message': f'Erro ao criar formulário: {str(e)}'})
    
    return render_template('formularios/novo.html')

@formularios_bp.route('/formularios/<int:id>/editar', methods=['GET', 'POST'])
def editar(id):
    """Edita um formulário existente"""
    formulario = Formulario.query.get_or_404(id)
    
    if request.method == 'POST':
        try:
            dados = request.get_json()
            
            formulario.nome = dados['nome']
            formulario.descricao = dados.get('descricao', '')
            formulario.ativo = dados.get('ativo', True)
            formulario.atualizado_em = datetime.utcnow()
            
            db.session.commit()
            
            return jsonify({'success': True, 'message': 'Formulário atualizado com sucesso!'})
        except Exception as e:
            return jsonify({'success': False, 'message': f'Erro ao atualizar formulário: {str(e)}'})
    
    return render_template('formularios/editar.html', formulario=formulario)

@formularios_bp.route('/formularios/<int:id>/excluir', methods=['POST'])
def excluir(id):
    """Exclui um formulário"""
    try:
        formulario = Formulario.query.get_or_404(id)
        db.session.delete(formulario)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Formulário excluído com sucesso!'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Erro ao excluir formulário: {str(e)}'})

@formularios_bp.route('/formularios/<int:id>/campos')
def campos(id):
    """Gerencia os campos de um formulário"""
    formulario = Formulario.query.get_or_404(id)
    return render_template('formularios/campos.html', formulario=formulario)

@formularios_bp.route('/formularios/<int:id>/campos/adicionar', methods=['POST'])
def adicionar_campo(id):
    """Adiciona um novo campo ao formulário"""
    try:
        formulario = Formulario.query.get_or_404(id)
        dados = request.get_json()
        
        # Determina a próxima ordem
        ultima_ordem = db.session.query(db.func.max(CampoFormulario.ordem)).filter_by(formulario_id=id).scalar() or 0
        
        campo = CampoFormulario(
            formulario_id=id,
            label=dados['label'],
            tipo=dados['tipo'],
            nome_campo=dados['nome_campo'],
            placeholder=dados.get('placeholder', ''),
            valor_padrao=dados.get('valor_padrao', ''),
            obrigatorio=dados.get('obrigatorio', False),
            tamanho_coluna=dados.get('tamanho_coluna', 'col-lg-12'),
            ordem=ultima_ordem + 1,
            opcoes=json.dumps(dados.get('opcoes', [])) if dados.get('opcoes') else None,
            validacao=dados.get('validacao', ''),
            ativo=True
        )
        
        db.session.add(campo)
        db.session.commit()
        
        return jsonify({'success': True, 'campo': campo.to_dict(), 'message': 'Campo adicionado com sucesso!'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Erro ao adicionar campo: {str(e)}'})

@formularios_bp.route('/formularios/campos/<int:campo_id>/editar', methods=['POST'])
def editar_campo(campo_id):
    """Edita um campo existente"""
    try:
        campo = CampoFormulario.query.get_or_404(campo_id)
        dados = request.get_json()
        
        campo.label = dados['label']
        campo.tipo = dados['tipo']
        campo.nome_campo = dados['nome_campo']
        campo.placeholder = dados.get('placeholder', '')
        campo.valor_padrao = dados.get('valor_padrao', '')
        campo.obrigatorio = dados.get('obrigatorio', False)
        campo.tamanho_coluna = dados.get('tamanho_coluna', 'col-lg-12')
        campo.opcoes = json.dumps(dados.get('opcoes', [])) if dados.get('opcoes') else None
        campo.validacao = dados.get('validacao', '')
        
        db.session.commit()
        
        return jsonify({'success': True, 'campo': campo.to_dict(), 'message': 'Campo atualizado com sucesso!'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Erro ao atualizar campo: {str(e)}'})

@formularios_bp.route('/formularios/campos/<int:campo_id>/excluir', methods=['POST'])
def excluir_campo(campo_id):
    """Exclui um campo"""
    try:
        campo = CampoFormulario.query.get_or_404(campo_id)
        db.session.delete(campo)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Campo excluído com sucesso!'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Erro ao excluir campo: {str(e)}'})

@formularios_bp.route('/formularios/campos/reordenar', methods=['POST'])
def reordenar_campos():
    """Reordena os campos do formulário"""
    try:
        dados = request.get_json()
        campos_ids = dados['campos_ids']
        
        for i, campo_id in enumerate(campos_ids):
            campo = CampoFormulario.query.get(campo_id)
            if campo:
                campo.ordem = i + 1
        
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Campos reordenados com sucesso!'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Erro ao reordenar campos: {str(e)}'})

@formularios_bp.route('/formularios/<int:id>/executar')
def executar(id):
    """Executa/preenche um formulário"""
    formulario = Formulario.query.get_or_404(id)
    return render_template('formularios/executar.html', formulario=formulario)

@formularios_bp.route('/formularios/<int:id>/salvar', methods=['POST'])
def salvar_registro(id):
    """Salva os dados de um formulário preenchido"""
    try:
        formulario = Formulario.query.get_or_404(id)
        dados = request.get_json()
        
        registro = RegistroFormulario(
            formulario_id=id,
            dados=json.dumps(dados['dados']),
            usuario_id=dados.get('usuario_id')
        )
        
        db.session.add(registro)
        db.session.commit()
        
        return jsonify({'success': True, 'id': registro.id, 'message': 'Registro salvo com sucesso!'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Erro ao salvar registro: {str(e)}'})

@formularios_bp.route('/formularios/<int:id>/registros')
def registros(id):
    """Lista os registros de um formulário"""
    formulario = Formulario.query.get_or_404(id)
    registros = RegistroFormulario.query.filter_by(formulario_id=id).order_by(RegistroFormulario.criado_em.desc()).all()
    return render_template('formularios/registros.html', formulario=formulario, registros=registros)

@formularios_bp.route('/formularios/registros/<int:registro_id>/editar', methods=['GET'])
def editar_registro(registro_id):
    """Página para editar um registro"""
    registro = RegistroFormulario.query.get_or_404(registro_id)
    formulario = Formulario.query.get_or_404(registro.formulario_id)
    return render_template('formularios/editar_registro.html', formulario=formulario, registro=registro)

@formularios_bp.route('/formularios/registros/<int:registro_id>/atualizar', methods=['POST'])
def atualizar_registro(registro_id):
    """Atualiza os dados de um registro"""
    try:
        registro = RegistroFormulario.query.get_or_404(registro_id)
        dados = request.get_json()
        
        registro.dados = json.dumps(dados['dados'])
        registro.atualizado_em = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Registro atualizado com sucesso!'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Erro ao atualizar registro: {str(e)}'})

@formularios_bp.route('/formularios/registros/<int:registro_id>/excluir', methods=['POST'])
def excluir_registro(registro_id):
    """Exclui um registro"""
    try:
        registro = RegistroFormulario.query.get_or_404(registro_id)
        db.session.delete(registro)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Registro excluído com sucesso!'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Erro ao excluir registro: {str(e)}'})

@formularios_bp.route('/api/formularios/<int:id>/campos')
def api_campos(id):
    """API para obter os campos de um formulário"""
    formulario = Formulario.query.get_or_404(id)
    campos = [campo.to_dict() for campo in formulario.campos if campo.ativo]
    return jsonify({'success': True, 'campos': campos})

@formularios_bp.route('/api/formularios/<int:id>/registros')
def api_registros(id):
    """API para obter os registros de um formulário"""
    registros = RegistroFormulario.query.filter_by(formulario_id=id).order_by(RegistroFormulario.criado_em.desc()).all()
    registros_dict = [registro.to_dict() for registro in registros]
    return jsonify({'success': True, 'registros': registros_dict})

@formularios_bp.route('/formularios/registros/criar-nota', methods=['POST'])
def criar_nota_registro():
    """Cria uma nota baseada nos dados de um registro de formulário"""
    try:
        data = request.get_json()
        registro_id = data.get('registro_id')
        formulario_id = data.get('formulario_id')
        dados_registro = data.get('dados', {})
        
        # Buscar o formulário e registro
        formulario = Formulario.query.get_or_404(formulario_id)
        registro = RegistroFormulario.query.get_or_404(registro_id)
        
        # Buscar campos do formulário para obter os labels
        campos = CampoFormulario.query.filter_by(formulario_id=formulario_id, ativo=True).order_by(CampoFormulario.ordem).all()
        
        # Criar título da nota (nome do formulário)
        titulo = f"{formulario.nome}"
        
        # Criar conteúdo da nota com os dados formatados
        conteudo = f"Formulário: {formulario.nome}\n"
        conteudo += f"Data do Registro: {registro.criado_em.strftime('%d/%m/%Y %H:%M')}\n"
        conteudo += f"ID do Registro: {registro.id}\n\n"
        conteudo += "Dados do Formulário:\n\n"
        
        # Adicionar cada campo com seu label e valor
        for campo in campos:
            valor = dados_registro.get(campo.nome_campo, '')
            if valor:
                if isinstance(valor, list):
                    valor = ', '.join(valor)
                conteudo += f"{campo.label}: {valor}\n"
            else:
                conteudo += f"{campo.label}: (vazio)\n"
        
        # Criar a nota
        nota = Nota(
            titulo=titulo,
            conteudo=conteudo,
            resumo=f"Registro do formulário {formulario.nome} - ID {registro.id}",
            tags=f"formulario,{formulario.nome.replace(' ', '_').lower()},registro_{registro.id}",
            usuario_id=1,  # TODO: Pegar do usuário logado
            favorita=False,
            arquivada=False
        )
        
        db.session.add(nota)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Nota criada com sucesso!',
            'nota_id': nota.id
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Erro ao criar nota: {str(e)}'
        }), 500 