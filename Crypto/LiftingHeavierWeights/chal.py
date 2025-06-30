from Crypto.Util.number import getPrime, GCD
import random

FLAG = b'??????????????????????????????????????'

def f(p, x):
    res = 0
    while x % p == 0 :
        x //= p
        res += 1
    return res

def encrypt_flag(flag):
    p = getPrime(512)
    first = getPrime(345)
    setup = pow(p, first)
    x = random.randrange(-setup, setup)
    y = x - setup
    while x % p == 0 or y % p == 0 or x == 0 or y == 0:
        x = random.randrange(-setup, setup)
        y = x - setup
        
    big_big_big = 1
    for byte in flag:
        n = pow(p, byte * big_big_big) * getPrime(512)
        temp = pow(x, n) - pow(y, n)
        big_big_big *= 1000

        while True:
            x = random.randrange(-temp, temp)
            y = x - temp
            if x % p != 0 and y % p != 0 and x != 0 and y != 0:
                break

    return (f(p, temp), first)


with open('out.txt', 'w') as f:
    f.write(str(encrypt_flag(FLAG)) + "\n")
