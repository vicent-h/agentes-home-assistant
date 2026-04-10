"""
Módulo de ações para Home Assistant.
Suporta diferentes tipos de dispositivos com suas ações específicas.
"""

from typing import Dict, List, Any, Optional


class DeviceAction:
    """Classe base para ações de dispositivos"""
    
    @staticmethod
    def get_domain_from_entity(entity_id: str) -> str:
        """
        Extrai o domínio de um entity_id.
        Exemplo: 'light.sala' -> 'light'
        """
        return entity_id.split('.')[0] if '.' in entity_id else None
    
    @staticmethod
    def get_entity_name(entity_id: str) -> str:
        """
        Extrai o nome da entidade.
        Exemplo: 'light.sala' -> 'sala'
        """
        return entity_id.split('.')[-1] if '.' in entity_id else entity_id


class LightActions(DeviceAction):
    """Ações para luzes (light)"""
    
    VALID_ACTIONS = ['on', 'off', 'toggle']
    
    @staticmethod
    def get_service_call(entity_id: str, action: str, **kwargs) -> Dict[str, Any]:
        """
        Retorna a chamada de serviço para controlar luzes.
        
        Args:
            entity_id: ID da luz
            action: 'on', 'off', 'toggle'
            **kwargs: Parâmetros adicionais (brightness, rgb_color, etc)
            
        Returns:
            Dict com domain, service, e service_data
        """
        action = action.lower()
        
        if action == 'on':
            return {
                'domain': 'light',
                'service': 'turn_on',
                'service_data': {'entity_id': entity_id, **kwargs}
            }
        elif action == 'off':
            return {
                'domain': 'light',
                'service': 'turn_off',
                'service_data': {'entity_id': entity_id}
            }
        elif action == 'toggle':
            return {
                'domain': 'light',
                'service': 'toggle',
                'service_data': {'entity_id': entity_id}
            }
        else:
            raise ValueError(f"Ação inválida para light: {action}. Válidas: {LightActions.VALID_ACTIONS}")
    
    @staticmethod
    def with_brightness(entity_id: str, action: str, brightness: int) -> Dict[str, Any]:
        """Liga luz com brilho específico (0-255)"""
        if brightness < 0 or brightness > 255:
            raise ValueError("Brightness deve estar entre 0 e 255")
        return LightActions.get_service_call(entity_id, action, brightness=brightness)
    
    @staticmethod
    def with_color(entity_id: str, action: str, rgb_color: tuple) -> Dict[str, Any]:
        """Liga luz com cor RGB específica"""
        if len(rgb_color) != 3:
            raise ValueError("RGB deve ter 3 valores: (R, G, B)")
        return LightActions.get_service_call(entity_id, action, rgb_color=rgb_color)


class SwitchActions(DeviceAction):
    """Ações para switches (switch)"""
    
    VALID_ACTIONS = ['on', 'off', 'toggle']
    
    @staticmethod
    def get_service_call(entity_id: str, action: str, **kwargs) -> Dict[str, Any]:
        """
        Retorna a chamada de serviço para controlar switches.
        
        Args:
            entity_id: ID do switch
            action: 'on', 'off', 'toggle'
            **kwargs: Parâmetros adicionais
            
        Returns:
            Dict com domain, service, e service_data
        """
        action = action.lower()
        
        if action == 'on':
            return {
                'domain': 'switch',
                'service': 'turn_on',
                'service_data': {'entity_id': entity_id}
            }
        elif action == 'off':
            return {
                'domain': 'switch',
                'service': 'turn_off',
                'service_data': {'entity_id': entity_id}
            }
        elif action == 'toggle':
            return {
                'domain': 'switch',
                'service': 'toggle',
                'service_data': {'entity_id': entity_id}
            }
        else:
            raise ValueError(f"Ação inválida para switch: {action}. Válidas: {SwitchActions.VALID_ACTIONS}")


