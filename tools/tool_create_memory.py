# tool create memory, salvando em arquivos de texto, cada arquivo é uma memória, o nome do arquivo é a data e hora da criação da memória
# Exemplo de nome de arquivo: 2024-06-01_12-00-00.txt
# O Agente deve criar um resumo do que foi identificado, o que o agente fez, e o que o usuário pediu, e salvar isso no arquivo de memória
# Deve criar tags junto com a memória, para facilitar a busca depois, as tags devem ser palavras-chave relacionadas ao conteúdo da memória, separadas por vírgula
# o arquivo deve ser um dict com as chaves: "content", "tags", "created_at"

import os
import json
from datetime import datetime
from typing import List

from smolagents import tool

FILE_PREFERENCES_USUARIO = os.environ["FILE_PREFERENCES_USUARIO"]
QTDE_TAGS = int(os.environ.get("QTDE_TAGS", 5))
TOP_N_RELEVANTES = int(os.environ.get("TOP_N_RELEVANTES", 3))
PATH_MEMORY = os.environ["MEMORY_PATH"]

@tool
def criar_memoria(
    content: str, 
    tags: List[str],
    usuario_concordou: bool = True,
    acao_necessaria: bool = False,
    nome_agente: str = ""
    ) -> str:
    """
    Cria uma memória e salva em um arquivo de texto. 
    O conteúdo da memória é um resumo do que foi identificado, o que o agente fez, e o que o usuário pediu. 
    As tags são palavras-chave relacionadas ao conteúdo da memória, separadas por vírgula.

    Args:
        content (str): O conteúdo da memória.
        tags (List[str]): As tags relacionadas à memória
        usuario_concordou (bool): Indica se o usuário concordou com a memória.
        acao_necessaria (bool): Indica se foi necessária alguma ação para resolver a situação.
        nome_agente (str): O nome do agente que criou a memória.

    Returns:
        str: O caminho do arquivo onde a memória foi salva.
    
    """
    memory = {
        "content": content,
        "tags": tags[:QTDE_TAGS],  # Salvar até {QTDE_TAGS} tags
        "created_at": datetime.now().isoformat(),
        "acao_necessaria": acao_necessaria,
        "usuario_concordou": usuario_concordou,
        "nome_agente": nome_agente
    }
    
    memory_path = os.getenv('MEMORY_PATH')
    if not os.path.exists(memory_path):
        os.makedirs(memory_path)
    
    filename = f"MEMORY_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.txt"
    filepath = os.path.join(memory_path, filename)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(memory, f, indent=4, ensure_ascii=False)
    
    return filepath

@tool
def ler_memoria_similar(tags: List[str]) -> str:
    """
    Lê as memórias salvas e retorna aquelas que possuem tags similares às fornecidas.

    Args:
        tags (List[str]): As tags para buscar memórias similares, listadas em uma lista de palavras-chave.
            Exemplo: ["volume", "echo", "sala"] ou ["cortina", "quarto", "ruído externo"]
    Returns:
        str: As memórias similares encontradas em texto corrido (resumo).
    """
    
    # a relevancia das memórias pode ser determinada pela quantidade de tags similares, ou seja, quanto mais tags em comum, mais relevante é a memória para a situação atual.
    memories = []
    if os.path.exists(PATH_MEMORY):
        for filename in os.listdir(PATH_MEMORY):
            if filename.endswith(".txt") and filename.startswith("MEMORY_"):
                try:
                    with open(os.path.join(PATH_MEMORY, filename), 'r', encoding='utf-8') as f:
                        memory = json.load(f)
                        memory_tags = set(memory.get("tags", []))
                        input_tags = set(tags)
                        common_tags = memory_tags.intersection(input_tags)
                        relevance = len(common_tags)
                        if relevance > 0:
                            memories.append((relevance, memory))
                except Exception as e:
                    print(f"Erro ao ler memória {filename}: {str(e)}")
    
    # Ordenar memórias por relevância e retornar as top N
    memories.sort(key=lambda x: x[0], reverse=True)
    top_memories = [mem[1] for mem in memories[:TOP_N_RELEVANTES]]

    if top_memories:
        return "\n\n".join([f"Memória criada em {mem['created_at']} com tags {', '.join(mem['tags'])}:\n{mem['content']}" for mem in top_memories])


@tool
def ler_preferencias_usuario() -> str:
    """
    Lê as preferências do usuário de um arquivo de texto.

    Returns:
        str: As preferências e perfil do usuário em texto corrido (resumo).
    """
    preferencias_path = os.path.join(PATH_MEMORY, FILE_PREFERENCES_USUARIO)
    if os.path.exists(preferencias_path):
        with open(preferencias_path, 'r', encoding='utf-8') as f:
            preferencias = f.read()
            return preferencias
    else:
        return "Nenhuma preferência do usuário encontrada."


@tool
def atualizar_preferencias_usuario(preferencias: str) -> str:
    """
    Lê as preferências do usuário, atualiza e salva em um arquivo de texto.

    Args:
        preferencias (str): As preferências do usuário atualizada.
    Returns:
        str: As preferências do usuário atualizada em texto corrido (resumo).
    """
    preferencias_path = os.path.join(PATH_MEMORY, FILE_PREFERENCES_USUARIO)
    with open(preferencias_path, 'w', encoding='utf-8') as f:
        f.write(preferencias)

    