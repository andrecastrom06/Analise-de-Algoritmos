"""
Buffer Ineficiente - Complexidade O(n)
Implementação anti-padrão com deslocamento ou pop(0)
"""

import time


class InefficientBuffer:
    """
    Buffer ineficiente com complexidade O(n) para remoção.
    Simula comportamento de sistemas mal otimizados.
    """
    
    def __init__(self, capacity: int):
        """
        Inicializa o buffer ineficiente.
        
        Args:
            capacity: Tamanho máximo do buffer
        """
        self.capacity = capacity
        self.buffer = []  # Lista dinâmica
        self.insertion_time_ns = 0
        self.removal_time_ns = 0
    
    def push(self, data):
        """
        Insere dado ao final da lista - O(1).
        
        Args:
            data: Dado a inserir
        """
        start = time.perf_counter_ns()
        
        self.buffer.append(data)
        
        # Se exceder capacidade, remove o primeiro (aqui não queremos overflow)
        # Para simular comportamento real, mantemos a lista crescendo
        
        self.insertion_time_ns = time.perf_counter_ns() - start
    
    def pop(self):
        """
        Remove e retorna o primeiro elemento - O(n).
        Deslocar todos os outros elementos é O(n).
        
        Returns:
            Elemento removido ou None se vazio
        """
        start = time.perf_counter_ns()
        
        if not self.buffer:
            self.removal_time_ns = time.perf_counter_ns() - start
            return None
        
        # INEFICIENTE: pop(0) é O(n) porque desloca todos os elementos
        data = self.buffer.pop(0)
        
        self.removal_time_ns = time.perf_counter_ns() - start
        return data
    
    def pop_with_loop(self):
        """
        Versão alternativa: deslocar manualmente - O(n).
        Este é um exemplo de código ruim que alguns ainda usam.
        
        Returns:
            Elemento removido ou None se vazio
        """
        start = time.perf_counter_ns()
        
        if not self.buffer:
            self.removal_time_ns = time.perf_counter_ns() - start
            return None
        
        data = self.buffer[0]
        
        # Deslocar manualmente: O(n)
        for i in range(len(self.buffer) - 1):
            self.buffer[i] = self.buffer[i + 1]
        
        self.buffer.pop()
        
        self.removal_time_ns = time.perf_counter_ns() - start
        return data
    
    def is_empty(self):
        """Verifica se buffer está vazio."""
        return len(self.buffer) == 0
    
    def is_full(self):
        """Verifica se buffer atingiu capacidade."""
        return len(self.buffer) >= self.capacity
    
    def get_size(self):
        """Retorna número de elementos atualmente no buffer."""
        return len(self.buffer)
    
    def get_capacity(self):
        """Retorna capacidade máxima do buffer."""
        return self.capacity
    
    def clear(self):
        """Limpa o buffer."""
        self.buffer = []
    
    def get_all(self):
        """Retorna cópia da lista de elementos."""
        return self.buffer.copy()


if __name__ == "__main__":
    # Teste simples
    ib = InefficientBuffer(5)
    
    print("=== Teste InefficientBuffer ===")
    print("\nInserindo 7 elementos...")
    for i in range(7):
        ib.push(f"dado_{i}")
        print(f"Push: dado_{i}, tamanho: {ib.get_size()}, tempo: {ib.insertion_time_ns:.0f} ns")
    
    print(f"\nBuffer cheio? {ib.is_full()}")
    print(f"Conteúdo: {ib.get_all()}")
    
    print("\nRemovendo 3 elementos com pop()...")
    for _ in range(3):
        removed = ib.pop()
        print(f"Pop: {removed}, tamanho: {ib.get_size()}, tempo: {ib.removal_time_ns:.0f} ns")
    
    print(f"\nConteúdo após pops: {ib.get_all()}")
