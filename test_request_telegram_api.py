from tools.tool_telegram import _aguardar_resposta_servidor, read_chat_id_telegram

ROTA_ENVIO_AGUARDO_MENSAGEM = '/enviar-mensagem-com-aguardo'
ROTA_ENVIAR_MENSAGEM = '/enviar-mensagem'
ROTA_CONSULTAR_TASK = '/consultar-task'


response = _aguardar_resposta_servidor(ROTA_ENVIO_AGUARDO_MENSAGEM, conteudo={'mensagem': 'Oi', 'chat_id': read_chat_id_telegram(), 'agent_atual': 'teste'})
print(response)