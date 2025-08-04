import os
from dotenv import load_dotenv
from telegram import Bot
import asyncio

# Carrega as variáveis de ambiente
load_dotenv()

# Obtém o token do bot do Telegram das variáveis de ambiente
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

async def enviar_mensagem_telegram(mensagem: str, chat_id: str = None) -> bool:
    """
    Envia uma mensagem via Telegram.
    
    Args:
        mensagem (str): Texto da mensagem a ser enviada
        chat_id (str, opcional): ID do chat para envio. Se não fornecido, usa o TELEGRAM_CHAT_ID do .env
    
    Returns:
        bool: True se a mensagem foi enviada com sucesso, False caso contrário
    """
    try:
        # Verifica se o token do bot está configurado
        if not TELEGRAM_BOT_TOKEN:
            raise ValueError("Token do bot do Telegram não configurado no arquivo .env")
        
        # Usa o chat_id fornecido ou o padrão das variáveis de ambiente
        destino = chat_id or TELEGRAM_CHAT_ID
        if not destino:
            raise ValueError("ID do chat do Telegram não fornecido nem configurado no arquivo .env")
        
        # Inicializa o bot
        bot = Bot(token=TELEGRAM_BOT_TOKEN)
        
        # Envia a mensagem
        await bot.send_message(
            chat_id=destino,
            text=mensagem,
            parse_mode='HTML'  # Permite formatação HTML básica na mensagem
        )
        
        return True
        
    except Exception as e:
        print(f"Erro ao enviar mensagem via Telegram: {str(e)}")
        return False

# Exemplo de uso
async def main():
    mensagem = "👋 Olá! Esta é uma mensagem de teste do <b>AgenteVirtus</b>!"
    sucesso = await enviar_mensagem_telegram(mensagem)
    print("Mensagem enviada com sucesso!" if sucesso else "Falha ao enviar mensagem.")

if __name__ == "__main__":
    # Executa o exemplo
    asyncio.run(main())
