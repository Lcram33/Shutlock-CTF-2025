from out import encrypted_flag

def recover_flag(v, first):
    s = v - first
    flag_bytes = []
    while s:
        s, r = divmod(s, 1000)
        if not (0 <= r <= 255):
            raise ValueError(f"Byte value {r} out of range [0,255]")
        flag_bytes.append(r)
    return bytes(flag_bytes)

f_pt, first = encrypted_flag
print(recover_flag(f_pt, first))