import os
from pathlib import Path
from tools.tool_covers import consultar_posicao_das_cortinas
from tools.tools_janelas import consultar_situacao_janelas
from tools.tool_volume_echos import consultar_volume_echo, set_volume_echo
from src.ha import read_token, read_token_deepseek
from tools.tool_telegram import (
    enviar_mensagem_telegram, 
    aguardar_confirmacao_telegram
)
from tools.tool_create_memory import (
    criar_memoria, 
    ler_memoria_similar, 
    ler_preferencias_usuario, 
    atualizar_preferencias_usuario
)
from smolagents import CodeAgent, tool
from smolagents.models import OpenAIModel 

os.environ["HA_URL"] = "https://ha.gratiaamorishome.com.br"  # Configurar URL do Home Assistant
os.environ["HA_TOKEN"] = read_token()  # Configurar token do Home Assistant

# Ler token DeepSeek do arquivo
os.environ["DEEPSEEK_API_KEY"] = read_token_deepseek()


class AgentVolumeEchos:
    def __init__(self):
        self.executando = False

    def get_name(self):
        return "Agente de Volume e Echos"
    
    def executando_atualmente(self):
        return self.executando
    
    def start(self):
        self.executando = True
        return "Agente de Volume e Echos iniciado."

    def stop(self):
        self.executando = False
        return "Agente de Volume e Echos parado."

    def run_agent(self, task):
        # Preparar a lista de ferramentas disponíveis
        self.start()
        tools = [
            consultar_posicao_das_cortinas, 
            consultar_situacao_janelas,
            aguardar_confirmacao_telegram,
            enviar_mensagem_telegram,
            criar_memoria, 
            ler_memoria_similar, 
            ler_preferencias_usuario, 
            atualizar_preferencias_usuario,
            consultar_volume_echo,
            set_volume_echo,
        ]

        # Criar modelo DeepSeek (compatível com OpenAI API)
        deepseek_model = OpenAIModel(
            model_id="deepseek-chat",
            api_base="https://api.deepseek.com/v1",
            api_key=os.environ.get("DEEPSEEK_API_KEY"),
        )

        # Criar o agente com DeepSeek (mais barato)
        agent = CodeAgent(
            tools=tools,
            model=deepseek_model,
            #limitar steps para evitar loops infinitos
            max_steps=10,
            additional_authorized_imports=[
                "datetime",
                "math",
            ],
        )

        # Adicionar instruções de sistema à tarefa
        system_instructions = f"""
    Você é um agente especializado calibração de volumes.

    Objetivo: Calibrar os volumes dos dispositivos echo pops, garantindo que estejam equilibrados e adequados para o ambiente.

    Regras:
    1. Os volumes devem ser calibrados para proporcionar uma experiência auditiva confortável, evitando volumes muito altos ou baixos.
    2. De noite, os volumes devem ser ajustados para níveis mais baixos para deixar o ambiente mais tranquilo.
    3. Durante o dia, os volumes podem ser um pouco mais altos, mas ainda devem ser confortáveis para os moradores.
    4. Se houver janelas abertas, os volumes devem ser ajustados para compensar o ruído externo, mas sem exceder níveis que possam causar desconforto.
    
    Echos a serem calibrados:
    - Echo 1: Localizado na sala de estar, próximo à TV (media_player.scottinho).
    - Echo 2: Localizado na cozinha, próximo à área de refeições (media_player.chamyto_echo_pop).
    - Echo 3: Localizado no quarto, próximo à cama (media_player.narutinho_echo_pop).
    - Echo 4: Localizado no escritório, próximo à mesa de trabalho (media_player.tiricutinho_echo_pop).
    - Echo 5: Localizado no banheiro, próximo ao espelho (media_player.pocoyo_echo_pop).
    Condições para calibração:
    - Se for noite (após as 19h), os volumes devem ser ajustados para níveis mais baixos (entre 40% e 50%).
    - Se for dia (entre 7h e 19h), os volumes podem ser ajustados para níveis um pouco mais altos (entre 50% e 70%).
    - Se alguma janela do ambiente onde os Echos Pops estão localizados estiver aberta, os volumes devem ser ajustados para compensar o ruído externo, de acordo com o horário e com a porcentagem de abertura da janela.

    Importante:
    No quarto e no escritório:
        Há a persiana junto à janela. Como a persiana fica na parte exterior, ela pode ajudar a reduzir o ruído externo quando as janelas estão abertas. 
        Portanto, ao calibrar os volumes dos Echos Pops nesses ambientes, leve em consideração a posição atual das persianas. 
        Se as persianas estiverem fechadas ou parcialmente fechadas, isso pode ajudar a reduzir o ruído externo, permitindo que os volumes sejam ajustados para níveis mais confortáveis mesmo com as janelas abertas.
    Na sala de estar:
        A porta da varanda abre para a área externa. Se a porta da varanda estiver aberta, isso pode permitir a entrada de ruído externo, especialmente se houver movimento ou atividades acontecendo do lado de fora.
        Portanto, ao calibrar os volumes dos Echos Pops na sala de estar, leve em consideração a situação da porta da varanda. Se a porta estiver aberta, ajuste os volumes para compensar o ruído externo, mas sem exceder níveis que possam causar desconforto.
    Na cozinha:
        A janela lavanderia dá para a área externa. Se a janela da lavanderia estiver aberta, isso pode permitir a entrada de ruído externo, especialmente se houver movimento ou atividades acontecendo do lado de fora.
        Portanto, ao calibrar os volumes dos Echos Pops na cozinha, leve em consideração a situação da janela da lavanderia. Se a janela estiver aberta, ajuste os volumes para compensar o ruído externo, mas sem exceder níveis que possam causar desconforto.

    1. Analise se é necessário fazer algo, caso não seja, não precise informar o usuário.
    2. Sempre use primeiro o 'aguardar_confirmacao_telegram()' para aguardar confirmação do usuário (5 minutos de timeout)
    3. Verifique o campo "confirmado" na resposta:
    - Se confirmado = True: Execute as ações
    - Se confirmado = False: Cancele as ações e informe o cancelamento
    - Se timeout: Cancele as ações e informe o timeout
    4. Sempre comunique o resultado final ao usuário pelo enviar_mensagem_telegram()

    Exemplo de fluxo:
    0. Leia as memorias anteriores usando 'ler_memoria_similar()' para verificar se há informações relevantes sobre as preferências do usuário ou situações similares.
    1. Leia as preferências do usuário usando 'ler_preferencias_usuario()' para entender melhor as preferências específicas do usuário.
    2. Enviar: "Identifiquei que os volumes dos Echos Pops estão descalibrados. Deseja que eu ajuste os volumes para proporcionar uma experiência auditiva mais confortável?"
    3. Aguardar: resposta do usuário (sim/não)
    4. Se sim: Executar ações
    5. Se não: Cancelar e informar

    Ao final, você deve resumir o que foi feito, utilizando as seguintes funções:
    1. criar_memoria(content, tags) - para criar uma memória do que foi identificado, o que o agente fez, e o que o usuário pediu. As tags são palavras-chave relacionadas ao conteúdo da memória, separadas por vírgula.
    2. Atualizar as preferências do usuário usando 'atualizar_preferencias_usuario()' observando as respostas do usuário para melhorar a experiência futura.

    Caso a preferência do usuário for diferente do que foi identificado, procure entender o motivo da divergência, e se necessário, adicione ou modifique as preferências do usuário usando 'atualizar_preferencias_usuario()' para melhorar a experiência futura.
    """.strip()
        
        full_task = f"{system_instructions}\n\nTarefa: {task}"
        # Executar o agente com a tarefa completa
        result = agent.run(full_task)
        self.stop()
        return result