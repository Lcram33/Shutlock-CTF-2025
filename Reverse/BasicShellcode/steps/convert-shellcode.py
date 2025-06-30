import struct

values = [
    0xC748564155415441,
    0x148B4C00000001C0,
    0x84850F20FA8349C7,
    0x7C3C749000000,
    0x2C0C7480000,
    0xC5C749C7248B4C00,
    0xC0C74800000000,
    0x4CC7348B4C000000,
    0xD23148E5F749D889,
    0x412E048A43F2F749,
    0x4D01C58349140488,
    0x3C0C748E37CD539,
    0x48C7348B4C000000,
    0xC74900000001C2C7,
    0xE7894C00000001C3,
    0xFF41534152DE894C,
    0x49C221485A5B41D6,
    0x4908C4834901C383,
    0xD08948E07C05FB83,
]

# Rest of v26 separately defined
v26_part1 = struct.pack('<Q', 0x48C35C415D415E41)
v26_part2 = struct.pack('<Q', 0xC0C748C35C)[:8]
v26_part3 = struct.pack('<Q', 0xC35C415D415E4100)

# Assemble full shellcode
shellcode = b''.join(struct.pack('<Q', val) for val in values)
shellcode += v26_part1
shellcode += v26_part2
shellcode += v26_part3

with open("shellcode.bin", "wb") as f:
    f.write(shellcode)
