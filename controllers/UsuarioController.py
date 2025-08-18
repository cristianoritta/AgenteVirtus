import os
import shutil
import json
import requests
from datetime import datetime
from flask import render_template, request, redirect, url_for, flash, jsonify, send_file
from werkzeug.security import generate_password_hash, check_password_hash
from models.models import Usuario, ApiIa, SystemConfig
from utils.database_utils import get_database_info, get_database_path

class UsuarioController:
    @staticmethod
    def minhaconta():
        """Página da minha conta"""
        # Buscar usuário atual e APIs de IA
        usuario = Usuario.query.first()
        apis_ia = ApiIa.query.all()
        
        if request.method == 'POST':
            nome = request.form.get('nome')
            email = request.form.get('email')
            telefone = request.form.get('telefone')
            
            # Salva no banco de dados
            if usuario:
                usuario.nome = nome
                usuario.email = email
                usuario.telefone = telefone
                from config import db
                db.session.commit()
                flash('Configurações atualizadas com sucesso!', 'success')
            else:
                # Criar usuário se não existir
                usuario = Usuario(nome=nome, email=email, telefone=telefone)
                from config import db
                db.session.add(usuario)
                db.session.commit()
                flash('Configurações atualizadas com sucesso!', 'success')
        else:
            # Se não há usuário, criar um padrão para evitar erro no template
            if not usuario:
                usuario = Usuario(nome='', email='', telefone='')
            
        # Carregar configurações de proxy
        proxy_config = {
            'endereco': SystemConfig.get_config('proxy_endereco', ''),
            'login': SystemConfig.get_config('proxy_login', ''),
            'senha': SystemConfig.get_config('proxy_senha', '')
        }
        
        return render_template('admin/minhaconta.html', usuario=usuario, apis_ia=apis_ia, proxy_config=proxy_config, 
                                    database_path=get_database_path().replace('utils\..\\', ''),
                                    database_info=get_database_info()
                                )
    
    @staticmethod
    def alterar_senha():
        """Altera a senha do usuário"""
        if request.method == 'POST':
            senha_atual = request.form.get('senha_atual')
            nova_senha = request.form.get('nova_senha')
            confirmar_senha = request.form.get('confirmar_senha')
            
            # Buscar usuário atual (assumindo que há apenas um usuário admin)
            usuario = Usuario.query.first()
            
            if not usuario:
                flash('Usuário não encontrado!', 'error')
                return redirect(url_for('minhaconta'))
            
            # Verificar senha atual
            if not check_password_hash(usuario.senha, senha_atual):
                flash('Senha atual incorreta!', 'error')
                return redirect(url_for('minhaconta'))
            
            # Verificar se as senhas novas coincidem
            if nova_senha != confirmar_senha:
                flash('As senhas não coincidem!', 'error')
                return redirect(url_for('minhaconta'))
            
            # Verificar se a senha tem pelo menos 6 caracteres
            if len(nova_senha) < 6:
                flash('A nova senha deve ter pelo menos 6 caracteres!', 'error')
                return redirect(url_for('minhaconta'))
            
            # Atualizar senha
            usuario.senha = generate_password_hash(nova_senha)
            from config import db
            db.session.commit()
            
            flash('Senha alterada com sucesso!', 'success')
            return redirect(url_for('minhaconta'))
        
        return redirect(url_for('minhaconta'))
    
    @staticmethod
    def apiia_listar():
        """Lista todas as APIs de IA"""
        apis = ApiIa.query.all()
        return jsonify([{
            'id': api.id,
            'nome': api.nome,
            'api_key': api.api_key,
            'modelo_chat': api.modelo_chat,
            'modelo_voz': api.modelo_voz,
            'modelo_visao': api.modelo_visao,
            'endpoint': api.endpoint,
            'ativo': api.ativo
        } for api in apis])
    
    @staticmethod
    def apiia_criar():
        """Cria uma nova API de IA"""
        if request.method == 'POST':
            nome = request.form.get('nome')
            api_key = request.form.get('api_key')
            modelo_chat = request.form.get('modelo_chat')
            modelo_voz = request.form.get('modelo_voz')
            modelo_visao = request.form.get('modelo_visao')
            endpoint = request.form.get('endpoint')
            
            if not nome or not api_key:
                flash('Nome e API Key são obrigatórios!', 'error')
                return redirect(url_for('minhaconta'))
            
            # Criar nova API
            nova_api = ApiIa(
                nome=nome,
                api_key=api_key,
                modelo_chat=modelo_chat,
                modelo_voz=modelo_voz,
                modelo_visao=modelo_visao,
                endpoint=endpoint,
                ativo=True
            )
            
            from config import db
            db.session.add(nova_api)
            db.session.commit()
            
            flash('API criada com sucesso!', 'success')
            return redirect(url_for('minhaconta'))
        
        return redirect(url_for('minhaconta'))
    
    @staticmethod
    def apiia_editar(id):
        """Edita uma API de IA existente"""
        if request.method == 'POST':
            api = ApiIa.query.get(id)
            if not api:
                flash('API não encontrada!', 'error')
                return redirect(url_for('minhaconta'))
            
            api.nome = request.form.get('nome')
            api.api_key = request.form.get('api_key')
            api.modelo_chat = request.form.get('modelo_chat')
            api.modelo_voz = request.form.get('modelo_voz')
            api.modelo_visao = request.form.get('modelo_visao')
            api.endpoint = request.form.get('endpoint')
            
            from config import db
            db.session.commit()
            
            flash('API atualizada com sucesso!', 'success')
            return redirect(url_for('minhaconta'))
        
        return redirect(url_for('minhaconta'))
    
    @staticmethod
    def apiia_excluir(id):
        """Exclui uma API de IA"""
        api = ApiIa.query.get(id)
        if not api:
            flash('API não encontrada!', 'error')
            return redirect(url_for('minhaconta'))
        
        from config import db
        db.session.delete(api)
        db.session.commit()
        
        flash('API excluída com sucesso!', 'success')
        return redirect(url_for('minhaconta'))
    
    @staticmethod
    def _gerar_html_tabela_apis():
        """Método auxiliar para gerar HTML da tabela de APIs"""
        apis_ia = ApiIa.query.all()
        if not apis_ia:
            return '<tr><td colspan="8" class="text-center text-muted">Nenhuma API cadastrada.</td></tr>'
        
        html = ''
        for api_item in apis_ia:
            # Gerar o botão de ativar/desativar
            if api_item.ativo:
                ativar_btn = f'<a href="/minhaconta/apiia/{api_item.id}/desativar" class="btn btn-success api" title="Clique para desativar" hx-get="/minhaconta/apiia/{api_item.id}/desativar" hx-target="closest tbody" hx-swap="innerHTML">Ativo</a>'
            else:
                ativar_btn = f'<a href="/minhaconta/apiia/{api_item.id}/ativar" class="btn btn-secondary api" title="Clique para ativar" hx-get="/minhaconta/apiia/{api_item.id}/ativar" hx-target="closest tbody" hx-swap="innerHTML">Inativo</a>'
            
            # Gerar o HTML da linha
            html += f'''
            <tr>
                <td>{api_item.nome}</td>
                <td>{ativar_btn}</td>
                <td>{api_item.api_key[:10] if api_item.api_key else ""}...</td>
                <td>{api_item.modelo_chat or ""}</td>
                <td>{api_item.modelo_voz or ""}</td>
                <td>{api_item.modelo_visao or ""}</td>
                <td>{api_item.endpoint or ""}</td>
                <td nowrap>
                    <button class="btn btn-sm btn-info btn-testar-api me-1" data-api-id="{api_item.id}" data-api-nome="{api_item.nome}" type="button" title="Testar API">
                        <i class="fas fa-play"></i> Testar
                    </button>
                    <button class="btn btn-sm btn-warning btn-editar-api me-1" data-api-id="{api_item.id}" data-api-nome="{api_item.nome}" data-api-key="{api_item.api_key or ""}" data-modelo-chat="{api_item.modelo_chat or ""}" data-modelo-voz="{api_item.modelo_voz or ""}" data-modelo-visao="{api_item.modelo_visao or ""}" data-endpoint="{api_item.endpoint or ""}" type="button" title="Editar API">
                        <i class="fas fa-edit"></i> Editar
                    </button>
                    <button class="btn btn-sm btn-danger btn-excluir-api" data-api-id="{api_item.id}" hx-get="/minhaconta/apiia/{api_item.id}/excluir" hx-target="closest tr" hx-swap="outerHTML remove" type="button">
                        Excluir
                    </button>
                </td>
            </tr>
            '''
        return html

    @staticmethod
    def apiia_ativar(id):
        """Ativa uma API de IA"""
        api = ApiIa.query.get(id)
        if not api:
            if request.headers.get('HX-Request'):
                return '<tr><td colspan="8" class="text-center text-danger">API não encontrada!</td></tr>'
            flash('API não encontrada!', 'error')
            return redirect(url_for('minhaconta'))
        
        api.ativo = True
        from config import db
        db.session.commit()
        
        # Se for requisição HTMX, retornar apenas o HTML da tabela atualizada
        if request.headers.get('HX-Request'):
            return UsuarioController._gerar_html_tabela_apis()
        
        flash('API ativada com sucesso!', 'success')
        return redirect(url_for('minhaconta'))
    
    @staticmethod
    def apiia_desativar(id):
        """Desativa uma API de IA"""
        api = ApiIa.query.get(id)
        if not api:
            if request.headers.get('HX-Request'):
                return '<tr><td colspan="8" class="text-center text-danger">API não encontrada!</td></tr>'
            flash('API não encontrada!', 'error')
            return redirect(url_for('minhaconta'))
        
        api.ativo = False
        from config import db
        db.session.commit()
        
        # Se for requisição HTMX, retornar apenas o HTML da tabela atualizada
        if request.headers.get('HX-Request'):
            return UsuarioController._gerar_html_tabela_apis()
        
        flash('API desativada com sucesso!', 'success')
        return redirect(url_for('minhaconta'))
    
    @staticmethod
    def exportar_banco():
        """
        Exporta o banco de dados SQLite para download
        """
        try:
            # Caminho fixo do banco de dados
            db_path = get_database_path()
            
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
    def importar_banco():
        """
        Importa um arquivo .db para substituir o banco de dados atual
        """
        try:
            # Verificar se foi enviado um arquivo
            if 'arquivo_banco' not in request.files:
                flash('Nenhum arquivo foi enviado!', 'error')
                return redirect(url_for('minhaconta'))
            
            arquivo = request.files['arquivo_banco']
            
            # Verificar se o arquivo foi selecionado
            if arquivo.filename == '':
                flash('Nenhum arquivo foi selecionado!', 'error')
                return redirect(url_for('minhaconta'))
            
            # Verificar se é um arquivo .db
            if not arquivo.filename.lower().endswith('.db'):
                flash('Por favor, selecione apenas arquivos .db!', 'error')
                return redirect(url_for('minhaconta'))
            
            # Verificar se o arquivo não está vazio
            arquivo.seek(0, 2)  # Ir para o final do arquivo
            tamanho = arquivo.tell()  # Obter o tamanho
            arquivo.seek(0)  # Voltar para o início
            
            if tamanho == 0:
                flash('O arquivo está vazio!', 'error')
                return redirect(url_for('minhaconta'))
            
            # Verificar se é um arquivo SQLite válido (deve começar com "SQLite format 3")
            conteudo_inicial = arquivo.read(16)
            arquivo.seek(0)  # Voltar para o início
            
            if not conteudo_inicial.startswith(b'SQLite format 3'):
                flash('O arquivo não parece ser um banco de dados SQLite válido!', 'error')
                return redirect(url_for('minhaconta'))
            
            # Caminho do banco de dados atual
            db_path = get_database_path()
            
            print(f"Banco de dados importado para: {db_path}")
            
            # Criar backup do banco atual antes de substituir
            if os.path.exists(db_path):
                backup_path = os.path.join(
                    os.path.dirname(db_path),
                    f'agente_virtus_backup_antes_importacao_{datetime.now().strftime("%Y%m%d_%H%M%S")}.db'
                )
                    
                shutil.copy2(db_path, backup_path)
                print(f"✅ Backup criado: {backup_path}")
            
            # Salvar o novo arquivo
            arquivo.save(db_path)
            
            flash(f'Banco de dados importado com sucesso! Arquivo "{arquivo.filename}" foi salvo como {db_path}. Recomenda-se reiniciar a aplicação para garantir que todas as mudanças sejam aplicadas corretamente.', 'success')
            
            # Redirecionar para a página inicial
            return redirect(url_for('minhaconta'))
            
        except Exception as e:
            flash(f'Erro ao importar banco de dados: {str(e)}', 'error')
            return redirect(url_for('minhaconta'))
    
    @staticmethod
    def info_sistema():
        """
        Retorna informações do sistema
        """
        try:
            # Informações do banco de dados
            db_info = get_database_info()
            
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

    @staticmethod
    def salvar_proxy():
        """Salvar configurações de proxy"""
        try:
            endereco = request.form.get('proxy_endereco', '').strip()
            login = request.form.get('proxy_login', '').strip()
            senha = request.form.get('proxy_senha', '').strip()
            
            # Salvar configurações no SystemConfig
            SystemConfig.set_config('proxy_endereco', endereco, 'Endereço do servidor proxy')
            SystemConfig.set_config('proxy_login', login, 'Login para autenticação no proxy')
            SystemConfig.set_config('proxy_senha', senha, 'Senha para autenticação no proxy')
            
            return jsonify({
                'status': 'success',
                'message': 'Configurações de proxy salvas com sucesso!'
            })
            
        except Exception as e:
            return jsonify({
                'status': 'error',
                'message': f'Erro ao salvar configurações de proxy: {str(e)}'
            }), 500

    @staticmethod
    def carregar_proxy():
        """Carregar configurações de proxy"""
        try:
            config = {
                'endereco': SystemConfig.get_config('proxy_endereco', ''),
                'login': SystemConfig.get_config('proxy_login', ''),
                'senha': SystemConfig.get_config('proxy_senha', '')
            }
            
            return jsonify({
                'status': 'success',
                'config': config
            })
            
        except Exception as e:
            return jsonify({
                'status': 'error',
                'message': f'Erro ao carregar configurações de proxy: {str(e)}'
            }), 500

    @staticmethod
    def testar_proxy():
        """Testar conexão com proxy"""
        try:
            data = request.get_json()
            endereco = data.get('endereco', '').strip()
            login = data.get('login', '').strip()
            senha = data.get('senha', '').strip()
            
            if not endereco:
                return jsonify({
                    'status': 'error',
                    'message': 'Endereço do proxy é obrigatório'
                }), 400
            
            # Configurar proxy para teste
            proxies = {}
            if endereco:
                proxy_url = f"http://{endereco}"
                if login and senha:
                    # Proxy com autenticação
                    proxy_url = f"http://{login}:{senha}@{endereco}"
                proxies = {
                    'http': proxy_url,
                    'https': proxy_url
                }
            
            # Testar conexão fazendo uma requisição simples
            try:
                response = requests.get(
                    'http://httpbin.org/ip',
                    proxies=proxies,
                    timeout=10
                )
                
                if response.status_code == 200:
                    return jsonify({
                        'status': 'success',
                        'message': 'Conexão com proxy estabelecida com sucesso!',
                        'ip_info': response.json()
                    })
                else:
                    return jsonify({
                        'status': 'error',
                        'message': f'Erro na conexão: Status {response.status_code}'
                    }), 400
                    
            except requests.exceptions.ProxyError:
                return jsonify({
                    'status': 'error',
                    'message': 'Erro de conexão com o proxy. Verifique o endereço e credenciais.'
                }), 400
            except requests.exceptions.Timeout:
                return jsonify({
                    'status': 'error',
                    'message': 'Timeout na conexão com o proxy. Verifique se o servidor está acessível.'
                }), 400
            except requests.exceptions.RequestException as e:
                return jsonify({
                    'status': 'error',
                    'message': f'Erro na requisição: {str(e)}'
                }), 400
                
        except Exception as e:
            return jsonify({
                'status': 'error',
                'message': f'Erro ao testar proxy: {str(e)}'
            }), 500

    @staticmethod
    def limpar_proxy():
        """Limpar configurações de proxy"""
        try:
            # Remover configurações do SystemConfig
            from config import db
            
            # Buscar e remover configurações existentes
            configs = SystemConfig.query.filter(
                SystemConfig.chave.in_(['proxy_endereco', 'proxy_login', 'proxy_senha'])
            ).all()
            
            for config in configs:
                db.session.delete(config)
            
            db.session.commit()
            
            return jsonify({
                'status': 'success',
                'message': 'Configurações de proxy removidas com sucesso!'
            })
            
        except Exception as e:
            return jsonify({
                'status': 'error',
                'message': f'Erro ao limpar configurações de proxy: {str(e)}'
            }), 500