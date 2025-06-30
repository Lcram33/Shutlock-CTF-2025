#include <stdio.h>
#include <stdint.h>
#include <cuda_runtime.h>

// Alphabet en mémoire constante (non utilisé ici, mais utile pour brute-force)
__constant__ char d_alphabet[] = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789";
const int alphabet_len = 62;

// WASM data (copiés sur GPU)
uint8_t wasm_data_at_8[] = {0xDC, 0x87, 0xDB, 0x6B, 0x7C, 0xFD, 0x6D, 0x20};
uint8_t wasm_data_at_16[] = {0x2C, 0xE4, 0x0E, 0x7B, 0x77, 0x02, 0x1A, 0x5D};

// Fonction GPU check corrigée
__device__ int check_gpu(const char *input_text, const uint8_t *wasm_data_at_8, const uint8_t *wasm_data_at_16) {
    uint8_t memory[24] = {0};

    // Initialisation mémoire
    for (int i = 0; i < 8; i++) memory[i] = input_text[i];
    for (int i = 0; i < 8; i++) memory[8 + i] = wasm_data_at_8[i];
    for (int i = 0; i < 8; i++) memory[16 + i] = wasm_data_at_16[i];

    for (int var1 = 0; var1 < 8; var1++) {
        uint8_t var5 = memory[var1] ^ memory[8 + var1];

        // Charger 4 octets à partir de var1 (i32.load)
        uint32_t temp_loaded_i32 = 0;
        for (int b = 0; b < 4; b++) {
            temp_loaded_i32 |= ((uint32_t)memory[var1 + b]) << (8 * b);
        }

        uint32_t var7 = temp_loaded_i32 & 0xFFFFFF00;
        uint32_t value_to_store = var5 + var7;

        // Stocker 4 octets à partir de var1 (i32.store)
        for (int b = 0; b < 4; b++) {
            memory[var1 + b] = (value_to_store >> (8 * b)) & 0xFF;
        }

        uint32_t call_param = var5 % 32;
        uint32_t func_index = var5 % 2;

        // Reconstituer les deux uint32_t pour rotation
        uint32_t val0 = 0, val4 = 0;
        for (int b = 0; b < 4; b++) val0 |= ((uint32_t)memory[b]) << (8 * b);
        for (int b = 0; b < 4; b++) val4 |= ((uint32_t)memory[4 + b]) << (8 * b);

        if (func_index == 0) {
            val0 = (val0 >> call_param) | (val0 << (32 - call_param));
            val4 = (val4 >> call_param) | (val4 << (32 - call_param));
        } else {
            val0 = (val0 << call_param) | (val0 >> (32 - call_param));
            val4 = (val4 << call_param) | (val4 >> (32 - call_param));
        }

        for (int b = 0; b < 4; b++) memory[b] = (val0 >> (8 * b)) & 0xFF;
        for (int b = 0; b < 4; b++) memory[4 + b] = (val4 >> (8 * b)) & 0xFF;
    }

    // Comparaison finale 64 bits
    for (int i = 0; i < 8; i++) {
        if (memory[i] != memory[16 + i]) return 0;
    }
    return 1;
}

// Kernel de test simple
__global__ void test_password_kernel(int *result, const uint8_t *wasm_data_at_8, const uint8_t *wasm_data_at_16) {
    const char test_pw[8] = {'p','a','s','s','w','o','r','d'};
    if (check_gpu(test_pw, wasm_data_at_8, wasm_data_at_16)) {
        *result = 1;
    } else {
        *result = 0;
    }
}

int main() {
    int *d_result;
    int h_result = 0;

    uint8_t *d_wasm_data_at_8, *d_wasm_data_at_16;

    cudaMalloc(&d_result, sizeof(int));
    cudaMalloc(&d_wasm_data_at_8, 8);
    cudaMalloc(&d_wasm_data_at_16, 8);

    cudaMemcpy(d_wasm_data_at_8, wasm_data_at_8, 8, cudaMemcpyHostToDevice);
    cudaMemcpy(d_wasm_data_at_16, wasm_data_at_16, 8, cudaMemcpyHostToDevice);
    cudaMemcpy(d_result, &h_result, sizeof(int), cudaMemcpyHostToDevice);

    test_password_kernel<<<1,1>>>(d_result, d_wasm_data_at_8, d_wasm_data_at_16);
    cudaDeviceSynchronize();

    cudaMemcpy(&h_result, d_result, sizeof(int), cudaMemcpyDeviceToHost);

    if (h_result == 1) {
        printf("Le mot de passe 'password' est reconnu comme valide.\n");
    } else {
        printf("Le mot de passe 'password' n'est PAS reconnu.\n");
    }

    cudaFree(d_result);
    cudaFree(d_wasm_data_at_8);
    cudaFree(d_wasm_data_at_16);

    return 0;
}
