"""
Cliente MQTT - Publicador de Telemetria
Usa paho-mqtt para comunicação com broker local
"""

import paho.mqtt.client as mqtt
import time
from typing import Callable


class MQTTClient:
    """Cliente MQTT para publicar dados de telemetria."""
    
    def __init__(self, broker_host: str = "localhost", broker_port: int = 1883, client_id: str = "telemetria_client"):
        """
        Inicializa cliente MQTT.
        
        Args:
            broker_host: Host do broker MQTT
            broker_port: Porta do broker MQTT
            client_id: ID único do cliente
        """
        self.broker_host = broker_host
        self.broker_port = broker_port
        self.client_id = client_id
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, client_id=client_id)
        self.connected = False
        self.publish_count = 0
        self.last_publish_time_ns = 0
        
        # Callbacks
        self.client.on_connect = self._on_connect
        self.client.on_disconnect = self._on_disconnect
        self.client.on_publish = self._on_publish
    
    def _on_connect(self, client, userdata, flags, rc):
        """Callback de conexão."""
        if rc == 0:
            self.connected = True
            print(f"[MQTT] Conectado ao broker {self.broker_host}:{self.broker_port}")
        else:
            print(f"[MQTT] Falha na conexão. Código: {rc}")
    
    def _on_disconnect(self, client, userdata, rc):
        """Callback de desconexão."""
        self.connected = False
        print(f"[MQTT] Desconectado do broker (código: {rc})")
    
    def _on_publish(self, client, userdata, mid):
        """Callback de publicação."""
        pass
    
    def connect(self):
        """Conecta ao broker MQTT."""
        try:
            self.client.connect(self.broker_host, self.broker_port, keepalive=60)
            self.client.loop_start()
            time.sleep(0.5)  # Aguarda conexão
        except Exception as e:
            print(f"[MQTT] Erro ao conectar: {e}")
    
    def disconnect(self):
        """Desconecta do broker MQTT."""
        self.client.loop_stop()
        self.client.disconnect()
    
    def publish(self, topic: str, payload, qos: int = 0, retain: bool = False):
        """
        Publica mensagem no tópico.
        
        Args:
            topic: Tópico MQTT
            payload: Dados a publicar (será convertido para string)
            qos: Nível de qualidade (0, 1 ou 2)
            retain: Manter última mensagem no broker
            
        Returns:
            Tempo de publicação em nanosegundos
        """
        start = time.perf_counter_ns()
        
        if not self.connected:
            return 0
        
        try:
            if not isinstance(payload, str):
                payload = str(payload)
            
            self.client.publish(topic, payload, qos=qos, retain=retain)
            self.publish_count += 1
        except Exception as e:
            print(f"[MQTT] Erro ao publicar: {e}")
        
        self.last_publish_time_ns = time.perf_counter_ns() - start
        return self.last_publish_time_ns
    
    def is_connected(self):
        """Verifica se está conectado."""
        return self.connected
    
    def get_publish_count(self):
        """Retorna número de mensagens publicadas."""
        return self.publish_count


class MQTTSimulator:
    """Simulador de MQTT com delay de rede artificial."""
    
    def __init__(self, network_delay_ms: float = 0):
        """
        Inicializa simulador.
        
        Args:
            network_delay_ms: Delay artificial em milissegundos
        """
        self.network_delay_ms = network_delay_ms
        self.publish_count = 0
        self.last_publish_time_ns = 0
        self.connected = True
    
    def connect(self):
        """Simula conexão."""
        self.connected = True
        print(f"[MQTT Simulator] Conectado (delay: {self.network_delay_ms}ms)")
    
    def disconnect(self):
        """Simula desconexão."""
        self.connected = False
    
    def publish(self, topic: str, payload):
        """
        Simula publicação com delay.
        
        Args:
            topic: Tópico MQTT
            payload: Dados a publicar
            
        Returns:
            Tempo de publicação em nanosegundos
        """
        start = time.perf_counter_ns()
        
        # Simula latência de rede
        if self.network_delay_ms > 0:
            time.sleep(self.network_delay_ms / 1000.0)
        
        self.publish_count += 1
        self.last_publish_time_ns = time.perf_counter_ns() - start
        
        return self.last_publish_time_ns
    
    def is_connected(self):
        """Verifica se está conectado."""
        return self.connected


if __name__ == "__main__":
    # Teste com simulador
    print("=== Teste MQTT Simulator ===\n")
    
    mqtt_sim = MQTTSimulator(network_delay_ms=50)
    mqtt_sim.connect()
    
    print("Publicando 5 mensagens com delay de 50ms...")
    for i in range(5):
        elapsed_ns = mqtt_sim.publish(f"telemetria/sensor_{i}", f"temperatura: {20+i}°C")
        elapsed_ms = elapsed_ns / 1_000_000
        print(f"  Publicação {i+1}: {elapsed_ms:.2f}ms")
    
    print(f"\nTotal de publicações: {mqtt_sim.publish_count}")
    mqtt_sim.disconnect()
