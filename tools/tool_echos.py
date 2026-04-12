from smolagents import tool
import os
import json

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




    