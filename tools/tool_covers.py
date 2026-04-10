from smolagents import tool
from src.ha import HA

@tool
def consultar_posicao_das_cortinas() -> dict:
    """
    Consulta a posição atual das cortinas/persianas.
    Onde 0 = totalmente fechada, 100 = totalmente aberta.
    
    Returns:
        Um dicionário com a posição de cada cortina, por exemplo:
        {
            "cortina_da_sala_curtain": 100,
            "persiana_do_quarto_curtain": 50,
            "persiana_do_escritorio_curtain": 0
        }

        A chave do dicionário é o entity_id da cortina e o valor é a posição atual (0-100).
    """
    try:
        ha: HA = HA()
        #fica nos attributo position
        entidades_cortinas = {
            "cover.cortina_da_sala_curtain": ha.get_entity_state("cover.cortina_da_sala_curtain")['attributes']['current_position'],
            "cover.persiana_do_quarto_curtain": ha.get_entity_state("cover.persiana_do_quarto_curtain")['attributes']['current_position'],
            "cover.persiana_do_escritorio_curtain": ha.get_entity_state("cover.persiana_do_escritorio_curtain")['attributes']['current_position'],
            "cover.porta_da_varanda_2": ha.get_entity_state("cover.porta_da_varanda_2")['attributes']['current_position'],
            "cover.persiana_da_lavanderia_curtain": ha.get_entity_state("cover.persiana_da_lavanderia_curtain")['attributes']['current_position']
        }
        return entidades_cortinas
    except Exception as e:
        return f"❌ Erro ao consultar posição das cortinas: {str(e)}"

@tool    
def abrir_multiplas_cortinas_posicao(posicoes: dict) -> str:
    """
    Abre múltiplas cortinas/persianas para posições específicas.
    
    Args:
        posicoes: Dicionário onde a chave é o entity_id da cortina e o valor é a posição desejada (0-100), por exemplo:
        {
            "cover.cortina_da_sala_curtain": 50,
            "cover.persiana_do_quarto_curtain": 75
        }

    Returns:
        Mensagem de confirmação
    """

    try:
        ha = HA()
        for entity_id, posicao in posicoes.items():
            ha.execute_action(entity_id, 'position', position=posicao)
        return f"✅ Cortinas ajustadas para as posições especificadas"
    except Exception as e:
        return f"❌ Erro ao ajustar cortinas: {str(e)}"