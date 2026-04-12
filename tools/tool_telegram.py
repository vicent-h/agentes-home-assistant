import datetime
import os
import asyncio
import logging
import traceback
import time
from typing import Optional

from smolagents import tool

try:
    from telegram import Bot
    from telegram.error import TelegramError
except ImportError:
    Bot = None
    TelegramError = None


# Armazenar o último update_id processado para polling
_last_update_id = 0
logger = logging.getLogger(__name__)

def read_token_telegram():
    """Lê o token do Telegram de um arquivo ou variável de ambiente."""
    token_file = "artifacts/telegram_bot_token.txt"
    
    if os.path.exists(token_file):
        with open(token_file, "r") as f:
            return f.read().strip()

def read_chat_id_telegram():
    """Lê o chat_id do Telegram de um arquivo ou variável de ambiente."""
    chat_id_file = "artifacts/telegram_chat_id.txt"
    
    if os.path.exists(chat_id_file):
        with open(chat_id_file, "r") as f:
            return f.read().strip()    

def _get_telegram_bot():
    """Obtém a instância do bot do Telegram."""
    telegram_token = os.getenv("TELEGRAM_TOKEN")
    if not telegram_token:
        raise ValueError(
            "❌ TELEGRAM_TOKEN não configurada nas variáveis de ambiente. "
            "Configure: export TELEGRAM_TOKEN='seu_token_aqui'"
        )
    
    if Bot is None:
        raise ImportError(
            "❌ Biblioteca 'python-telegram-bot' não instalada. "
            "Instale com: pip install python-telegram-bot"
        )
    
    return Bot(token=telegram_token)


@tool
def enviar_mensagem_telegram(mensagem: str, chat_id: Optional[str] = None) -> dict:
    """
    Envia uma mensagem de texto via Telegram.
    
    Args:
        mensagem: O texto da mensagem a enviar
        chat_id: ID do chat (opcional, usa TELEGRAM_CHAT_ID do env se não fornecido)
    
    Returns:
        Um dicionário com o status e informações da mensagem:
        {
            "sucesso": True/False,
            "mensagem_id": int (se sucesso),
            "erro": str (se falho),
            "chat_id": str
        }
    
    Exemplos:
        >>> enviar_mensagem_telegram("Olá! Saí de casa há 1 hora")
        >>> enviar_mensagem_telegram("Perigo: Janela aberta!", chat_id="123456789")
    """
    try:
        if not chat_id:
            chat_id = os.getenv("TELEGRAM_CHAT_ID")
            if not chat_id:
                raise ValueError(
                    "❌ chat_id não fornecido e TELEGRAM_CHAT_ID não configurada. "
                    "Configure: export TELEGRAM_CHAT_ID='seu_chat_id'"
                )
        
        bot = _get_telegram_bot()
        
        # Enviar mensagem de forma síncrona usando asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            response = loop.run_until_complete(
                bot.send_message(chat_id=chat_id, text=mensagem)
            )
            
            return {
                "sucesso": True,
                "mensagem_id": response.message_id,
                "chat_id": chat_id,
                "timestamp": response.date.isoformat() if hasattr(response.date, 'isoformat') else str(response.date)
            }
        finally:
            loop.close()
    
    except TelegramError as e:
        logger.error(f"Erro do Telegram: {str(e)}")
        return {
            "sucesso": False,
            "erro": f"Erro do Telegram: {str(e)}",
            "chat_id": chat_id
        }
    except Exception as e:
        logger.error(f"Erro ao enviar mensagem: {str(e)}")
        traceback.print_exc()
        return {
            "sucesso": False,
            "erro": f"Erro: {str(e)}",
            "chat_id": chat_id if chat_id else "não fornecido"
        }


