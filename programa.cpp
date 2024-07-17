#include <iostream>
#include <iomanip>
#include <cuda_runtime.h>
#include <chrono>
#include <crt/math_functions.h>
#include <device_launch_parameters.h>

__device__ void decimal_to_bytes(uint64_t decimal_value, uint8_t* bytes, int length) {
    for (int i = 0; i < length; ++i) {
        bytes[length - i - 1] = (decimal_value >> (8 * i)) & 0xFF;
    }
}

__global__ void worker_kernel(uint64_t start, uint64_t end, uint64_t step, uint64_t* results) {
    int idx = threadIdx.x + blockIdx.x * blockDim.x;
    uint64_t stride = gridDim.x * blockDim.x;

    for (uint64_t i = idx * step + start; i < min((idx + 1) * step + start, end); i += stride) {
        results[idx * step + i - start] = i;

        // Exemplo de como criar bytes privados (não está sendo usado além do armazenamento de resultados):
        uint8_t priv_key_bytes[32];
        decimal_to_bytes(i, priv_key_bytes, 32);

        // O código a seguir é apenas para ilustrar a criação da chave privada e não faz nada além disso.
        // Para operações adicionais, você precisa incluir outras funções ou bibliotecas.
    }
}

void create_workers(uint64_t start, uint64_t end, uint64_t step, int num_workers) {
    uint64_t total_values = end - start;
    uint64_t* results = new uint64_t[total_values];
    uint64_t* results_device;

    cudaMalloc(&results_device, total_values * sizeof(uint64_t));

    int threads_per_block = 128;
    int blocks_per_grid = (num_workers + threads_per_block - 1) / threads_per_block;

    auto start_time = std::chrono::high_resolution_clock::now();

    for (uint64_t worker_id = 0; worker_id < total_values; worker_id += step) {
        uint64_t current_start = start + worker_id;
        uint64_t current_end = std::min(start + worker_id + step, end);

        cudaMemcpy(results_device, results + worker_id, step * sizeof(uint64_t), cudaMemcpyHostToDevice);

        worker_kernel<<<blocks_per_grid, threads_per_block>>>(current_start, current_end, step, results_device);

        cudaMemcpy(results + worker_id, results_device, step * sizeof(uint64_t), cudaMemcpyDeviceToHost);

        // Atualizar o progresso e exibir informações
        auto end_time = std::chrono::high_resolution_clock::now();
        std::chrono::duration<double> elapsed_time = end_time - start_time;
        double percentage_completed = static_cast<double>(worker_id + step) / total_values * 100;

        std::cout << "Worker " << (worker_id / step + 1) << " - Início: " << std::hex << current_start
                  << ", Fim: " << std::hex << (current_end - 1) << ", Tempo decorrido: " 
                  << std::fixed << std::setprecision(2) << elapsed_time.count() << " segundos, "
                  << std::fixed << std::setprecision(2) << percentage_completed << "% concluído" << std::endl;
    }

    cudaFree(results_device);
    delete[] results;
}

int main() {
    uint64_t start = 0x1000000;
    uint64_t end = 0x1ffffff;
    uint64_t step = 1000;
    int num_workers = 1024;  // Ajuste conforme necessário

    create_workers(start, end, step, num_workers);

    return 0;
}