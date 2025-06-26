from flask import render_template, request
from controllers.UsuarioController import UsuarioController
from controllers.AgentesController import AgentesController
from controllers.FerramentasController import FerramentasController
from controllers.PesquisarController import PesquisarController

def init_routes(app):
    """
    Inicializa todas as rotas da aplicação
    """
    
    # Rota da página inicial
    @app.route('/')
    def index():
        return render_template('index.html')
    
    @app.route('/minhaconta', methods=['GET', 'POST'])
    def minhaconta():
        return UsuarioController.minhaconta()
    
    
    ##########################################################################################################
    # Rotas de agentes inteligentes
    ##########################################################################################################
    # Rotas de agentes inteligentes
    @app.route('/agentesinteligentes/equipes')
    def listar_equipes_inteligentes():
        return AgentesController.listar_equipes_inteligentes()
    
    @app.route('/agentesinteligentes/canva', defaults={'equipe_id': None})
    @app.route('/agentesinteligentes/canva/<int:equipe_id>')
    def canva(equipe_id):
        return AgentesController.canva(equipe_id)

    @app.route('/agentesinteligentes/criar_equipe/', methods=['POST'])
    def criar_equipe_inteligente():
        return AgentesController.criar_equipe_inteligente()
    
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
    
    @app.route('/agentesinteligentes/download_arquivo/<int:equipe_id>/<node_id>/<formato>')
    def download_arquivo_formato(equipe_id, node_id, formato):
        return AgentesController.download_arquivo_formato(equipe_id, node_id, formato)
    
    
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
    # Pesquisar
    ##########################################################################################################
    # Rotas de pesquisa
    @app.route('/pesquisar', methods=['GET', 'POST'])
    def pesquisar():
        return PesquisarController.pesquisar()
    
    
    
    
    
    
    
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
    