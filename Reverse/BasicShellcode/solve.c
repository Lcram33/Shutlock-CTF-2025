#include <stdio.h>
#include <stdint.h>
#include <string.h>

void reverse_flag_full(uint8_t *buf) {
    const char *v3 = "y0UFouNdmYx0rKEy";
    const uint64_t v4[4] = {
        0xE2D4429123B432ALL,
        0x3702212D0826305FLL,
        0x5F111232551D6A1ALL,
        0x1C0B26094968363CLL
    };
    for (int a2 = 1; a2 <= 4; ++a2) {
        for (int v7 = 0; v7 <= 7; ++v7) {
            int idx = 4 * a2 - 4 + (v7 & 3);
            buf[(a2-1)*8 + v7] = v3[idx] ^ ((const uint8_t *)&v4[a2-1])[v7];
        }
    }
}

void reverse_arithmetic_copy(uint8_t *src, const uint8_t *dest) {
    // inverse of 7 mod 32 is 23
    for (int idx = 0; idx < 32; idx++) {
        int i = (23 * idx) % 32;
        src[i] = dest[idx];
    }
}

int main() {
    uint8_t transformed[32] = {0};
    uint8_t flag[32] = {0};

    reverse_flag_full(transformed);
    reverse_arithmetic_copy(flag, transformed);

    printf("Flag: '%.32s'\n", (char *)flag);
    return 0;
}
