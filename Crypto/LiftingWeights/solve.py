import math
from out import encrypted_flag

def recover_flag(encrypted):
    flag = b""
    for r, fval in encrypted:
        byte = fval // (2 * r)
        flag += bytes([byte])
    return flag


print(recover_flag(encrypted_flag))