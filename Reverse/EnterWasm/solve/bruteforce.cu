// Compile :
// nvcc -o bruteforce bruteforce.cu

// Launch (within screen, writing to file as well for safety):
// screen
// ./bruteforce | tee resultats.txt
// Ctrl+A and d to detach from the screen session

// To reattach to the screen session:
// screen -ls
// screen -r <session_id>

#include <stdio.h>
#include <stdint.h>
#include <time.h>
#include <cuda_runtime.h>


// Macro to check CUDA errors
#define CUDA_CHECK(err) \
if (err != cudaSuccess) { \
        fprintf(stderr, "[X] CUDA Error: %s (code %d), line %d\n", cudaGetErrorString(err), err, __LINE__); \
        exit(EXIT_FAILURE); \
    }

// Charset
__constant__ char d_alphabet[] = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-"; // prod
const int alphabet_len = 2 * 26 + 10 + 2; // !! Make sure to update this if you change the alphabet !!
// __constant__ char d_alphabet[] = "pasword"; // testing
// const int alphabet_len = 7; // !! Make sure to update this if you change the alphabet !!

// WASM data
uint8_t wasm_data_at_8[] = {0xDC, 0x87, 0xDB, 0x6B, 0x7C, 0xFD, 0x6D, 0x20};
uint8_t wasm_data_at_16[] = {0x8B, 0xC9, 0xDA, 0x58, 0xF2, 0xBF, 0x1E, 0xA1}; // prod
// uint8_t wasm_data_at_16[] = {0x2C, 0xE4, 0x0E, 0x7B, 0x77, 0x02, 0x1A, 0x5D}; // testing

// check function, for GPU
__device__ int check_gpu(const char *input_text, const uint8_t *wasm_data_at_8, const uint8_t *wasm_data_at_16) {
    uint8_t memory[24] = {0};

    for (int i = 0; i < 8; i++) memory[i] = input_text[i];
    for (int i = 0; i < 8; i++) memory[8 + i] = wasm_data_at_8[i];
    for (int i = 0; i < 8; i++) memory[16 + i] = wasm_data_at_16[i];

    for (int var1 = 0; var1 < 8; var1++) {
        uint8_t var5 = memory[var1] ^ memory[8 + var1];

        uint32_t temp_loaded_i32 = 0;
        for (int b = 0; b < 4; b++) {
            temp_loaded_i32 |= ((uint32_t)memory[var1 + b]) << (8 * b);
        }

        uint32_t var7 = temp_loaded_i32 & 0xFFFFFF00;
        uint32_t value_to_store = var5 + var7;

        for (int b = 0; b < 4; b++) {
            memory[var1 + b] = (value_to_store >> (8 * b)) & 0xFF;
        }

        uint32_t call_param = var5 % 32;
        uint32_t func_index = var5 % 2;

        uint32_t val0 = 0, val4 = 0;
        for (int b = 0; b < 4; b++) val0 |= ((uint32_t)memory[b]) << (8 * b);
        for (int b = 0; b < 4; b++) val4 |= ((uint32_t)memory[4 + b]) << (8 * b);

        if (func_index == 0) { // rotate right
            val0 = (val0 >> call_param) | (val0 << (32 - call_param));
            val4 = (val4 >> call_param) | (val4 << (32 - call_param));
        } else { // rotate left
            val0 = (val0 << call_param) | (val0 >> (32 - call_param));
            val4 = (val4 << call_param) | (val4 >> (32 - call_param));
        }

        for (int b = 0; b < 4; b++) memory[b] = (val0 >> (8 * b)) & 0xFF;
        for (int b = 0; b < 4; b++) memory[4 + b] = (val4 >> (8 * b)) & 0xFF;
    }

    for (int i = 0; i < 8; i++) {
        if (memory[i] != memory[16 + i]) return 0;
    }
    return 1;
}