class CoverActions(DeviceAction):
    """Ações para cortinas/persianas (cover)"""
    
    VALID_ACTIONS = ['open', 'close', 'stop', 'position']
    
    @staticmethod
    def get_service_call(entity_id: str, action: str, **kwargs) -> Dict[str, Any]:
        """
        Retorna a chamada de serviço para controlar cortinas.
        
        Args:
            entity_id: ID da cortina
            action: 'open', 'close', 'stop', 'position'
            **kwargs: Para 'position', deve conter 'position' (0-100)
            
        Returns:
            Dict com domain, service, e service_data
        """
        action = action.lower()
        
        if action == 'open':
            return {
                'domain': 'cover',
                'service': 'open_cover',
                'service_data': {'entity_id': entity_id}
            }
        elif action == 'close':
            return {
                'domain': 'cover',
                'service': 'close_cover',
                'service_data': {'entity_id': entity_id}
            }
        elif action == 'stop':
            return {
                'domain': 'cover',
                'service': 'stop_cover',
                'service_data': {'entity_id': entity_id}
            }
        elif action == 'position':
            position = kwargs.get('position')
            if position is None or position < 0 or position > 100:
                raise ValueError("position deve estar entre 0 e 100")
            return {
                'domain': 'cover',
                'service': 'set_cover_position',
                'service_data': {'entity_id': entity_id, 'position': position}
            }
        else:
            raise ValueError(f"Ação inválida para cover: {action}. Válidas: {CoverActions.VALID_ACTIONS}")


class ClimateActions(DeviceAction):
    """Ações para termostatos/ar condicionado (climate)"""
    
    VALID_ACTIONS = ['set_temperature', 'set_mode', 'set_hvac_mode']
    
    # Modos comuns
    HVAC_MODES = ['off', 'heat', 'cool', 'heat_cool', 'auto', 'fan_only', 'dry']
    
    @staticmethod
    def get_service_call(entity_id: str, action: str, **kwargs) -> Dict[str, Any]:
        """
        Retorna a chamada de serviço para controlar clima.
        
        Args:
            entity_id: ID do clima
            action: 'set_temperature', 'set_mode', 'set_hvac_mode'
            **kwargs: 'temperature' para set_temperature, 'hvac_mode' para set_hvac_mode
            
        Returns:
            Dict com domain, service, e service_data
        """
        action = action.lower()
        
        if action == 'set_temperature':
            temperature = kwargs.get('temperature')
            if temperature is None:
                raise ValueError("temperature é obrigatório para set_temperature")
            return {
                'domain': 'climate',
                'service': 'set_temperature',
                'service_data': {'entity_id': entity_id, 'temperature': temperature}
            }
        elif action == 'set_hvac_mode':
            hvac_mode = kwargs.get('hvac_mode')
            if hvac_mode not in ClimateActions.HVAC_MODES:
                raise ValueError(f"hvac_mode inválido. Válidos: {ClimateActions.HVAC_MODES}")
            return {
                'domain': 'climate',
                'service': 'set_hvac_mode',
                'service_data': {'entity_id': entity_id, 'hvac_mode': hvac_mode}
            }
        else:
            raise ValueError(f"Ação inválida para climate: {action}. Válidas: {ClimateActions.VALID_ACTIONS}")


class MediaPlayerActions(DeviceAction):
    """Ações para media players (media_player)"""
    
    VALID_ACTIONS = ['play', 'pause', 'stop', 'play_pause', 'volume_set', 'mute']
    
    @staticmethod
    def get_service_call(entity_id: str, action: str, **kwargs) -> Dict[str, Any]:
        """
        Retorna a chamada de serviço para controlar media player.
        
        Args:
            entity_id: ID do media player
            action: 'play', 'pause', 'stop', 'play_pause', 'volume_set', 'mute'
            **kwargs: 'volume_level' para volume_set (0-1)
            
        Returns:
            Dict com domain, service, e service_data
        """
        action = action.lower()
        
        if action == 'play':
            return {
                'domain': 'media_player',
                'service': 'media_play',
                'service_data': {'entity_id': entity_id}
            }
        elif action == 'pause':
            return {
                'domain': 'media_player',
                'service': 'media_pause',
                'service_data': {'entity_id': entity_id}
            }
        elif action == 'stop':
            return {
                'domain': 'media_player',
                'service': 'media_stop',
                'service_data': {'entity_id': entity_id}
            }
        elif action == 'play_pause':
            return {
                'domain': 'media_player',
                'service': 'media_play_pause',
                'service_data': {'entity_id': entity_id}
            }
        elif action == 'volume_set':
            volume_level = kwargs.get('volume_level')
            if volume_level is None or volume_level < 0 or volume_level > 1:
                raise ValueError("volume_level deve estar entre 0 e 1")
            return {
                'domain': 'media_player',
                'service': 'volume_set',
                'service_data': {'entity_id': entity_id, 'volume_level': volume_level}
            }
        elif action == 'mute':
            is_volume_mute = kwargs.get('is_volume_mute', True)
            return {
                'domain': 'media_player',
                'service': 'volume_mute',
                'service_data': {'entity_id': entity_id, 'is_volume_mute': is_volume_mute}
            }
        else:
            raise ValueError(f"Ação inválida para media_player: {action}. Válidas: {MediaPlayerActions.VALID_ACTIONS}")


