#include <stdio.h>
#include <stdint.h>
#include <string.h>

// Simule la mémoire WebAssembly
uint8_t memory[65536]; // 1 page = 64KB

// Les données fixes du WASM, initialisées une seule fois
uint8_t wasm_data_at_8[] = {0xDC, 0x87, 0xDB, 0x6B, 0x7C, 0xFD, 0x6D, 0x20};
// La CIBLE que vous avez modifiée dans le WAT : 0x1D F6 58 C8 B4 99 ED DE
// uint8_t wasm_data_at_16_target[] = {0x8B, 0xC9, 0xDA, 0x58, 0xF2, 0xBF, 0x1E, 0xA1}; // original, to break
uint8_t wasm_data_at_16_target[] = {0x2C, 0xE4, 0x0E, 0x7B, 0x77, 0x02, 0x1A, 0x5D}; // password for testing

// Helper pour afficher la mémoire
void print_memory_state(const char* label, int offset, int len) {
    printf("%s [0x%02X..0x%02X]: ", label, offset, offset + len -1);
    for (int i = 0; i < len; ++i) {
        printf("%02X ", memory[offset + i]);
    }
    printf("\n");
}

// func 0: i32.rotr (Rotation Droite)
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

// func 2: i32.rotl (Rotation Gauche)
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

typedef void (*WasmFuncType0)(uint32_t);
WasmFuncType0 func_table[2]; // Corresponds aux elem (0: func0, 1: func2)

// La fonction check exportée par le module WebAssembly
int32_t check(uint32_t input_offset) {
    // Initialiser la mémoire avec les données fixes du WASM
    memcpy(&memory[8], wasm_data_at_8, 8);
    memcpy(&memory[16], wasm_data_at_16_target, 8); // La cible de comparaison

    // Initialisation de la table de fonctions pour l'appel indirect
    func_table[0] = func0_rotr; // $elem0 référence $func0
    func_table[1] = func2_rotl; // $elem1 référence $func2

    uint32_t var1 = 0; // $var1: Loop index
    uint32_t var5;     // $var5: XOR result, rotation param
    uint32_t var6;     // $var6: Byte from wasm_data_at_8
    uint32_t var7;     // $var7: Masked i32 from memory

    printf("--- CHECK FUNCTION START ---\n");
    print_memory_state("Initial memory[0..7]", 0, 8);
    print_memory_state("Data at 8", 8, 8);
    print_memory_state("Target at 16", 16, 8);
    printf("\n");

    // Loop
    while (var1 < 8) {
        printf("--- Loop Iteration: %u ($var1 = %u) ---\n", var1, var1); // WASM $var1 semble être 1-indexed

        var5 = memory[input_offset + var1]; // Simulates i32.load and i32.and 255 for the first part of $var5
        var6 = memory[input_offset + 8 + var1]; // Simulates i32.load and i32.and 255 for $var6
        var5 = var5 ^ var6;

        uint32_t temp_loaded_i32;
        memcpy(&temp_loaded_i32, &memory[input_offset + var1], sizeof(uint32_t));
        var7 = temp_loaded_i32 & 0xFFFFFF00;

        printf("  C_Vars (Loop %u):\n", var1); // $var1 in DevTools is (var1_in_C + 1)
        printf("    $var5 (XOR result) = %u (0x%08X)\n", var5, var5); // Change here: Use %08X for full 32-bit hex
        printf("    $var6 (Data8 byte) = %u (0x%02X)\n", var6, var6);
        printf("    $var7 (Masked i32 from mem[%u]) = %i (0x%08X)\n", var1, var7, var7);

        printf("  Memory[0..7] before i32.store at offset %u:\n", var1);
        print_memory_state("    ", 0, 8);

        uint32_t value_to_store = var5 + var7;
        memcpy(&memory[input_offset + var1], &value_to_store, sizeof(uint32_t));
        printf("  Memory[0..7] after i32.store at offset %u:\n", var1);
        print_memory_state("    ", 0, 8);

        uint32_t call_param = var5 % 32;
        uint32_t func_index = var5 % 2;

        printf("  Calling func_table[%u] (param %u)\n", func_index, call_param);
        func_table[func_index](call_param);
        printf("  Memory[0..7] after rotation:\n");
        print_memory_state("    ", 0, 8);

        var1++;
        printf("\n");
    }

    printf("--- CHECK FUNCTION END ---\n");

    // Comparaison finale
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
    memset(memory, 0, sizeof(memory)); // Efface toute la mémoire

    char input_text[] = "password"; // L'entrée que vous utilisez dans le navigateur
    printf("Input: %s\n", input_text);
    memcpy(&memory[0], input_text, 8); // Place l'entrée dans les 8 premiers octets

    int result = check(0); // input_offset est 0

    if (result == 1) {
        printf("Access Granted!\n");
    } else {
        printf("Access Denied.\n");
    }

    return 0;
}