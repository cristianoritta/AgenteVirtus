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

            # Salva temporariamente o arquivo
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
                audio_content = audio_file.read()
                temp_file.write(audio_content)
                temp_audio_path = temp_file.name

            # Transcreve o áudio usando o serviço de IA
            with open(temp_audio_path, "rb") as file:
                transcricao = IaController.groq_transcrever(file)

            # Remove o arquivo temporário
            os.unlink(temp_audio_path)

            return jsonify({
                'status': 'success',
                'transcricao': transcricao
            })

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
            return render_template('ferramentas/chatbot.html')

        if request.form.get('chat') == 'init':
            return render_template('ferramentas/chatbot.html', mensagem=request.form.get('mensagem'))

        try:
            # Recebe a mensagem do usuário
            mensagem = request.form.get('mensagem', '')

            if not mensagem.strip():
                return jsonify({
                    'status': 'error',
                    'message': 'Mensagem não pode estar vazia'
                }), 400

            # Chama o chatbot usando o IaController
            resposta = IaController.groq(mensagem)
            return resposta

        except Exception as e:
            print(f"Erro no chatbot: {e}")
            return jsonify({
                'status': 'error',
                'message': f'Erro ao processar chatbot: {str(e)}'
            }), 500