class FanActions(DeviceAction):
    """Ações para ventiladores (fan)"""
    
    VALID_ACTIONS = ['on', 'off', 'toggle', 'set_speed']
    SPEEDS = ['off', 'low', 'medium', 'high']
    
    @staticmethod
    def get_service_call(entity_id: str, action: str, **kwargs) -> Dict[str, Any]:
        """
        Retorna a chamada de serviço para controlar ventiladores.
        
        Args:
            entity_id: ID do ventilador
            action: 'on', 'off', 'toggle', 'set_speed'
            **kwargs: 'speed' para set_speed ('off', 'low', 'medium', 'high')
            
        Returns:
            Dict com domain, service, e service_data
        """
        action = action.lower()
        
        if action == 'on':
            return {
                'domain': 'fan',
                'service': 'turn_on',
                'service_data': {'entity_id': entity_id}
            }
        elif action == 'off':
            return {
                'domain': 'fan',
                'service': 'turn_off',
                'service_data': {'entity_id': entity_id}
            }
        elif action == 'toggle':
            return {
                'domain': 'fan',
                'service': 'toggle',
                'service_data': {'entity_id': entity_id}
            }
        elif action == 'set_speed':
            speed = kwargs.get('speed')
            if speed not in FanActions.SPEEDS:
                raise ValueError(f"speed inválido. Válidos: {FanActions.SPEEDS}")
            return {
                'domain': 'fan',
                'service': 'set_speed',
                'service_data': {'entity_id': entity_id, 'speed': speed}
            }
        else:
            raise ValueError(f"Ação inválida para fan: {action}. Válidas: {FanActions.VALID_ACTIONS}")


# Mapeamento de domínios para classes de ação
DOMAIN_ACTIONS_MAP = {
    'light': LightActions,
    'switch': SwitchActions,
    'cover': CoverActions,
    'climate': ClimateActions,
    'media_player': MediaPlayerActions,
    'fan': FanActions,
}


def get_action_class(domain: str):
    """Retorna a classe de ação para um domínio específico"""
    return DOMAIN_ACTIONS_MAP.get(domain)


def build_service_call(entity_id: str, action: str, **kwargs) -> Dict[str, Any]:
    """
    Função genérica que roteia para a classe correta.
    
    Args:
        entity_id: ID da entidade (ex: 'light.sala')
        action: Ação a executar (ex: 'on', 'off', 'toggle')
        **kwargs: Parâmetros adicionais
        
    Returns:
        Dict com a chamada de serviço formatada
        
    Example:
        >>> call = build_service_call('light.sala', 'on', brightness=150)
        >>> print(call)
        {'domain': 'light', 'service': 'turn_on', 'service_data': {...}}
    """
    domain = DeviceAction.get_domain_from_entity(entity_id)
    
    if not domain:
        raise ValueError(f"Entity ID inválido: {entity_id}")
    
    action_class = get_action_class(domain)
    
    if not action_class:
        raise ValueError(f"Domínio '{domain}' não suportado. Disponíveis: {list(DOMAIN_ACTIONS_MAP.keys())}")
    
    return action_class.get_service_call(entity_id, action, **kwargs)


if __name__ == "__main__":
    # Exemplos de uso
    print("=== Exemplos de chamadas de serviço ===\n")
    
    # Light
    print("1. Ligar luz:")
    print(build_service_call('light.sala', 'on'))
    
    print("\n2. Ligar luz com brilho:")
    print(build_service_call('light.sala', 'on', brightness=200))
    
    print("\n3. Ligar luz com cor RGB:")
    print(build_service_call('light.sala', 'on', rgb_color=(255, 0, 0)))
    
    # Switch
    print("\n4. Desligar switch:")
    print(build_service_call('switch.tomada', 'off'))
    
    # Cover
    print("\n5. Abrir cortina:")
    print(build_service_call('cover.sala', 'open'))
    
    print("\n6. Cortina em posição específica:")
    print(build_service_call('cover.sala', 'position', position=50))
    
    # Climate
    print("\n7. Definir temperatura:")
    print(build_service_call('climate.quarto', 'set_temperature', temperature=22))
    
    # Media Player
    print("\n8. Reproduzir:")
    print(build_service_call('media_player.tv', 'play'))
    
    print("\n9. Definir volume:")
    print(build_service_call('media_player.tv', 'volume_set', volume_level=0.5))
    
    # Fan
    print("\n10. Definir velocidade do ventilador:")
    print(build_service_call('fan.quarto', 'set_speed', speed='high'))
