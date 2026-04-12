import traceback

from smolagents import tool
from src.ha import HA

@tool
def obter_estado_atual_da_casa() -> dict:
    """
        Obtém o estado atual da casa, retornando os input_booleans, que contém informação
        se há pessoas em casa, se está chovendo, se alguém está dormindo, etc.

        Returns:
            Um dicionário com o estado de cada input_boolean, por exemplo:
            {
                "pessoas_em_casa": True,
                "chovendo": False,
                "alguem_dormindo": True,
                "alguem_no_banho": False,
                "alguem_no_banheiro": False,
                "modo_privacidade": False,
                "visita": False,
                "faxina": True
            }
    """

    try:
        ha: HA = HA()
        estado_casa = {
            "pessoas_em_casa": ha.get_entity_state("input_boolean.geral_status_em_casa")['state'] == "on",
            "esta_chovendo": ha.get_entity_state("input_boolean.modo_chuva")['state'] == "on",
            "alguem_dormindo": ha.get_entity_state("input_boolean.modo_boa_noite")['state'] == "on",
            "alguem_no_banho": ha.get_entity_state("input_boolean.modo_banho")['state'] == "on",
            "alguem_no_banheiro": ha.get_entity_state("input_boolean.switch_movimento_do_banheiro")['state'] == "on",
            "privacidade": ha.get_entity_state("input_boolean.modo_privacidade")['state'] == "on",
            "ha_visita_em_casa": ha.get_entity_state("input_boolean.modo_visitante")['state'] == "on",
            "faxinando_no_momento": ha.get_entity_state("input_boolean.modo_faxina")['state'] == "on",
        }
        return estado_casa
    except Exception as e:
        traceback.print_exc()
        return f"❌ Erro ao obter estado da casa: {str(e)}"


@tool
def verificar_se_esta_chovendo():
    """
        Exemplo de como verificar se está chovendo usando o estado da casa

        Returns:
            True se estiver chovendo, False caso contrário
    """
    ha = HA()
    estado_casa = ha.get_entity_state("input_boolean.modo_chuva")
    return estado_casa == "on"

@tool
def verificar_se_ha_pessoas_em_casa():
    """
        Exemplo de como verificar se há pessoas em casa usando o estado da casa

        Returns:
            True se houver pessoas em casa, False caso contrário
    """
    ha = HA()
    estado_casa = ha.get_entity_state("input_boolean.geral_status_em_casa")
    return estado_casa == "on"


@tool
def verificar_se_alguem_esta_dormindo():
    """
        Exemplo de como verificar se alguém está dormindo usando o estado da casa

        Returns:
            True se alguém estiver dormindo, False caso contrário
    """
    ha = HA()
    estado_casa = ha.get_entity_state("input_boolean.modo_boa_noite")
    return estado_casa == "on"
