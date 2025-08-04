import os
import requests
from flask import jsonify
from services.ConversaService import ConversaService
from models.models import ApiIa
from dotenv import load_dotenv
from openai import OpenAI  

load_dotenv()

def api_ativa():
    api_ia = ApiIa.query.filter_by(ativo=True).first()
    return api_ia

def configurar_openai_client(api):
    """
    Devolve um objeto `OpenAI` apontando para o servidor definido em `api`.

    O objeto `api` deve ter:
      • api.api_key   – chave de acesso
      • api.endpoint  – raiz da API (ex.: https://api.groq.com/openai/v1)
    """

    # --- saneamento da URL ---------------------------------------------------
    base_url = api.endpoint.rstrip("/")
    if base_url.endswith("/chat/completions"):
        # Usuário passou o endpoint completo; remove o sufixo duplicado
        base_url = base_url.rsplit("/chat/completions", 1)[0]
    if not base_url.endswith("/v1"):
        # Garante que termina em /v1
        base_url += "/v1"

    # --- cria o cliente OpenAI ----------------------------------------------
    # Usar uma abordagem mais robusta para evitar conflitos de argumentos
    try:
        # Primeira tentativa: configuração básica
        client = OpenAI(
            api_key = api.api_key,
            base_url = base_url
        )
    except TypeError as e:
        if "proxies" in str(e):
            # Se o erro for de proxies, tentar sem configurações extras
            import os
            # Limpar variáveis de ambiente que podem causar conflito
            os.environ.pop('HTTP_PROXY', None)
            os.environ.pop('HTTPS_PROXY', None)
            os.environ.pop('http_proxy', None)
            os.environ.pop('https_proxy', None)
            
            client = OpenAI(
                api_key = api.api_key,
                base_url = base_url
            )
        else:
            raise e

    # Logs úteis (remova se não precisar)
    print("-" * 100)
    print("Endpoint configurado:", base_url)
    print("Cliente:", client)
    print("-" * 100)

    return client


def groq_gemini(api_ia, historico, conversa):
    """
    Função específica para processar requisições Gemini
    """
    try:
        # Construir a URL completa para Gemini
        url = f"{api_ia.endpoint}/models/{api_ia.modelo_chat}:generateContent"
        
        headers = {
            'Content-Type': 'application/json',
            'X-goog-api-key': api_ia.api_key
        }
        
        # Converter histórico para formato Gemini
        contents = []
        for msg in historico:
            if msg['role'] == 'user':
                contents.append({
                    "parts": [{"text": msg['content']}]
                })
            elif msg['role'] == 'assistant':
                contents.append({
                    "parts": [{"text": msg['content']}]
                })
        
        payload = {
            "contents": contents
        }
        
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            if 'candidates' in data and len(data['candidates']) > 0:
                resposta_ia = data['candidates'][0]['content']['parts'][0]['text']
                
                # Adicionar resposta da IA à conversa
                ConversaService.adicionar_mensagem(conversa.id, 'assistant', resposta_ia)
                
                return jsonify({
                    'status': 'success',
                    'resultado': {
                        'choices': [{
                            'message': {
                                'content': resposta_ia
                            }
                        }]
                    },
                    'resposta': resposta_ia,
                    'conversa_id': conversa.id,
                    'hash_conversa': conversa.hash_conversa
                }), 200
            else:
                return jsonify({
                    'status': 'error',
                    'message': 'Resposta da API não contém dados válidos'
                }), 500
        else:
            return jsonify({
                'status': 'error',
                'message': f'Erro na requisição: {response.status_code} - {response.text}'
            }), 500
            
    except requests.exceptions.Timeout:
        return jsonify({
            'status': 'error',
            'message': 'Timeout na requisição'
        }), 500
    except requests.exceptions.ConnectionError:
        return jsonify({
            'status': 'error',
            'message': 'Erro de conexão'
        }), 500
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Erro inesperado: {str(e)}'
        }), 500

