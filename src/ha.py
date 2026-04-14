import os
import requests
import json
import websocket
import asyncio
import websockets
from typing import List, Dict, Any, Callable, Optional
from datetime import datetime
import traceback
import tqdm

# Importar módulo de ações
try:
    from .actions import build_service_call
except ImportError:
    from actions import build_service_call


class HA:
    """
    Classe para integração com Home Assistant API.
    
    Parâmetros de ambiente necessários:
    - HA_URL: URL do servidor Home Assistant (ex: http://localhost:8123)
    - HA_TOKEN: Token de autenticação do Home Assistant
    """
    
    def __init__(self):
        """Inicializa a conexão com o Home Assistant usando variáveis de ambiente."""
        self.base_url = os.getenv("HA_URL", "http://localhost:8123")
        self.token = os.getenv("HA_TOKEN")
        
        if not self.token:
            raise ValueError("HA_TOKEN não configurado nas variáveis de ambiente")
        
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        
        self.api_url = f"{self.base_url}/api"
        
        # Cache de entidades com áreas (carregado no primeiro acesso)
        self._entities_with_areas = None
    
    def _request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """
        Realiza uma requisição à API do Home Assistant.
        
        Args:
            method: Método HTTP (GET, POST, etc)
            endpoint: Endpoint da API (ex: /states)
            **kwargs: Argumentos adicionais para requests
            
        Returns:
            Response em JSON
            
        Raises:
            requests.exceptions.RequestException: Erro na requisição
        """
        url = f"{self.api_url}{endpoint}"
        
        try:
            response = requests.request(
                method=method,
                url=url,
                headers=self.headers,
                timeout=10,
                **kwargs
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.ConnectionError:
            raise ConnectionError(f"Erro ao conectar em {self.base_url}")
        except requests.exceptions.HTTPError as e:
            raise Exception(f"Erro HTTP {e.response.status_code}: {e.response.text}")
        except requests.exceptions.Timeout:
            raise TimeoutError(f"Timeout ao conectar em {self.base_url}")
    
    def get_all_entities(self) -> List[Dict[str, Any]]:
        """
        Busca todas as entidades do servidor Home Assistant.
        
        Returns:
            Lista de entidades com seus estados e atributos
            
        Example:
            >>> ha = HA()
            >>> entities = ha.get_all_entities()
            >>> print(entities[0])
            {
                'entity_id': 'light.sala',
                'state': 'on',
                'attributes': {...},
                'last_changed': '2024-01-01T10:00:00',
                'last_updated': '2024-01-01T10:00:00'
            }
        """
        return self._request("GET", "/states")
    
    def get_entity_state(self, entity_id: str, keys_needed: List[str] = None) -> Dict[str, Any]:
        """
        Busca o estado atual de uma entidade específica.
        
        Args:
            entity_id: ID da entidade (ex: 'light.sala', 'sensor.temperatura')
            keys_needed: Lista de chaves que devem ser incluídas no resultado
            
        Returns:
            Dicionário contendo o estado e atributos da entidade
            
        Raises:
            Exception: Se a entidade não for encontrada
            
        Example:
            >>> ha = HA()
            >>> state = ha.get_entity_state('light.sala')
            >>> print(state['state'])
            'on'
        """
        
        situacao = self._request("GET", f"/states/{entity_id}")

        if self._entities_with_areas and entity_id in self._entities_with_areas:
            situacao['area'] = self._entities_with_areas[entity_id].get('area_name')

        if not situacao:
            raise Exception(f"Entidade {entity_id} não encontrada")
        
        if keys_needed is None:
            return situacao
        
        resultado = {key: situacao.get(key) for key in keys_needed if key in situacao}
        return resultado
    
    def get_all_states(self) -> Dict[str, Any]:
        """
        Busca o estado atual de todas as entidades.
        
        Returns:
            Dicionário organizado por entity_id com seus estados
            
        Example:
            >>> ha = HA()
            >>> states = ha.get_all_states()
            >>> if states['light.sala']['state'] == 'on':
            ...     print("Luz da sala está ligada")
        """
        entities = self.get_all_entities()
        return {entity['entity_id']: entity for entity in entities}
    
    def call_service(self, domain: str, service: str, entity_id: str = None, 
                    **service_data) -> Dict[str, Any]:
        """
        Chama um serviço no Home Assistant.
        
        Args:
            domain: Domínio do serviço (ex: 'light', 'switch')
            service: Nome do serviço (ex: 'turn_on', 'turn_off')
            entity_id: ID da entidade (opcional)
            **service_data: Dados adicionais do serviço
            
        Returns:
            Resposta da API
            
        Example:
            >>> ha = HA()
            >>> ha.call_service('light', 'turn_on', entity_id='light.sala')
        """
        data = {"entity_id": entity_id, **service_data} if entity_id else service_data
        return self._request(
            "POST",
            f"/services/{domain}/{service}",
            json=data
        )
    
    def execute_action(self, entity_id: str, action: str, **kwargs) -> Dict[str, Any]:
        """
        Executa uma ação em uma entidade de forma genérica.
        Detecta automaticamente o tipo de dispositivo e executa a ação apropriada.
        
        Args:
            entity_id: ID da entidade (ex: 'light.sala', 'switch.tomada')
            action: Ação a executar (ex: 'on', 'off', 'toggle', 'open', etc)
            **kwargs: Parâmetros adicionais conforme o tipo de dispositivo
            
        Returns:
            Resposta da API
            
        Examples:
            >>> ha = HA()
            
            # Ligar luz
            >>> ha.execute_action('light.sala', 'on')
            
            # Ligar luz com brilho
            >>> ha.execute_action('light.sala', 'on', brightness=200)
            
            # Desligar switch
            >>> ha.execute_action('switch.tomada', 'off')
            
            # Abrir cortina
            >>> ha.execute_action('cover.sala', 'open')
            
            # Cortina em posição específica
            >>> ha.execute_action('cover.sala', 'position', position=50)
            
            # Definir temperatura
            >>> ha.execute_action('climate.quarto', 'set_temperature', temperature=22)
        """
        try:
            # Construir chamada de serviço
            service_call = build_service_call(entity_id, action, **kwargs)
            
            # Executar serviço
            domain = service_call['domain']
            service = service_call['service']
            service_data = service_call['service_data']
            
            print(f"🎬 Executando: {domain}.{service} em {entity_id}")
            print(f"   Parâmetros: {service_data}")
            
            result = self.call_service(domain, service, **service_data)
            print(f"✅ Ação executada com sucesso")
            
            return result
            
        except Exception as e:
            print(f"❌ Erro ao executar ação: {e}")
            raise
    
    def turn_on(self, entity_id: str, **kwargs) -> Dict[str, Any]:
        """Atalho: Ligar uma entidade"""
        return self.execute_action(entity_id, 'on', **kwargs)
    
    def turn_off(self, entity_id: str) -> Dict[str, Any]:
        """Atalho: Desligar uma entidade"""
        return self.execute_action(entity_id, 'off')
    
    def toggle(self, entity_id: str) -> Dict[str, Any]:
        """Atalho: Alternar estado de uma entidade"""
        return self.execute_action(entity_id, 'toggle')
    
    def get_config(self) -> Dict[str, Any]:
        """
        Busca a configuração do Home Assistant.
        
        Returns:
            Dicionário com informações de configuração
        """
        return self._request("GET", "/config")
    
    def filter_entities_by_domain(self, domain: str) -> List[Dict[str, Any]]:
        """
        Filtra entidades por domínio (ex: todos os lights, todos os sensors).
        
        Args:
            domain: Domínio desejado (ex: 'light', 'sensor', 'switch')
            
        Returns:
            Lista de entidades do domínio especificado
            
        Example:
            >>> ha = HA()
            >>> lights = ha.filter_entities_by_domain('light')
        """
        all_entities = self.get_all_entities()
        return [
            entity for entity in all_entities
            if entity['entity_id'].startswith(f"{domain}.")
        ]
    
    def filter_entities_by_state(self, state: str) -> List[Dict[str, Any]]:
        """
        Filtra entidades por estado.
        
        Args:
            state: Estado desejado (ex: 'on', 'off', 'unavailable')
            
        Returns:
            Lista de entidades com o estado especificado
            
        Example:
            >>> ha = HA()
            >>> entities_on = ha.filter_entities_by_state('on')
        """
        all_entities = self.get_all_entities()
        return [
            entity for entity in all_entities
            if entity['state'] == state
        ]
    
    def get_entities_with_areas(self) -> Dict[str, Dict[str, Any]]:
        """
        Busca todas as entidades com suas áreas associadas via WebSocket.
        Cacheia o resultado para uso posterior.
        
        Returns:
            Dicionário organizado por entity_id contendo:
            - entity_id: ID da entidade
            - area_name: Nome da área (None se não houver)
            - area_id: ID da área (None se não houver)
            - state: Estado atual
            
        Example:
            >>> ha = HA()
            >>> entities_areas = ha.get_entities_with_areas()
            >>> print(entities_areas['light.sala']['area_name'])
            'Sala'
        """
        try:
            # Chamar função assíncrona para obter dados via WebSocket
            entities_with_areas = asyncio.run(self._get_entities_async())
            
            # Cachear resultado
            self._entities_with_areas = entities_with_areas
            return entities_with_areas
            
        except Exception as e:
            traceback.print_exc()
            print(f"Erro ao obter entidades com áreas: {e}")
            # Fallback: retornar sem áreas
            try:
                states = self.get_all_entities()
                return {
                    state['entity_id']: {
                        'entity_id': state['entity_id'],
                        'area_id': None,
                        'area_name': None,
                        'state': state.get('state', 'unavailable')
                    }
                    for state in states
                }
            except Exception as e:
                return {}
    
    async def _ws_call(self, ws, msg_id: int, msg_type: str, extra: Dict = None) -> Dict[str, Any]:
        """
        Faz uma chamada assíncrona via WebSocket.
        
        Args:
            ws: Conexão WebSocket
            msg_id: ID da mensagem
            msg_type: Tipo da mensagem
            extra: Dados extras para a mensagem
            
        Returns:
            Resposta do servidor
        """
        payload = {"id": msg_id, "type": msg_type}
        if extra:
            payload.update(extra)
        
        await ws.send(json.dumps(payload))
        
        while True:
            resp = json.loads(await ws.recv())
            if resp.get("id") == msg_id:
                return resp
    
    async def _get_entities_async(self) -> Dict[str, Dict[str, Any]]:
        """
        Obtém entidades e áreas via WebSocket de forma assíncrona.
        """
        ws_url = self.base_url.replace("http://", "ws://").replace("https://", "wss://")
        ws_url = f"{ws_url}/api/websocket"
        
        print(f"🔌 Conectando ao WebSocket: {ws_url}")
        
        async with websockets.connect(ws_url, max_size=None) as ws:
            # Receber mensagem de boas-vindas do servidor
            hello = await ws.recv()
            print("✅ Conectado ao WebSocket")
            
            # Autenticar
            auth_msg = {
                "type": "auth",
                "access_token": self.token
            }
            await ws.send(json.dumps(auth_msg))
            
            auth_resp = json.loads(await ws.recv())
            if auth_resp.get("type") != "auth_ok":
                raise Exception(f"Autenticação falhou: {auth_resp}")
            print("✅ Autenticado")
            
            msg_id = 1
            
            # Obter device_registry
            print("📌 Pegando device_registry...")
            devices_resp = await self._ws_call(ws, msg_id, "config/device_registry/list")
            devices = devices_resp.get("result", [])
            msg_id += 1
            
            # Obter entity_registry
            print("📌 Pegando entity_registry...")
            entities_resp = await self._ws_call(ws, msg_id, "config/entity_registry/list")
            entities = entities_resp.get("result", [])
            msg_id += 1
            
            # Obter areas
            print("📌 Pegando areas...")
            areas_resp = await self._ws_call(ws, msg_id, "config/area_registry/list")
            areas = areas_resp.get("result", [])
            msg_id += 1
            
            # Obter TODOS os estados em uma única chamada (muito mais rápido!)
            print("📌 Pegando estados de todas as entidades...")
            states = self.get_all_entities()
            state_map = {state['entity_id']: state.get('state', 'unavailable') for state in states}
            
            # Criar mapas
            device_id_to_area = {d["id"]: d.get("area_id") for d in devices}
            area_id_to_name = {a["area_id"]: a.get("name") for a in areas}
            
            # Construir resultado
            entities_with_areas = {}
            for entity in tqdm.tqdm(entities, desc="Processando entidades"):
                entity_id = entity.get("entity_id")
                if not entity_id:
                    continue
                
                device_id = entity.get("device_id")
                area_id = entity.get("area_id") or device_id_to_area.get(device_id)
                area_name = area_id_to_name.get(area_id) if area_id else None
                
                # Usar estado do mapa em cache ao invés de fazer requisição HTTP individual
                current_state = state_map.get(entity_id, 'unavailable')
                
                entities_with_areas[entity_id] = {
                    'entity_id': entity_id,
                    'area_id': area_id,
                    'area_name': area_name,
                    'state': current_state
                }
            
            print(f"✅ Carregadas {len(entities_with_areas)} entidades com áreas")
            return entities_with_areas
    
    def get_area_for_entity(self, entity_id: str) -> Optional[str]:
        """
        Obtém a área de uma entidade específica usando o cache.
        
        Args:
            entity_id: ID da entidade
            
        Returns:
            Nome da área ou None se não houver
        """
        # Carregar cache se não estiver carregado
        if self._entities_with_areas is None:
            self.get_entities_with_areas()
        
        # Procurar a área da entidade
        if self._entities_with_areas and entity_id in self._entities_with_areas:
            return self._entities_with_areas[entity_id].get('area_name')
        
        return None
    
    def listen_to_events(self, callback: Callable[[Dict[str, Any]], None], 
                        entity_filter: Optional[str] = None, load_areas: bool = True) -> None:
        """
        Escuta eventos em tempo real do Home Assistant via WebSocket.
        Retorna um dicionário com nome da entidade, estado anterior, estado atual, área e horário.
        
        Args:
            callback: Função que será chamada quando um evento ocorrer.
                     Recebe um dicionário com:
                     - entity_id: ID da entidade
                     - area: Área da entidade (None se não houver)
                     - old_state: Estado anterior
                     - new_state: Estado atual
                     - timestamp: Horário do evento (ISO format)
            entity_filter: (Opcional) Filtrar eventos de uma entidade específica
            load_areas: (Opcional) Carregar áreas no início (padrão: True)
            
        Example:
            >>> ha = HA()
            >>> def handle_event(event):
            ...     print(f"{event['entity_id']}: {event['old_state']} -> {event['new_state']}")
            ...     print(f"Horário: {event['timestamp']}")
            >>> ha.listen_to_events(handle_event)
            
            >>> # Ou filtrar por uma entidade específica:
            >>> ha.listen_to_events(handle_event, entity_filter='light.sala')
        """
        # Converter URL HTTP para WS
        ws_url = self.base_url.replace("http://", "ws://").replace("https://", "wss://")
        ws_url = f"{ws_url}/api/websocket"
        
        ws = websocket.WebSocketApp(
            ws_url,
            on_message=lambda ws, msg: self._handle_ws_message(ws, msg, callback, entity_filter),
            on_error=self._handle_ws_error,
            on_close=self._handle_ws_close
        )
        
        ws.on_open = lambda ws: self._handle_ws_open(ws)
        
        # Carregar áreas antes de iniciar a escuta
        if load_areas:
            print("Carregando mapa de entidades e áreas...")
            self.get_entities_with_areas()
            print("Mapa de áreas carregado!")
        
        print(f"Conectando ao WebSocket: {ws_url}")
        ws.run_forever()
    
    def _handle_ws_open(self, ws) -> None:
        """Autentica quando a conexão WebSocket é aberta."""
        auth_message = {
            "type": "auth",
            "access_token": self.token
        }
        ws.send(json.dumps(auth_message))
        print("Autenticado no WebSocket")
        
        # Inscrever em eventos de estado
        subscribe_message = {
            "id": 1,
            "type": "subscribe_events",
            "event_type": "state_changed"
        }
        ws.send(json.dumps(subscribe_message))
        print("Inscrito em eventos de mudança de estado")
    
    def _handle_ws_message(self, ws, message: str, callback: Callable, 
                          entity_filter: Optional[str]) -> None:
        """Processa mensagens recebidas do WebSocket."""
        try:
            data = json.loads(message)
            
            # Ignorar mensagens de autenticação e inscrição
            if data.get("type") in ["auth_ok", "auth_invalid", "result"]:
                return
            
            # Processar eventos de mudança de estado
            if data.get("type") == "event":
                event = data.get("event", {})
                
                if event.get("event_type") == "state_changed":
                    event_data = event.get("data", {})
                    entity_id = event_data.get("entity_id")
                    
                    # Aplicar filtro se fornecido
                    if entity_filter and entity_id != entity_filter:
                        return
                    
                    old_state_obj = event_data.get("old_state", {})
                    new_state_obj = event_data.get("new_state", {})
                    
                    # Extrair estados
                    old_state = old_state_obj.get("state") if old_state_obj else None
                    new_state = new_state_obj.get("state") if new_state_obj else None
                    
                    # Usar timestamp do novo estado
                    timestamp = new_state_obj.get("last_changed") if new_state_obj else None
                    
                    # Obter área da entidade
                    area = self.get_area_for_entity(entity_id)
                    
                    # Chamar callback com o evento formatado
                    event_dict = {
                        "entity_id": entity_id,
                        "area": area,
                        "old_state": old_state,
                        "new_state": new_state,
                        "timestamp": timestamp,
                        "old_attributes": old_state_obj.get("attributes", {}) if old_state_obj else {},
                        "new_attributes": new_state_obj.get("attributes", {}) if new_state_obj else {}
                    }
                    
                    callback(event_dict)
        
        except json.JSONDecodeError:
            print(f"Erro ao decodificar JSON: {message}")
        except Exception as e:
            print(f"Erro ao processar evento: {e}")
    
    def _handle_ws_error(self, ws, error: Exception) -> None:
        """Trata erros da conexão WebSocket."""
        print(f"Erro WebSocket: {error}")
    
    def _handle_ws_close(self, ws, close_status_code, close_msg) -> None:
        """Trata o fechamento da conexão WebSocket."""
        print(f"WebSocket fechado: {close_status_code} - {close_msg}")

def read_token():
    """Função auxiliar para ler o token de um arquivo (opcional)."""
    try:
        with open("artifacts/ha_token.txt", "r") as file:
            return file.read().strip()
    except FileNotFoundError:
        raise FileNotFoundError("Arquivo ha_token.txt não encontrado. Configure o token nas variáveis de ambiente ou crie o arquivo.")

def read_token_deepseek():
    """Função auxiliar para ler o token do DeepSeek de um arquivo (opcional)."""
    try:
        with open("artifacts/deepseek_token.txt", "r") as file:
            return file.read().strip()
    except FileNotFoundError:
        print("⚠️ Arquivo de token do DeepSeek não encontrado. Use Groq como fallback.")
        return None

if __name__ == "__main__":
    # Exemplo de uso
    try:
        os.environ["HA_URL"] = "https://ha.gratiaamorishome.com.br/"  # Configurar URL do Home Assistant
        os.environ["HA_TOKEN"] = read_token()

        ha = HA()
        
        # Buscar todas as entidades
        print("=== Todas as Entidades ===")
        entities = ha.get_all_entities()
        print(f"Total de entidades: {len(entities)}\n")
        
        # Mostrar as primeiras 5 entidades
        for entity in entities[-5:]:
            print(f"ID: {entity['entity_id']}")
            print(f"Estado: {entity['state']}\n")
        
        # Buscar estado de uma entidade específica
        print("=== Estado de Entidade Específica ===")
        try:
            state = ha.get_entity_state('binary_sensor.sensor_da_porta_principal')
            print(f"Estado da luz da sala: {state['state']}")
        except Exception as e:
            print(f"Entidade não encontrada: {e}")
        
        # Buscar estados de todas as entidades
        print("\n=== Estados de Todas as Entidades ===")
        all_states = ha.get_all_states()
        print(f"Total de estados: {len(all_states)}")
        
        # Filtrar entidades por domínio
        print("\n=== Lights ===")
        lights = ha.filter_entities_by_domain('light')
        print(f"Total de lights: {len(lights)}")
        
        # Filtrar entidades por estado
        print("\n=== Entidades Ligadas ===")
        on_entities = ha.filter_entities_by_state('on')
        print(f"Total ligadas: {len(on_entities)}")
        
    except Exception as e:
        print(f"Erro: {e}")
