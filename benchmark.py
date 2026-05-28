"""
Benchmark - Testes de escalabilidade e coleta de métricas
Compara RingBuffer (O(1)) vs InefficientBuffer (O(n))
"""

import time
import csv
import os
import psutil
from producer import Producer, SensorSimulator
from consumer import Consumer
from ring_buffer import RingBuffer
from inefficient_buffer import InefficientBuffer
from mqtt_client import MQTTSimulator


class MemoryMonitor:
    """Monitora uso de memória do processo."""
    
    def __init__(self):
        """Inicializa monitor."""
        self.process = psutil.Process(os.getpid())
        self.measurements = []
        self.start_memory_mb = 0
        self.peak_memory_mb = 0
    
    def start(self):
        """Registra memória inicial."""
        self.start_memory_mb = self.process.memory_info().rss / (1024 * 1024)
        self.peak_memory_mb = self.start_memory_mb
    
    def measure(self):
        """Mede memória atual."""
        current_mb = self.process.memory_info().rss / (1024 * 1024)
        self.measurements.append(current_mb)
        
        if current_mb > self.peak_memory_mb:
            self.peak_memory_mb = current_mb
        
        return current_mb
    
    def get_stats(self):
        """Retorna estatísticas de memória."""
        if not self.measurements:
            return {}
        
        avg_mb = sum(self.measurements) / len(self.measurements)
        delta_mb = self.peak_memory_mb - self.start_memory_mb
        
        return {
            'start_memory_mb': round(self.start_memory_mb, 2),
            'peak_memory_mb': round(self.peak_memory_mb, 2),
            'avg_memory_mb': round(avg_mb, 2),
            'delta_memory_mb': round(delta_mb, 2)
        }