def groq_openai_requests(api_ia, historico, conversa):
    """
    Função específica para processar requisições OpenAI/Groq usando requests
    """
    try:
        # Construir a URL completa
        base_url = api_ia.endpoint.rstrip("/")
        if not base_url.endswith("/v1"):
            base_url += "/v1"
        
        url = f"{base_url}/chat/completions"
        
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {api_ia.api_key}'
        }
        
        payload = {
            "model": api_ia.modelo_chat,
            "messages": historico
        }
        
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            if 'choices' in data and len(data['choices']) > 0:
                resposta_ia = data['choices'][0]['message']['content']
                
                # Adicionar resposta da IA à conversa
                ConversaService.adicionar_mensagem(conversa.id, 'assistant', resposta_ia)
                
                return jsonify({
                    'status': 'success',
                    'resultado': {
                        'choices': [{
                            'message': {
                                'content': resposta_ia
                            }
                        }]
                    },
                    'resposta': resposta_ia,
                    'conversa_id': conversa.id,
                    'hash_conversa': conversa.hash_conversa
                }), 200
            else:
                return jsonify({
                    'status': 'error',
                    'message': 'Resposta da API não contém dados válidos'
                }), 500
        else:
            return jsonify({
                'status': 'error',
                'message': f'Erro na requisição: {response.status_code} - {response.text}'
            }), 500
            
    except requests.exceptions.Timeout:
        return jsonify({
            'status': 'error',
            'message': 'Timeout na requisição'
        }), 500
    except requests.exceptions.ConnectionError:
        return jsonify({
            'status': 'error',
            'message': 'Erro de conexão'
        }), 500
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Erro inesperado: {str(e)}'
        }), 500

def groq_openai(api_ia, historico, conversa):
    """
    Função específica para processar requisições OpenAI/Groq (versão segura)
    """
    return groq_openai_requests(api_ia, historico, conversa)

def groq(prompt, conversa_id=None, hash_conversa=None):
    # Fazer requisição para a API ativa
    
    api_ia = api_ativa()
    
    try:
        # Buscar ou criar conversa
        conversa = None
        if conversa_id:
            conversa = ConversaService.buscar_conversa_por_id(conversa_id)
        elif hash_conversa:
            conversa = ConversaService.buscar_conversa_por_hash(hash_conversa)
        
        if not conversa:
            # Criar nova conversa
            conversa = ConversaService.criar_conversa(tipo_conversa='chatbot')
        
        # Adicionar mensagem do usuário
        ConversaService.adicionar_mensagem(conversa.id, 'user', prompt)
        
        # Obter histórico da conversa para contexto
        historico = ConversaService.obter_mensagens_para_ia(conversa.id, limit=10)
        
        # Detectar tipo de API e usar método apropriado
        tipo_api = detectar_tipo_api(api_ia)
        
        if tipo_api == 'gemini':
            return groq_gemini(api_ia, historico, conversa)
        else:
            return groq_openai(api_ia, historico, conversa)

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Erro ao processar requisição: {str(e)}'
        }), 500


