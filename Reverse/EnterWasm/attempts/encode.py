import struct
import random
from mywasmlib import wasm_check


VALID_PASSWORD = "password"

# Constants from WASM data
wasm_data_at_8 = [0xDC, 0x87, 0xDB, 0x6B, 0x7C, 0xFD, 0x6D, 0x20]
# wasm_data_at_16 = [0x8B, 0xC9, 0xDA, 0x58, 0xF2, 0xBF, 0x1E, 0xA1] # original, to break
wasm_data_at_16 = [0x2C, 0xE4, 0x0E, 0x7B, 0x77, 0x02, 0x1A, 0x5D] # password, for testing


memory = bytearray(3 * 8) # We only need 3 * 8 bytes for this example

def rotr(rotation_amount):
    val0 = struct.unpack('<I', memory[0:4])[0]
    val4 = struct.unpack('<I', memory[4:8])[0]
    val0 = ((val0 >> rotation_amount) | (val0 << (32 - rotation_amount))) & 0xFFFFFFFF
    val4 = ((val4 >> rotation_amount) | (val4 << (32 - rotation_amount))) & 0xFFFFFFFF
    memory[0:4] = struct.pack('<I', val0)
    memory[4:8] = struct.pack('<I', val4)

def rotl(rotation_amount):
    val0 = struct.unpack('<I', memory[0:4])[0]
    val4 = struct.unpack('<I', memory[4:8])[0]
    val0 = ((val0 << rotation_amount) | (val0 >> (32 - rotation_amount))) & 0xFFFFFFFF
    val4 = ((val4 << rotation_amount) | (val4 >> (32 - rotation_amount))) & 0xFFFFFFFF
    memory[0:4] = struct.pack('<I', val0)
    memory[4:8] = struct.pack('<I', val4)

def check(input_text):
    # convert to bytes and check len
    input_bytes = input_text.encode('ascii', 'ignore')
    if len(input_bytes) != 8:
        raise ValueError("Input must be exactly 8 characters long.")
    
    # setup memory
    memory[:] = b'\x00' * len(memory)
    memory[:8] = input_bytes.ljust(8, b'\x00')[:8]
    memory[8:16] = bytes(wasm_data_at_8)
    memory[16:24] = bytes(wasm_data_at_16)
    
    for var1 in range(8):
        var5 = memory[var1] ^ memory[8 + var1]
        
        start = var1
        end = start + 4
        if end > len(memory):
            break
        
        try:
            temp_loaded_i32 = struct.unpack('<I', memory[start:end])[0]
            var7 = temp_loaded_i32 & 0xFFFFFF00
        except:
            var7 = 0
        
        value_to_store = (var5 & 0xFF) + (var7 & 0xFFFFFFFF)
        value_to_store = value_to_store & 0xFFFFFFFF
        try:
            memory[start:end] = struct.pack('<I', value_to_store)
        except:
            pass

        call_param = var5 % 32
        func_index = var5 % 2
        if func_index == 0:
            rotr(call_param)
        else:
            rotl(call_param)

    final_val_at_0 = struct.unpack('<Q', memory[0:8])[0]
    target_val_at_16 = struct.unpack('<Q', memory[16:24])[0]
    return 1 if final_val_at_0 == target_val_at_16 else 0


# Main program

def test_if_this_ducking_works():
    NB_TESTS = 3_000
    ascii_printable = [chr(i) for i in range(32, 126+1)]
    for i in range(NB_TESTS):
        input_text = ''.join(random.choice(ascii_printable) for _ in range(8))
        result_python = check(0, input_text)
        result_wasm = wasm_check(input_text)
        assert result_python == result_wasm, f"Mismatch for input {input_text}: {result_python} vs {result_wasm}"
    
    assert wasm_check(VALID_PASSWORD) == 1, "The valid password should return 1."
    NB_TESTS += 1
    
    print(f"All {NB_TESTS} tests passed successfully!")

if __name__ == "__main__":
    test_if_this_ducking_works()
    print()

    input1 = VALID_PASSWORD
    print("Input:", input1)
    result = check(0, input1)
    print("Access Granted!" if result == 1 else "Access Denied.")
    print("Expected : Access Granted!")
    print()

    input2 = "pass1234"
    print("Input:", input2)
    result = check(0, input2)
    print("Access Granted!" if result == 1 else "Access Denied.")
    print("Expected : Access Denied.")
    print()

    print("Input:", input1)
    result = check(0, input1)
    print("Access Granted!" if result == 1 else "Access Denied.")
    print("Expected : Access Granted!")
    print()