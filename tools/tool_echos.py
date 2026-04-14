from smolagents import tool
import os
import json
from src.ha import HA

PATH_ECHO = os.environ.get("PATH_ECHO")

@tool
def salvar_volume_anterior(nome_echo: str, volume: int) -> str:
    """
    Salva o volume anterior do Echo em um json para referência futura

    Args:
        nome_echo (str): O nome do dispositivo Echo (por exemplo, "Echo da Sala").
        volume (int): O volume anterior do Echo (0-100).
    Returns:
        str: Mensagem de confirmação do salvamento.
    """

    if os.path.exists(os.path.join(PATH_ECHO, "volumes_anteriores.json")):
        with open(os.path.join(PATH_ECHO, "volumes_anteriores.json"), "r") as f:
            volumes_anteriores = json.load(f)

    else:
        volumes_anteriores = {}

    volumes_anteriores[nome_echo] = volume

    with open(os.path.join(PATH_ECHO, "volumes_anteriores.json"), "w") as f:
        json.dump(volumes_anteriores, f, indent=4, ensure_ascii=False)

    return f"✅ Volume anterior do {nome_echo} salvo com sucesso!"

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
        entity_id: O entity_id do Echo (por exemplo, "media_player.narutinho_echo_pop").
        volume: O nível de volume desejado (0-100).
    Returns:
        Mensagem de confirmação ou erro.
    """
    try:
        volume = max(0, min(100, int(volume)))
        volume_level = volume / 100.0

        ha = HA()
        ha.call_service(
            "media_player",
            "volume_set",
            entity_id=entity_id,
            volume_level=volume_level
        )

        return f"Volume do {entity_id} definido para {volume}%."

    except Exception as e:
        return f"❌ Erro ao definir volume do {entity_id}: {str(e)}"