def groq_transcrever_openai_requests(api_ia, file, conversa):
    """
    Função específica para transcrição usando OpenAI/Groq com requests
    """
    try:
        # Construir a URL completa
        base_url = api_ia.endpoint.rstrip("/")
        if not base_url.endswith("/v1"):
            base_url += "/v1"
        
        url = f"{base_url}/audio/transcriptions"
        
        headers = {
            'Authorization': f'Bearer {api_ia.api_key}'
        }
        
        # Preparar o arquivo para upload
        files = {
            'file': ('audio.wav', file, 'audio/wav')
        }
        
        data = {
            'model': api_ia.modelo_voz,
            'prompt': 'Depois de fazer a transcrição, faça uma verificação e correção da pontuação, com virgulas (,), pontos nos finais de frases (.) e letras maiusculas nos inícios de frases.',
            'temperature': '0.5'
        }
        
        response = requests.post(url, headers=headers, files=files, data=data, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            transcricao = data.get('text', '')
            
            # Adicionar transcrição à conversa
            ConversaService.adicionar_mensagem(conversa.id, 'user', f"[AUDIO TRANSCRITO] {transcricao}")
            
            return {
                'status': 'success',
                'transcricao': transcricao,
                'conversa_id': conversa.id,
                'hash_conversa': conversa.hash_conversa
            }
        else:
            return {
                'status': 'error',
                'message': f'Erro na requisição: {response.status_code} - {response.text}'
            }

    except requests.exceptions.Timeout:
        return {
            'status': 'error',
            'message': 'Timeout na requisição'
        }
    except requests.exceptions.ConnectionError:
        return {
            'status': 'error',
            'message': 'Erro de conexão'
        }
    except Exception as e:
        return {
            'status': 'error',
            'message': f'Erro ao processar transcrição: {str(e)}'
        }

def groq_transcrever_openai(api_ia, file, conversa):
    """
    Função específica para transcrição usando OpenAI/Groq (versão segura)
    """
    return groq_transcrever_openai_requests(api_ia, file, conversa)

def groq_transcrever_gemini(api_ia, file, conversa):
    """
    Função específica para transcrição usando Gemini
    """
    try:
        # Construir a URL completa para Gemini
        url = f"{api_ia.endpoint}/models/{api_ia.modelo_voz}:generateContent"
        
        headers = {
            'Content-Type': 'application/json',
            'X-goog-api-key': api_ia.api_key
        }
        
        # Para Gemini, precisamos converter o arquivo para base64
        import base64
        file_content = file.read()
        file.seek(0)  # Reset file pointer
        
        # Converter para base64
        file_base64 = base64.b64encode(file_content).decode('utf-8')
        
        payload = {
            "contents": [
                {
                    "parts": [
                        {
                            "text": "Transcreva este áudio e corrija a pontuação, com vírgulas, pontos nos finais de frases e letras maiúsculas nos inícios de frases."
                        },
                        {
                            "inline_data": {
                                "mime_type": "audio/wav",
                                "data": file_base64
                            }
                        }
                    ]
                }
            ]
        }
        
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            if 'candidates' in data and len(data['candidates']) > 0:
                transcricao = data['candidates'][0]['content']['parts'][0]['text']
                
                # Adicionar transcrição à conversa
                ConversaService.adicionar_mensagem(conversa.id, 'user', f"[AUDIO TRANSCRITO] {transcricao}")
                
                return {
                    'status': 'success',
                    'transcricao': transcricao,
                    'conversa_id': conversa.id,
                    'hash_conversa': conversa.hash_conversa
                }
            else:
                return {
                    'status': 'error',
                    'message': 'Resposta da API não contém dados válidos'
                }
        else:
            return {
                'status': 'error',
                'message': f'Erro na requisição: {response.status_code} - {response.text}'
            }
            
    except Exception as e:
        return {
            'status': 'error',
            'message': f'Erro ao processar transcrição: {str(e)}'
        }

def groq_transcrever(file, conversa_id=None, hash_conversa=None):
    api_ia = api_ativa()
    
    try:
        # Buscar ou criar conversa para transcrição
        conversa = None
        if conversa_id:
            conversa = ConversaService.buscar_conversa_por_id(conversa_id)
        elif hash_conversa:
            conversa = ConversaService.buscar_conversa_por_hash(hash_conversa)
        
        if not conversa:
            conversa = ConversaService.criar_conversa(tipo_conversa='transcricao')

        # Detectar tipo de API e usar método apropriado
        tipo_api = detectar_tipo_api(api_ia)
        
        if tipo_api == 'gemini':
            return groq_transcrever_gemini(api_ia, file, conversa)
        else:
            return groq_transcrever_openai(api_ia, file, conversa)

    except Exception as e:
        return {
            'status': 'error',
            'message': f'Erro ao processar transcrição: {str(e)}'
        }


def testar_gemini_api(api):
    """
    Testa uma API Gemini usando requests
    """
    try:
        # Construir a URL completa para Gemini
        url = f"{api.endpoint}/models/{api.modelo_chat}:generateContent"
        
        headers = {
            'Content-Type': 'application/json',
            'X-goog-api-key': api.api_key
        }
        
        payload = {
            "contents": [
                {
                    "parts": [
                        {
                            "text": "Olá! Responda apenas com 'API funcionando corretamente!'"
                        }
                    ]
                }
            ]
        }
        
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            if 'candidates' in data and len(data['candidates']) > 0:
                resposta = data['candidates'][0]['content']['parts'][0]['text']
                return {
                    'status': 'success',
                    'api_nome': api.nome,
                    'endpoint': api.endpoint,
                    'modelo': api.modelo_chat,
                    'resposta': resposta
                }
            else:
                return {
                    'status': 'error',
                    'message': 'Resposta da API não contém dados válidos',
                    'api_nome': api.nome,
                    'endpoint': api.endpoint,
                    'modelo': api.modelo_chat
                }
        else:
            return {
                'status': 'error',
                'message': f'Erro na requisição: {response.status_code} - {response.text}',
                'api_nome': api.nome,
                'endpoint': api.endpoint,
                'modelo': api.modelo_chat
            }
            
    except requests.exceptions.Timeout:
        return {
            'status': 'error',
            'message': 'Timeout na requisição',
            'api_nome': api.nome,
            'endpoint': api.endpoint,
            'modelo': api.modelo_chat
        }
    except requests.exceptions.ConnectionError:
        return {
            'status': 'error',
            'message': 'Erro de conexão',
            'api_nome': api.nome,
            'endpoint': api.endpoint,
            'modelo': api.modelo_chat
        }
    except Exception as e:
        return {
            'status': 'error',
            'message': f'Erro inesperado: {str(e)}',
            'api_nome': api.nome,
            'endpoint': api.endpoint,
            'modelo': api.modelo_chat
        }

def testar_openai_api_requests(api):
    """
    Testa uma API OpenAI/Groq usando requests diretamente
    """
    try:
        # Construir a URL completa
        base_url = api.endpoint.rstrip("/")
        if not base_url.endswith("/v1"):
            base_url += "/v1"
        
        url = f"{base_url}/chat/completions"
        
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {api.api_key}'
        }
        
        payload = {
            "model": api.modelo_chat,
            "messages": [
                {
                    "role": "user",
                    "content": "Olá! Responda apenas com 'API funcionando corretamente!'"
                }
            ],
            "max_tokens": 50
        }
        
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            if 'choices' in data and len(data['choices']) > 0:
                resposta = data['choices'][0]['message']['content']
                return {
                    'status': 'success',
                    'api_nome': api.nome,
                    'endpoint': api.endpoint,
                    'modelo': api.modelo_chat,
                    'resposta': resposta
                }
            else:
                return {
                    'status': 'error',
                    'message': 'Resposta da API não contém dados válidos',
                    'api_nome': api.nome,
                    'endpoint': api.endpoint,
                    'modelo': api.modelo_chat
                }
        else:
            return {
                'status': 'error',
                'message': f'Erro na requisição: {response.status_code} - {response.text}',
                'api_nome': api.nome,
                'endpoint': api.endpoint,
                'modelo': api.modelo_chat
            }
            
    except requests.exceptions.Timeout:
        return {
            'status': 'error',
            'message': 'Timeout na requisição',
            'api_nome': api.nome,
            'endpoint': api.endpoint,
            'modelo': api.modelo_chat
        }
    except requests.exceptions.ConnectionError:
        return {
            'status': 'error',
            'message': 'Erro de conexão',
            'api_nome': api.nome,
            'endpoint': api.endpoint,
            'modelo': api.modelo_chat
        }
    except Exception as e:
        return {
            'status': 'error',
            'message': f'Erro inesperado: {str(e)}',
            'api_nome': api.nome,
            'endpoint': api.endpoint,
            'modelo': api.modelo_chat
        }

