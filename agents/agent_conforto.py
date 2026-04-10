import os
from pathlib import Path
from tools.tool_covers import abrir_multiplas_cortinas_posicao, consultar_posicao_das_cortinas
from tools.tool_temperatura import obter_clima_da_casa
from tools.tools_estados import obter_estado_atual_da_casa
from tools.tools_janelas import consultar_situacao_janelas
from src.ha import read_token, read_token_deepseek
from tools.tool_telegram import (
    enviar_mensagem_telegram, 
    enviar_mensagem_formatada_telegram,
    aguardar_confirmacao_telegram
)
from smolagents import CodeAgent, tool
from smolagents.models import OpenAIModel 

os.environ["HA_URL"] = "https://ha.gratiaamorishome.com.br"  # Configurar URL do Home Assistant
os.environ["HA_TOKEN"] = read_token()  # Configurar token do Home Assistant

# Ler token DeepSeek do arquivo
os.environ["DEEPSEEK_API_KEY"] = read_token_deepseek()

def run_agent(task):
    # Preparar a lista de ferramentas disponíveis
    tools = [
        consultar_posicao_das_cortinas, 
        abrir_multiplas_cortinas_posicao, 
        obter_estado_atual_da_casa, 
        obter_clima_da_casa, 
        consultar_situacao_janelas,
        aguardar_confirmacao_telegram
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
    )
    
    # Adicionar instruções de sistema à tarefa
    system_instructions = """
Você é um agente especializado em conforto térmico residencial.

Objetivo: Determinar o percentual ideal de abertura de cortinas/persianas para maximizar conforto quando estiver calor.

Abra apenas quando:
- Há pessoas em casa
- Não está chovendo
- Não está faxinando ou alguém tomando banho
- Privacidade desligada
- Se dormindo: máximo 20%
- Se persiana do quarto: máximo 20%.

Janelas são sensores (fechadas/abertas), cortinas/persianas são motorizadas.

Exemplos (quando há pessoas, sem chuva, sem banho, privacidade off):
- Calor + persiana fechada + janela fechada → não abra (ar quente não entra)
- Calor + persiana fechada + janela aberta → abra persiana (circula ar)
- Calor + persiana fechada + janela aberta → abra persiana (circula ar)
- Calor + janela aberta + persiana aberta → nada a fazer (já está circulando)
- Janela fechada + persiana aberta → não feche (deixa luz entrar)

Não se limite a esses exemplos.
Pode não ser necessário fazer nada.

Para conforto, no mínimo é preciso ter duas janelas/portas aberturas, caso as respectivas janelas não estejam abertas.
IMPORTANTE - FLUXO DE CONFIRMAÇÃO:
1. Sempre primeiro use 'enviar_mensagem_formatada_telegram()' para comunicar o que você vai fazer
2. Depois use 'aguardar_confirmacao_telegram()' para aguardar confirmação do usuário (5 minutos de timeout)
3. Verifique o campo "confirmado" na resposta:
   - Se confirmado = True: Execute as ações de abertura/fechamento
   - Se confirmado = False: Cancele as ações e informe o cancelamento
   - Se timeout: Cancele as ações e informe o timeout
4. Sempre comunique o resultado final ao usuário

Exemplo de fluxo:
1. Enviar: "Vou abrir a persiana da sala em 70%"
2. Aguardar: resposta do usuário (sim/não)
3. Se sim: Executar ações
4. Se não: Cancelar e informar
Você deve somente determinar e enviar mensagem ao telegram mostrando o que irá fazer, esperando a confirmação do usuário.
    """.strip()
    
    # Combinar instruções do sistema com a tarefa
    full_task = f"{system_instructions}\n\n### Tarefa:\n{task}"

    agent.run(full_task)