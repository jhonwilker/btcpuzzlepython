import numpy as np
import numba
from numba import cuda
import math
import time
import base58
import hashlib
import ecdsa


wallets = ["66","162"]


# Função CUDA para cada worker
@cuda.jit
def worker_kernel(start, end, step, results):
    idx = cuda.grid(1)
    stride = cuda.gridsize(1)
    for i in range(idx * step + start, min((idx + 1) * step + start, end), stride):
        decimal_value = i
        bytes_arr = cuda.local.array(shape=32, dtype=numba.uint8)
        #for i in range(32):
        #    bytes_arr[32 - i - 1] = decimal_value & 0xFF
        #    decimal_value >>= 8
        #priv_key_bytes = bytes_arr
        #priv_key_bytes = decimal_to_bytes(decimal_value,32)  # Chamada da função de conversão
        
        results[idx * step + i - start] = decimal_value  # Armazena apenas o valor decimal por simplicidade

        # priv_key = ecdsa.SigningKey.from_string(priv_key_bytes, curve=ecdsa.SECP256k1)
        # compressed_pub_key = priv_key.verifying_key.to_string("compressed")
        # pub_key_hash = hashlib.new('ripemd160', hashlib.sha256(compressed_pub_key).digest()).digest()
        # address =  pub_key_hash


    
# Função para criar e iniciar os workers na GPU
def create_workers(start_hex, end_hex, step, num_workers):
    
    start = int(start_hex, 16)
    end = int(end_hex, 16)
    total_values = end - start
    results = np.zeros(total_values, dtype=np.int64)
    
    threads_per_block = 128
    blocks_per_grid = math.ceil(num_workers / threads_per_block)
    
    completed = 0
    start_time = time.time()

    for worker_id in range(0, total_values, step):
        current_start = start + worker_id
        current_end = min(start + worker_id + step, end)
        
        # Alocar memória na GPU para o intervalo atual
        results_device = cuda.to_device(results[worker_id:worker_id + step])
        
        # Executar o kernel na GPU para o intervalo atual
        worker_kernel[blocks_per_grid, threads_per_block](current_start, current_end, step, results_device)
        
        # Copiar resultados de volta para a CPU
        results_device.copy_to_host(results[worker_id:worker_id + step])
        
        completed += step
        elapsed_time = time.time() - start_time
        percentage_completed = (completed / total_values) * 100
        print(f"Worker {worker_id // step + 1} - Início: {hex(current_start)}, Fim: {hex(current_end - 1)}, "
              f"Tempo decorrido: {elapsed_time:.2f} segundos, {percentage_completed:.2f}% concluído")

# Função principal
def main():
    start_hex = "0x1000000"
    end_hex = "0x1ffffff"
    step = 1000
    num_workers = 1024  # Ajuste conforme necessário

    create_workers(start_hex, end_hex, step, num_workers)

if __name__ == "__main__":
    main()