def testar_openai_api(api):
    """
    Testa uma API OpenAI/Groq usando requests (versão segura)
    """
    return testar_openai_api_requests(api)

def detectar_tipo_api(api):
    """
    Detecta o tipo de API baseado no endpoint
    """
    endpoint = api.endpoint.lower()
    
    if 'generativelanguage.googleapis.com' in endpoint or 'gemini' in endpoint:
        return 'gemini'
    elif 'openai.com' in endpoint or 'api.openai.com' in endpoint:
        return 'openai'
    elif 'groq.com' in endpoint:
        return 'groq'
    else:
        # Para APIs desconhecidas, tenta usar OpenAI primeiro
        return 'openai'

def testar_api_especifica(api_id):
    """
    Testa uma API específica pelo ID usando abordagem híbrida
    """
    try:
        # Buscar a API pelo ID
        api = ApiIa.query.get(api_id)
        
        if not api:
            return {
                'status': 'error',
                'message': 'API não encontrada'
            }
        
        # Verificar se a API tem as configurações necessárias
        if not api.api_key or not api.endpoint or not api.modelo_chat:
            return {
                'status': 'error',
                'message': 'API não configurada corretamente. Verifique API Key, Endpoint e Modelo Chat.',
                'api_nome': api.nome
            }
        
        # Detectar tipo de API e usar método apropriado
        tipo_api = detectar_tipo_api(api)
        
        if tipo_api == 'gemini':
            return testar_gemini_api(api)
        else:
            return testar_openai_api(api)

    except Exception as e:
        print(f"Erro em testar_api_especifica: {e}")
        return {
            'status': 'error',
            'message': f'Erro inesperado: {str(e)}',
            'api_nome': api.nome if 'api' in locals() else 'Desconhecida',
            'endpoint': api.endpoint if 'api' in locals() else 'Desconhecido'
        }


