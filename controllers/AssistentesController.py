from flask import render_template, request, redirect, url_for, jsonify
from models.models import Assistente, db
import controllers.IaController as IaController

class AssistentesController:
    @staticmethod
    def index():
        """Renderiza a página com os assistentes"""
        
        assistentes = Assistente.query.all()
        
        return render_template('assistentes/index.html', assistentes=assistentes)
    
    @staticmethod
    def novo(id=None):
        """Renderiza a página para criar um novo assistente"""
        assistente = None
        if id:
            assistente = Assistente.query.get_or_404(id)
        
        return render_template('assistentes/novo.html', assistente=assistente)

    @staticmethod
    def salvar():
        """Salva um novo assistente"""
        nome = request.form['nome']
        descricao = request.form['descricao']
        conhecimento = request.files['conhecimento']
        
        # Inicializa conhecimento como None
        conhecimento_texto = None
        
        # Se um arquivo foi enviado, lê seu conteúdo
        if conhecimento and conhecimento.filename:
            try:
                # Lê o conteúdo do arquivo como texto
                conhecimento_texto = conhecimento.read().decode('utf-8')
            except UnicodeDecodeError:
                # Se não conseguir decodificar como UTF-8, tenta outras codificações
                conhecimento.seek(0)  # Volta ao início do arquivo
                try:
                    conhecimento_texto = conhecimento.read().decode('latin-1')
                except:
                    conhecimento_texto = str(conhecimento.read())
        
        assistente = Assistente(nome=nome, descricao=descricao, conhecimento=conhecimento_texto)
        db.session.add(assistente)
        db.session.commit()
        
        return redirect(url_for('assistentes'))

    @staticmethod
    def executar(id):
        """Executa um assistente"""
        assistente = Assistente.query.get_or_404(id)
        
        return render_template('assistentes/executar.html', assistente=assistente)

    @staticmethod
    def executar_post():
        """Processa a execução do assistente com o texto enviado pelo usuário"""
        pergunta = request.form['pergunta']
        assistente_id = request.form['assistente_id']
        
        assistente = Assistente.query.get_or_404(assistente_id)
        
        # Garantir que todas as variáveis sejam strings válidas
        pergunta_str = str(pergunta) if pergunta is not None else ""
        descricao_str = str(assistente.descricao) if assistente.descricao is not None else ""
        conhecimento_str = str(assistente.conhecimento) if assistente.conhecimento is not None else ""
        
        # Construir o prompt de forma segura
        prompt = f"{pergunta_str}\n\n{descricao_str}\n\n{conhecimento_str}"
        
        resultado = IaController.groq(prompt, None, None)
        
        if hasattr(resultado[0], 'get_json'):
            resultado_data = resultado[0].get_json()
        else:
            resultado_data = resultado[0]
            
        print(resultado_data)
        
        return jsonify(resultado_data)
    

    @staticmethod
    def editar(id):
        """Renderiza o formulário de edição de assistente usando o template de novo assistente"""
        assistente = Assistente.query.get_or_404(id)
        return render_template('assistentes/novo.html', assistente=assistente)

    @staticmethod
    def editar_post(id):
        """Processa o formulário de edição de assistente"""
        assistente = Assistente.query.get_or_404(id)
        assistente.nome = request.form['nome']
        assistente.descricao = request.form['descricao']
        db.session.commit()
        return redirect(url_for('assistentes'))

    @staticmethod
    def excluir(id):
        """Exclui um assistente"""
        assistente = Assistente.query.get_or_404(id)
        db.session.delete(assistente)
        db.session.commit()
        return redirect(url_for('assistentes'))