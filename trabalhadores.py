import numpy as np
from numba import cuda, int32
import math
import threading

# Função CUDA para cada worker
@cuda.jit
def worker_kernel(start, end):
    idx = cuda.grid(1)
    stride = cuda.gridsize(1)

    for i in range(idx + start, end, stride):
        decimal_value = i
        print(f"Hex: {i}, Decimal: {decimal_value}")

# Função para criar e iniciar os workers na GPU
def create_workers(start_hex, end_hex, num_workers):
    start = int(start_hex, 16)
    end = int(end_hex, 16)
    
    threads_per_block = 10
    blocks_per_grid = math.ceil(num_workers / threads_per_block)

    worker_kernel[blocks_per_grid, threads_per_block](start, end)
    cuda.synchronize()

# Função principal
def main():
    start_hex = "0x10000"
    end_hex = "0x1ffff"
    num_workers = 10  # Ajuste conforme necessário

    create_workers(start_hex, end_hex, num_workers)

if __name__ == "__main__":
    main()