@tool
def enviar_mensagem_formatada_telegram(
    titulo: str,
    detalhes: str,
    chat_id: Optional[str] = None
) -> dict:
    """
    Envia uma mensagem formatada via Telegram com título e detalhes.
    
    Args:
        titulo: Título/assunto da mensagem
        detalhes: Corpo da mensagem com detalhes
        chat_id: ID do chat (opcional, usa TELEGRAM_CHAT_ID do env se não fornecido)
    
    Returns:
        Um dicionário com o status
    
    Exemplo:
        >>> enviar_mensagem_formatada_telegram(
        ...     titulo="⚠️ Saiu de casa",
        ...     detalhes="Saída detectada às 14:30\\nCasa em modo ausência"
        ... )
    """
    mensagem_formatada = f"*{titulo}*\n\n{detalhes}"
    
    try:
        if not chat_id:
            chat_id = os.getenv("TELEGRAM_CHAT_ID")
        
        bot = _get_telegram_bot()
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            response = loop.run_until_complete(
                bot.send_message(
                    chat_id=chat_id,
                    text=mensagem_formatada,
                    parse_mode="Markdown"
                )
            )
            
            return {
                "sucesso": True,
                "mensagem_id": response.message_id,
                "chat_id": chat_id
            }
        finally:
            loop.close()
    
    except Exception as e:
        logger.error(f"Erro ao enviar mensagem formatada: {str(e)}")
        return {
            "sucesso": False,
            "erro": str(e),
            "chat_id": chat_id if chat_id else "não fornecido"
        }


@tool
def enviar_foto_telegram(
    url_foto: str,
    legenda: Optional[str] = None,
    chat_id: Optional[str] = None
) -> dict:
    """
    Envia uma foto via Telegram usando URL.
    
    Args:
        url_foto: URL da foto a enviar
        legenda: Legenda opcional para a foto
        chat_id: ID do chat (opcional)
    
    Returns:
        Um dicionário com o status
    
    Exemplo:
        >>> enviar_foto_telegram(
        ...     url_foto="https://example.com/camera.jpg",
        ...     legenda="Câmera da porta"
        ... )
    """
    try:
        if not chat_id:
            chat_id = os.getenv("TELEGRAM_CHAT_ID")
        
        bot = _get_telegram_bot()
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            response = loop.run_until_complete(
                bot.send_photo(
                    chat_id=chat_id,
                    photo=url_foto,
                    caption=legenda
                )
            )
            
            return {
                "sucesso": True,
                "mensagem_id": response.message_id,
                "chat_id": chat_id
            }
        finally:
            loop.close()
    
    except Exception as e:
        logger.error(f"Erro ao enviar foto: {str(e)}")
        return {
            "sucesso": False,
            "erro": str(e),
            "chat_id": chat_id if chat_id else "não fornecido"
        }


@tool
def aguardar_confirmacao_telegram(
    mensagem_confirmacao: str = "Por favor, confirme (responda 'sim' ou 'não')",
    timeout_segundos: int = 30,
    chat_id: Optional[str] = None
) -> dict:
    """
    Aguarda uma mensagem de confirmação do usuário via Telegram (sim/não).
    
    Args:
        mensagem_confirmacao: Mensagem a enviar pedindo confirmação
        timeout_segundos: Tempo máximo de espera em segundos (padrão: 300 = 5 minutos)
        chat_id: ID do chat (opcional, usa TELEGRAM_CHAT_ID do env se não fornecido)
    
    Returns:
        Um dicionário com:
        {
            "confirmado": True/False,
            "resposta": "sim"/"não"/"timeout",
            "mensagem": str,
            "chat_id": str
        }
    
    Exemplos:
        >>> resultado = aguardar_confirmacao_telegram(
        ...     mensagem_confirmacao="Abrir cortinas em 50%?",
        ...     timeout_segundos=30
        ... )
        >>> if resultado["confirmado"]:
        ...     print("Usuário confirmou!")
        ... else:
        ...     print("Cancelado ou timeout")
    """
    global _last_update_id
    try:
        if not chat_id:
            chat_id = os.getenv("TELEGRAM_CHAT_ID")
            if not chat_id:
                raise ValueError("❌ chat_id não fornecido")
        
        bot = _get_telegram_bot()
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        loop.run_until_complete(bot.delete_webhook())
        try:
            # Enviar mensagem de confirmação
            loop.run_until_complete(
                bot.send_message(chat_id=chat_id, text=f"{mensagem_confirmacao}\n\nResponda com 'sim' ou 'não'")
            )
            agora = datetime.utcnow()
            
            # Aguardar resposta com timeout - loop até timeout total
            inicio = time.time()
            while (time.time() - inicio) < timeout_segundos:
                print(f"Aguardando confirmação... ({int(time.time() - inicio)}s/{timeout_segundos}s)")
                updates = loop.run_until_complete(
                    bot.get_updates(offset=_last_update_id, timeout=10)
                )
                print("Updates recebidos:", updates)
                for update in updates:
                    _last_update_id = update.update_id + 1
                    print(f"Update recebido: {update}")
                    # a data do update precisa ser
                    if (
                        update.message
                        and update.message.chat_id == int(chat_id)
                        and update.message.date > agora
                    ):
                        print(f"Resposta recebida: {update.message.text} (de {update.message.from_user.username})")
                        resposta = update.message.text.lower().strip()
                        
                        return {
                            "mensagem": update.message.text,
                            "chat_id": chat_id
                        }
                            
            # Timeout
            return {
                "confirmado": False,
                "resposta": "timeout",
                "mensagem": f"⏱️ Timeout após {timeout_segundos} segundos",
                "chat_id": chat_id
            }
        
        finally:
            loop.close()
    
    except Exception as e:
        logger.error(f"Erro ao aguardar confirmação: {str(e)}")
        traceback.print_exc()
        return {
            "confirmado": False,
            "resposta": "erro",
            "mensagem": f"❌ Erro: {str(e)}",
            "chat_id": chat_id if chat_id else "não fornecido"
        }


