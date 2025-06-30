import os
from secret import key

def func_key(word, key):
    return bytes([(word[i] * key[i % 4]) % 256 for i in range(len(word))])

def feistel_round(L, R, key):
    new_L = R
    F = func_key(R, key)
    new_R = bytes([L[j] ^ F[j] for j in range(len(L))])
    return new_L, new_R

def feistel_cipher(data, key, rounds=1):
    if len(data) % 2 != 0:
        data += b"\x00"  # padding
        
    mid = len(data) // 2
    L, R = data[:mid], data[mid:]
    
    for _ in range(rounds):
        L, R = feistel_round(L, R, key)
    
    return L + R

input_file = "L-is-dead.mp4"
output_encrypted = "video_encrypted.mp4"

#Check header MP4
expected_bits = "0000000000000000000000000001100001100110011101000111100101110000"

with open(input_file, "rb") as f:
    data = f.read(8)
    actual_bits = ''.join(f'{byte:08b}' for byte in data)

if actual_bits == expected_bits:
    print("OK")
else:
    print("KO")
    print(f"actual bits : {actual_bits}")


with open(input_file, "rb") as f:
    data = f.read()

ciphered_data = feistel_cipher(data, key)
with open(output_encrypted, "wb") as f:
    f.write(ciphered_data)

print("OK")
