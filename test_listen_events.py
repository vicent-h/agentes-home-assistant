import os
from src.ha import HA, read_token
os.environ["HA_URL"] = "https://ha.gratiaamorishome.com.br"  # Configurar URL do Home Assistant
os.environ["HA_TOKEN"] = read_token()

ha = HA()
ENTITIES_TO_LISTEN = [
    "binary_sensor.sensor_de_presenca_do_escritorio_presenca",
    "sensor.sensor_de_presenca_do_escritorio_illuminance",
    "binary_sensor.sensor_de_presenca_da_cozinha",
    "sensor.sensor_de_presenca_da_cozinha_intensidade_da_luz",
    "switch.interruptor_do_escritorio_switch_1",
    "switch.interruptor_do_escritorio_switch_2",
    "switch.interruptor_da_cozinha_switch_1",
    "switch.interruptor_da_cozinha_switch_2",
    "switch.interruptor_da_sala_switch_1",
    "switch.interruptor_da_sala_switch_2",
    "switch.interruptor_do_quarto_switch_1",
    "switch.interruptor_do_quarto_switch_2",
    "switch.interruptor_do_banheiro_switch_1",
    "switch.interruptor_do_banheiro_switch_2",
    "switch.interruptor_do_banheiro_switch_3"
]

# 3. Com lógica condicional
def handle_with_logic(event):
    if (
        event['new_state'] != event['old_state']
        and event['entity_id'] in ENTITIES_TO_LISTEN
        and event['old_state'] not in (None, "unavailable", "unknown")
    ):
        print(f"Entidade: {event['entity_id']}")
        print(f"Área: {event['area']}")
        print(f"Estado: {event['old_state']} -> {event['new_state']}")
        print(f"Horário: {event['timestamp']}\n")
        print()

        
ha.listen_to_events(handle_with_logic)