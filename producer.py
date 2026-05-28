"""
Produtor - Captura dados continuamente e insere no buffer
Thread responsável por ler sensor e alimentar o buffer
"""

import threading
import time
import random
from typing import Union
from ring_buffer import RingBuffer
from inefficient_buffer import InefficientBuffer


class SensorSimulator:
    """Simula um sensor de temperatura IoT."""
    
    def __init__(self, base_temp: float = 25.0, max_variance: float = 5.0):
        """
        Inicializa simulador de sensor.
        
        Args:
            base_temp: Temperatura base em °C
            max_variance: Variação máxima da temperatura
        """
        self.base_temp = base_temp
        self.max_variance = max_variance
        self.reading_count = 0
    
    def read(self) -> dict:
        """
        Lê valor do sensor.
        
        Returns:
            Dict com temperatura, timestamp e ID
        """
        self.reading_count += 1
        temperature = self.base_temp + random.uniform(-self.max_variance, self.max_variance)
        
        return {
            'id': self.reading_count,
            'temperature': round(temperature, 2),
            'timestamp_ns': time.perf_counter_ns(),
            'value': temperature
        }


class Producer(threading.Thread):
    """
    Produtor de dados - executa em thread separada.
    Lê sensor continuamente e insere no buffer.
    """
    
    def __init__(self, buffer: Union[RingBuffer, InefficientBuffer], 
                 frequency_hz: int = 1000, 
                 duration_s: float = 10.0,
                 name: str = "Producer"):
        """
        Inicializa produtor.
        
        Args:
            buffer: Buffer (RingBuffer ou InefficientBuffer)
            frequency_hz: Frequência de leitura em Hz
            duration_s: Duração da coleta em segundos
            name: Nome da thread
        """
        super().__init__(name=name, daemon=True)
        
        self.buffer = buffer
        self.frequency_hz = frequency_hz
        self.duration_s = duration_s
        self.period_ns = int(1e9 / frequency_hz)  # Período em nanosegundos
        
        self.sensor = SensorSimulator()
        self.running = False
        self.data_produced = 0
        self.total_insertion_time_ns = 0
        self.insertion_times = []
        
    def run(self):
        """Executa thread produtora."""
        self.running = True
        print(f"[{self.name}] Iniciando produção a {self.frequency_hz} Hz por {self.duration_s}s")
        
        start_time = time.perf_counter_ns()
        deadline = start_time + int(self.duration_s * 1e9)
        
        while self.running:
            current_time = time.perf_counter_ns()
            
            if current_time >= deadline:
                break
            
            # Lê sensor
            data = self.sensor.read()
            
            # Insere no buffer
            self.buffer.push(data)
            self.data_produced += 1
            
            # Registra tempo de inserção
            insertion_time = self.buffer.insertion_time_ns
            self.insertion_times.append(insertion_time)
            self.total_insertion_time_ns += insertion_time
            
            # Respeita frequência
            sleep_time_ns = self.period_ns - (time.perf_counter_ns() - current_time)
            if sleep_time_ns > 0:
                time.sleep(sleep_time_ns / 1e9)
        
        self.running = False
        elapsed = (time.perf_counter_ns() - start_time) / 1e9
        print(f"[{self.name}] Finalizado. Produziu {self.data_produced} dados em {elapsed:.2f}s")
    
    def stop(self):
        """Para a thread produtora."""
        self.running = False
    
    def get_stats(self):
        """Retorna estatísticas do produtor."""
        if not self.insertion_times:
            return {}
        
        insertion_times_us = [t / 1000 for t in self.insertion_times]  # Converter para μs
        
        return {
            'data_produced': self.data_produced,
            'avg_insertion_time_us': sum(insertion_times_us) / len(insertion_times_us),
            'max_insertion_time_us': max(insertion_times_us),
            'min_insertion_time_us': min(insertion_times_us),
            'total_insertion_time_us': sum(insertion_times_us)
        }