def testar_gemini_chatbot(api, mensagem):
    """
    Testa o chatbot Gemini com uma mensagem específica
    """
    try:
        # Construir a URL completa para Gemini
        url = f"{api.endpoint}/models/{api.modelo_chat}:generateContent"
        
        headers = {
            'Content-Type': 'application/json',
            'X-goog-api-key': api.api_key
        }
        
        payload = {
            "contents": [
                {
                    "parts": [
                        {
                            "text": mensagem
                        }
                    ]
                }
            ]
        }
        
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            if 'candidates' in data and len(data['candidates']) > 0:
                resposta = data['candidates'][0]['content']['parts'][0]['text']
                return {
                    'status': 'success',
                    'api_nome': api.nome,
                    'endpoint': api.endpoint,
                    'modelo': api.modelo_chat,
                    'resposta': resposta
                }
            else:
                return {
                    'status': 'error',
                    'message': 'Resposta da API não contém dados válidos',
                    'api_nome': api.nome,
                    'endpoint': api.endpoint,
                    'modelo': api.modelo_chat
                }
        else:
            return {
                'status': 'error',
                'message': f'Erro na requisição: {response.status_code} - {response.text}',
                'api_nome': api.nome,
                'endpoint': api.endpoint,
                'modelo': api.modelo_chat
            }
            
    except requests.exceptions.Timeout:
        return {
            'status': 'error',
            'message': 'Timeout na requisição',
            'api_nome': api.nome,
            'endpoint': api.endpoint,
            'modelo': api.modelo_chat
        }
    except requests.exceptions.ConnectionError:
        return {
            'status': 'error',
            'message': 'Erro de conexão',
            'api_nome': api.nome,
            'endpoint': api.endpoint,
            'modelo': api.modelo_chat
        }
    except Exception as e:
        return {
            'status': 'error',
            'message': f'Erro inesperado: {str(e)}',
            'api_nome': api.nome,
            'endpoint': api.endpoint,
            'modelo': api.modelo_chat
        }

def testar_openai_chatbot_requests(api, mensagem):
    """
    Testa o chatbot OpenAI/Groq com uma mensagem específica usando requests
    """
    try:
        # Construir a URL completa
        base_url = api.endpoint.rstrip("/")
        if not base_url.endswith("/v1"):
            base_url += "/v1"
        
        url = f"{base_url}/chat/completions"
        
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {api.api_key}'
        }
        
        payload = {
            "model": api.modelo_chat,
            "messages": [
                {
                    "role": "user",
                    "content": mensagem
                }
            ],
            "max_tokens": 500
        }
        
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            if 'choices' in data and len(data['choices']) > 0:
                resposta_ia = data['choices'][0]['message']['content']
                return {
                    'status': 'success',
                    'api_nome': api.nome,
                    'endpoint': api.endpoint,
                    'modelo': api.modelo_chat,
                    'resposta': resposta_ia
                }
            else:
                return {
                    'status': 'error',
                    'message': 'Resposta da API não contém dados válidos',
                    'api_nome': api.nome,
                    'endpoint': api.endpoint,
                    'modelo': api.modelo_chat
                }
        else:
            return {
                'status': 'error',
                'message': f'Erro na requisição: {response.status_code} - {response.text}',
                'api_nome': api.nome,
                'endpoint': api.endpoint,
                'modelo': api.modelo_chat
            }
            
    except requests.exceptions.Timeout:
        return {
            'status': 'error',
            'message': 'Timeout na requisição',
            'api_nome': api.nome,
            'endpoint': api.endpoint,
            'modelo': api.modelo_chat
        }
    except requests.exceptions.ConnectionError:
        return {
            'status': 'error',
            'message': 'Erro de conexão',
            'api_nome': api.nome,
            'endpoint': api.endpoint,
            'modelo': api.modelo_chat
        }
    except Exception as e:
        return {
            'status': 'error',
            'message': f'Erro inesperado: {str(e)}',
            'api_nome': api.nome,
            'endpoint': api.endpoint,
            'modelo': api.modelo_chat
        }

