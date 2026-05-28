#!/usr/bin/env python3
"""
Main Orchestrator - Executa projeto completo de telemetria
Coordena produtor-consumidor, benchmark e geração de gráficos
"""

import sys
import time
from pathlib import Path

# Adiciona diretório atual ao path
sys.path.insert(0, str(Path(__file__).parent))

from producer import Producer
from consumer import Consumer
from ring_buffer import RingBuffer
from inefficient_buffer import InefficientBuffer
from mqtt_client import MQTTSimulator
from benchmark import Benchmark
from plot_graphs import GraphGenerator


def print_header(text: str):
    """Imprime cabeçalho formatado."""
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70 + "\n")


def run_producer_consumer_test():
    """Executa teste produtor-consumidor simples."""
    print_header("TESTE 2: Produtor-Consumidor Simples (10 Hz, 1s)")
    
    # RingBuffer
    print("2.1 - RingBuffer...")
    rb = RingBuffer(capacity=50)
    mqtt = MQTTSimulator(network_delay_ms=5)
    mqtt.connect()
    
    producer = Producer(rb, frequency_hz=10, duration_s=1, name="Producer-RB")
    consumer = Consumer(rb, mqtt, network_delay_ms=5, name="Consumer-RB")
    
    producer.start()
    consumer.start()
    producer.join()
    time.sleep(0.3)
    consumer.stop()
    consumer.join()
    
    prod_stats = producer.get_stats()
    cons_stats = consumer.get_stats()
    
    print(f"  Produtor: {prod_stats.get('data_produced', 0)} dados")
    print(f"  Consumidor: {cons_stats.get('data_consumed', 0)} dados")
    print(f"  Latência média: {cons_stats.get('avg_latency_ms', 0):.2f}ms")
    
    # InefficientBuffer
    print("\n2.2 - InefficientBuffer...")
    ib = InefficientBuffer(capacity=50)
    mqtt2 = MQTTSimulator(network_delay_ms=5)
    mqtt2.connect()
    
    producer2 = Producer(ib, frequency_hz=10, duration_s=1, name="Producer-IB")
    consumer2 = Consumer(ib, mqtt2, network_delay_ms=5, name="Consumer-IB")
    
    producer2.start()
    consumer2.start()
    producer2.join()
    time.sleep(0.3)
    consumer2.stop()
    consumer2.join()
    
    prod_stats2 = producer2.get_stats()
    cons_stats2 = consumer2.get_stats()
    
    print(f"  Produtor: {prod_stats2.get('data_produced', 0)} dados")
    print(f"  Consumidor: {cons_stats2.get('data_consumed', 0)} dados")
    print(f"  Latência média: {cons_stats2.get('avg_latency_ms', 0):.2f}ms")


def run_benchmark():
    """Executa benchmark completo."""
    print_header("TESTE 3: Benchmark Completo")
    
    benchmark = Benchmark()
    
    # Cenário 1: Sem carga
    print("\n3.1 - Cenário 1: Sem Carga (100 Hz, 2s, 0ms delay)")
    benchmark.run_scenario("ring", frequency_hz=100, duration_s=2, network_delay_ms=0)
    benchmark.run_scenario("inefficient", frequency_hz=100, duration_s=2, network_delay_ms=0)
    
    # Cenário 2: Carga média
    print("\n3.2 - Cenário 2: Carga Média (500 Hz, 3s, 20ms delay)")
    benchmark.run_scenario("ring", frequency_hz=500, duration_s=3, network_delay_ms=20)
    benchmark.run_scenario("inefficient", frequency_hz=500, duration_s=3, network_delay_ms=20)
    
    # Cenário 3: Carga pesada
    print("\n3.3 - Cenário 3: Carga Pesada (1000 Hz, 5s, 50ms delay)")
    benchmark.run_scenario("ring", frequency_hz=1000, duration_s=5, network_delay_ms=50)
    benchmark.run_scenario("inefficient", frequency_hz=1000, duration_s=5, network_delay_ms=50)
    
    # Salva métricas
    print("\n3.4 - Salvando métricas em CSV...")
    benchmark.save_metrics()
    
    return True


def generate_graphs():
    """Gera gráficos a partir dos CSVs."""
    print_header("TESTE 4: Geração de Gráficos")
    
    generator = GraphGenerator()
    generator.generate_all()


def main():
    """Função principal."""
    print_header("SISTEMA DE TELEMETRIA COM BUFFER CIRCULAR")
    print("Projeto Comparativo: O(n) vs O(1)")
    print("Python | MQTT | Produtor-Consumidor | Benchmarking\n")
    
    # Menu
    print("Opções:")
    print("  1 - Teste produtor-consumidor")
    print("  2 - Benchmark completo")
    print("  3 - Gerar gráficos")
    print("  4 - Executar tudo (1+2+3)")
    print("  0 - Sair\n")
    
    choice = input("Escolha uma opção (0-4): ").strip()
    
    try:
        if choice == "1":
            run_producer_consumer_test()
        
        elif choice == "2":
            run_benchmark()
        
        elif choice == "3":
            generate_graphs()
        
        elif choice == "4":
            run_producer_consumer_test()
            
            proceed = input("\nProsseguir com benchmark? (s/n): ").strip().lower()
            if proceed == 's':
                run_benchmark()
                
                proceed2 = input("\nGerar gráficos? (s/n): ").strip().lower()
                if proceed2 == 's':
                    generate_graphs()
        
        elif choice == "0":
            print("Saindo...")
            return
        
        else:
            print("Opção inválida!")
            return
        
        print_header("TESTE CONCLUÍDO COM SUCESSO!")
    
    except KeyboardInterrupt:
        print("\n\nTeste interrompido pelo usuário.")
    except Exception as e:
        print(f"\n✗ Erro: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
