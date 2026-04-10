from tools.tool_telegram import read_token_telegram, enviar_mensagem_telegram
import os
os.environ["TELEGRAM_TOKEN"] = read_token_telegram()  # Configurar token do Telegram para ferramentas que precisarem
os.environ["TELEGRAM_CHAT_ID"] = "-5201409685"

enviar_mensagem_telegram("Teste de envio de mensagem via Telegram usando a ferramenta!")