// Kernel brute-force
__global__ void brute_force_kernel(char *results, int max_results, const uint8_t *wasm_data_at_8, const uint8_t *wasm_data_at_16, uint64_t start_idx, uint64_t end_idx) {
    uint64_t idx = start_idx + (uint64_t)blockIdx.x * blockDim.x + threadIdx.x;
    if (idx >= end_idx) return;

    char candidate[9] = {0};
    uint64_t tmp = idx;
    for (int i = 0; i < 8; i++) {
        candidate[i] = d_alphabet[tmp % alphabet_len];
        tmp /= alphabet_len;
    }
    candidate[8] = '\0';

    if (check_gpu(candidate, wasm_data_at_8, wasm_data_at_16)) {
        int pos = atomicAdd((int*)results, 1);
        if (pos < max_results - 1) {
            for (int i = 0; i < 9; i++) results[(pos + 1) * 9 + i] = candidate[i];
        }
    }
}

int main() {
    // Disable buffering
    setvbuf(stdout, NULL, _IOLBF, 0); // Output line by line

    uint8_t *d_wasm_data_at_8, *d_wasm_data_at_16;
    char *d_results;
    char *h_results;
    int max_results = 10;

    CUDA_CHECK(cudaMalloc(&d_wasm_data_at_8, 8));
    CUDA_CHECK(cudaMalloc(&d_wasm_data_at_16, 8));
    CUDA_CHECK(cudaMemcpy(d_wasm_data_at_8, wasm_data_at_8, 8, cudaMemcpyHostToDevice));
    CUDA_CHECK(cudaMemcpy(d_wasm_data_at_16, wasm_data_at_16, 8, cudaMemcpyHostToDevice));

    h_results = (char*)malloc((1 + max_results) * 9);
    CUDA_CHECK(cudaMalloc(&d_results, (1 + max_results) * 9));
    CUDA_CHECK(cudaMemset(d_results, 0, (1 + max_results) * 9));

    uint64_t total_combinations = 1;
    for (int i = 0; i < 8; i++) total_combinations *= alphabet_len;
    printf("[i] Total number of combinations : %llu combinaisons\n", total_combinations);

    int threads_per_block = 256;
    uint64_t chunk_size = (uint64_t)threads_per_block * 1024 * 1024; // ~256M par chunk

    printf("[i] Starting bruteforce...\n");
    clock_t start_bruteforce = clock();

    int found_any = 0;
    for (uint64_t start_idx = 0; start_idx < total_combinations; start_idx += chunk_size) {
        uint64_t end_idx = start_idx + chunk_size;
        if (end_idx > total_combinations) end_idx = total_combinations;

        int blocks_per_grid = (int)((end_idx - start_idx + threads_per_block - 1) / threads_per_block);

        brute_force_kernel<<<blocks_per_grid, threads_per_block>>>(d_results, max_results, d_wasm_data_at_8, d_wasm_data_at_16, start_idx, end_idx);

        CUDA_CHECK(cudaGetLastError());
        CUDA_CHECK(cudaDeviceSynchronize());

        CUDA_CHECK(cudaMemcpy(h_results, d_results, (1 + max_results) * 9, cudaMemcpyDeviceToHost));
        int found_count = *((int*)h_results);

        if (found_count > 0) {
            printf("\n[!][i] Password(s) found :\n");
            for (int i = 0; i < found_count; i++) {
                printf("  -> %s\n", &h_results[(i + 1) * 9]);
            }
            found_any = 1;
            break;
        }
    }
    
    if (!found_any) {
        printf("[X] No password found in the whole search space.\n");
    }

    clock_t end_bruteforce = clock();
    double elapsed_time = (double)(end_bruteforce - start_bruteforce) / CLOCKS_PER_SEC;
    printf("[i] Bruteforce completed in %.2f seconds.\n", elapsed_time);

    cudaFree(d_wasm_data_at_8);
    cudaFree(d_wasm_data_at_16);
    cudaFree(d_results);
    free(h_results);

    return 0;
}
