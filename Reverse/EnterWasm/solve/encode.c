#include <stdio.h>
#include <stdint.h>
#include <string.h>

#define INPUT_OFFSET 0 // Offset for input text in memory


// WebAssembly memory
uint8_t memory[65536]; // 1 page = 64KB

// WASM data
uint8_t wasm_data_at_8[] = {0xDC, 0x87, 0xDB, 0x6B, 0x7C, 0xFD, 0x6D, 0x20};
// uint8_t wasm_data_at_16[] = {0x8B, 0xC9, 0xDA, 0x58, 0xF2, 0xBF, 0x1E, 0xA1}; // original, to break
uint8_t wasm_data_at_16[] = {0x2C, 0xE4, 0x0E, 0x7B, 0x77, 0x02, 0x1A, 0x5D}; // "password", for testing

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

// check function exported by the WebAssembly module
int32_t check(uint32_t input_offset, char *input_text) {
    // We removed input_offset from the code as it is 0, but it is still in the function signature
    // as it is required by the WebAssembly module (it's a reminder)

    // Zero out memory (necessary if multiple runs are expected)
    memset(memory, 0, sizeof(memory));

    // Initialize memory with input text
    memcpy(&memory[0], input_text, 8);

    // Initialize memory with WASM data
    memcpy(&memory[8], wasm_data_at_8, 8);
    memcpy(&memory[16], wasm_data_at_16, 8); // Compare target

    uint32_t var5;     // $var5: XOR result, rotation param
    uint32_t var6;     // $var6: Byte from wasm_data_at_8
    uint32_t var7;     // $var7: Masked i32 from memory

    // Loop
    for (int var1 = 0; var1 < 8; var1++) {
        var5 = memory[var1]; // Simulates i32.load and i32.and 255 for the first part of $var5
        var6 = memory[8 + var1]; // Simulates i32.load and i32.and 255 for $var6
        var5 = var5 ^ var6;

        uint32_t temp_loaded_i32;
        memcpy(&temp_loaded_i32, &memory[var1], sizeof(uint32_t));
        var7 = temp_loaded_i32 & 0xFFFFFF00;

        uint32_t value_to_store = var5 + var7;
        memcpy(&memory[var1], &value_to_store, sizeof(uint32_t));

        uint32_t call_param = var5 % 32;
        uint32_t func_index = var5 % 2;

        if (func_index == 0) func0_rotr(call_param);
        else func2_rotl(call_param);
    }

    // Final comparison
    uint64_t final_val_at_0;
    memcpy(&final_val_at_0, &memory[0], sizeof(uint64_t));

    uint64_t target_val_at_16;
    memcpy(&target_val_at_16, &memory[16], sizeof(uint64_t));

    if (final_val_at_0 == target_val_at_16) {
        return 1;
    } else {
        return 0;
    }
}

int main() {
    char input1[] = "password"; // password input like in browser
    printf("Input: %s\n", input1);
    int result = check(INPUT_OFFSET, input1); // input_offset is 0
    if (result == 1) {
        printf("Access Granted!\n");
    } else {
        printf("Access Denied.\n");
    }

    char input2[] = "passpass"; // password input like in browser
    printf("Input: %s\n", input2);
    result = check(INPUT_OFFSET, input2); // input_offset is 0
    if (result == 1) {
        printf("Access Granted!\n");
    } else {
        printf("Access Denied.\n");
    }

    printf("Input: %s\n", input1);
    result = check(INPUT_OFFSET, input1); // input_offset is 0
    if (result == 1) {
        printf("Access Granted!\n");
    } else {
        printf("Access Denied.\n");
    }

    return 0;
}