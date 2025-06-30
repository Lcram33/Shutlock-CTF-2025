# Prerequisite: shellcode-py.txt, obtained from disass.py

with open('shellcode-py.txt', 'r') as f:
    lines = f.read().splitlines()

xor_values = list()
expected_bits = list()
curr_bits_list = list()

for line in lines:
    if "XOR_IMM R2" in line:
        xor_val = line.split(' ')[-1]
        xor_values.append(int(xor_val))
    elif "MOV_IMM R5" in line:
        ex_bit = line.split(' ')[-1]
        curr_bits_list.append(ex_bit)
        if len(curr_bits_list) == 8:
            expected_bits.append(curr_bits_list[::-1])  # Reverse the bits to match the expected order
            curr_bits_list.clear()

expected_bits = expected_bits[::-1]  # Reverse the list to match the expected order

expected_bytes = [int(''.join(x), 2) for x in expected_bits]
password = [xor_values[i] ^ expected_bytes[i] for i in range(len(expected_bytes))]
password = bytes(password).decode()

print("SHLK{" + password + '}')