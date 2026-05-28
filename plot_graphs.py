"""
Gerador de Gráficos - Visualiza resultados dos benchmarks
Cria gráficos de latência, memória, jitter e throughput
"""

import matplotlib.pyplot as plt
import pandas as pd
import os


class GraphGenerator:
    """Gera gráficos a partir de dados CSV."""
    
    def __init__(self, metrics_dir: str = "metrics", output_dir: str = "graficos"):
        """
        Inicializa gerador de gráficos.
        
        Args:
            metrics_dir: Diretório com arquivos CSV
            output_dir: Diretório para salvar gráficos
        """
        self.metrics_dir = metrics_dir
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
        self.latencia_df = None
        self.heap_df = None
        self.jitter_df = None
    
    def load_data(self):
        """Carrega dados dos CSV."""
        latencia_file = os.path.join(self.metrics_dir, "latencia.csv")
        heap_file = os.path.join(self.metrics_dir, "heap.csv")
        jitter_file = os.path.join(self.metrics_dir, "jitter.csv")
        
        if os.path.exists(latencia_file):
            self.latencia_df = pd.read_csv(latencia_file)
            print(f"✓ Carregado: {latencia_file}")
        else:
            print(f"✗ Arquivo não encontrado: {latencia_file}")
        
        if os.path.exists(heap_file):
            self.heap_df = pd.read_csv(heap_file)
            print(f"✓ Carregado: {heap_file}")
        else:
            print(f"✗ Arquivo não encontrado: {heap_file}")
        
        if os.path.exists(jitter_file):
            self.jitter_df = pd.read_csv(jitter_file)
            print(f"✓ Carregado: {jitter_file}")
        else:
            print(f"✗ Arquivo não encontrado: {jitter_file}")
    
    def plot_latencia(self):
        """Gera gráfico de latência."""
        if self.latencia_df is None:
            print("Dados de latência não carregados!")
            return
        
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        fig.suptitle('Análise de Latência: RingBuffer (O(1)) vs InefficientBuffer (O(n))', 
                     fontsize=16, fontweight='bold')
        
        # Latência média vs frequência
        ax1 = axes[0, 0]
        for buf_type in self.latencia_df['buffer_type'].unique():
            data = self.latencia_df[self.latencia_df['buffer_type'] == buf_type]
            ax1.plot(data['frequency_hz'], data['avg_latency_ms'], 
                    marker='o', label=buf_type, linewidth=2)
        
        ax1.set_xlabel('Frequência (Hz)')
        ax1.set_ylabel('Latência Média (ms)')
        ax1.set_title('Latência Média vs Frequência')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Latência máxima vs frequência
        ax2 = axes[0, 1]
        for buf_type in self.latencia_df['buffer_type'].unique():
            data = self.latencia_df[self.latencia_df['buffer_type'] == buf_type]
            ax2.plot(data['frequency_hz'], data['max_latency_ms'], 
                    marker='s', label=buf_type, linewidth=2)
        
        ax2.set_xlabel('Frequência (Hz)')
        ax2.set_ylabel('Latência Máxima (ms)')
        ax2.set_title('Latência Máxima vs Frequência')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        # Jitter vs frequência
        ax3 = axes[1, 0]
        for buf_type in self.latencia_df['buffer_type'].unique():
            data = self.latencia_df[self.latencia_df['buffer_type'] == buf_type]
            ax3.plot(data['frequency_hz'], data['jitter_ms'], 
                    marker='^', label=buf_type, linewidth=2)
        
        ax3.set_xlabel('Frequência (Hz)')
        ax3.set_ylabel('Jitter (ms)')
        ax3.set_title('Jitter vs Frequência (Variância de Latência)')
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        
        # Box plot de latência por tipo de buffer
        ax4 = axes[1, 1]
        data_to_plot = []
        labels = []
        for buf_type in self.latencia_df['buffer_type'].unique():
            data = self.latencia_df[self.latencia_df['buffer_type'] == buf_type]
            # Criar dados fictícios com média e máxima para visualizar
            latencies = []
            for _, row in data.iterrows():
                latencies.extend([row['avg_latency_ms']] * 5 + [row['max_latency_ms']])
            data_to_plot.append(latencies)
            labels.append(buf_type)
        
        ax4.boxplot(data_to_plot, labels=labels)
        ax4.set_ylabel('Latência (ms)')
        ax4.set_title('Distribuição de Latência por Tipo')
        ax4.grid(True, alpha=0.3, axis='y')
        
        plt.tight_layout()
        output_file = os.path.join(self.output_dir, "latencia.png")
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"✓ Gráfico salvo: {output_file}")
        plt.close()
    
    def plot_heap(self):
        """Gera gráfico de memória (heap)."""
        if self.heap_df is None:
            print("Dados de heap não carregados!")
            return
        
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        fig.suptitle('Análise de Memória: RingBuffer vs InefficientBuffer', 
                     fontsize=16, fontweight='bold')
        
        # Memória pico vs frequência
        ax1 = axes[0, 0]
        for buf_type in self.heap_df['buffer_type'].unique():
            data = self.heap_df[self.heap_df['buffer_type'] == buf_type]
            ax1.plot(data['frequency_hz'], data['peak_memory_mb'], 
                    marker='o', label=buf_type, linewidth=2)
        
        ax1.set_xlabel('Frequência (Hz)')
        ax1.set_ylabel('Memória Pico (MB)')
        ax1.set_title('Memória Pico vs Frequência')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Delta memória vs frequência (crescimento)
        ax2 = axes[0, 1]
        for buf_type in self.heap_df['buffer_type'].unique():
            data = self.heap_df[self.heap_df['buffer_type'] == buf_type]
            ax2.plot(data['frequency_hz'], data['delta_memory_mb'], 
                    marker='s', label=buf_type, linewidth=2)
        
        ax2.set_xlabel('Frequência (Hz)')
        ax2.set_ylabel('Δ Memória (MB)')
        ax2.set_title('Crescimento de Memória vs Frequência (O(n) deve crescer mais)')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        # Memória média vs duração
        ax3 = axes[1, 0]
        for buf_type in self.heap_df['buffer_type'].unique():
            data = self.heap_df[self.heap_df['buffer_type'] == buf_type]
            ax3.plot(data['duration_s'], data['avg_memory_mb'], 
                    marker='^', label=buf_type, linewidth=2)
        
        ax3.set_xlabel('Duração (s)')
        ax3.set_ylabel('Memória Média (MB)')
        ax3.set_title('Memória Média vs Duração')
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        
        # Comparação de crescimento
        ax4 = axes[1, 1]
        x = range(len(self.heap_df))
        width = 0.35
        
        ring_data = self.heap_df[self.heap_df['buffer_type'] == 'ring']['delta_memory_mb'].values
        ineff_data = self.heap_df[self.heap_df['buffer_type'] == 'inefficient']['delta_memory_mb'].values
        
        if len(ring_data) > 0 and len(ineff_data) > 0:
            x_pos = range(len(ring_data))
            ax4.bar([i - width/2 for i in x_pos], ring_data, width, label='ring', alpha=0.8)
            ax4.bar([i + width/2 for i in x_pos], ineff_data, width, label='inefficient', alpha=0.8)
            ax4.set_xlabel('Cenário')
            ax4.set_ylabel('Δ Memória (MB)')
            ax4.set_title('Comparação: Crescimento de Memória por Cenário')
            ax4.legend()
            ax4.grid(True, alpha=0.3, axis='y')
        
        plt.tight_layout()
        output_file = os.path.join(self.output_dir, "heap.png")
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"✓ Gráfico salvo: {output_file}")
        plt.close()
    
    def plot_jitter(self):
        """Gera gráfico de jitter e throughput."""
        if self.jitter_df is None:
            print("Dados de jitter não carregados!")
            return
        
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        fig.suptitle('Análise de Jitter e Throughput', 
                     fontsize=16, fontweight='bold')
        
        # Tempo de remoção vs frequência
        ax1 = axes[0, 0]
        for buf_type in self.jitter_df['buffer_type'].unique():
            data = self.jitter_df[self.jitter_df['buffer_type'] == buf_type]
            ax1.plot(data['frequency_hz'], data['avg_removal_time_us'], 
                    marker='o', label=buf_type, linewidth=2)
        
        ax1.set_xlabel('Frequência (Hz)')
        ax1.set_ylabel('Tempo de Remoção Médio (μs)')
        ax1.set_title('Tempo de Remoção: O(1) vs O(n)')
        ax1.set_yscale('log')  # Escala logarítmica para melhor visualização
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Tempo máximo de remoção vs frequência
        ax2 = axes[0, 1]
        for buf_type in self.jitter_df['buffer_type'].unique():
            data = self.jitter_df[self.jitter_df['buffer_type'] == buf_type]
            ax2.plot(data['frequency_hz'], data['max_removal_time_us'], 
                    marker='s', label=buf_type, linewidth=2)
        
        ax2.set_xlabel('Frequência (Hz)')
        ax2.set_ylabel('Tempo de Remoção Máximo (μs)')
        ax2.set_title('Tempo Máximo de Remoção (pior caso O(n))')
        ax2.set_yscale('log')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        # Throughput vs frequência
        ax3 = axes[1, 0]
        for buf_type in self.jitter_df['buffer_type'].unique():
            data = self.jitter_df[self.jitter_df['buffer_type'] == buf_type]
            ax3.plot(data['frequency_hz'], data['throughput_msg_per_sec'], 
                    marker='^', label=buf_type, linewidth=2)
        
        ax3.set_xlabel('Frequência (Hz)')
        ax3.set_ylabel('Throughput (msg/s)')
        ax3.set_title('Throughput vs Frequência')
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        
        # Dados consumidos vs frequência
        ax4 = axes[1, 1]
        for buf_type in self.jitter_df['buffer_type'].unique():
            data = self.jitter_df[self.jitter_df['buffer_type'] == buf_type]
            ax4.plot(data['frequency_hz'], data['data_consumed'], 
                    marker='d', label=buf_type, linewidth=2)
        
        ax4.set_xlabel('Frequência (Hz)')
        ax4.set_ylabel('Dados Consumidos')
        ax4.set_title('Volume de Dados Consumidos')
        ax4.legend()
        ax4.grid(True, alpha=0.3)
        
        plt.tight_layout()
        output_file = os.path.join(self.output_dir, "jitter.png")
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"✓ Gráfico salvo: {output_file}")
        plt.close()
    
    def generate_all(self):
        """Gera todos os gráficos."""
        print("\n" + "="*60)
        print("GERANDO GRÁFICOS...")
        print("="*60 + "\n")
        
        self.load_data()
        
        print("\nCriando gráficos...\n")
        self.plot_latencia()
        self.plot_heap()
        self.plot_jitter()
        
        print("\n" + "="*60)
        print("GRÁFICOS GERADOS COM SUCESSO!")
        print("="*60)


if __name__ == "__main__":
    generator = GraphGenerator()
    generator.generate_all()
