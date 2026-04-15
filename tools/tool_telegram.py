from datetime import datetime, timezone

import os
import asyncio
import logging
import traceback
import time
from typing import Optional

from smolagents import tool
import requests

try:
    from telegram import Bot
    from telegram.error import TelegramError
except ImportError:
    Bot = None
    TelegramError = None


# Armazenar o último update_id processado para polling
_last_update_id = 0
logger = logging.getLogger(__name__)
URL_API_TELEGRAM = 'http://127.0.0.1:645'
ROTA_ENVIO_AGUARDO_MENSAGEM = '/enviar-mensagem-com-aguardo'
ROTA_ENVIAR_MENSAGEM = '/enviar-mensagem'
ROTA_CONSULTAR_TASK = '/consultar-task'

def read_chat_id_telegram():
    """Lê o chat_id do Telegram de um arquivo ou variável de ambiente."""
    chat_id_file = "artifacts/telegram_chat_id.txt"
    
    if os.path.exists(chat_id_file):
        with open(chat_id_file, "r") as f:
            return f.read().strip()    
        

def _aguardar_resposta_servidor(rota, conteudo, type='POST'):
    response = requests.post(
        url=URL_API_TELEGRAM+rota, 
        json=conteudo,
        headers={'Content-Type': 'application/json'}
    )

    if(response.status_code != 202):
        raise Exception('Erro ao enviar a requisição')

    task_id = response.json()['task_id']

    response = requests.get(
        url=URL_API_TELEGRAM+ROTA_CONSULTAR_TASK+f'/{task_id}', 
    )

    result = None
    while response.status_code == 200:
        data = response.json()
        if(data['result']):
            result = data['result']
            break
        response = requests.get(
            url=URL_API_TELEGRAM+ROTA_CONSULTAR_TASK+f'/{task_id}', 
        )

        time.sleep(1)

    return result

import requests

def _setar_config(rota, conteudo):
    response = requests.post(
        url=URL_API_TELEGRAM + rota,
        json=conteudo
    )
    return response.status_code


def criar_tool_iniciar_conversa(agent_atual: str):
    @tool
    def iniciar_conversa() -> dict:
        """
        Tenta iniciar uma conversa com o usuário, definindo este agente como o atual.

        Returns:
            dict com status da operação
        """
        try:
            status = _setar_config(
                rota="/set-agente-atual",
                conteudo={"agent_name": agent_atual}
            )

            if status == 200:
                return {
                    "sucesso": True,
                    "mensagem": f"Agente '{agent_atual}' iniciou a conversa"
                }
            else:
                return {
                    "sucesso": False,
                    "mensagem": f"Não foi possível iniciar a conversa (status {status})"
                }

        except Exception as e:
            return {
                "sucesso": False,
                "erro": str(e)
            }
    return iniciar_conversa()

def criar_tool_finalizar_conversa(agent_atual): 
    @tool
    def finalizar_conversa() -> dict:
        """
        Finaliza a conversa, liberando o agente atual.

        Returns:
            dict com status da operação
        """
        try:
            status = _setar_config(
                rota="/reset-agente-atual",
                conteudo={"agent_name": agent_atual}
            )

            if status == 200:
                return {
                    "sucesso": True,
                    "mensagem": f"Agente '{agent_atual}' finalizou a conversa"
                }
            else:
                return {
                    "sucesso": False,
                    "mensagem": f"Não foi possível finalizar a conversa (status {status})"
                }

        except Exception as e:
            return {
                "sucesso": False,
                "erro": str(e)
            }
    return finalizar_conversa

def criar_tool_enviar_mensagem_telegram(agent_atual: str):
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
                "sucesso": True/False
            }
        
        Exemplos:
            >>> enviar_mensagem_telegram("Olá! Saí de casa há 1 hora")
            >>> enviar_mensagem_telegram("Perigo: Janela aberta!", chat_id="123456789")
        """
        if not chat_id:
            chat_id = os.getenv("TELEGRAM_CHAT_ID")
            if not chat_id:
                raise ValueError(
                    "❌ chat_id não fornecido e TELEGRAM_CHAT_ID não configurada. "
                    "Configure: export TELEGRAM_CHAT_ID='seu_chat_id'"
                )
        
        conteudo = {
            'mensagem': mensagem,
            'chat_id': chat_id,
            "agent_atual": agent_atual
        }

        print(conteudo)
        
        resposta = _aguardar_resposta_servidor(ROTA_ENVIAR_MENSAGEM, conteudo, 'POST')

        return {
            "sucesso": resposta is not None
        }
    return enviar_mensagem_telegram

def criar_tool_aguardar_confirmacao_telegram(agent_atual: str):

    @tool
    def aguardar_confirmacao_telegram(
        mensagem_confirmacao: str = "Por favor, confirme (responda 'sim' ou 'não')",
        chat_id: Optional[str] = None,
        
    ) -> dict:
        """
        Aguarda uma mensagem de confirmação do usuário via Telegram (sim/não).
        
        Args:
            mensagem_confirmacao: Mensagem a enviar pedindo confirmação
            chat_id: ID do chat (opcional, usa TELEGRAM_CHAT_ID do env se não fornecido)
        
        Returns:
            Um dicionário com:
            {
                "mensagem": str,
                "chat_id": str
            }
        
        Exemplos:
            >>> resultado = aguardar_confirmacao_telegram(
            ...     mensagem_confirmacao="Abrir cortinas em 50%?",
            ... )

        Vai ser concatenada a mensagem "O que deseja fazer?"
        """
        global _last_update_id
        try:
            if not chat_id:
                chat_id = os.getenv("TELEGRAM_CHAT_ID")
                if not chat_id:
                    raise ValueError("❌ chat_id não fornecido")
            
            conteudo = {
                'mensagem': mensagem_confirmacao+ "\n\nO que deseja fazer?",
                'chat_id': chat_id,
                "agent_atual": agent_atual
                }
            
            data = _aguardar_resposta_servidor(ROTA_ENVIO_AGUARDO_MENSAGEM, conteudo, 'POST')

            return {
                "mensagem": data['mensagem'],
                "chat_id": data['chat_id'],
                "resposta_chamada": data['resposta']
                
            }
        
        except Exception as e:
            logger.error(f"Erro ao aguardar confirmação: {str(e)}")
            traceback.print_exc()
            return {
            "resposta_chamada": "erro",
                "mensagem": f"❌ Erro: {str(e)}",
                "chat_id": chat_id if chat_id else "não fornecido"
            }
    return aguardar_confirmacao_telegram