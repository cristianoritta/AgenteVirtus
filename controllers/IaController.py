import os
import requests
from flask import jsonify

from dotenv import load_dotenv

load_dotenv()

def groq(prompt):
    # Fazer requisição para o Groq
    
    api_key = os.getenv('GROQ_API_KEY')
    
    if not api_key:
        return jsonify({
            'status': 'error',
            'message': 'GROQ_API_KEY não configurada'
        }), 400
    
    try:
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": "llama-3.3-70b-versatile",
            "messages": [{
                "role": "user",
                "content": prompt
            }]
        }

        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers=headers,
            json=payload
        )
        
        if response.status_code == 200:
            resultado = response.json()
            print(resultado['choices'][0])
            return jsonify({
                'status': 'success',
                'resultado': resultado,
                'resposta': resultado['choices'][0]['message']['content']
            }), 200
        else:
            return jsonify({
                'status': 'error',
                'message': f'Erro na requisição ao Groq: {response.status_code} - {response.text}'
            }), response.status_code

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Erro ao processar requisição: {str(e)}'
        }), 500


def groq_transcrever(file):
    api_key = os.getenv('GROQ_API_KEY')
    
    print(file)
    
    if not api_key:
        return jsonify({
            'status': 'error', 
            'message': 'GROQ_API_KEY não configurada'
        }), 400

    try:
        headers = {
            "Authorization": f"Bearer {api_key}"
        }

        files = {
            'file': file
        }
        
        data = {
            'model': 'whisper-large-v3',
            'prompt': 'Depois de fazer a transcrição, faça uma verificação e correção da pontuação, com virgulas (,), pontos nos finais de frases (.) e letras maiusculas nos inícios de frases.',
            'temperature': '0.5'
        }
        
        response = requests.post(
            "https://api.groq.com/openai/v1/audio/transcriptions",
            headers=headers,
            files=files,
            data=data
        )
        
        print(response)
        print(f"Response: {response.json()}")
        
        if response.status_code == 200:
            resultado = response.json()
            return resultado.get('text', 'Transcrição não encontrada')
        else:
            return f'Erro na transcrição: {response.status_code} - {response.text}'

    except Exception as e:
        return f'Erro ao processar transcrição: {str(e)}'