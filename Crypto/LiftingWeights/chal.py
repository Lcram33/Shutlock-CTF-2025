from Crypto.Util.number import getPrime
import random

FLAG = b'????????????????????????????????'

def f(x):
    res = 0
    while x % 2 == 0 :
        x //= 2
        res += 1
    return res

def encrypt_flag(flag):
    encrypted = []
    for byte in flag:
        r = getPrime(512)
        n = pow(2, r * byte)
        x = random.randrange(-n, n, 2) + 1
        y = x - n
        t = pow(x, n) - pow(y, n)

        encrypted.append((r, f(t)))

    return encrypted

with open('out.txt', 'w') as f:
    f.write(str(encrypt_flag(FLAG)) + "\n")
