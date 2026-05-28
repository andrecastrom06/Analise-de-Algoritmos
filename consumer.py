"""
Consumidor - Remove dados do buffer e envia via MQTT
Thread responsável por transmitir dados e simular gargalo de rede
"""

import threading
import time
import json
from typing import Union, Optional
from ring_buffer import RingBuffer
from inefficient_buffer import InefficientBuffer
from mqtt_client import MQTTSimulator


class Consumer(threading.Thread):
    """
    Consumidor de dados - executa em thread separada.
    Remove dados do buffer e envia via MQTT com latência simulada.
    """
    
    def __init__(self, 
                 buffer: Union[RingBuffer, InefficientBuffer],
                 mqtt_client: MQTTSimulator,
                 network_delay_ms: float = 0,
                 topic: str = "telemetria/dados",
                 name: str = "Consumer"):
        """
        Inicializa consumidor.
        
        Args:
            buffer: Buffer (RingBuffer ou InefficientBuffer)
            mqtt_client: Cliente MQTT para publicar
            network_delay_ms: Latência de rede simulada em ms
            topic: Tópico MQTT para publicar
            name: Nome da thread
        """
        super().__init__(name=name, daemon=True)
        
        self.buffer = buffer
        self.mqtt_client = mqtt_client
        self.network_delay_ms = network_delay_ms
        self.topic = topic
        
        self.running = False
        self.data_consumed = 0
        self.total_removal_time_ns = 0
        self.total_publish_time_ns = 0
        self.removal_times = []
        self.publish_times = []
        self.latencies = []  # E2E latency (producer -> consumer)
        
    def run(self):
        """Executa thread consumidora."""
        self.running = True
        print(f"[{self.name}] Iniciando consumo (delay de rede: {self.network_delay_ms}ms)")
        
        while self.running:
            if self.buffer.is_empty():
                time.sleep(0.001)  # Evita busy-waiting
                continue
            
            # Remove do buffer
            data = self.buffer.pop()
            removal_time = self.buffer.removal_time_ns
            self.removal_times.append(removal_time)
            self.total_removal_time_ns += removal_time
            
            if data is None:
                continue
            
            # Calcula latência E2E
            current_time_ns = time.perf_counter_ns()
            producer_timestamp_ns = data.get('timestamp_ns', current_time_ns)
            e2e_latency_ns = current_time_ns - producer_timestamp_ns
            self.latencies.append(e2e_latency_ns)
            
            # Publica via MQTT (com delay simulado)
            publish_time = self._publish_data(data)
            self.publish_times.append(publish_time)
            self.total_publish_time_ns += publish_time
            
            self.data_consumed += 1
    
    def _publish_data(self, data: dict) -> int:
        """
        Publica dado via MQTT.
        
        Args:
            data: Dado a publicar
            
        Returns:
            Tempo de publicação em nanosegundos
        """
        # Simula latência de rede
        if self.network_delay_ms > 0:
            time.sleep(self.network_delay_ms / 1000.0)
        
        start = time.perf_counter_ns()
        
        # Formata e publica
        payload = json.dumps({
            'id': data.get('id'),
            'temperature': data.get('temperature'),
            'timestamp_producer_ns': data.get('timestamp_ns'),
            'timestamp_consumer_ns': time.perf_counter_ns()
        })
        
        self.mqtt_client.publish(self.topic, payload)
        
        return time.perf_counter_ns() - start
    
    def stop(self):
        """Para a thread consumidora."""
        self.running = False
    
    def get_stats(self):
        """Retorna estatísticas do consumidor."""
        if not self.removal_times:
            return {}
        
        removal_times_us = [t / 1000 for t in self.removal_times]  # Converter para μs
        publish_times_ms = [t / 1_000_000 for t in self.publish_times]  # Converter para ms
        latencies_ms = [l / 1_000_000 for l in self.latencies]  # Converter para ms
        
        # Calcular jitter (variância de latência)
        if latencies_ms:
            avg_latency = sum(latencies_ms) / len(latencies_ms)
            jitter = sum((l - avg_latency) ** 2 for l in latencies_ms) / len(latencies_ms)
            jitter = jitter ** 0.5  # Desvio padrão
        else:
            jitter = 0
        
        return {
            'data_consumed': self.data_consumed,
            'avg_removal_time_us': sum(removal_times_us) / len(removal_times_us) if removal_times_us else 0,
            'max_removal_time_us': max(removal_times_us) if removal_times_us else 0,
            'min_removal_time_us': min(removal_times_us) if removal_times_us else 0,
            'avg_publish_time_ms': sum(publish_times_ms) / len(publish_times_ms) if publish_times_ms else 0,
            'avg_latency_ms': sum(latencies_ms) / len(latencies_ms) if latencies_ms else 0,
            'max_latency_ms': max(latencies_ms) if latencies_ms else 0,
            'min_latency_ms': min(latencies_ms) if latencies_ms else 0,
            'jitter_ms': jitter,
            'total_removal_time_us': sum(removal_times_us) if removal_times_us else 0,
        }

