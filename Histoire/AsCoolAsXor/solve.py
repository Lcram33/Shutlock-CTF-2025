import hashlib


# Global var
DEBUG = False


def sha256sum(filename):
    with open(filename, 'rb', buffering=0) as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()

def func_key(word, key):
    return bytes([(word[i] * key[i % 4]) % 256 for i in range(len(word))])

def feistel_round_rev(L, R, key):
    new_R = L # Ri = Li+1
    F = func_key(L, key) # F = Li+1 * Ki
    new_L = bytes([R[j] ^ F[j] for j in range(len(L))]) # Li = Ri+1 ^ F
    return new_L, new_R

def feistel_deciper(encrypted, key, rounds=1):
    mid = len(encrypted) // 2
    L, R = encrypted[:mid], encrypted[mid:]
    
    for _ in range(rounds):
        L, R = feistel_round_rev(L, R, key)
    
    return L + R

def bits_to_bytes(bit_string):
    if len(bit_string) % 8 != 0:
        raise ValueError("Number of bits should be multiple of 8 !")

    bytes_list = []
    for i in range(0, len(bit_string), 8):
        byte_string = bit_string[i:i+8]
        byte = int(byte_string, 2)
        bytes_list.append(byte)

    bytes_object = bytes(bytes_list)
    return bytes_object

"""
def recover_key(ciphered_data, clear_header):
    KEY_SIZE = 4  # Size of the key in bytes
    
    mid = len(ciphered_data) // 2
    L1 = ciphered_data[:mid]
    R1 = ciphered_data[mid:]

    start_of_L0 = clear_header[KEY_SIZE:]
    start_of_L1 = L1[len(start_of_L0):]
    start_of_R1 = R1[len(start_of_L0):]
    
    key_bytes = []
    for i in range(KEY_SIZE):
        curr_L1 = start_of_L1[i]
        F = start_of_L0[i] ^ start_of_R1[i]
        
        # Inverse L1
        solutions = []
        for x in range(256):
            if (curr_L1 * x) % 256 == F:
                solutions.append(x)
        
        if solutions:
            # Prendre la première solution (normalement unique si a inversible)
            key_bytes.append(solutions[0])
        else:
            # Solution par défaut si aucune trouvée
            key_bytes.append(0)
    
    return bytes(key_bytes)
"""


# Main program

input_encrypted = "video_encrypted.mp4"
output_file = "L-is-dead.mp4"

with open(input_encrypted, "rb") as f:
    ciphered_data = f.read()

expected_bits = "0000000000000000000000000001100001100110011101000111100101110000" # Hex : 00 00 00 18 66 74 79 70
clear_header = bits_to_bytes(expected_bits)

# key = recover_key(ciphered_data, clear_header)
# print(f"Key recovered : {key.hex(' ').upper()}") # DEBUG
# Initially, I tried to recover the key with the above commented function. As it is 4 bytes long, we can either use the first or last parts of the header.
# However, they give slightly different results. I tried to "merge" them, but it didn't work as expected : one byte was residually different.
# So I bruteforced it !

if not DEBUG:
    print("[i] Bruteforcing the last byte of the key, this may take a while. Please wait...")

# Bruteforce the challenging byte of the key
# If you want to skip, the correct key is 53 48 4C 4B
key_bytes = list(bytes.fromhex("53 48 AA 4B")) # AA is the byte to bruteforce
for i in range(256):
    key_bytes[2] = i  # Change the byte to bruteforce
    
    key = bytes(key_bytes)
    data = feistel_deciper(ciphered_data, key)
    
    data_header = data[:len(clear_header)]
    actual_bits = ''.join(f'{byte:08b}' for byte in data_header)
    
    if actual_bits == expected_bits:
        print(f"[✓] Key found : {key.hex(' ').upper()}")
        break
    else:
        if DEBUG:
            print(f"[i] Invalid key {key.hex(' ').upper()} ({i}/256)")


# data = feistel_deciper(ciphered_data, key) # already computed above, comes from previous attempts
data_header = data[:len(clear_header)]
actual_bits = ''.join(f'{byte:08b}' for byte in data_header)
if actual_bits == expected_bits: # Last check to ensure the header matches
    print("[✓] OK - File successfully decrypted")
    with open(output_file, "wb") as f:
        f.write(data)
    
    # Compute flag
    flag = sha256sum(output_file)
    print(f"[✓] Flag : SHLK{'{' + flag + '}'}")
else:
    print("[X] ERROR - Decrypt failed. Header mismatch.")
    print(f"[!] Obtained header  :  {' '.join([actual_bits[i:i+8] for i in range(0, len(actual_bits), 8)])}")
    print(f"[!] Expected header  :  {' '.join([expected_bits[i:i+8] for i in range(0, len(expected_bits), 8)])}")
    diff = [i if actual_bits[i] != expected_bits[i] else False for i in range(len(actual_bits))]
    # for ind in diff: # <=== DEBUG
    #     if ind:
    #         print(f"Mismatch at index {ind}")
    print(f"[!] Number of bits mismatch : {len(diff) - diff.count(False)}")