import os
from dotenv import load_dotenv
from telegram import Bot
import asyncio

# Carrega as variáveis de ambiente
load_dotenv()


def enviar_mensagem_telegram(mensagem: str, chat_id: str = None) -> bool:
    """
    Envia uma mensagem via Telegram.

    Args:
        mensagem (str): Texto da mensagem a ser enviada
        chat_id (str, opcional): ID do chat para envio. Se não fornecido, usa o TELEGRAM_CHAT_ID do .env

    Returns:
        bool: True se a mensagem foi enviada com sucesso, False caso contrário
    """
    print("DEBUG - Iniciando envio de mensagem via Telegram")

    # Obtém o token do bot do Telegram das variáveis de ambiente
    TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
    TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

    print(f"DEBUG - Token configurado: {'Sim' if TELEGRAM_BOT_TOKEN else 'Não'}")
    print(f"DEBUG - Chat ID padrão configurado: {'Sim' if TELEGRAM_CHAT_ID else 'Não'}")
    print(f"DEBUG - Chat ID fornecido: {'Sim' if chat_id else 'Não'}")

    try:
        # Verifica se o token do bot está configurado
        if not TELEGRAM_BOT_TOKEN:
            erro = "Token do bot do Telegram não configurado no arquivo .env"
            print(f"DEBUG - Erro: {erro}")
            raise ValueError(erro)

        # Usa o chat_id fornecido ou o padrão das variáveis de ambiente
        destino = chat_id or TELEGRAM_CHAT_ID
        if not destino:
            erro = "ID do chat do Telegram não fornecido nem configurado no arquivo .env"
            print(f"DEBUG - Erro: {erro}")
            raise ValueError(erro)

        print(f"DEBUG - Usando chat_id: {destino}")
        print(f"DEBUG - Tamanho da mensagem: {len(mensagem)} caracteres")
        print(f"DEBUG - Primeiros 100 caracteres da mensagem: {mensagem[:100]}")

        # Inicializa o bot
        bot = Bot(token=TELEGRAM_BOT_TOKEN)
        print("DEBUG - Bot inicializado com sucesso")

        # Função assíncrona para enviar a mensagem
        async def enviar():
            return await bot.send_message(
                chat_id=destino,
                text=mensagem,
                parse_mode='HTML'  # Permite formatação HTML básica na mensagem
            )

        # Executa a função assíncrona de forma síncrona
        resultado = asyncio.run(enviar())

        print("DEBUG - Mensagem enviada com sucesso")
        print(f"DEBUG - ID da mensagem: {resultado.message_id}")
        return True

    except Exception as e:
        print(f"DEBUG - Erro ao enviar mensagem via Telegram: {str(e)}")
        print(f"DEBUG - Tipo do erro: {type(e).__name__}")
        if hasattr(e, 'response') and hasattr(e.response, 'json'):
            print(f"DEBUG - Resposta da API: {e.response.json()}")
        return False
