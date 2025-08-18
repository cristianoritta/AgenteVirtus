from flask import render_template, request, jsonify
from controllers.UsuarioController import UsuarioController
from controllers.AgentesController import AgentesController
from controllers.FerramentasController import FerramentasController
from controllers.PesquisarController import PesquisarController
from controllers.AssistentesController import AssistentesController
from controllers.ConversaController import ConversaController
from controllers.NotasController import NotasController
from controllers.PdfController import PdfController
from controllers.FormulariosController import formularios_bp
from controllers.IaController import testar_api_especifica, testar_api_ia, testar_chatbot
from controllers.SobreController import SobreController

from models.models import ApiIa

def init_routes(app):
    """
    Inicializa todas as rotas da aplicação
    """
    
    # Registra o blueprint de formulários
    app.register_blueprint(formularios_bp)
    
    # Rota da página inicial
    @app.route('/')
    def index():
        return render_template('index.html')
    
    @app.route('/sobre')
    def sobre():
        return SobreController.index()
    
    @app.route('/minhaconta', methods=['GET', 'POST'])
    def minhaconta():
        return UsuarioController.minhaconta()
    
    @app.route('/minhaconta/apiia/adicionar', methods=['POST'])
    def apiia_adicionar():
        return UsuarioController.apiia_criar()

    @app.route('/minhaconta/apiia/<int:id>/editar', methods=['GET', 'POST'])
    def apiia_editar(id):
        return UsuarioController.apiia_editar(id)

    @app.route('/minhaconta/apiia/<int:id>/excluir')
    def apiia_excluir(id):
        return UsuarioController.apiia_excluir(id)

    @app.route('/minhaconta/apiia/<int:id>/ativar')
    def apiia_ativar(id):
        return UsuarioController.apiia_ativar(id)

    @app.route('/minhaconta/apiia/<int:id>/desativar')
    def apiia_desativar(id):
        return UsuarioController.apiia_desativar(id)
    
    @app.route('/minhaconta/exportar-banco')
    def exportar_banco():
        return UsuarioController.exportar_banco()
    
    @app.route('/minhaconta/importar-banco', methods=['POST'])
    def importar_banco():
        return UsuarioController.importar_banco()
    
    @app.route('/minhaconta/proxy/salvar', methods=['POST'])
    def salvar_proxy():
        return UsuarioController.salvar_proxy()
    
    @app.route('/minhaconta/proxy/carregar')
    def carregar_proxy():
        return UsuarioController.carregar_proxy()
    
    @app.route('/minhaconta/proxy/testar', methods=['POST'])
    def testar_proxy():
        return UsuarioController.testar_proxy()
    
    @app.route('/minhaconta/proxy/limpar', methods=['POST'])
    def limpar_proxy():
        return UsuarioController.limpar_proxy()
    
    @app.route('/minhaconta/info-sistema')
    def info_sistema():
        return UsuarioController.info_sistema()
    
    ##########################################################################################################
    # Rotas de agentes inteligentes
    ##########################################################################################################
    # Rotas de agentes inteligentes
    @app.route('/agentesinteligentes/equipes')
    def listar_equipes_inteligentes():
        return AgentesController.equipes()
    
    @app.route('/agentesinteligentes/canva', defaults={'equipe_id': None})
    @app.route('/agentesinteligentes/canva/<int:equipe_id>')
    def canva(equipe_id):
        return AgentesController.canva(equipe_id)

    @app.route('/agentesinteligentes/criar_equipe/', methods=['POST'])
    def criar_equipe_inteligente():
        return AgentesController.criar_equipe_inteligente()
    
    @app.route('/agentesinteligentes/upload_template', methods=['POST'])
    def upload_template():
        return AgentesController.upload_template()
    
    @app.route('/agentesinteligentes/equipe/<int:equipe_id>/editar', methods=['POST'])
    def editar_equipe_inteligente(equipe_id):
        return AgentesController.editar_equipe_inteligente(equipe_id)    
    
    @app.route('/agentesinteligentes/equipe/<int:id>/deletar')
    def deletar_equipe(id):
        return AgentesController.deletar_equipe(id) 

    @app.route('/agentesinteligentes/executar_tarefas/<int:equipe_id>', methods=['GET', 'POST'])
    def executar_tarefas(equipe_id):
        if request.method == 'POST':
            return AgentesController.executar_tarefas(equipe_id, trigger=False)
        else:
            return AgentesController.executar_tarefas(equipe_id, trigger=True)    
    
    @app.route('/agentesinteligentes/equipe/<int:id>/download')
    def download_equipe(id):
        return AgentesController.download_equipe(id)
    
    @app.route('/agentesinteligentes/importar_equipe', methods=['POST'])
    def importar_equipe():
        return AgentesController.importar_equipe()
    
    @app.route('/agentesinteligentes/criar_fluxo_com_ia', methods=['POST'])
    def criar_fluxo_com_ia():
        return AgentesController.criar_fluxo_com_ia()
    
    @app.route('/agentesinteligentes/download_arquivo/<int:equipe_id>/<node_id>/<formato>')
    def download_arquivo_formato(equipe_id, node_id, formato):
        return AgentesController.download_arquivo_formato(equipe_id, node_id, formato)
    
    @app.route('/agentesinteligentes/equipe/<int:equipe_id>/salvar-menu', methods=['POST'])
    def salvar_menu(equipe_id):
        return AgentesController.salvar_menu(equipe_id)
    
    # Rota para acessar agentes do menu dinâmico
    @app.route('/agentesinteligentes/menu/<int:id>')
    def agentes_menu(id):
        return AgentesController.agentes_menu(id)
    
    # Rotas para execuções
    @app.route('/agentesinteligentes/execucoes')
    def listar_execucoes():
        return AgentesController.listar_execucoes()
    
    @app.route('/agentesinteligentes/equipe/<int:equipe_id>/execucoes')
    def listar_execucoes_equipe(equipe_id):
        return AgentesController.listar_execucoes(equipe_id)
    
    @app.route('/agentesinteligentes/execucao/<int:execucao_id>')
    def detalhes_execucao(execucao_id):
        return AgentesController.detalhes_execucao(execucao_id)
    
    @app.route('/agentesinteligentes/execucao/<int:execucao_id>/excluir', methods=['POST'])
    def excluir_execucao(execucao_id):
        return AgentesController.excluir_execucao(execucao_id)
    
    @app.route('/agentesinteligentes/execucoes/exportar')
    def exportar_execucoes():
        return AgentesController.exportar_execucoes()
    
    @app.route('/agentesinteligentes/equipe/<int:equipe_id>/execucoes/exportar')
    def exportar_execucoes_equipe(equipe_id):
        return AgentesController.exportar_execucoes(equipe_id)
    
    
    ##########################################################################################################
    # Rotas de assistentes
    ##########################################################################################################
    @app.route('/assistentes')
    def assistentes():
        return AssistentesController.index()
    
    @app.route('/assistentes/novo')
    def assistentes_novo():
        return AssistentesController.novo()
    
    @app.route('/assistentes/salvar', methods=['POST'])
    def assistentes_salvar():
        return AssistentesController.salvar()
    
    @app.route('/assistentes/executar/<int:id>')
    def assistentes_executar(id):
        return AssistentesController.executar(id)
    
    @app.route('/assistentes/executar', methods=['POST'])
    def assistentes_executar_post():
        return AssistentesController.executar_post()
    
    @app.route('/assistentes/<int:id>/editar', methods=['GET'])
    def assistentes_editar(id):
        return AssistentesController.editar(id)

    @app.route('/assistentes/<int:id>/editar', methods=['POST'])
    def assistentes_editar_post(id):
        return AssistentesController.editar_post(id)
    
    @app.route('/assistentes/<int:id>/excluir', methods=['POST'])
    def assistentes_excluir(id):
        return AssistentesController.excluir(id)
    
    ##########################################################################################################
    # Rotas de ferramentas
    ##########################################################################################################
    # Rotas de ferramentas
    @app.route('/ferramentas/transcrever', methods=['GET', 'POST'])
    def transcrever():
        return FerramentasController.transcrever()
    
    # Chat
    @app.route('/ferramentas/chatbot', methods=['GET', 'POST'])
    def chatbot():
        return FerramentasController.chatbot()
    
    # Template parcial para mensagens do chat
    @app.route('/ferramentas/chat_mensagem_partial', methods=['POST'])
    def chat_mensagem_partial():
        return FerramentasController.chat_mensagem_partial()
    
    ##########################################################################################################
    # Rotas de PDF
    ##########################################################################################################
    @app.route('/pdf')
    def pdf_index():
        return PdfController.index()
    
    @app.route('/pdf/unir', methods=['GET', 'POST'])
    def pdf_unir():
        return PdfController.unir_pdfs()
    
    @app.route('/pdf/separar', methods=['GET', 'POST'])
    def pdf_separar():
        return PdfController.separar_pdf()
    
    @app.route('/pdf/girar', methods=['GET', 'POST'])
    def pdf_girar():
        return PdfController.girar_pdf()
    
    @app.route('/pdf/bookmarks', methods=['GET', 'POST'])
    def pdf_bookmarks():
        return PdfController.dividir_por_bookmarks()
    
    @app.route('/pdf/extrair-texto', methods=['GET', 'POST'])
    def pdf_extrair_texto():
        return PdfController.extrair_texto()
    
    @app.route('/pdf/extrair-paginas', methods=['GET', 'POST'])
    def pdf_extrair_paginas():
        return PdfController.extrair_paginas()
    
    @app.route('/pdf/resumir', methods=['GET', 'POST'])
    def pdf_resumir():
        return PdfController.resumir_pdf()
    
    @app.route('/pdf/markdown', methods=['GET', 'POST'])
    def pdf_markdown():
        return PdfController.pdf_para_markdown()
    
    @app.route('/pdf/mapa-mental', methods=['GET', 'POST'])
    def pdf_mapa_mental():
        return PdfController.pdf_para_mapa_mental()
    
    @app.route('/pdf/docx', methods=['GET', 'POST'])
    def pdf_docx():
        return PdfController.pdf_para_docx()
    
    @app.route('/pdf/xlsx', methods=['GET', 'POST'])
    def pdf_xlsx():
        return PdfController.pdf_para_xlsx()
    
    @app.route('/pdf/csv', methods=['GET', 'POST'])
    def pdf_csv():
        return PdfController.pdf_para_csv()
    
    @app.route('/pdf/inserir', methods=['GET', 'POST'])
    def pdf_inserir():
        return PdfController.inserir_pdf()
    
    @app.route('/pdf/ocr', methods=['GET', 'POST'])
    def pdf_ocr():
        return PdfController.ocr_pdf()
    
    @app.route('/pdf/comprimir', methods=['GET', 'POST'])
    def pdf_comprimir():
        return PdfController.comprimir_pdf()
    
    ##########################################################################################################
    # Pesquisar
    ##########################################################################################################
    # Rotas de pesquisa
    @app.route('/pesquisar', methods=['GET', 'POST'])
    def pesquisar():
        return PesquisarController.pesquisar()
    
    
    
    
    
    
    ##########################################################################################################
    # Usuário
    ##########################################################################################################
    # API endpoints
    @app.route('/api/usuarios')
    def api_usuarios():
        return UsuarioController.api_usuarios()
    
    @app.route('/api/usuario/<int:id>')
    def api_usuario(id):
        return UsuarioController.api_usuario(id)
    
    
    
    ##########################################################################################################
    # Usuários
    ##########################################################################################################
    # Rotas de usuários
    @app.route('/usuarios')
    def usuarios():
        return UsuarioController.index()
    
    @app.route('/usuario/novo', methods=['GET', 'POST'])
    def novo_usuario():
        return UsuarioController.novo()
    
    @app.route('/usuario/<int:id>')
    def ver_usuario(id):
        return UsuarioController.ver(id)
    
    @app.route('/usuario/<int:id>/editar', methods=['GET', 'POST'])
    def editar_usuario(id):
        return UsuarioController.editar(id)
    
    @app.route('/usuario/<int:id>/deletar', methods=['POST'])
    def deletar_usuario(id):
        return UsuarioController.deletar(id)
    
    ##########################################################################################################
    # Rotas de conversas (Sistema de Memória)
    ##########################################################################################################
    @app.route('/conversas')
    def conversas():
        return render_template('conversas/index.html')
    
    @app.route('/api/conversas', methods=['GET'])
    def api_listar_conversas():
        return ConversaController.listar_conversas()
    
    @app.route('/api/conversas/sidebar', methods=['GET'])
    def api_listar_conversas_sidebar():
        return ConversaController.listar_conversas_sidebar()
    
    @app.route('/api/conversa', methods=['GET'])
    def api_obter_conversa():
        return ConversaController.obter_conversa()
    
    @app.route('/api/conversa/criar', methods=['POST'])
    def api_criar_conversa():
        return ConversaController.criar_conversa()
    
    @app.route('/api/conversa/atualizar-titulo', methods=['POST'])
    def api_atualizar_titulo_conversa():
        return ConversaController.atualizar_titulo()
    
    @app.route('/api/conversa/encerrar', methods=['POST'])
    def api_encerrar_conversa():
        return ConversaController.encerrar_conversa()
    
    @app.route('/api/conversa/deletar', methods=['POST'])
    def api_deletar_conversa():
        return ConversaController.deletar_conversa()
    
    
    ##########################################################################################################
    # Rotas para Notas (Zettelkasten/Supernotes)
    ##########################################################################################################
    @app.route('/notas')
    def notas():
        return NotasController.index()
    
    @app.route('/notas/<int:id>')
    def ver_nota(id):
        return NotasController.ver_nota(id)

    @app.route('/notas/kanban')
    def notas_kanban():
        return render_template('notas/kanban.html')
    
    # API para listar notas
    @app.route('/api/notas', methods=['GET'])
    def api_listar_notas():
        return NotasController.api_listar_notas()
    
    # API para obter uma nota específica
    @app.route('/api/nota', methods=['GET'])
    def api_obter_nota():
        return NotasController.api_obter_nota()
    
    # API para criar nota
    @app.route('/api/nota/criar', methods=['POST'])
    def api_criar_nota():
        return NotasController.api_criar_nota()
    
    # API para atualizar nota
    @app.route('/api/nota/atualizar', methods=['POST'])
    def api_atualizar_nota():
        return NotasController.api_atualizar_nota()
    
    # API para deletar nota
    @app.route('/api/nota/deletar', methods=['POST'])
    def api_deletar_nota():
        return NotasController.api_deletar_nota()
    
    # API para listar categorias
    @app.route('/api/notas/categorias', methods=['GET'])
    def api_listar_categorias():
        return NotasController.api_listar_categorias()
    
    # API para criar categoria
    @app.route('/api/notas/categoria/criar', methods=['POST'])
    def api_criar_categoria():
        return NotasController.api_criar_categoria()
    
    # API para buscar notas
    @app.route('/api/notas/buscar', methods=['GET'])
    def api_buscar_notas():
        return NotasController.api_buscar_notas()
    
    # API para gerar resumo
    @app.route('/api/notas/gerar-resumo', methods=['POST'])
    def api_gerar_resumo():
        return NotasController.api_gerar_resumo()
    
    # API para estatísticas
    @app.route('/api/notas/estatisticas', methods=['GET'])
    def api_estatisticas():
        return NotasController.api_estatisticas()
    
    # API para atualizar categoria da nota
    @app.route('/api/notas/<int:nota_id>/categoria', methods=['PUT'])
    def api_atualizar_categoria_nota(nota_id):
        return NotasController.api_atualizar_categoria_nota(nota_id)
    
    # API para download de todas as notas
    @app.route('/api/notas/download', methods=['GET'])
    def api_download_notas():
        return NotasController.api_download_notas()
    
    # API para listar equipes inteligentes
    @app.route('/api/agentes/equipes', methods=['GET'])
    def api_listar_equipes():
        return AgentesController.api_listar_equipes()
    
    # API para executar equipe com nota
    @app.route('/api/agentes/equipe/<int:equipe_id>/executar', methods=['POST'])
    def api_executar_equipe_com_nota(equipe_id):
        return AgentesController.api_executar_equipe_com_nota(equipe_id)
    
    ##########################################################################################################
    # Teste da API de IA
    ##########################################################################################################
    @app.route('/api/testar-ia', methods=['GET'])
    def testar_api_ia():
        resultado = testar_api_ia()
        return jsonify(resultado)
    
    @app.route('/ferramentas/testar-api/<int:api_id>')
    def testar_api_page(api_id):
        api = ApiIa.query.get(api_id)
        
        return render_template('ferramentas/testar_api.html', api=api)
    
    @app.route('/api/testar-chatbot', methods=['POST'])
    def testar_chatbot_api():
        mensagem = request.form.get('mensagem', 'Olá, como você está?')
        resultado = testar_chatbot(mensagem)
        return jsonify(resultado)
    
    @app.route('/api/testar-api/<int:api_id>', methods=['GET'])
    def testar_api_especifica_api(api_id):
        resultado = testar_api_especifica(api_id)
        return jsonify(resultado)
    
    
    