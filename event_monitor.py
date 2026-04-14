import os

import asyncio
import websockets
import json
import logging
from datetime import datetime
from typing import List, Dict, Callable, Any
from pathlib import Path
import threading

from src.triggers import (
    ModoDesligadoTempo,
    Trigger, 
    TemperatureTrigger, 
    JanelaAbertaFechadaTrigger, 
    EntidadeDesligadaTrigger
)
from src.ha import HA, read_token
from tools.tool_telegram import read_chat_id_telegram, read_token_telegram

os.environ["TELEGRAM_TOKEN"] = read_token_telegram()  # Configurar token do Telegram para ferramentas que precisarem
os.environ["TELEGRAM_CHAT_ID"] = read_chat_id_telegram()
os.environ['MEMORY_PATH'] = "/media/alvarinho/dados/Memories"
os.environ["QTDE_TAGS"] = "5"
os.environ["TOP_N_RELEVANTES"] = "3"
os.environ["FILE_PREFERENCES_USUARIO"] = "preferencias_usuario.txt"
os.environ["PATH_ECHO"] = "/media/alvarinho/dados/Echos"

from agents.agent_conforto import AgentConforto
from agents.agent_volume_echos import AgentVolumeEchos

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class EventMonitor:
    """
    Monitor de eventos do Home Assistant que verifica triggers e executa agentes.
    """
    
    def __init__(self):
        """Inicializa o monitor com a configuração do Home Assistant."""
        self.ha_url = os.getenv("HA_URL", "http://localhost:8123")
        self.ha_token = os.getenv("HA_TOKEN") or read_token()
        
        if not self.ha_token:
            raise ValueError("HA_TOKEN não configurado nas variáveis de ambiente")
        
        # Converter URL HTTP para WS
        self.ws_url = self.ha_url.replace("http://", "ws://").replace("https://", "wss://")
        self.ws_url += "/api/websocket"
        
        self.triggers: List[Dict[str, Any]] = []
        self.agent_mapping: Dict[str, Callable] = {
            'conforto': AgentConforto(),
            'volume_echos': AgentVolumeEchos()
        }
        
        self.running = False
    
    def register_trigger(self, trigger: Trigger, entity_ids: List[str], agent_name: str):
        """
        Registra um trigger para monitorar entidades específicas.
        
        Args:
            trigger: Instância do Trigger
            entity_ids: IDs das entidades a monitorar
            agent_name: Nome do agente a executar quando trigger dispara
        """
        for entity_id in entity_ids:
            self.triggers.append({
                'trigger': trigger,
                'entity_id': entity_id,
                'agent_name': agent_name
            })
            logger.info(f"Trigger '{trigger.name}' registrado para entidade '{entity_id}' (agente: {agent_name})")
    
    async def connect_and_monitor(self):
        """Conecta ao Home Assistant via WebSocket e monitora eventos."""
        try:
            async with websockets.connect(self.ws_url) as websocket:
                logger.info(f"Conectado ao Home Assistant em {self.ws_url}")
                
                # Etapa 1: Receber mensagem de autenticação requerida
                auth_required = await websocket.recv()
                auth_required_data = json.loads(auth_required)
                logger.debug(f"Resposta do servidor: {auth_required_data}")
                
                if auth_required_data.get("type") != "auth_required":
                    logger.error(f"Resposta inesperada: {auth_required_data}")
                    return
                
                # Etapa 2: Enviar credenciais de autenticação
                auth_message = {
                    "type": "auth",
                    "access_token": self.ha_token
                }
                await websocket.send(json.dumps(auth_message))
                logger.debug("Credenciais de autenticação enviadas")
                
                # Etapa 3: Receber confirmação de autenticação
                auth_response = await websocket.recv()
                auth_data = json.loads(auth_response)
                logger.debug(f"Resposta de autenticação: {auth_data}")
                
                if auth_data.get("type") != "auth_ok":
                    logger.error(f"Falha na autenticação com Home Assistant: {auth_data}")
                    return
                
                logger.info("Autenticado com sucesso no Home Assistant")
                
                # Etapa 4: Subscribir a eventos de mudança de estado
                subscribe_message = {
                    "id": 1,
                    "type": "subscribe_events",
                    "event_type": "state_changed"
                }
                await websocket.send(json.dumps(subscribe_message))
                logger.info("Inscrição em eventos state_changed realizada")
                
                # Etapa 5: Monitorar eventos
                self.running = True
                logger.info("Aguardando eventos...")
                async for message in websocket:
                    try:
                        data = json.loads(message)
                        await self.process_event(data)
                    except json.JSONDecodeError:
                        logger.warning(f"Mensagem inválida recebida: {message}")
                    except Exception as e:
                        logger.error(f"Erro ao processar evento: {e}", exc_info=True)
        
        except websockets.exceptions.WebSocketException as e:
            logger.error(f"Erro de WebSocket: {e}")
        except Exception as e:
            logger.error(f"Erro não esperado: {e}", exc_info=True)
        finally:
            self.running = False
    
    async def process_event(self, data: Dict[str, Any]):
        """
        Processa um evento do Home Assistant.
        
        Args:
            data: Dados do evento em formato JSON
        """
        # Verificar se é um evento de mudança de estado
        if data.get("type") != "event":
            return
        
        event = data.get("event", {})
        if event.get("event_type") != "state_changed":
            return
        
        event_data = event.get("data", {})
        entity_id = event_data.get("entity_id")
        old_state = event_data.get("old_state", {})
        new_state = event_data.get("new_state", {})
        
        if not entity_id or not new_state:
            return
        
        old_state_value = old_state.get("state", "unknown") if old_state else "unknown"
        new_state_value = new_state.get("state", "unknown")
        last_changed = new_state.get("last_changed")
        
        # Parse timestamp
        try:
            timestamp = datetime.fromisoformat(last_changed.replace('Z', '+00:00'))
        except (ValueError, TypeError, AttributeError):
            print("⚠️ Formato de data inválido, usando horário atual como fallback")
            timestamp = datetime.now()
        
        logger.debug(f"Evento de mudança: {entity_id} -> {old_state_value} para {new_state_value}")
        
        # Verificar cada trigger registrado para essa entidade
        for trigger_config in self.triggers:
            if trigger_config['entity_id'] != entity_id:
                continue
            
            trigger = trigger_config['trigger']
            agent_name = trigger_config['agent_name']
            
            # Verificar se o trigger deve disparar
            logger.info(f"Evento de mudança: {entity_id} -> {old_state_value} para {new_state_value}")
            result = trigger.check_condition(entity_id, old_state_value, new_state_value, timestamp)

            print(result)
            
            if result['triggered']:
                logger.info(f"Trigger '{trigger.name}' disparado para {entity_id}")
                
                # Executar o agente apropriado
                await self.execute_agent(agent_name, result['task_description'])
    
    async def execute_agent(self, agent_name: str, task_description: str):
        """
        Executa um agente em thread separada (para não bloquear o monitor).
        
        Args:
            agent_name: Nome do agente
            task_description: Descrição da tarefa a executar
        """
        if agent_name not in self.agent_mapping:
            logger.error(f"Agente '{agent_name}' não registrado")
            return
        
        agent = self.agent_mapping[agent_name]

        if(agent.executando_atualmente()):
            logger.info(f"Agente '{agent_name}' já está em execução, pulando nova execução")
            return
        
        # Executar em thread separada para não bloquear o monitor
        def run_in_thread():
            try:
                logger.info(f"Executando agente '{agent_name}' com tarefa:\n{task_description}")
                result = agent.run_agent(task_description)
                logger.info(f"Agente '{agent_name}' concluído com sucesso")
                logger.debug(f"Resultado: {result}")
            except Exception as e:
                logger.error(f"Erro ao executar agente '{agent_name}': {e}", exc_info=True)
        
        thread = threading.Thread(target=run_in_thread, daemon=True)
        thread.start()
    
    def start(self):
        """Inicia o monitor de eventos."""
        try:
            asyncio.run(self.connect_and_monitor())
        except KeyboardInterrupt:
            logger.info("Monitor interrompido pelo usuário")
        except Exception as e:
            logger.error(f"Erro fatal no monitor: {e}", exc_info=True)