def testar_openai_chatbot(api, mensagem):
    """
    Testa o chatbot OpenAI/Groq com uma mensagem específica (versão segura)
    """
    return testar_openai_chatbot_requests(api, mensagem)

def testar_chatbot(mensagem):
    """
    Testa o chatbot com uma mensagem específica usando abordagem híbrida
    """
    try:
        # Buscar a API ativa
        api = api_ativa()
        
        if not api:
            return {
                'status': 'error',
                'message': 'Nenhuma API ativa encontrada'
            }
        
        # Verificar se a API tem as configurações necessárias
        if not api.api_key or not api.endpoint or not api.modelo_chat:
            return {
                'status': 'error',
                'message': 'API não configurada corretamente. Verifique API Key, Endpoint e Modelo Chat.',
                'api_nome': api.nome
            }
        
        # Detectar tipo de API e usar método apropriado
        tipo_api = detectar_tipo_api(api)
        
        if tipo_api == 'gemini':
            return testar_gemini_chatbot(api, mensagem)
        else:
            return testar_openai_chatbot(api, mensagem)

    except Exception as e:
        print(f"Erro em testar_chatbot: {e}")
        return {
            'status': 'error',
            'message': f'Erro inesperado: {str(e)}',
            'api_nome': api.nome if 'api' in locals() else 'Desconhecida',
            'endpoint': api.endpoint if 'api' in locals() else 'Desconhecido'
        }


def testar_api_ia():
    """
    Testa a API de IA ativa usando abordagem híbrida
    """
    try:
        # Buscar a API ativa
        api = api_ativa()
        
        if not api:
            return {
                'status': 'error',
                'message': 'Nenhuma API ativa encontrada'
            }
        
        # Verificar se a API tem as configurações necessárias
        if not api.api_key or not api.endpoint or not api.modelo_chat:
            return {
                'status': 'error',
                'message': 'API não configurada corretamente. Verifique API Key, Endpoint e Modelo Chat.',
                'api_nome': api.nome
            }
        
        # Detectar tipo de API e usar método apropriado
        tipo_api = detectar_tipo_api(api)
        
        if tipo_api == 'gemini':
            return testar_gemini_api(api)
        else:
            return testar_openai_api(api)

    except Exception as e:
        print(f"Erro em testar_api_ia: {e}")
        return {
            'status': 'error',
            'message': f'Erro inesperado: {str(e)}',
            'api_nome': api.nome if 'api' in locals() else 'Desconhecida',
            'endpoint': api.endpoint if 'api' in locals() else 'Desconhecido'
        }

