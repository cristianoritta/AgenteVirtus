from flask import render_template, request, redirect, url_for, flash, jsonify, make_response
from datetime import datetime
from models.models import EquipeInteligente, Usuario
from config import db
import json
import base64
import os
import requests
import controllers.IaController as IaController
import PyPDF2
import tempfile
import csv
import io
from docx import Document
from docx.shared import Inches
import markdown
import matplotlib.pyplot as plt
import networkx as nx
from io import BytesIO
import pandas as pd

class AgentesController:
    @staticmethod
    def canva(equipe_id=None):
        """Renderiza a página do canvas para criação ou edição de equipes"""
        equipe_data = None
        if equipe_id:
            equipe = EquipeInteligente.query.get_or_404(equipe_id)
            equipe_data = {
                'id': equipe.id,
                'nome': equipe.nome,
                'descricao': equipe.descricao,
                'processo': equipe.processo,
                'layout': json.loads(equipe.layout) if equipe.layout else {'nodes': [], 'connections': []}
            }
        
        return render_template('agentes/canva.html', equipe_data=equipe_data)
    
    @staticmethod
    def criar_equipe_inteligente():
        """Cria uma nova equipe inteligente a partir dos dados do canvas"""
        data = request.get_json()
        
        try:
            # 1. Criar a equipe
            nova_equipe = EquipeInteligente(
                nome=data.get('nome'),
                descricao=data.get('descricao'),
                processo=data.get('process_type'),
                layout=json.dumps(data.get('layout'))
            )
            db.session.add(nova_equipe)
            db.session.commit()
            
            return jsonify({'status': 'success', 'message': 'Equipe criada com sucesso!', 'equipe_id': nova_equipe.id})

        except Exception as e:
            db.session.rollback()
            print(f"Erro ao salvar equipe: {e}")
            return jsonify({'status': 'error', 'message': f'Erro ao salvar equipe: {str(e)}'}), 500

    @staticmethod
    def editar_equipe_inteligente(equipe_id):
        """Atualiza uma equipe inteligente existente."""
        equipe = EquipeInteligente.query.get_or_404(equipe_id)
        data = request.get_json()

        try:
            equipe.nome = data.get('nome')
            equipe.descricao = data.get('descricao')
            equipe.processo = data.get('process_type')
            equipe.layout = json.dumps(data.get('layout'))

            db.session.commit()
            
            return jsonify({'status': 'success', 'message': 'Equipe atualizada com sucesso!', 'equipe_id': equipe.id})

        except Exception as e:
            db.session.rollback()
            print(f"Erro ao atualizar equipe: {e}")
            return jsonify({'status': 'error', 'message': f'Erro ao atualizar equipe: {str(e)}'}), 500

    @staticmethod
    def equipes():
        """Página para listar todas as equipes"""
        equipes = EquipeInteligente.query.all()
        return render_template('agentes/equipes.html', equipes=equipes)

    @staticmethod
    def executar_tarefas(equipe_id, trigger = True):
        """Página para executar as tarefas da equipe criada"""
        equipe = EquipeInteligente.query.get(equipe_id)
        
        usuario = Usuario.query.get(1)
        print(usuario)
        
        # Fazer o parse do JSON do layout para que seja acessível no template
        if equipe.layout:
            try:
                equipe.layout = json.loads(equipe.layout)
            except json.JSONDecodeError:
                equipe.layout = {'nodes': [], 'connections': []}
        else:
            equipe.layout = {'nodes': [], 'connections': []}
        
        if trigger:
            return render_template('agentes/executar_tarefas.html', equipe=equipe, trigger=trigger)
        
        # Tipo de Equipe
        tipo_equipe = equipe.layout['nodes'][0]['config']['type']
        
        # Imprimir o arquivo recebido
        if request.method == 'POST':
            
            respostas = []
            
            texto = f"""<meta_parametros>
            Meu nome: {usuario.nome}
            Meu email: {usuario.email}
            Data: {datetime.now().strftime('%d/%m/%Y')}
            Hora: {datetime.now().strftime('%H:%M:%S')}
            </meta_parametros>
            
            """
            
            ########################################################################################
            # TRIGGER
            ########################################################################################
            if tipo_equipe == 'text':
                texto += request.form['texto']

            else:
                """
                Nós que contém arquivos
                """
                arquivo = request.files['arquivo']
                
                if tipo_equipe == 'pdf':
                    # Ler o conteúdo do arquivo diretamente do objeto FileStorage
                    pdf_reader = PyPDF2.PdfReader(arquivo)
                    
                    for page in pdf_reader.pages:
                        texto += page.extract_text()
                elif tipo_equipe == 'audio':
                    # Salvar o arquivo de áudio temporariamente no disco
                    audio_file = request.files['arquivo']
                    temp_audio_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
                        # Ler o conteúdo do arquivo e escrever no arquivo temporário
                        audio_content = audio_file.read()
                        temp_file.write(audio_content)
                        temp_audio_path = temp_file.name  # Caminho do arquivo temporário

                    with open(temp_audio_path, "rb") as file:
                        texto = IaController.groq_transcrever(file)
                
                    
            ########################################################################################
            # PROCESSA TODA A TAREFA, EM SEQUENCIA DE CADA AGENTE
            ########################################################################################
            for node in equipe.layout['nodes']:
                if node['type'] == 'agent':
                    
                    prompt = f"""{node['config']['backstory']}
                    ### TAREFA ###
                    <tarefa>
                    {node['config']['goal']}
                    </tarefa>

                    ### TEXTO PARA PROCESSAR ###
                    <texto_processar>
                    {texto}
                    </texto_processar>
                    """
                    
                    # Testar primeiro sem o arquivo base64
                    resultado = IaController.groq(prompt)
                    
                    # Extrair a resposta do resultado
                    if isinstance(resultado, dict):
                        resultado_data = resultado
                    elif hasattr(resultado, 'get_json'):
                        resultado_data = resultado.get_json()
                    else:
                        resultado_data = resultado
                    
                    if isinstance(resultado_data, dict) and 'resposta' in resultado_data:
                        resposta_texto = resultado_data['resposta']
                    else:
                        resposta_texto = str(resultado_data)
                    
                    texto += f'<node_{node["id"]}>{resposta_texto}</node_{node["id"]}>\n\n\n'
                    
                    respostas.append({
                        'resposta': resposta_texto,
                        'node': node
                    })
                
                ########################################################################################
                # TAREFA
                ########################################################################################
                if node['type'] == 'task':
                    
                    # Obter a última resposta e garantir que seja uma string
                    ultima_resposta = respostas[-1]['resposta']
                    
                    # Se for uma tupla (Response, status_code), extrair o conteúdo
                    if isinstance(ultima_resposta, tuple):
                        if hasattr(ultima_resposta[0], 'get_data'):
                            # Se for um objeto Response do Flask
                            texto_entrada = ultima_resposta[0].get_data(as_text=True)
                        else:
                            texto_entrada = str(ultima_resposta[0])
                    else:
                        texto_entrada = str(ultima_resposta)
                    
                    # Obter o código Python da configuração da task
                    codigo_python = node['config']['expectedOutput']
                    
                    texto_entrada = '00008323520184013202'
                    
                    # Preparar o código completo com a variável texto_entrada definida
                    codigo_completo = codigo_python.replace('{texto_entrada}', texto_entrada)
                    
                    # Executar o código em um namespace local para capturar variáveis
                    local_vars = {}
                    exec(codigo_completo, globals(), local_vars)
                    
                    # Capturar o resultado - pode ser de uma variável 'resultado' ou a última expressão
                    resultado_task = local_vars.get('resultado', 'Código executado com sucesso')
                    
                    # Adicionar o resultado ao array de respostas
                    respostas.append({
                        'resposta': resultado_task,
                        'node': node
                    })
                    
                    # Atualizar o texto para o próximo agente/task
                    texto += '\n\n ########' + resultado_task
                
                if node['type'] == 'guardrail':
                    
                    prompt = f"""
                    ### GUARDRAIL ###
                    <tarefa>
                    {node['config']['rules']}
                    </tarefa>

                    ### TEXTO PARA PROCESSAR ###
                    <texto_processar>
                    {respostas[-1]['resposta']}
                    </texto_processar>

                    ### FORMATO DE SAÍDA ###
                    <formato_saida>
                    REESCREVA o <texto_processar> observando o formato de saída: {node['config']['outputFormat']}
                    
                    ATENÇÃO.
                    ESCREVA APENAS O TEXTO REESCRITO, SEM NADA MAIS. Se o formato de saída for JSON, escreva apenas o JSON, sem aspas.
                    Se o formato de saída for Texto, escreva apenas o texto, sem comentários nem nada além do texto.
                    </formato_saida>
                    """
                    
                    print(prompt)
                    
                    # Testar primeiro sem o arquivo base64
                    resultado = IaController.groq(prompt)
                    
                    print(resultado)
                    print(type(resultado))
                    
                    # Extrair a resposta do resultado
                    if isinstance(resultado, dict):
                        resultado_data = resultado
                    elif hasattr(resultado, 'get_json'):
                        resultado_data = resultado.get_json()
                    else:
                        resultado_data = resultado
                    
                    if isinstance(resultado_data, dict) and 'resposta' in resultado_data:
                        resposta_texto = resultado_data['resposta']
                    else:
                        resposta_texto = str(resultado_data)
                    
                    texto += f'<node_{node["id"]}>{resposta_texto}</node_{node["id"]}>\n\n\n'
                    
                    respostas.append({
                        'resposta': resposta_texto,
                        'node': node
                    })
                
                if node['type'] == 'formatoSaida':
                    # Obter o conteúdo da última resposta
                    ultima_resposta = respostas[-1]['resposta']
                    
                    # Se for uma tupla (Response, status_code), extrair o conteúdo
                    if isinstance(ultima_resposta, tuple):
                        if hasattr(ultima_resposta[0], 'get_data'):
                            # Se for um objeto Response do Flask
                            conteudo_para_formatar = ultima_resposta[0].get_data(as_text=True)
                        else:
                            conteudo_para_formatar = str(ultima_resposta[0])
                    else:
                        conteudo_para_formatar = str(ultima_resposta)
                    
                    # Gerar arquivo no formato especificado
                    formato = node['config']['type']
                    nome_arquivo = f"resultado_{equipe.nome}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                    
                    arquivo_output, nome_arquivo_final, content_type = AgentesController.gerar_arquivo_saida(
                        conteudo_para_formatar, formato, nome_arquivo
                    )
                    
                    # Criar resposta para download
                    response = make_response(arquivo_output.getvalue())
                    response.headers['Content-Disposition'] = f'attachment; filename={nome_arquivo_final}'
                    response.headers['Content-Type'] = content_type
                    
                    # Adicionar à lista de respostas
                    respostas.append({
                        'resposta': f"Arquivo gerado: {nome_arquivo_final}",
                        'node': node,
                        'arquivo_download': response
                    })
                    
                    # Atualizar o texto para o próximo agente/task
                    texto += f'\n\n<node_{node["id"]}>Arquivo gerado: {nome_arquivo_final}</node_{node["id"]}>'
                
                # Se for o ultimo agente, retorna o resultado
                if node == equipe.layout['nodes'][-1]:
                    if node['type'] == 'agent' or node['type'] == 'guardrail':
                        resultado = resposta_texto
                    elif node['type'] == 'task':
                        resultado = resultado_task
                    elif node['type'] == 'formatoSaida':
                        # Se o último nó for formatoSaida, retornar o arquivo para download
                        return respostas[-1]['arquivo_download']
                    else:
                        resultado = "Processamento concluído"
            
            return render_template('agentes/resultado.html', resultado=resultado, respostas=respostas, equipe=equipe)
    
    @staticmethod
    def listar_equipes_inteligentes():
        """Lista todas as equipes inteligentes salvas"""
        equipes = EquipeInteligente.query.order_by(EquipeInteligente.criado_em.desc()).all()
        return render_template('agentes/equipes.html', equipes=equipes)
    
    @staticmethod
    def editar_equipe(id):
        """Página para editar uma equipe"""
        equipe = EquipeInteligente.query.get(id)
        
        return render_template('agentes/canva.html', equipe=equipe)
    
    @staticmethod
    def deletar_equipe(id):
        """Deleta uma equipe"""
        try:
            equipe = EquipeInteligente.query.get(id)
            db.session.delete(equipe)
            db.session.commit()
            return redirect(url_for('listar_equipes_inteligentes'))
        except Exception as e:
            db.session.rollback()
            print(f"Erro ao deletar equipe: {e}")
            flash(f'Erro ao deletar equipe: {str(e)}', 'danger')
            return jsonify({'status': 'error', 'message': f'Erro ao deletar equipe: {str(e)}'}), 500
    
    
    
    @staticmethod
    def download_equipe(id):
        """Download de uma equipe"""
        equipe = EquipeInteligente.query.get(id)
        
        # Prepara um dicionário com os dados da equipe
        equipe_data = {
            'nome': equipe.nome,
            'descricao': equipe.descricao,
            'processo': equipe.processo,
            'layout': json.loads(equipe.layout)
        }
        
        # Retorna um arquivo JSON para download
        response = make_response(json.dumps(equipe_data))
        response.headers['Content-Disposition'] = 'attachment; filename=equipe.json'
        response.headers['Content-Type'] = 'application/json'
        return response
    
    @staticmethod
    def importar_equipe():
        """Importa uma equipe"""
        arquivo = request.files['arquivo']
        
        # Ler o conteúdo do arquivo
        conteudo = arquivo.read()
        
        # Converter o conteúdo para JSON
        equipe_data = json.loads(conteudo)
        
        # Criar a equipe
        equipe = EquipeInteligente(
            nome=equipe_data['nome'],
            descricao=equipe_data['descricao'],
            processo=equipe_data['processo'],
            layout=json.dumps(equipe_data['layout'])
        )
        
        db.session.add(equipe)
        db.session.commit()
        
        return redirect(url_for('listar_equipes_inteligentes'))

    @staticmethod
    def gerar_arquivo_saida(conteudo, formato, nome_arquivo="resultado"):
        """
        Gera um arquivo de saída no formato especificado
        
        Args:
            conteudo: Conteúdo a ser formatado
            formato: Tipo de formato ('texto', 'word', 'csv', 'pdf', 'mapamental', 'markdown', 'json')
            nome_arquivo: Nome base do arquivo
        
        Returns:
            BytesIO: Arquivo em memória pronto para download
        """
        try:
            if formato == 'texto':
                # Arquivo de texto simples
                output = BytesIO()
                output.write(conteudo.encode('utf-8'))
                output.seek(0)
                return output, f"{nome_arquivo}.txt", "text/plain"
                
            elif formato == 'word':
                # Documento Word
                doc = Document()
                doc.add_heading('Resultado do Processamento', 0)
                doc.add_paragraph(conteudo)
                
                output = BytesIO()
                doc.save(output)
                output.seek(0)
                return output, f"{nome_arquivo}.docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                
            elif formato == 'csv':
                # Arquivo CSV
                output = BytesIO()
                writer = csv.writer(output)
                
                # Se o conteúdo for uma string, dividir por linhas
                if isinstance(conteudo, str):
                    linhas = conteudo.split('\n')
                    for linha in linhas:
                        if linha.strip():  # Ignorar linhas vazias
                            writer.writerow([linha])
                else:
                    # Se for uma lista ou outro formato
                    writer.writerow([conteudo])
                
                output.seek(0)
                return output, f"{nome_arquivo}.csv", "text/csv"
                
            elif formato == 'pdf':
                # Arquivo PDF (usando matplotlib para simplicidade)
                fig, ax = plt.subplots(figsize=(12, 8))
                ax.text(0.1, 0.9, 'Resultado do Processamento', transform=ax.transAxes, 
                       fontsize=16, fontweight='bold')
                ax.text(0.1, 0.8, conteudo, transform=ax.transAxes, fontsize=10, 
                       verticalalignment='top', wrap=True)
                ax.set_xlim(0, 1)
                ax.set_ylim(0, 1)
                ax.axis('off')
                
                output = BytesIO()
                plt.savefig(output, format='pdf', bbox_inches='tight')
                plt.close()
                output.seek(0)
                return output, f"{nome_arquivo}.pdf", "application/pdf"
                
            elif formato == 'mapamental':
                # Mapa mental usando networkx
                G = nx.DiGraph()
                
                # Dividir o conteúdo em tópicos principais
                topicos = conteudo.split('\n')[:10]  # Limitar a 10 tópicos
                
                # Adicionar nó central
                G.add_node("Resultado", pos=(0, 0))
                
                # Adicionar tópicos como nós conectados
                for i, topico in enumerate(topicos):
                    if topico.strip():
                        G.add_node(f"Tópico {i+1}", pos=(0.5 * (i % 3 - 1), -0.5 * (i // 3 + 1)))
                        G.add_edge("Resultado", f"Tópico {i+1}")
                
                # Criar visualização
                fig, ax = plt.subplots(figsize=(12, 8))
                pos = nx.get_node_attributes(G, 'pos')
                nx.draw(G, pos, with_labels=True, node_color='lightblue', 
                       node_size=2000, font_size=8, font_weight='bold',
                       arrows=True, edge_color='gray', arrowsize=20)
                
                output = BytesIO()
                plt.savefig(output, format='pdf', bbox_inches='tight')
                plt.close()
                output.seek(0)
                return output, f"{nome_arquivo}_mapamental.pdf", "application/pdf"
                
            elif formato == 'markdown':
                # Arquivo Markdown
                md_content = f"# Resultado do Processamento\n\n{conteudo}"
                output = BytesIO()
                output.write(md_content.encode('utf-8'))
                output.seek(0)
                return output, f"{nome_arquivo}.md", "text/markdown"
                
            elif formato == 'json':
                # Arquivo JSON
                try:
                    # Tentar fazer parse do conteúdo como JSON
                    if isinstance(conteudo, str):
                        json_data = json.loads(conteudo)
                    else:
                        json_data = conteudo
                except:
                    # Se não for JSON válido, criar um objeto com o conteúdo
                    json_data = {"resultado": conteudo, "timestamp": datetime.now().isoformat()}
                
                output = BytesIO()
                json.dump(json_data, output, indent=2, ensure_ascii=False)
                output.seek(0)
                return output, f"{nome_arquivo}.json", "application/json"
                
            else:
                # Formato não reconhecido, retornar como texto
                output = BytesIO()
                output.write(conteudo.encode('utf-8'))
                output.seek(0)
                return output, f"{nome_arquivo}.txt", "text/plain"
                
        except Exception as e:
            print(f"Erro ao gerar arquivo {formato}: {e}")
            # Em caso de erro, retornar como texto
            output = BytesIO()
            output.write(f"Erro ao gerar arquivo: {str(e)}\n\nConteúdo original:\n{conteudo}".encode('utf-8'))
            output.seek(0)
            return output, f"{nome_arquivo}_erro.txt", "text/plain"

    @staticmethod
    def download_arquivo_formato(equipe_id, node_id, formato):
        """Download de arquivo gerado por um nó formatoSaida"""
        try:
            equipe = EquipeInteligente.query.get_or_404(equipe_id)
            
            # Carregar o layout da equipe
            if equipe.layout:
                layout = json.loads(equipe.layout)
            else:
                return jsonify({'error': 'Layout não encontrado'}), 404
            
            # Encontrar o nó específico
            node = None
            for n in layout['nodes']:
                if n['id'] == node_id and n['type'] == 'formatoSaida':
                    node = n
                    break
            
            if not node:
                return jsonify({'error': 'Nó formatoSaida não encontrado'}), 404
            
            # Gerar o arquivo
            nome_arquivo = f"resultado_{equipe.nome}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            arquivo_output, nome_arquivo_final, content_type = AgentesController.gerar_arquivo_saida(
                "Conteúdo do arquivo", formato, nome_arquivo
            )
            
            # Criar resposta para download
            response = make_response(arquivo_output.getvalue())
            response.headers['Content-Disposition'] = f'attachment; filename={nome_arquivo_final}'
            response.headers['Content-Type'] = content_type
            
            return response
            
        except Exception as e:
            print(f"Erro ao gerar download: {e}")
            return jsonify({'error': f'Erro ao gerar arquivo: {str(e)}'}), 500