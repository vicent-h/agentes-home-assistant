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

class AgentConforto:
    def __init__(self):
        self.executando = False

    def get_name(self):
        return "Agente de Conforto Térmico"
    
    def executando_atualmente(self):
        return self.executando
    
    def start(self):
        self.executando = True
        return "Agente de Conforto Térmico iniciado."

    def stop(self):
        self.executando = False
        return "Agente de Conforto Térmico parado."

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

    Janelas são sensores (fechadas/abertas), cortinas/persianas (abertura) são motorizadas.

    Exemplos quando há pessoas, sem chuva, sem banho, privacidade off:
    - Calor + abertura fechada + janela fechada → não abra (ar não vai conseguir circular)
    - Calor + abertura fechada + janela aberta → abra persiana (circula ar)
    - Calor + abertura fechada + janela aberta → abra persiana (circula ar)
    - Calor + janela aberta + abertura aberta → nada a fazer (já está circulando)
    - Janela fechada + abertura aberta → não feche (deixa luz entrar)

    Os covers porta da varanda e janela da lavanderia abrem as janelas, então elas tem poderes de abrir a janela, mesmo que estejam fechadas.

    Exemplos quando não há pessoas em casa:
    - Calor + abertura fechada + janela fechada → não abra (ar não vai conseguir circular)
    - Calor + abertura fechada + janela aberta → abra 20% da abertura (para deixar um pouco de ar circular e evitar exposição da casa)

    Não se limite a esses exemplos.
    Pode não ser necessário fazer nada.

    Para conforto, no máximo é preciso ter duas janelas/portas aberturas em diferentes cômodos (importante), caso as respectivas janelas não estejam abertas.
    IMPORTANTE - FLUXO DE CONFIRMAÇÃO (somente se for necessário fazer algo):
    1. Analise se é necessário fazer algo para melhorar o conforto térmico, caso não seja, não precise informar o usuário.
    2. Sempre use primeiro o 'aguardar_confirmacao_telegram()' para aguardar confirmação do usuário (5 minutos de timeout)
    3. Verifique o campo "confirmado" na resposta:
    - Se confirmado = True: Execute as ações de abertura/fechamento
    - Se confirmado = False: Cancele as ações e informe o cancelamento
    - Se timeout: Cancele as ações e informe o timeout
    4. Sempre comunique o resultado final ao usuário pelo enviar_mensagem_telegram()

    Exemplo de fluxo:
    0. Leia as memorias anteriores usando 'ler_memoria_similar()' para verificar se há informações relevantes sobre as preferências do usuário ou situações similares.
    1. Leia as preferências do usuário usando 'ler_preferencias_usuario()' para entender melhor as preferências específicas do usuário em relação ao conforto térmico.
    2. Enviar: "Vou abrir a persiana da sala em 70%"
    3. Aguardar: resposta do usuário (sim/não)
    4. Se sim: Executar ações
    5. Se não: Cancelar e informar

    Ao final, você deve resumir o que foi feito, utilizando as seguintes funções:
    1. criar_memoria(content, tags) - para criar uma memória do que foi identificado, o que o agente fez, e o que o usuário pediu. As tags são palavras-chave relacionadas ao conteúdo da memória, separadas por vírgula.
    2. Atualizar as preferências do usuário usando 'atualizar_preferencias_usuario()' observando as respostas do usuário para melhorar a experiência futura.

    Caso a preferência do usuário for diferente do que foi identificado, procure entender o motivo da divergência, e se necessário, adicione ou modifique as preferências do usuário usando 'atualizar_preferencias_usuario()' para melhorar a experiência futura.

    Dê preferencia para abrir a janela da lavanderia e o porta da varanda, pois são os cômodos mais arejados da casa. Evite abrir a janela do quarto para não comprometer a privacidade.

        """.strip()
        
        # Combinar instruções do sistema com a tarefa
        full_task = f"{system_instructions}\n\n### Tarefa:\n{task}"

        agent.run(full_task)
        self.stop()