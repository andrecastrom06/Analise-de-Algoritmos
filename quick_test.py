#!/usr/bin/env python3
"""
Quick Test Script - Validação rápida do sistema
Executa testes básicos em ~30 segundos
"""

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from ring_buffer import RingBuffer
from inefficient_buffer import InefficientBuffer
from producer import Producer
from consumer import Consumer
from mqtt_client import MQTTSimulator


def quick_test():
    """Executa teste rápido."""
    
    print("\n" + "="*70)
    print("  TESTE RÁPIDO DO SISTEMA DE TELEMETRIA")
    print("="*70 + "\n")
    
    # 1. Teste de Buffer
    print("1️⃣  TESTE DE BUFFERS")
    print("-" * 70)
    
    rb = RingBuffer(10)
    for i in range(15):
        rb.push(f"data_{i}")
    
    print(f"✓ RingBuffer: {rb.get_size()} elementos armazenados")
    
    ib = InefficientBuffer(10)
    for i in range(15):
        ib.push(f"data_{i}")
    
    print(f"✓ InefficientBuffer: {ib.get_size()} elementos armazenados")
    
    # 2. Teste Produtor-Consumidor
    print("\n2️⃣  TESTE PRODUTOR-CONSUMIDOR (RingBuffer)")
    print("-" * 70)
    
    rb2 = RingBuffer(capacity=100)
    mqtt = MQTTSimulator(network_delay_ms=10)
    mqtt.connect()
    
    producer = Producer(rb2, frequency_hz=50, duration_s=1)
    consumer = Consumer(rb2, mqtt, network_delay_ms=10)
    
    print("Executando por 1 segundo...")
    start = time.time()
    
    producer.start()
    consumer.start()
    producer.join()
    time.sleep(0.2)
    consumer.stop()
    consumer.join()
    
    elapsed = time.time() - start
    
    prod_stats = producer.get_stats()
    cons_stats = consumer.get_stats()
    
    print(f"✓ Produtor: {prod_stats.get('data_produced', 0)} dados em {elapsed:.2f}s")
    print(f"✓ Consumidor: {cons_stats.get('data_consumed', 0)} dados processados")
    print(f"✓ Latência média: {cons_stats.get('avg_latency_ms', 0):.2f}ms")
    print(f"✓ Jitter: {cons_stats.get('jitter_ms', 0):.4f}ms")
    
    # 3. Teste com InefficientBuffer
    print("\n3️⃣  TESTE PRODUTOR-CONSUMIDOR (InefficientBuffer)")
    print("-" * 70)
    
    ib2 = InefficientBuffer(capacity=100)
    mqtt2 = MQTTSimulator(network_delay_ms=10)
    mqtt2.connect()
    
    producer2 = Producer(ib2, frequency_hz=50, duration_s=1, name="Producer-IB")
    consumer2 = Consumer(ib2, mqtt2, network_delay_ms=10, name="Consumer-IB")
    
    print("Executando por 1 segundo...")
    start = time.time()
    
    producer2.start()
    consumer2.start()
    producer2.join()
    time.sleep(0.2)
    consumer2.stop()
    consumer2.join()
    
    elapsed = time.time() - start
    
    prod_stats2 = producer2.get_stats()
    cons_stats2 = consumer2.get_stats()
    
    print(f"✓ Produtor: {prod_stats2.get('data_produced', 0)} dados em {elapsed:.2f}s")
    print(f"✓ Consumidor: {cons_stats2.get('data_consumed', 0)} dados processados")
    print(f"✓ Latência média: {cons_stats2.get('avg_latency_ms', 0):.2f}ms")
    print(f"✓ Jitter: {cons_stats2.get('jitter_ms', 0):.4f}ms")
    
    # 4. Comparação
    print("\n4️⃣  COMPARAÇÃO")
    print("-" * 70)
    
    rb_latency = cons_stats.get('avg_latency_ms', 0)
    ib_latency = cons_stats2.get('avg_latency_ms', 0)
    
    if rb_latency < ib_latency:
        diff = ((ib_latency - rb_latency) / rb_latency) * 100
        print(f"✓ RingBuffer é {diff:.1f}% mais rápido!")
    
    rb_jitter = cons_stats.get('jitter_ms', 0)
    ib_jitter = cons_stats2.get('jitter_ms', 0)
    
    if rb_jitter < ib_jitter:
        diff = ((ib_jitter - rb_jitter) / rb_jitter) * 100 if rb_jitter > 0 else 0
        print(f"✓ RingBuffer tem {diff:.1f}% menos jitter!")
    
    print("\n" + "="*70)
    print("  ✅ TESTE RÁPIDO CONCLUÍDO COM SUCESSO!")
    print("="*70)
    print("\nPróximos passos:")
    print("  1. Execute 'python main.py' para menu completo")
    print("  2. Execute 'python benchmark.py' para teste profundo")
    print("  3. Execute 'python plot_graphs.py' para gerar gráficos")
    print("  4. Consulte README.md para mais informações\n")


if __name__ == "__main__":
    try:
        quick_test()
    except KeyboardInterrupt:
        print("\n\n⚠️  Teste interrompido!")
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        import traceback
        traceback.print_exc()
