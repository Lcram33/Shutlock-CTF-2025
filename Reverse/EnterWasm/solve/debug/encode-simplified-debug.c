#include <stdio.h>
#include <stdint.h>
#include <string.h>

#define INPUT_OFFSET 0 // Offset for input text in memory


// WebAssembly memory
uint8_t memory[65536]; // 1 page = 64KB

// WASM data
uint8_t wasm_data_at_8[] = {0xDC, 0x87, 0xDB, 0x6B, 0x7C, 0xFD, 0x6D, 0x20};
// uint8_t wasm_data_at_16_target[] = {0x8B, 0xC9, 0xDA, 0x58, 0xF2, 0xBF, 0x1E, 0xA1}; // original, to break
uint8_t wasm_data_at_16_target[] = {0x2C, 0xE4, 0x0E, 0x7B, 0x77, 0x02, 0x1A, 0x5D}; // password for testing

// Print memory for debugging
void print_memory_state(const char* label, int offset, int len) {
    printf("%s [0x%02X..0x%02X]: ", label, offset, offset + len -1);
    for (int i = 0; i < len; ++i) {
        printf("%02X ", memory[offset + i]);
    }
    printf("\n");
}

// func 0: i32.rotr (Right Rotation)
void func0_rotr(uint32_t rotation_amount) {
    uint32_t val0;
    memcpy(&val0, &memory[0], sizeof(uint32_t));
    uint32_t val4;
    memcpy(&val4, &memory[4], sizeof(uint32_t));

    val0 = (val0 >> rotation_amount) | (val0 << (32 - rotation_amount));
    val4 = (val4 >> rotation_amount) | (val4 << (32 - rotation_amount));

    memcpy(&memory[0], &val0, sizeof(uint32_t));
    memcpy(&memory[4], &val4, sizeof(uint32_t));
}

// func 2: i32.rotl (Left Rotation)
void func2_rotl(uint32_t rotation_amount) {
    uint32_t val0;
    memcpy(&val0, &memory[0], sizeof(uint32_t));
    uint32_t val4;
    memcpy(&val4, &memory[4], sizeof(uint32_t));

    val0 = (val0 << rotation_amount) | (val0 >> (32 - rotation_amount));
    val4 = (val4 << rotation_amount) | (val4 >> (32 - rotation_amount));

    memcpy(&memory[0], &val0, sizeof(uint32_t));
    memcpy(&memory[4], &val4, sizeof(uint32_t));
}

// chec function exported by the WebAssembly module
int32_t check(uint32_t input_offset, char *input_text) {
    // Zero out memory (necessary if multiple runs are expected)
    memset(memory, 0, sizeof(memory));

    // Initialize memory with input text
    memcpy(&memory[0], input_text, 8);

    // Initialize memory with WASM data
    memcpy(&memory[8], wasm_data_at_8, 8);
    memcpy(&memory[16], wasm_data_at_16_target, 8); // Compare target

    uint32_t var5;     // $var5: XOR result, rotation param
    uint32_t var6;     // $var6: Byte from wasm_data_at_8
    uint32_t var7;     // $var7: Masked i32 from memory

    printf("--- CHECK FUNCTION START ---\n");
    print_memory_state("Initial memory[0..7]", 0, 8);
    print_memory_state("Data at 8", 8, 8);
    print_memory_state("Target at 16", 16, 8);
    printf("\n");

    // Loop
    for (int var1 = 0; var1 < 8; var1++) {
        // We add 1 to var1 as we debugged WebAssembly at the end of each loop iteration
        printf("--- Loop Iteration: %u ($var1 = %u) ---\n", var1, var1 + 1);

        var5 = memory[input_offset + var1]; // Simulates i32.load and i32.and 255 for the first part of $var5
        var6 = memory[input_offset + 8 + var1]; // Simulates i32.load and i32.and 255 for $var6
        var5 = var5 ^ var6;

        uint32_t temp_loaded_i32;
        memcpy(&temp_loaded_i32, &memory[input_offset + var1], sizeof(uint32_t));
        var7 = temp_loaded_i32 & 0xFFFFFF00;

        printf("  C_Vars (Loop %u):\n", var1);
        printf("    $var5 (XOR result) = %u (0x%08X)\n", var5, var5);
        printf("    $var6 (Data8 byte) = %u (0x%02X)\n", var6, var6);
        printf("    $var7 (Masked i32 from mem[%u]) = %i (0x%08X)\n", var1, var7, var7);

        uint32_t value_to_store = var5 + var7;
        memcpy(&memory[input_offset + var1], &value_to_store, sizeof(uint32_t));
        printf("  Memory[0..7] after i32.store at offset %u:\n", var1);
        print_memory_state("    ", 0, 8);

        uint32_t call_param = var5 % 32;
        uint32_t func_index = var5 % 2;

        printf("  Calling func_table[%u] (param %u)\n", func_index, call_param);
        if (func_index == 0) func0_rotr(call_param);
        else func2_rotl(call_param);
        printf("  Memory[0..7] after rotation:\n");
        print_memory_state("    ", 0, 8);

        printf("\n");
    }

    printf("--- CHECK FUNCTION END ---\n");

    // Final comparison
    uint64_t final_val_at_0;
    memcpy(&final_val_at_0, &memory[0], sizeof(uint64_t));

    uint64_t target_val_at_16;
    memcpy(&target_val_at_16, &memory[16], sizeof(uint64_t));

    printf("[C Debug] Final memory[0..7]:             ");
    for (int i = 0; i < 8; ++i) { printf("%02X ", memory[i]); } printf("\n");
    printf("[C Debug] Target (memory[16..23]):        ");
    for (int i = 0; i < 8; ++i) { printf("%02X ", memory[16 + i]); } printf("\n");


    if (final_val_at_0 == target_val_at_16) {
        return 1;
    } else {
        return 0;
    }
}

// Fonction main pour tester
int main() {
    char input_text[] = "password"; // password input like in browser
    printf("Input: %s\n", input_text);

    int result = check(INPUT_OFFSET, input_text); // input_offset is 0

    if (result == 1) {
        printf("Access Granted!\n");
    } else {
        printf("Access Denied.\n");
    }

    return 0;
}