@tool
def aguardar_mensagem_telegram(
    mensagem_espera: str = "Aguardando sua resposta...",
    timeout_segundos: int = 300,
    chat_id: Optional[str] = None
) -> dict:
    """
    Aguarda qualquer mensagem de texto do usuário via Telegram.
    
    Args:
        mensagem_espera: Mensagem a enviar antes de aguardar
        timeout_segundos: Tempo máximo de espera em segundos (padrão: 300 = 5 minutos)
        chat_id: ID do chat (opcional, usa TELEGRAM_CHAT_ID do env se não fornecido)
    
    Returns:
        Um dicionário com:
        {
            "recebido": True/False,
            "mensagem": str (conteúdo da mensagem recebida),
            "usuario_id": int,
            "status": "sucesso"/"timeout"/"erro",
            "chat_id": str
        }
    
    Exemplo:
        >>> resultado = aguardar_mensagem_telegram(
        ...     mensagem_espera="Qual temperatura você deseja?",
        ...     timeout_segundos=300
        ... )
        >>> if resultado["recebido"]:
        ...     print(f"Recebido: {resultado['mensagem']}")
    """
    global _last_update_id
    try:
        if not chat_id:
            chat_id = os.getenv("TELEGRAM_CHAT_ID")
            if not chat_id:
                raise ValueError("❌ chat_id não fornecido")
        
        bot = _get_telegram_bot()
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            # Enviar mensagem inicial
            loop.run_until_complete(
                bot.send_message(chat_id=chat_id, text=mensagem_espera)
            )
            
            # Aguardar resposta com timeout - loop até timeout total
            inicio = time.time()
            while (time.time() - inicio) < timeout_segundos:
                updates = loop.run_until_complete(
                    bot.get_updates(offset=_last_update_id, timeout=10)
                )
                
                for update in updates:
                    _last_update_id = update.update_id + 1
                    
                    if update.message and update.message.chat_id == int(chat_id):
                        return {
                            "recebido": True,
                            "mensagem": update.message.text,
                            "usuario_id": update.message.from_user.id,
                            "status": "sucesso",
                            "chat_id": chat_id
                        }
                
                time.sleep(1)
            
            # Timeout
            return {
                "recebido": False,
                "mensagem": f"⏱️ Timeout após {timeout_segundos} segundos",
                "usuario_id": None,
                "status": "timeout",
                "chat_id": chat_id
            }
        
        finally:
            loop.close()
    
    except Exception as e:
        logger.error(f"Erro ao aguardar mensagem: {str(e)}")
        traceback.print_exc()
        return {
            "recebido": False,
            "mensagem": f"❌ Erro: {str(e)}",
            "usuario_id": None,
            "status": "erro",
            "chat_id": chat_id if chat_id else "não fornecido"
        }

