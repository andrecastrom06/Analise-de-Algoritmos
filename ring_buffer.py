"""
Buffer Circular - Complexidade O(1)
Implementação eficiente com índices (head/tail)
"""

import time


class RingBuffer:
    """
    Buffer circular com complexidade O(1) para inserção e remoção.
    Usa apenas deslocamento de índices, sem realocação.
    """
    
    def __init__(self, capacity: int):
        """
        Inicializa o buffer circular.
        
        Args:
            capacity: Tamanho máximo do buffer
        """
        self.capacity = capacity
        self.buffer = [None] * capacity
        self.head = 0  # Próxima posição para inserir
        self.tail = 0  # Próxima posição para remover
        self.count = 0  # Número de elementos
        self.insertion_time_ns = 0
        self.removal_time_ns = 0
    
    def push(self, data):
        """
        Insere dado no buffer - O(1).
        Se cheio, sobrescreve o elemento mais antigo.
        
        Args:
            data: Dado a inserir
        """
        start = time.perf_counter_ns()
        
        self.buffer[self.head] = data
        self.head = (self.head + 1) % self.capacity
        
        if self.count < self.capacity:
            self.count += 1
        else:
            # Buffer cheio, tail avança também
            self.tail = (self.tail + 1) % self.capacity
        
        self.insertion_time_ns = time.perf_counter_ns() - start
    
    def pop(self):
        """
        Remove e retorna o elemento mais antigo - O(1).
        
        Returns:
            Elemento removido ou None se vazio
        """
        start = time.perf_counter_ns()
        
        if self.count == 0:
            self.removal_time_ns = time.perf_counter_ns() - start
            return None
        
        data = self.buffer[self.tail]
        self.tail = (self.tail + 1) % self.capacity
        self.count -= 1
        
        self.removal_time_ns = time.perf_counter_ns() - start
        return data
    
    def is_empty(self):
        """Verifica se buffer está vazio."""
        return self.count == 0
    
    def is_full(self):
        """Verifica se buffer está cheio."""
        return self.count == self.capacity
    
    def get_size(self):
        """Retorna número de elementos atualmente no buffer."""
        return self.count
    
    def get_capacity(self):
        """Retorna capacidade máxima do buffer."""
        return self.capacity
    
    def clear(self):
        """Limpa o buffer."""
        self.head = 0
        self.tail = 0
        self.count = 0
        self.buffer = [None] * self.capacity
    
    def get_all(self):
        """Retorna lista com todos os elementos do buffer."""
        if self.count == 0:
            return []
        
        result = []
        idx = self.tail
        for _ in range(self.count):
            result.append(self.buffer[idx])
            idx = (idx + 1) % self.capacity
        
        return result


if __name__ == "__main__":
    # Teste simples
    rb = RingBuffer(5)
    
    print("=== Teste RingBuffer ===")
    print("\nInserindo 7 elementos em buffer de capacidade 5...")
    for i in range(7):
        rb.push(f"dado_{i}")
        print(f"Push: dado_{i}, tamanho: {rb.get_size()}")
    
    print(f"\nBuffer cheio? {rb.is_full()}")
    print(f"Conteúdo: {rb.get_all()}")
    
    print("\nRemovendo 3 elementos...")
    for _ in range(3):
        removed = rb.pop()
        print(f"Pop: {removed}, tamanho: {rb.get_size()}")
    
    print(f"\nConteúdo após pops: {rb.get_all()}")
