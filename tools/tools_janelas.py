from smolagents import tool
from src.ha import HA

@tool
def consultar_situacao_janelas() -> dict:
    """
    Consulta a situação atual das janelas, retornando se estão abertas ou fechadas.
    
    Returns:
        Um dicionário com a situação de cada janela, por exemplo:
        {
            "janela_da_sala": "fechada",
            "janela_do_quarto": "aberta",
            "janela_do_escritorio": "fechada"
        }

        A chave do dicionário é o entity_id da janela e o valor é a situação atual ("aberta" ou "fechada").
    """
    try:
        ha: HA = HA()
        janelas = {
            "janela_da_lavanderia": ha.get_entity_state("input_boolean.janela_da_lavanderia_grupo"),
            "janela_do_quarto": ha.get_entity_state("input_boolean.janela_do_quarto_grupo"),
            "janela_do_escritorio": ha.get_entity_state("input_boolean.janela_do_escritorio_grupo"),
            "porta_da_varanda": ha.get_entity_state("input_boolean.porta_da_varanda_grupo"),
        }
        return janelas
    except Exception as e:
        return f"❌ Erro ao consultar situação das janelas: {str(e)}"