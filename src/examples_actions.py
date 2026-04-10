"""
Exemplos de uso das funções de ação do Home Assistant.
Demonstra como controlar diferentes tipos de dispositivos.
"""

import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

from ha import HA


def exemplo_lights():
    """Exemplos de controle de luzes"""
    print("\n" + "="*60)
    print("🔴 EXEMPLOS: CONTROLE DE LUZES")
    print("="*60)
    
    ha = HA()
    
    print("\n1️⃣  Ligar luz:")
    ha.turn_on('light.sala')
    
    print("\n2️⃣  Desligar luz:")
    ha.turn_off('light.sala')
    
    print("\n3️⃣  Alternar luz:")
    ha.toggle('light.sala')
    
    print("\n4️⃣  Ligar luz com brilho (0-255):")
    ha.execute_action('light.sala', 'on', brightness=200)
    
    print("\n5️⃣  Ligar luz com cor RGB:")
    # Vermelho
    ha.execute_action('light.sala', 'on', rgb_color=(255, 0, 0))
    
    # Verde
    ha.execute_action('light.sala', 'on', rgb_color=(0, 255, 0))
    
    # Azul
    ha.execute_action('light.sala', 'on', rgb_color=(0, 0, 255))


def exemplo_switches():
    """Exemplos de controle de switches/tomadas"""
    print("\n" + "="*60)
    print("🔌 EXEMPLOS: CONTROLE DE SWITCHES/TOMADAS")
    print("="*60)
    
    ha = HA()
    
    print("\n1️⃣  Ligar tomada:")
    ha.turn_on('switch.tomada_sala')
    
    print("\n2️⃣  Desligar tomada:")
    ha.turn_off('switch.tomada_sala')
    
    print("\n3️⃣  Alternar tomada:")
    ha.toggle('switch.tomada_sala')


def exemplo_covers():
    """Exemplos de controle de cortinas/persianas"""
    print("\n" + "="*60)
    print("🪟 EXEMPLOS: CONTROLE DE CORTINAS/PERSIANAS")
    print("="*60)
    
    ha = HA()
    
    print("\n1️⃣  Abrir cortina:")
    ha.execute_action('cover.sala', 'open')
    
    print("\n2️⃣  Fechar cortina:")
    ha.execute_action('cover.sala', 'close')
    
    print("\n3️⃣  Parar cortina:")
    ha.execute_action('cover.sala', 'stop')
    
    print("\n4️⃣  Colocar cortina em posição específica (0-100):")
    # 50% aberta
    ha.execute_action('cover.sala', 'position', position=50)
    
    # 75% aberta
    ha.execute_action('cover.sala', 'position', position=75)
    
    # Totalmente fechada (0%)
    ha.execute_action('cover.sala', 'position', position=0)


def exemplo_climate():
    """Exemplos de controle de clima/ar condicionado"""
    print("\n" + "="*60)
    print("❄️  EXEMPLOS: CONTROLE DE CLIMA/AR CONDICIONADO")
    print("="*60)
    
    ha = HA()
    
    print("\n1️⃣  Definir temperatura:")
    ha.execute_action('climate.quarto', 'set_temperature', temperature=22)
    
    print("\n2️⃣  Definir modo HVAC (aquecimento):")
    ha.execute_action('climate.quarto', 'set_hvac_mode', hvac_mode='heat')
    
    print("\n3️⃣  Definir modo HVAC (refrigeração):")
    ha.execute_action('climate.quarto', 'set_hvac_mode', hvac_mode='cool')
    
    print("\n4️⃣  Definir modo HVAC (automático):")
    ha.execute_action('climate.quarto', 'set_hvac_mode', hvac_mode='auto')
    
    print("\n5️⃣  Desligar:")
    ha.execute_action('climate.quarto', 'set_hvac_mode', hvac_mode='off')
    
    # Modos disponíveis: 'off', 'heat', 'cool', 'heat_cool', 'auto', 'fan_only', 'dry'


def exemplo_media_player():
    """Exemplos de controle de media players"""
    print("\n" + "="*60)
    print("🎬 EXEMPLOS: CONTROLE DE MEDIA PLAYER")
    print("="*60)
    
    ha = HA()
    
    print("\n1️⃣  Reproduzir:")
    ha.execute_action('media_player.tv', 'play')
    
    print("\n2️⃣  Pausar:")
    ha.execute_action('media_player.tv', 'pause')
    
    print("\n3️⃣  Parar:")
    ha.execute_action('media_player.tv', 'stop')
    
    print("\n4️⃣  Play/Pause:")
    ha.execute_action('media_player.tv', 'play_pause')
    
    print("\n5️⃣  Definir volume (0-1):")
    ha.execute_action('media_player.tv', 'volume_set', volume_level=0.5)
    
    print("\n6️⃣  Mutar:")
    ha.execute_action('media_player.tv', 'mute', is_volume_mute=True)
    
    print("\n7️⃣  Desmutar:")
    ha.execute_action('media_player.tv', 'mute', is_volume_mute=False)


