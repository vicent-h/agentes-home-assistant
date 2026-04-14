from smolagents import tool
from src.ha import HA

@tool
def consultar_volume_echo(entity_id: str) -> int:
    """
    Consulta o volume atual de um Echo específico.
    
    Args:
        entity_id: O entity_id do Echo (por exemplo, "media_player.echo_sala").
    
    Returns:
        O nível de volume atual (0-100) ou mensagem de erro.
    """
    try:
        ha = HA()
        estado = ha.get_entity_state(entity_id, keys_needed=['attributes', 'state', 'area'])
        if estado is None:
            return f"❌ Echo com entity_id '{entity_id}' não encontrado."
        
        volume_atual = estado['attributes'].get('volume_level')
        if volume_atual is not None:
            return int(volume_atual * 100)  # Converter para escala de 0-100
        else:
            return f"❌ Volume do {entity_id} não disponível."
    except Exception as e:
        return f"❌ Erro ao consultar volume do {entity_id}: {str(e)}"

@tool
def set_volume_echo(entity_id: str, volume: int) -> str:
    """
    Define o volume de um Echo específico.
    
    Args:
        entity_id: O entity_id do Echo (por exemplo, "media_player.echo_sala").
        volume: O nível de volume desejado (0-100).
    
    Returns:
        Mensagem de confirmação ou erro.
    """
    try:
        ha = HA()
        ha.call_service(
            "media_player",
            "volume_set",
            {
                "entity_id": entity_id,
                "volume_level": volume / 100.0  # HA espera um valor entre 0.0 e 1.0
            }
        )
        
        return f"Volume do {entity_id} definido para {volume}%."
    except Exception as e:
        return f"❌ Erro ao definir volume do {entity_id}: {str(e)}"