def create_monitor_with_triggers() -> EventMonitor:
    """
    Cria e configura um monitor com triggers pré-definidos.
    
    Returns:
        EventMonitor configurado e pronto para usar
    """
    monitor = EventMonitor()
    
    # Exemplo: Monitorar temperatura da sala
    temp_trigger = TemperatureTrigger(threshold=26.0, comparator='greater')
    monitor.register_trigger(
        trigger=temp_trigger,
        entity_ids=['sensor.temperatura_do_quarto_temperature'],  # Ajustar conforme suas entidades
        agent_name='conforto'
    )

    trigger_saida_1h = ModoDesligadoTempo(minutos_decorridos=60, margem_minutos=5)
    monitor.register_trigger(
        trigger=trigger_saida_1h,
        entity_ids=["input_boolean.geral_status_em_casa"],
        agent_name="conforto"  # ou qual agente você quer executar
    )
    
    # Exemplo: Monitorar janelas
    janela_trigger = JanelaAbertaFechadaTrigger(desired_state='open')
    monitor.register_trigger(
        trigger=janela_trigger,
        entity_ids=[
            'input_boolean.janela_do_quarto_grupo', 
            'input_boolean.janela_do_escritorio_grupo',
            'input_boolean.janela_da_lavanderia_grupo',
            'input_boolean.porta_da_varanda_grupo'
            ],  # Ajustar conforme necessário
        agent_name='conforto'
    )
    monitor.register_trigger(
        trigger=janela_trigger,
        entity_ids=[
            'input_boolean.janela_do_quarto_grupo', 
            'input_boolean.janela_do_escritorio_grupo',
            'input_boolean.janela_da_lavanderia_grupo',
            'input_boolean.porta_da_varanda_grupo'
            ],  # Ajustar conforme necessário
        agent_name='volume_echos'
    )

    # Exemplo: Monitorar descalibragem dos volumes dos Echos Pops
    descalibragem_trigger = EntidadeDesligadaTrigger()
    monitor.register_trigger(
        trigger=descalibragem_trigger,
        entity_ids=[
            'input_boolean.geral_status_em_casa',
            'input_boolean.modo_banho',
        ],  # Ajustar conforme necessário
        agent_name='volume_echos'
    )
    
    
    return monitor


if __name__ == "__main__":
    # Configurar variáveis de ambiente
    os.environ["HA_URL"] = "https://ha.gratiaamorishome.com.br"
    os.environ["HA_TOKEN"] = read_token()
    
    # Criar e iniciar monitor
    monitor = create_monitor_with_triggers()
    logger.info("Iniciando monitor de eventos...")
    monitor.start()
