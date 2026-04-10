"""
Ferramentas (Tools) para controle de luzes via Home Assistant.
Estas são as funções que o agente pode chamar.
"""

from src.ha import HA
from src.actions import build_service_call


def ligar_luz(entity_id: str, brilho: int = 255) -> str:
    """
    Liga uma luz específica.
    
    Args:
        entity_id: ID da luz (ex: 'light.sala')
        brilho: Brilho de 0-255 (padrão: 255)
        
    Returns:
        Mensagem de confirmação
    """
    try:
        ha = HA()
        ha.execute_action(entity_id, 'on', brightness=brilho)
        return f"✅ Luz {entity_id} ligada com brilho {brilho}"
    except Exception as e:
        return f"❌ Erro ao ligar {entity_id}: {str(e)}"


def desligar_luz(entity_id: str) -> str:
    """
    Desliga uma luz específica.
    
    Args:
        entity_id: ID da luz (ex: 'light.sala')
        
    Returns:
        Mensagem de confirmação
    """
    try:
        ha = HA()
        ha.execute_action(entity_id, 'off')
        return f"✅ Luz {entity_id} desligada"
    except Exception as e:
        return f"❌ Erro ao desligar {entity_id}: {str(e)}"


def alternar_luz(entity_id: str) -> str:
    """
    Alterna o estado de uma luz (liga se desligada, desliga se ligada).
    
    Args:
        entity_id: ID da luz (ex: 'light.sala')
        
    Returns:
        Mensagem de confirmação
    """
    try:
        ha = HA()
        ha.execute_action(entity_id, 'toggle')
        return f"✅ Luz {entity_id} alternada"
    except Exception as e:
        return f"❌ Erro ao alternar {entity_id}: {str(e)}"


def mudar_cor_luz(entity_id: str, r: int, g: int, b: int) -> str:
    """
    Muda a cor de uma luz RGB.
    
    Args:
        entity_id: ID da luz (ex: 'light.sala')
        r: Valor de vermelho (0-255)
        g: Valor de verde (0-255)
        b: Valor de azul (0-255)
        
    Returns:
        Mensagem de confirmação
    """
    try:
        if not (0 <= r <= 255 and 0 <= g <= 255 and 0 <= b <= 255):
            return "❌ Valores RGB devem estar entre 0-255"
        
        ha = HA()
        ha.execute_action(entity_id, 'on', rgb_color=(r, g, b))
        return f"✅ Cor da luz {entity_id} alterada para RGB({r}, {g}, {b})"
    except Exception as e:
        return f"❌ Erro ao mudar cor {entity_id}: {str(e)}"


def obter_luzes() -> str:
    """
    Lista todas as luzes disponíveis no Home Assistant.
    
    Returns:
        Lista de luzes
    """
    try:
        ha = HA()
        luzes = ha.filter_entities_by_domain('light')
        
        if not luzes:
            return "❌ Nenhuma luz encontrada"
        
        resultado = "📋 Luzes disponíveis:\n"
        for luz in luzes:
            entity_id = luz['entity_id']
            estado = luz['state']
            resultado += f"  • {entity_id}: {estado}\n"
        
        return resultado
    except Exception as e:
        return f"❌ Erro ao listar luzes: {str(e)}"


# Dicionário de ferramentas para o agente
TOOLS = {
    'ligar_luz': ligar_luz,
    'desligar_luz': desligar_luz,
    'alternar_luz': alternar_luz,
    'mudar_cor_luz': mudar_cor_luz,
    'obter_luzes': obter_luzes,
}
