from flask import render_template, request, jsonify
import tempfile
import controllers.IaController as IaController
import os
from datetime import datetime


class FerramentasController:
    @staticmethod
    def transcrever():
        """Página para transcrição de áudio"""
        if request.method == 'GET':
            return render_template('ferramentas/transcrever.html')

        try:
            # Recebe o arquivo de áudio
            audio_file = request.files['arquivo']
            
            # Recebe informações da conversa se existirem
            conversa_id = request.form.get('conversa_id')
            hash_conversa = request.form.get('hash_conversa')

            # Salva temporariamente o arquivo
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
                audio_content = audio_file.read()
                temp_file.write(audio_content)
                temp_audio_path = temp_file.name

            # Transcreve o áudio usando o serviço de IA
            with open(temp_audio_path, "rb") as file:
                resultado = IaController.groq_transcrever(file, conversa_id, hash_conversa)

            # Remove o arquivo temporário
            os.unlink(temp_audio_path)

            if resultado['status'] == 'success':
                return jsonify({
                    'status': 'success',
                    'transcricao': resultado['transcricao'],
                    'conversa_id': resultado.get('conversa_id'),
                    'hash_conversa': resultado.get('hash_conversa')
                })
            else:
                return jsonify(resultado), 500

        except Exception as e:
            print(e)
            return jsonify({
                'status': 'error',
                'message': f'Erro ao transcrever áudio: {str(e)}'
            }), 500

    @staticmethod
    def chatbot():
        """Página para chatbot"""
        if request.method == 'GET':
            # Verificar se há conversa_id na URL
            conversa_id = request.args.get('conversa_id')
            return render_template('ferramentas/chatbot.html', conversa_id=conversa_id)

        if request.form.get('chat') == 'init':
            return render_template('ferramentas/chatbot.html', mensagem=request.form.get('mensagem'))

        try:
            # Recebe a mensagem do usuário
            mensagem = request.form.get('mensagem', '')
            
            # Recebe informações da conversa se existirem
            conversa_id = request.form.get('conversa_id')
            hash_conversa = request.form.get('hash_conversa')

            if not mensagem.strip():
                return jsonify({
                    'status': 'error',
                    'message': 'Mensagem não pode estar vazia'
                }), 400

            # Chama o chatbot usando o IaController
            resposta = IaController.groq(mensagem, conversa_id, hash_conversa)
            return resposta

        except Exception as e:
            print(f"Erro no chatbot: {e}")
            return jsonify({
                'status': 'error',
                'message': f'Erro ao processar chatbot: {str(e)}'
            }), 500
