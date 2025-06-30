from shellcode import shellcode


class VirtualMachine:
    def __init__(self, bytecode):
        self.bytecode = bytecode
        self.stack = []
        self.registers = [0] * 8
        self.flags = [0] * 8
        self.pc = 0
        self.running = True
        
        self.opcode_table = {
            34: ("ADD_REG", 2),    # reg_dest, reg_src
            145: ("ADD_IMM", 2),   # reg_dest, value
            216: ("AND_IMM", 2),   # reg_dest, value
            205: ("READ_INPUT", 1),# reg_dest
            195: ("JUMP_ABS", 1),  # address
            16: ("JUMP_COND", 1),  # address
            65: ("JUMP_REL_COND", 1),# offset
            30: ("READ_CHAR", 2),  # reg_dest, reg_src
            126: ("MOV_REG", 2),   # reg_dest, reg_src
            194: ("MOV_IMM", 2),   # reg_dest, value
            115: ("POP", 1),       # reg_dest
            120: ("PUSH", 1),      # reg_src
            166: ("HALT", 0),      # No operands
            97: ("SHIFT_RIGHT", 2),# reg_dest, shift
            201: ("CMP", 2),       # reg_a, reg_b
            53: ("XOR_IMM", 2)     # reg_dest, value
        }
        
    def fetch(self):
        if self.pc >= len(self.bytecode):
            raise IndexError("End of bytecode reached")
        instruction = self.bytecode[self.pc]
        self.pc += 1
        return instruction

def disassemble(bytecode):
    vm = VirtualMachine(bytecode)
    buffer = ""
    
    while vm.pc < len(vm.bytecode):
        current_pc = vm.pc
        try:
            opcode = vm.fetch()
            
            if opcode not in vm.opcode_table:
                print("[!] Disassembler interrupted: the shellcode is malformed or incomplete.")
                print(f"[{current_pc:04x}] UNKNOWN_OPCODE: {opcode}")
                break 
            
            instruction_info = vm.opcode_table[opcode]
            mnemonic = instruction_info[0]
            num_operands = instruction_info[1]
            
            operands = []
            for _ in range(num_operands):
                if vm.pc < len(vm.bytecode):
                    operands.append(vm.fetch())
                else:
                    print("[!] Disassembler interrupted: the shellcode is malformed or incomplete.")
                    print(f"[{current_pc:04x}] {mnemonic} {' '.join(map(str, operands))} <TRUNCATED_OPERANDS>")
                    return
            
            operand_str = ""
            if mnemonic.startswith(("MOV", "ADD", "AND", "XOR", "SHR")):
                if len(operands) == 2:
                    operand_str = f"R{operands[0]}, {operands[1] if mnemonic.endswith('_IMM') or mnemonic.startswith('SHR') else f'R{operands[1]}'}"
            elif mnemonic == "READ_INPUT" or mnemonic == "POP" or mnemonic == "PUSH":
                if len(operands) == 1:
                    operand_str = f"R{operands[0]}"
            elif mnemonic == "READ_CHAR":
                 if len(operands) == 2:
                    operand_str = f"R{operands[0]}, R{operands[1]}"
            elif mnemonic == "CMP":
                 if len(operands) == 2:
                    operand_str = f"R{operands[0]}, R{operands[1]}"
            elif mnemonic.startswith("JUMP"):
                if len(operands) == 1:
                    operand_str = f"{operands[0]}"
            
            buffer += f"[{current_pc:04x}] {mnemonic} {operand_str}".strip()
            buffer += "\n"
        except IndexError as e:
            print(f"[X] Error disassembling at address {current_pc:04x}: {e}")
            break
    
    with open('shellcode-py.txt', 'w') as f:
        f.write(buffer)

    print("[+] End of disassembly")


# Main program
disassemble(shellcode)