from src.ha import HA, read_token
import os

os.environ["HA_URL"] = "https://ha.gratiaamorishome.com.br"  # Configurar URL do Home Assistant
os.environ["HA_TOKEN"] = read_token()
ha = HA()

ha.turn_off('light.led_da_pia')