import traceback

from smolagents import tool
from src.ha import HA

@tool
def obter_clima_da_casa() -> dict:
    """
    Obtém a temperatura atual da casa.
    
    Returns:
        Um dicionário com a temperatura, velocidade do vento e temperatura confortável.
    """
    try:
        ha: HA = HA()
        temperatura = ha.get_entity_state("sensor.temperatura_do_quarto_temperature")['state']
        velocidade_vento = ha.get_entity_state("weather.forecast_home")['attributes']['wind_speed']
        temperatura_acima_da_confortavel = ha.get_entity_state("input_number.temperatura_para_abrir_as_portas_e_persianas")['state']
        return {
            "temperatura": temperatura,
            "velocidade_vento": velocidade_vento,
            # "temperatura_acima_da_confortavel": temperatura_acima_da_confortavel
            "temperatura_acima_da_confortavel": 23
        }
    except Exception as e:
        print("❌ Erro ao obter clima:")
        traceback.print_exc()
        return f"❌ Erro ao obter clima: {str(e)}"