class Benchmark:
    """Executa benchmarks comparativos."""
    
    def __init__(self, output_dir: str = "metrics"):
        """
        Inicializa benchmark.
        
        Args:
            output_dir: Diretório para salvar métricas
        """
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
        self.scenarios = []
    
    def run_scenario(self, 
                     buffer_type: str,
                     frequency_hz: int,
                     duration_s: float,
                     network_delay_ms: float = 0):
        """
        Executa um cenário de teste.
        
        Args:
            buffer_type: "ring" ou "inefficient"
            frequency_hz: Frequência de produção
            duration_s: Duração em segundos
            network_delay_ms: Latência de rede simulada
        """
        print(f"\n{'='*60}")
        print(f"Cenário: {buffer_type} | {frequency_hz} Hz | {duration_s}s | Delay {network_delay_ms}ms")
        print(f"{'='*60}")
        
        # Cria buffer apropriado
        capacity = int(frequency_hz * duration_s * 1.5)  # 50% margem
        
        if buffer_type == "ring":
            buffer = RingBuffer(capacity)
            buffer_name = "RingBuffer"
        else:
            buffer = InefficientBuffer(capacity)
            buffer_name = "InefficientBuffer"
        
        # Inicializa MQTT simulado
        mqtt = MQTTSimulator(network_delay_ms=network_delay_ms)
        mqtt.connect()
        
        # Cria produtor e consumidor
        producer = Producer(buffer, frequency_hz, duration_s, name=f"Producer-{buffer_type}")
        consumer = Consumer(buffer, mqtt, network_delay_ms, name=f"Consumer-{buffer_type}")
        
        # Monitor de memória
        memory_monitor = MemoryMonitor()
        memory_monitor.start()
        
        # Executa teste
        print(f"Iniciando produtor-consumidor...")
        start_time = time.perf_counter()
        
        producer.start()
        consumer.start()
        
        # Monitora memória periodicamente
        monitor_interval_s = duration_s / 10 if duration_s >= 1 else duration_s / 2
        while producer.is_alive():
            time.sleep(min(0.1, monitor_interval_s))
            memory_monitor.measure()
        
        producer.join()
        time.sleep(0.5)  # Deixa consumidor processar resto
        consumer.stop()
        consumer.join()
        
        elapsed_s = time.perf_counter() - start_time
        
        # Coleta estatísticas
        producer_stats = producer.get_stats()
        consumer_stats = consumer.get_stats()
        memory_stats = memory_monitor.get_stats()
        
        scenario_data = {
            'timestamp': time.time(),
            'buffer_type': buffer_type,
            'buffer_name': buffer_name,
            'frequency_hz': frequency_hz,
            'duration_s': duration_s,
            'network_delay_ms': network_delay_ms,
            'buffer_capacity': capacity,
            'elapsed_time_s': round(elapsed_s, 2),
            **producer_stats,
            **consumer_stats,
            **memory_stats
        }
        
        self.scenarios.append(scenario_data)
        
        # Exibe resultado
        print(f"\nResultado:")
        print(f"  Tempo total: {elapsed_s:.2f}s")
        print(f"  Dados produzidos: {producer_stats.get('data_produced', 0)}")
        print(f"  Dados consumidos: {consumer_stats.get('data_consumed', 0)}")
        print(f"  Latência média: {consumer_stats.get('avg_latency_ms', 0):.2f}ms")
        print(f"  Jitter: {consumer_stats.get('jitter_ms', 0):.4f}ms")
        print(f"  Memória pico: {memory_stats.get('peak_memory_mb', 0):.2f}MB")
        print(f"  Δ Memória: {memory_stats.get('delta_memory_mb', 0):.2f}MB")
        
        return scenario_data
    
    def save_metrics(self):
        """Salva métricas em CSV."""
        if not self.scenarios:
            print("Nenhum cenário executado!")
            return
        
        # Latência
        latencia_file = os.path.join(self.output_dir, "latencia.csv")
        with open(latencia_file, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=[
                'buffer_type', 'frequency_hz', 'network_delay_ms',
                'avg_latency_ms', 'max_latency_ms', 'min_latency_ms', 'jitter_ms'
            ])
            writer.writeheader()
            for scenario in self.scenarios:
                writer.writerow({
                    'buffer_type': scenario['buffer_type'],
                    'frequency_hz': scenario['frequency_hz'],
                    'network_delay_ms': scenario['network_delay_ms'],
                    'avg_latency_ms': scenario.get('avg_latency_ms', 0),
                    'max_latency_ms': scenario.get('max_latency_ms', 0),
                    'min_latency_ms': scenario.get('min_latency_ms', 0),
                    'jitter_ms': scenario.get('jitter_ms', 0)
                })
        
        # Memória (heap)
        heap_file = os.path.join(self.output_dir, "heap.csv")
        with open(heap_file, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=[
                'buffer_type', 'frequency_hz', 'duration_s',
                'start_memory_mb', 'peak_memory_mb', 'avg_memory_mb', 'delta_memory_mb'
            ])
            writer.writeheader()
            for scenario in self.scenarios:
                writer.writerow({
                    'buffer_type': scenario['buffer_type'],
                    'frequency_hz': scenario['frequency_hz'],
                    'duration_s': scenario['duration_s'],
                    'start_memory_mb': scenario.get('start_memory_mb', 0),
                    'peak_memory_mb': scenario.get('peak_memory_mb', 0),
                    'avg_memory_mb': scenario.get('avg_memory_mb', 0),
                    'delta_memory_mb': scenario.get('delta_memory_mb', 0)
                })
        
        # Jitter e throughput
        jitter_file = os.path.join(self.output_dir, "jitter.csv")
        with open(jitter_file, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=[
                'buffer_type', 'frequency_hz', 'duration_s',
                'avg_removal_time_us', 'max_removal_time_us',
                'data_consumed', 'throughput_msg_per_sec'
            ])
            writer.writeheader()
            for scenario in self.scenarios:
                throughput = (scenario.get('data_consumed', 0) / 
                            scenario.get('duration_s', 1)) if scenario.get('duration_s', 0) > 0 else 0
                writer.writerow({
                    'buffer_type': scenario['buffer_type'],
                    'frequency_hz': scenario['frequency_hz'],
                    'duration_s': scenario['duration_s'],
                    'avg_removal_time_us': scenario.get('avg_removal_time_us', 0),
                    'max_removal_time_us': scenario.get('max_removal_time_us', 0),
                    'data_consumed': scenario.get('data_consumed', 0),
                    'throughput_msg_per_sec': round(throughput, 2)
                })
        
        print(f"\n✓ Métricas salvas em:")
        print(f"  - {latencia_file}")
        print(f"  - {heap_file}")
        print(f"  - {jitter_file}")


if __name__ == "__main__":
    benchmark = Benchmark()
    
    # Teste 1: Cenário sem carga
    print("\n" + "="*60)
    print("TESTE 1: Sem carga (100 Hz, 2s, sem delay)")
    print("="*60)
    
    benchmark.run_scenario("ring", frequency_hz=100, duration_s=2, network_delay_ms=0)
    benchmark.run_scenario("inefficient", frequency_hz=100, duration_s=2, network_delay_ms=0)
    
    # Teste 2: Com carga média
    print("\n" + "="*60)
    print("TESTE 2: Carga média (500 Hz, 3s, delay 20ms)")
    print("="*60)
    
    benchmark.run_scenario("ring", frequency_hz=500, duration_s=3, network_delay_ms=20)
    benchmark.run_scenario("inefficient", frequency_hz=500, duration_s=3, network_delay_ms=20)
    
    # Teste 3: Carga pesada
    print("\n" + "="*60)
    print("TESTE 3: Carga pesada (1000 Hz, 5s, delay 50ms)")
    print("="*60)
    
    benchmark.run_scenario("ring", frequency_hz=1000, duration_s=5, network_delay_ms=50)
    benchmark.run_scenario("inefficient", frequency_hz=1000, duration_s=5, network_delay_ms=50)
    
    # Salva métricas
    benchmark.save_metrics()
    
    print("\n" + "="*60)
    print("BENCHMARK COMPLETO!")
    print("="*60)
