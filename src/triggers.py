from datetime import datetime
from datetime import datetime, timedelta

class Trigger:
    def __init__(self, name):
        self.name = name

    def check_condition(self, entity_id: str, old_state: str, new_state: str, timestamp: datetime) -> dict:
        """
        Verifica se o trigger deve disparar.
        
        Args:
            entity_id: ID da entidade que mudou
            old_state: Estado anterior
            new_state: Estado atual
            timestamp: Horário da mudança
            
        Returns:
            dict com 'triggered': bool, 'task_description': str ou None
        """
        raise NotImplementedError("Subclasses devem implementar check_condition")
    

class TemperatureTrigger(Trigger):
    def __init__(self, threshold, comparator):
        super().__init__(name="TemperatureTrigger")
        self.threshold = threshold
        self.comparator = comparator

    def check_condition(self, entity_id: str, old_state: str, new_state: str, timestamp: datetime) -> dict:
        """
        Verifica se houve mudança significativa de temperatura.
        
        Args:
            entity_id: ID da entidade de temperatura
            old_state: Temperatura anterior (string convertida para float)
            new_state: Temperatura atual (string convertida para float)
            timestamp: Horário da mudança
            
        Returns:
            dict com trigger disparado e descrição da tarefa
        """
        try:
            old_temp = float(old_state)
            new_temp = float(new_state)
        except (ValueError, TypeError):
            return {'triggered': False, 'task_description': None}
        
        # Verifica a condição de acordo com o comparador
        condition_met = False
        if self.comparator == 'greater' and new_temp > self.threshold:
            condition_met = True
        elif self.comparator == 'less' and new_temp < self.threshold:
            condition_met = True
        
        if not condition_met:
            return {'triggered': False, 'task_description': None}
        
        # Gera descrição da tarefa
        task_description = f"""
Evento: Mudança de Temperatura detectada

Entidade: {entity_id}
Horário: {timestamp.isoformat()}

Estados:
- Temperatura anterior: {old_temp}°C
- Temperatura atual: {new_temp}°C
- Limiar monitorado: {self.threshold}°C (verificando se {self.comparator})

Ação requeria: Ajustar o conforto térmico da casa conforme necessário.
        """.strip()
        
        return {'triggered': True, 'task_description': task_description}

class JanelaAbertaFechadaTrigger(Trigger):
    def __init__(self, desired_state):
        super().__init__(name="JanelaAbertaFechadaTrigger")
        self.desired_state = desired_state

    def check_condition(self, entity_id: str, old_state: str, new_state: str, timestamp: datetime) -> dict:
        """
        Verifica se a janela mudou para o estado desejado.
        
        Args:
            entity_id: ID da entidade de janela
            old_state: Estado anterior ('open', 'closed', etc)
            new_state: Estado atual ('open', 'closed', etc)
            timestamp: Horário da mudança
            
        Returns:
            dict com trigger disparado e descrição da tarefa
        """
        # Verifica se o novo estado corresponde ao desejado
        # if new_state.lower() != self.desired_state.lower():
        #     return {'triggered': False, 'task_description': None}
        
        # Se a janela já estava nesse estado, não dispara
        if old_state.lower() == new_state.lower():
            return {'triggered': False, 'task_description': None}
        
        # Gera descrição da tarefa
        task_description = f"""
Evento: Mudança de Estado de Janela detectada

Entidade: {entity_id}
Horário: {timestamp.isoformat()}

Estados:
- Estado anterior: {old_state}
- Estado atual: {new_state}

Ação requerida: Processar a mudança de estado da janela e ajustar dispositivos conforme necessário.
        """.strip()
        
        return {'triggered': True, 'task_description': task_description}

class SaiuDeCasaTrigger(Trigger):
    """
    Trigger que dispara quando a pessoa sai de casa por mais de um tempo específico.
    
    Fluxo:
    1. Detecta saída (estado "on" → "off")
    2. Aguarda o tempo especificado
    3. Dispara uma única vez dentro de uma margem temporal
    4. Reseta ao chegar em casa (estado "off" → "on")
    """
    
    def __init__(self, minutos_decorridos=60, margem_minutos=5):
        """
        Args:
            minutos_decorridos: Tempo em minutos até disparar (padrão: 60)
            margem_minutos: Janela temporal para capturar o disparo (padrão: 5)
        """
        super().__init__(name="SaiuDeCasaTrigger")
        self.minutos_decorridos = minutos_decorridos
        self.margem_minutos = margem_minutos
        self.saida_timestamp = None
        self.triggered_timestamp = None

    def check_condition(self, entity_id: str, old_state: str, new_state: str, timestamp: datetime) -> dict:
        """
        Verifica se disparou após tempo decorrido.
        
        Args:
            entity_id: ID da entidade (input_boolean.geral_status_em_casa)
            old_state: Estado anterior ('on' ou 'off')
            new_state: Estado atual ('on' ou 'off')
            timestamp: Horário da mudança
            
        Returns:
            dict com trigger disparado e descrição da tarefa
        """
        
        # Se voltou pra casa (chegou em casa)
        if new_state == "on":
            self.saida_timestamp = None
            self.triggered_timestamp = None
            return {'triggered': False, 'task_description': None}
        
        # Se acabou de sair
        if old_state == "on" and new_state == "off":
            self.saida_timestamp = timestamp
            self.triggered_timestamp = None
            return {'triggered': False, 'task_description': None}
        
        # Se já disparou uma vez, não dispara novamente
        if self.triggered_timestamp is not None:
            return {'triggered': False, 'task_description': None}
        
        # Verifica o tempo decorrido
        if new_state == "off" and self.saida_timestamp:
            tempo_decorrido = (timestamp - self.saida_timestamp).total_seconds() / 60
            
            # Dispara apenas na margem temporal especificada
            # (ex: entre 60 e 65 minutos)
            if self.minutos_decorridos <= tempo_decorrido < (self.minutos_decorridos + self.margem_minutos):
                self.triggered_timestamp = timestamp
                
                task_description = f"""
Evento: Saiu de casa há {self.minutos_decorridos} minutos

Horário de saída: {self.saida_timestamp.isoformat()}
Tempo decorrido: {tempo_decorrido:.1f} minutos
Timestamp do trigger: {timestamp.isoformat()}

Processar saída de casa e ajustar dispositivos conforme necessário.
                """.strip()
                
                return {'triggered': True, 'task_description': task_description}
        
        return {'triggered': False, 'task_description': None}