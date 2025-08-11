from flask import render_template, request, redirect, url_for, flash, jsonify, send_file
from datetime import datetime
import os
from models.models import Usuario, ApiIa, SystemConfig
from config import db, configure_database_uri
from utils.database_utils import DatabasePathManager

class UsuarioController:
    @staticmethod
    def index():
        usuarios = Usuario.query.all()
        return render_template('admin/usuarios.html', usuarios=usuarios)
    
    @staticmethod
    def minhaconta():
        usuario = Usuario.query.get(1)
        apis_ia = ApiIa.query.all()
        
        if request.method == 'POST':
            nome = request.form['nome']
            email = request.form['email']
            telefone = request.form['telefone']
            
            # Salva no banco de dados
            if usuario:
                usuario.nome = nome
                usuario.email = email
                usuario.telefone = telefone
                db.session.commit()
                flash('Configurações atualizadas com sucesso!', 'success')
            else:
                # Criar usuário se não existir
                usuario = Usuario(nome=nome, email=email, telefone=telefone)
                db.session.add(usuario)
                db.session.commit()
                flash('Configurações atualizadas com sucesso!', 'success')
            
        return render_template('admin/minhaconta.html', usuario=usuario, apis_ia=apis_ia)
    
    @staticmethod
    def novo():
        if request.method == 'POST':
            nome = request.form['nome']
            email = request.form['email']
            
            if not nome or not email:
                flash('Por favor, preencha todos os campos!', 'error')
                return redirect(url_for('novo_usuario'))
            
            # Verificar se o email já existe
            usuario_existente = Usuario.query.filter_by(email=email).first()
            if usuario_existente:
                flash('Este email já está cadastrado!', 'error')
                return redirect(url_for('novo_usuario'))
            
            novo_usuario = Usuario(nome=nome, email=email)
            db.session.add(novo_usuario)
            db.session.commit()
            
            flash('Usuário criado com sucesso!', 'success')
            return redirect(url_for('usuarios'))
        
        return render_template('novo_usuario.html')
    
    @staticmethod
    def ver(id):
        usuario = Usuario.query.get_or_404(id)
        now = datetime.utcnow()
        return render_template('ver_usuario.html', usuario=usuario, now=now)
    
    @staticmethod
    def editar(id):
        usuario = Usuario.query.get_or_404(id)
        
        if request.method == 'POST':
            nome = request.form['nome']
            email = request.form['email']
            
            if not nome or not email:
                flash('Por favor, preencha todos os campos!', 'error')
                return redirect(url_for('editar_usuario', id=id))
            
            # Verificar se o email já existe (exceto para o usuário atual)
            usuario_existente = Usuario.query.filter_by(email=email).first()
            if usuario_existente and usuario_existente.id != id:
                flash('Este email já está cadastrado!', 'error')
                return redirect(url_for('editar_usuario', id=id))
            
            usuario.nome = nome
            usuario.email = email
            db.session.commit()
            
            flash('Usuário atualizado com sucesso!', 'success')
            return redirect(url_for('ver_usuario', id=id))
        
        return render_template('editar_usuario.html', usuario=usuario)
    
    @staticmethod
    def deletar(id):
        usuario = Usuario.query.get_or_404(id)
        db.session.delete(usuario)
        db.session.commit()
        flash('Usuário deletado com sucesso!', 'success')
        return redirect(url_for('usuarios'))
    
    @staticmethod
    def api_usuarios():
        usuarios = Usuario.query.all()
        return jsonify([{
            'id': u.id,
            'nome': u.nome,
            'email': u.email,
            'data_criacao': u.data_criacao.isoformat()
        } for u in usuarios])

    @staticmethod
    def apiia_adicionar():
        nome = request.form.get('nome')
        api_key = request.form.get('api_key')
        modelo_chat = request.form.get('modelo_chat')
        modelo_voz = request.form.get('modelo_voz')
        modelo_visao = request.form.get('modelo_visao')
        endpoint = request.form.get('endpoint')

        # Verifica se já existe uma API com a mesma chave
        if ApiIa.query.filter_by(api_key=api_key).first():
            flash('Já existe uma API cadastrada com essa API Key!', 'danger')
            return redirect(url_for('minhaconta'))

        api = ApiIa(
            nome=nome,
            api_key=api_key,
            modelo_chat=modelo_chat,
            modelo_voz=modelo_voz,
            modelo_visao=modelo_visao,
            endpoint=endpoint,
        )
        db.session.add(api)
        db.session.commit()
        flash('API adicionada com sucesso!', 'success')
        return redirect(url_for('minhaconta'))

    @staticmethod
    def apiia_excluir(id):
        api = ApiIa.query.get_or_404(id)
        db.session.delete(api)
        db.session.commit()
        print("API excluída com sucesso!")
        flash('API excluída com sucesso!', 'success')
        
        return jsonify({'success': True})

    @staticmethod
    def apiia_ativar(id):
        
        # Só pode ter uma api ativa. Define todas como inativas
        apis = ApiIa.query.all()
        for api in apis:
            api.ativo = False
            db.session.commit()
        
        api = ApiIa.query.get_or_404(id)
        api.ativo = True
        db.session.commit()
        
        # Retorna o conteúdo do tbody atualizado para htmx
        from flask import render_template_string
        html = render_template_string('''
            {% for api in apis %}
            <tr>
                <td>{{ api.nome }}</td>
                <td>
                    {% if api.ativo %}
                    <a href="/minhaconta/apiia/{{ api.id}}/desativar" class="btn btn-success api"
                        title="Clique para desativar" hx-get="/minhaconta/apiia/{{ api.id}}/desativar"
                        hx-target="closest tbody" hx-swap="innerHTML">Ativo</a>
                    {% else %}
                    <a href="/minhaconta/apiia/{{ api.id}}/ativar" class="btn btn-secondary api"
                        title="Clique para ativar" hx-get="/minhaconta/apiia/{{ api.id}}/ativar"
                        hx-target="closest tbody" hx-swap="innerHTML">Inativo</a>
                    {% endif %}
                </td>
                <td>{{ api.api_key[:10] }}...</td>
                <td>{{ api.modelo_chat }}</td>
                <td>{{ api.modelo_voz }}</td>
                <td>{{ api.modelo_visao }}</td>
                <td>{{ api.endpoint }}</td>
                <td nowrap>
                    <button class="btn btn-sm btn-info btn-testar-api me-1" data-api-id="{{ api.id }}"
                        data-api-nome="{{ api.nome }}" type="button" title="Testar API">
                        <i class="fas fa-play"></i> Testar
                    </button>
                    <button class="btn btn-sm btn-warning btn-editar-api me-1" data-api-id="{{ api.id }}"
                        data-api-nome="{{ api.nome }}" data-api-key="{{ api.api_key }}"
                        data-modelo-chat="{{ api.modelo_chat }}" data-modelo-voz="{{ api.modelo_voz }}"
                        data-modelo-visao="{{ api.modelo_visao }}" data-endpoint="{{ api.endpoint }}"
                        type="button" title="Editar API">
                        <i class="fas fa-edit"></i> Editar
                    </button>
                    <button class="btn btn-sm btn-danger btn-excluir-api" data-api-id="{{ api.id }}"
                        hx-get="/minhaconta/apiia/{{ api.id }}/excluir" hx-target="closest tr"
                        hx-swap="outerHTML remove" type="button">
                        Excluir
                    </button>
                </td>
            </tr>
            {% else %}
            <tr>
                <td colspan="8" class="text-center text-muted">Nenhuma API cadastrada.</td>
            </tr>
            {% endfor %}
        ''', apis=ApiIa.query.all())
        
        return html

    @staticmethod
    def apiia_desativar(id):
        api = ApiIa.query.get_or_404(id)
        api.ativo = False
        db.session.commit()
        
        # Retorna o conteúdo do tbody atualizado para htmx
        from flask import render_template_string
        html = render_template_string('''
            {% for api in apis %}
            <tr>
                <td>{{ api.nome }}</td>
                <td>
                    {% if api.ativo %}
                    <a href="/minhaconta/apiia/{{ api.id}}/desativar" class="btn btn-success api"
                        title="Clique para desativar" hx-get="/minhaconta/apiia/{{ api.id}}/desativar"
                        hx-target="closest tbody" hx-swap="innerHTML">Ativo</a>
                    {% else %}
                    <a href="/minhaconta/apiia/{{ api.id}}/ativar" class="btn btn-secondary api"
                        title="Clique para ativar" hx-get="/minhaconta/apiia/{{ api.id}}/ativar"
                        hx-target="closest tbody" hx-swap="innerHTML">Inativo</a>
                    {% endif %}
                </td>
                <td>{{ api.api_key }}</td>
                <td>{{ api.modelo_chat }}</td>
                <td>{{ api.modelo_voz }}</td>
                <td>{{ api.modelo_visao }}</td>
                <td>{{ api.endpoint }}</td>
                <td>
                    <button class="btn btn-sm btn-info btn-testar-api me-1" data-api-id="{{ api.id }}"
                        data-api-nome="{{ api.nome }}" type="button" title="Testar API">
                        <i class="fas fa-play"></i> Testar
                    </button>
                    <button class="btn btn-sm btn-warning btn-editar-api me-1" data-api-id="{{ api.id }}"
                        data-api-nome="{{ api.nome }}" data-api-key="{{ api.api_key }}"
                        data-modelo-chat="{{ api.modelo_chat }}" data-modelo-voz="{{ api.modelo_voz }}"
                        data-modelo-visao="{{ api.modelo_visao }}" data-endpoint="{{ api.endpoint }}"
                        type="button" title="Editar API">
                        <i class="fas fa-edit"></i> Editar
                    </button>
                    <button class="btn btn-sm btn-danger btn-excluir-api" data-api-id="{{ api.id }}"
                        hx-get="/minhaconta/apiia/{{ api.id }}/excluir" hx-target="closest tr"
                        hx-swap="outerHTML remove" type="button">
                        Excluir
                    </button>
                </td>
            </tr>
            {% else %}
            <tr>
                <td colspan="8" class="text-center text-muted">Nenhuma API cadastrada.</td>
            </tr>
            {% endfor %}
        ''', apis=ApiIa.query.all())
        
        return html

    @staticmethod
    def apiia_editar(id):
        if request.method == 'POST':
            nome = request.form.get('nome')
            api_key = request.form.get('api_key')
            modelo_chat = request.form.get('modelo_chat')
            modelo_voz = request.form.get('modelo_voz')
            modelo_visao = request.form.get('modelo_visao')
            endpoint = request.form.get('endpoint')

            # Buscar a API existente
            api = ApiIa.query.get_or_404(id)
            
            # Verificar se já existe uma API com a mesma chave (exceto a atual)
            if api_key and api_key != api.api_key:
                api_existente = ApiIa.query.filter_by(api_key=api_key).first()
                if api_existente:
                    flash('Já existe uma API cadastrada com essa API Key!', 'danger')
                    return redirect(url_for('minhaconta'))

            # Atualizar os dados da API
            api.nome = nome
            api.api_key = api_key
            api.modelo_chat = modelo_chat
            api.modelo_voz = modelo_voz
            api.modelo_visao = modelo_visao
            api.endpoint = endpoint
            
            db.session.commit()
            flash('API atualizada com sucesso!', 'success')
            return redirect(url_for('minhaconta'))
        
        return redirect(url_for('minhaconta'))
    
    @staticmethod
    def exportar_banco():
        """
        Exporta o banco de dados SQLite para download
        """
        try:
            # Obter o caminho atual do banco de dados
            db_path = DatabasePathManager.get_database_path()
            
            # Verificar se o arquivo existe
            if not os.path.exists(db_path):
                flash('Arquivo do banco de dados não encontrado!', 'error')
                return redirect(url_for('minhaconta'))
            
            # Nome do arquivo para download
            filename = f'agente_virtus_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.db'
            
            # Retornar o arquivo para download
            return send_file(
                db_path,
                as_attachment=True,
                download_name=filename,
                mimetype='application/octet-stream'
            )
            
        except Exception as e:
            flash(f'Erro ao exportar banco de dados: {str(e)}', 'error')
            return redirect(url_for('minhaconta'))
    
    @staticmethod
    def configurar_banco():
        """
        Configura o caminho do banco de dados
        """
        if request.method == 'POST':
            novo_caminho = request.form.get('database_path', '').strip()
            
            # Validar o caminho
            is_valid, message = DatabasePathManager.validate_database_path(novo_caminho)
            
            if not is_valid:
                flash(f'Caminho inválido: {message}', 'error')
                return redirect(url_for('minhaconta'))
            
            try:
                # Definir o novo caminho
                DatabasePathManager.set_database_path(novo_caminho)
                
                # Aplicar a nova configuração do banco de dados
                configure_database_uri()
                
                flash('Caminho do banco de dados atualizado com sucesso!', 'success')
            except Exception as e:
                flash(f'Erro ao atualizar caminho: {str(e)}', 'error')
            
            return redirect(url_for('minhaconta'))
        
        # GET: retorna informações do banco atual
        db_info = DatabasePathManager.get_database_info()
        return jsonify(db_info)
    
    @staticmethod
    def info_sistema():
        """
        Retorna informações do sistema
        """
        try:
            # Informações do banco de dados
            db_info = DatabasePathManager.get_database_info()
            
            # Contadores de registros
            from models.models import EquipeInteligente, ExecucaoEquipe, Nota, Conversa, ApiIa
            
            system_info = {
                'database': db_info,
                'statistics': {
                    'usuarios': Usuario.query.count(),
                    'apis_ia': ApiIa.query.count(),
                    'equipes': EquipeInteligente.query.count(),
                    'execucoes': ExecucaoEquipe.query.count(),
                    'notas': Nota.query.count(),
                    'conversas': Conversa.query.count(),
                    'formularios': 0  # Será implementado quando necessário
                },
                'system': {
                    'python_version': os.sys.version,
                    'current_time': datetime.now().isoformat()
                }
            }
            
            return jsonify(system_info)
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500