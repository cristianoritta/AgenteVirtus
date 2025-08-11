import requests
import time
from flask import current_app
from typing import Optional, Dict, Any


def make_api_request_with_retry(
    method: str,
    url: str,
    headers: Optional[Dict[str, str]] = None,
    json_data: Optional[Dict[str, Any]] = None,
    files: Optional[Dict[str, Any]] = None,
    data: Optional[Dict[str, Any]] = None,
    timeout: Optional[int] = None,
    max_retries: Optional[int] = None,
    retry_delay: Optional[int] = None
) -> requests.Response:
    """
    Faz uma requisição HTTP com retry automático em caso de timeout ou erro de conexão.
    
    Args:
        method: Método HTTP (GET, POST, etc.)
        url: URL da requisição
        headers: Headers da requisição
        json_data: Dados JSON para enviar
        files: Arquivos para enviar
        data: Dados form para enviar
        timeout: Timeout em segundos (usa configuração padrão se None)
        max_retries: Número máximo de tentativas (usa configuração padrão se None)
        retry_delay: Delay entre tentativas em segundos (usa configuração padrão se None)
    
    Returns:
        requests.Response: Resposta da requisição
        
    Raises:
        requests.exceptions.RequestException: Se todas as tentativas falharem
    """
    
    # Obter configurações da aplicação
    app_config = current_app.config if current_app else {}
    default_timeout = app_config.get('API_TIMEOUT', 120)
    default_max_retries = app_config.get('API_RETRY_ATTEMPTS', 3)
    default_retry_delay = app_config.get('API_RETRY_DELAY', 2)
    backoff_factor = app_config.get('API_BACKOFF_FACTOR', 2)
    
    # Usar valores fornecidos ou padrões
    timeout = timeout or default_timeout
    max_retries = max_retries or default_max_retries
    retry_delay = retry_delay or default_retry_delay
    
    last_exception = None
    
    for attempt in range(max_retries + 1):
        try:
            print(f"DEBUG - Tentativa {attempt + 1}/{max_retries + 1} para {method} {url}")
            
            response = requests.request(
                method=method,
                url=url,
                headers=headers,
                json=json_data,
                files=files,
                data=data,
                timeout=timeout
            )
            
            print(f"DEBUG - Requisição bem-sucedida após {attempt + 1} tentativa(s)")
            return response
            
        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
            last_exception = e
            print(f"DEBUG - Erro na tentativa {attempt + 1}: {type(e).__name__} - {str(e)}")
            
            if attempt < max_retries:
                # Calcular delay com backoff exponencial
                delay = retry_delay * (backoff_factor ** attempt)
                print(f"DEBUG - Aguardando {delay} segundos antes da próxima tentativa...")
                time.sleep(delay)
            else:
                print(f"DEBUG - Todas as {max_retries + 1} tentativas falharam")
                break
                
        except Exception as e:
            print(f"DEBUG - Erro inesperado na tentativa {attempt + 1}: {str(e)}")
            last_exception = e
            break
    
    # Se chegou aqui, todas as tentativas falharam
    raise last_exception


def make_post_request_with_retry(
    url: str,
    headers: Optional[Dict[str, str]] = None,
    json_data: Optional[Dict[str, Any]] = None,
    files: Optional[Dict[str, Any]] = None,
    data: Optional[Dict[str, Any]] = None,
    timeout: Optional[int] = None,
    max_retries: Optional[int] = None,
    retry_delay: Optional[int] = None
) -> requests.Response:
    """
    Conveniência para fazer requisições POST com retry.
    """
    return make_api_request_with_retry(
        method='POST',
        url=url,
        headers=headers,
        json_data=json_data,
        files=files,
        data=data,
        timeout=timeout,
        max_retries=max_retries,
        retry_delay=retry_delay
    ) 