def groq_visao_openai_requests(api_ia, prompt, imagens_base64, conversa):
    """
    Função específica para processamento de imagens usando OpenAI/Groq
    """
    try:
        # Construir a URL completa
        base_url = api_ia.endpoint.rstrip("/")
        if not base_url.endswith("/v1"):
            base_url += "/v1"
        
        url = f"{base_url}/chat/completions"
        
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {api_ia.api_key}'
        }
        
        # Preparar mensagens com imagens
        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt
                    }
                ]
            }
        ]
        
        # Adicionar imagens ao conteúdo
        for i, img_base64 in enumerate(imagens_base64):
            messages[0]["content"].append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{img_base64}"
                }
            })
        
        payload = {
            "model": api_ia.modelo_visao or api_ia.modelo_chat,  # Usar modelo_visao se disponível
            "messages": messages,
            "max_tokens": 4000
        }
        
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        
        if response.status_code == 200:
            data = response.json()
            if 'choices' in data and len(data['choices']) > 0:
                resposta_ia = data['choices'][0]['message']['content']
                
                # Adicionar resposta da IA à conversa
                ConversaService.adicionar_mensagem(conversa.id, 'assistant', resposta_ia)
                
                return jsonify({
                    'status': 'success',
                    'resultado': {
                        'choices': [{
                            'message': {
                                'content': resposta_ia
                            }
                        }]
                    },
                    'resposta': resposta_ia,
                    'conversa_id': conversa.id,
                    'hash_conversa': conversa.hash_conversa
                }), 200
            else:
                return jsonify({
                    'status': 'error',
                    'message': 'Resposta da API não contém dados válidos'
                }), 500
        else:
            return jsonify({
                'status': 'error',
                'message': f'Erro na API: {response.status_code} - {response.text}'
            }), response.status_code
            
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Erro inesperado: {str(e)}'
        }), 500


def groq_visao_gemini(api_ia, prompt, imagens_base64, conversa):
    """
    Função específica para processamento de imagens usando Gemini
    """
    try:
        # Construir a URL completa para Gemini
        url = f"{api_ia.endpoint}/models/{api_ia.modelo_visao or api_ia.modelo_chat}:generateContent"
        
        headers = {
            'Content-Type': 'application/json',
            'X-goog-api-key': api_ia.api_key
        }
        
        # Preparar conteúdo com imagens
        parts = [
            {
                "text": prompt
            }
        ]
        
        # Adicionar imagens
        for img_base64 in imagens_base64:
            parts.append({
                "inline_data": {
                    "mime_type": "image/jpeg",
                    "data": img_base64
                }
            })
        
        payload = {
            "contents": [
                {
                    "parts": parts
                }
            ]
        }
        
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        
        if response.status_code == 200:
            data = response.json()
            if 'candidates' in data and len(data['candidates']) > 0:
                resposta_ia = data['candidates'][0]['content']['parts'][0]['text']
                
                # Adicionar resposta da IA à conversa
                ConversaService.adicionar_mensagem(conversa.id, 'assistant', resposta_ia)
                
                return jsonify({
                    'status': 'success',
                    'resultado': {
                        'choices': [{
                            'message': {
                                'content': resposta_ia
                            }
                        }]
                    },
                    'resposta': resposta_ia,
                    'conversa_id': conversa.id,
                    'hash_conversa': conversa.hash_conversa
                }), 200
            else:
                return jsonify({
                    'status': 'error',
                    'message': 'Resposta da API não contém dados válidos'
                }), 500
        else:
            return jsonify({
                'status': 'error',
                'message': f'Erro na API: {response.status_code} - {response.text}'
            }), response.status_code
            
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Erro inesperado: {str(e)}'
        }), 500


def groq_visao(prompt, imagens_base64, conversa_id=None, hash_conversa=None):
    """
    Função principal para processamento de imagens com IA
    """
    # Fazer requisição para a API ativa
    api_ia = api_ativa()
    
    if not api_ia:
        return jsonify({
            'status': 'error',
            'message': 'Nenhuma API de IA ativa encontrada'
        }), 500
    
    try:
        # Buscar ou criar conversa
        conversa = None
        if conversa_id:
            conversa = ConversaService.buscar_conversa_por_id(conversa_id)
        elif hash_conversa:
            conversa = ConversaService.buscar_conversa_por_hash(hash_conversa)
        
        if not conversa:
            # Criar nova conversa
            conversa = ConversaService.criar_conversa(tipo_conversa='chatbot')
        
        # Adicionar mensagem do usuário
        ConversaService.adicionar_mensagem(conversa.id, 'user', prompt)
        
        # Detectar tipo de API e usar método apropriado
        tipo_api = detectar_tipo_api(api_ia)
        
        if tipo_api == 'gemini':
            return groq_visao_gemini(api_ia, prompt, imagens_base64, conversa)
        else:
            return groq_visao_openai_requests(api_ia, prompt, imagens_base64, conversa)

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Erro ao processar requisição: {str(e)}'
        }), 500