def exemplo_fan():
    """Exemplos de controle de ventiladores"""
    print("\n" + "="*60)
    print("💨 EXEMPLOS: CONTROLE DE VENTILADOR")
    print("="*60)
    
    ha = HA()
    
    print("\n1️⃣  Ligar ventilador:")
    ha.turn_on('fan.quarto')
    
    print("\n2️⃣  Desligar ventilador:")
    ha.turn_off('fan.quarto')
    
    print("\n3️⃣  Alternar ventilador:")
    ha.toggle('fan.quarto')
    
    print("\n4️⃣  Definir velocidade:")
    ha.execute_action('fan.quarto', 'set_speed', speed='low')
    ha.execute_action('fan.quarto', 'set_speed', speed='medium')
    ha.execute_action('fan.quarto', 'set_speed', speed='high')
    ha.execute_action('fan.quarto', 'set_speed', speed='off')


def exemplo_generico():
    """Exemplo de uso genérico com qualquer tipo de entidade"""
    print("\n" + "="*60)
    print("🎯 EXEMPLO: USO GENÉRICO")
    print("="*60)
    
    ha = HA()
    
    # Você não precisa saber o tipo de dispositivo!
    # A função detecta automaticamente
    
    entities = [
        'light.sala',
        'light.quarto',
        'switch.tomada_cozinha',
        'cover.cortina_sala',
    ]
    
    print("\n1️⃣  Ligar todos os dispositivos:")
    for entity in entities:
        try:
            ha.turn_on(entity)
        except Exception as e:
            print(f"   ⚠️ Erro em {entity}: {e}")
    
    print("\n2️⃣  Desligar todos os dispositivos:")
    for entity in entities:
        try:
            ha.turn_off(entity)
        except Exception as e:
            print(f"   ⚠️ Erro em {entity}: {e}")


def exemplo_automacao():
    """Exemplo de sequência de automação"""
    print("\n" + "="*60)
    print("🤖 EXEMPLO: AUTOMAÇÃO (Cena Dormir)")
    print("="*60)
    
    ha = HA()
    
    print("\n🌙 Ativando cena: DORMIR")
    
    # Desligar todas as luzes
    print("  1. Desligando luzes...")
    ha.turn_off('light.sala')
    ha.turn_off('light.quarto')
    ha.turn_off('light.cozinha')
    
    # Fechar cortinas
    print("  2. Fechando cortinas...")
    ha.execute_action('cover.sala', 'close')
    ha.execute_action('cover.quarto', 'close')
    
    # Desligar TV
    print("  3. Desligando TV...")
    ha.turn_off('media_player.tv')
    
    # Definir ar condicionado
    print("  4. Configurando ar condicionado...")
    ha.execute_action('climate.quarto', 'set_temperature', temperature=20)
    ha.execute_action('climate.quarto', 'set_hvac_mode', hvac_mode='cool')
    
    print("\n✅ Cena DORMIR ativada com sucesso!")


if __name__ == "__main__":
    print("\n" + "="*60)
    print("EXEMPLOS DE USO: CONTROLE HOME ASSISTANT")
    print("="*60)
    
    print("\n⚠️  NOTA: Descomentar a função desejada e executar!")
    print("    As funções requerem entidades existentes no seu HA")
    
    # Descomente a função que deseja testar:
    
    # exemplo_lights()
    # exemplo_switches()
    # exemplo_covers()
    # exemplo_climate()
    # exemplo_media_player()
    # exemplo_fan()
    # exemplo_generico()
    # exemplo_automacao()
    
    print("\n💡 Para usar, importe a classe HA e chame os métodos:")
    print("""
    from src.ha import HA
    
    ha = HA()
    
    # Atalhos rápidos
    ha.turn_on('light.sala')
    ha.turn_off('light.sala')
    ha.toggle('light.sala')
    
    # Ações genéricas com parâmetros
    ha.execute_action('light.sala', 'on', brightness=200)
    ha.execute_action('cover.sala', 'position', position=50)
    ha.execute_action('climate.quarto', 'set_temperature', temperature=22)
    """)
