import os
from pathlib import Path
from tools.tool_covers import abrir_multiplas_cortinas_posicao, consultar_posicao_das_cortinas
from tools.tool_temperatura import obter_clima_da_casa
from tools.tools_estados import obter_estado_atual_da_casa
from tools.tools_janelas import consultar_situacao_janelas
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
            abrir_multiplas_cortinas_posicao, 
            obter_estado_atual_da_casa, 
            obter_clima_da_casa, 
            consultar_situacao_janelas,
            aguardar_confirmacao_telegram,
            enviar_mensagem_telegram,
            criar_memoria, 
            ler_memoria_similar, 
            ler_preferencias_usuario, 
            atualizar_preferencias_usuario
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