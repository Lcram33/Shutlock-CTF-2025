from shellcode import shellcode


# Constants
HALT = False
RUN = True

class VirtualMachine:
    def __init__(self, bytecode):
        self.bytecode = bytecode
        self.stack = []
        self.registers = [0] * 8  # General registers
        self.flags = [0] * 8      # Flags registers
        self.pc = 0               # Program Counter
        self.running = RUN
        
        # opcodes table : [code instruction] -> associated method
        self.opcode_table = {
            34: self.add_reg,
            145: self.add_imm,
            216: self.and_imm,
            205: self.read_input,
            195: self.jump_abs,
            16: self.jump_cond,
            65: self.jump_rel_cond,
            30: self.read_char,
            126: self.mov_reg,
            194: self.mov_imm,
            115: self.pop,
            120: self.push,
            166: self.halt,
            97: self.shift_right,
            201: self.compare,
            53: self.xor_imm
        }
        
        # Starting VM
        if not self.execute():
            print("Mot de passe valide !")
        else:
            print("Mot de passe invalide !")
    
    def execute(self):
        """ Main loop of the VM """
        self.running = RUN
        while self.running:
            try:
                opcode = self.fetch()
            except:
                return 1  # Execution error
            
            if self.dispatch(opcode):
                return 1  # Instruction error
        return self.get_register(0)  # Final result in reg[0]
    
    def dispatch(self, opcode):
        """ Execute instruction corresponding to the opcode """
        if opcode in self.opcode_table:
            self.opcode_table[opcode]()
            return 0
        return 1  # unknown opcode
    
    # -----------------------------------------------------------------
    # Data access methods
    # -----------------------------------------------------------------
    def get_register(self, reg_id):
        return self.registers[reg_id]
    
    def set_register(self, reg_id, value):
        self.registers[reg_id] = value
    
    def fetch(self):
        """ Get byte pointed by PC and increment PC """
        instruction = self.bytecode[self.pc]
        self.pc += 1
        return instruction
    
    # -----------------------------------------------------------------
    # VM instructions
    # -----------------------------------------------------------------
    def mov_imm(self):
        """ Immediate MOV : reg[dest] = value """
        reg_dest = self.fetch()
        value = self.fetch()
        self.set_register(reg_dest, value)
    
    def mov_reg(self):
        """ Register MOV : reg[dest] = reg[src] """
        reg_dest = self.fetch()
        reg_src = self.fetch()
        self.set_register(reg_dest, self.get_register(reg_src))
    
    def add_imm(self):
        """ Immediate ADD : reg[dest] += value """
        reg_dest = self.fetch()
        value = self.fetch()
        self.set_register(reg_dest, self.get_register(reg_dest) + value)
    
    def add_reg(self):
        """ Register ADD : reg[dest] += reg[src] """
        reg_dest = self.fetch()
        reg_src = self.fetch()
        self.set_register(reg_dest, 
            self.get_register(reg_dest) + self.get_register(reg_src))
    
    def push(self):
        """ PUSH reg[src] """
        reg_src = self.fetch()
        self.stack.append(self.get_register(reg_src))
    
    def pop(self):
        """ POP to reg[dest] """
        reg_dest = self.fetch()
        self.set_register(reg_dest, self.stack.pop() if self.stack else 0)
    
    def jump_abs(self):
        """ Absolute JMP : PC = adress """
        address = self.fetch()
        self.pc = address
    
    def jump_cond(self):
        """ Conditional JMP : if flag[0]: PC = adress """
        address = self.fetch()
        if self.flags[0]:
            self.pc = address
    
    def jump_rel_cond(self):
        """ Relative conditional JMP : if flag[0]: PC += offset """
        offset = self.fetch()
        if self.flags[0]:
            self.pc += offset + 1
    
    def compare(self):
        """ CMP: Compare two registers and update flags"""
        reg_a = self.fetch()
        reg_b = self.fetch()
        a = self.get_register(reg_a)
        b = self.get_register(reg_b)
        
        # Update flags
        self.flags[0] = int(a == b)  # Equal
        self.flags[1] = int(a < b)   # Less than
    
    def read_input(self):
        """ INPUT: Read user input and store it in a register """
        reg_dest = self.fetch()
        user_input = input()
        self.set_register(reg_dest, user_input)
    
    def read_char(self):
        """ READ_CHAR: Extract the first character from a string in a register """
        reg_dest = self.fetch()
        reg_src = self.fetch()
        string = self.get_register(reg_src)
        
        if len(string) < 1:
            self.set_register(reg_dest, 0)
        else:
            # Store the first character and update the string
            self.set_register(reg_dest, ord(string[0]))
            self.set_register(reg_src, string[1:])
    
    def xor_imm(self):
        """ Immediate XOR : reg[dest] = int(reg[dest]) ^ value """
        reg_dest = self.fetch()
        value = self.fetch()
        current = int(self.get_register(reg_dest))
        self.set_register(reg_dest, current ^ value)
    
    def shift_right(self):
        """ SHR: reg[dest] >>= value """
        reg_dest = self.fetch()
        shift = self.fetch()
        self.set_register(reg_dest, self.get_register(reg_dest) >> shift)
    
    def and_imm(self):
        """ Immediate AND: reg[dest] &= value """
        reg_dest = self.fetch()
        value = self.fetch()
        self.set_register(reg_dest, self.get_register(reg_dest) & value)
    
    def halt(self):
        """ HALT: Stop the VM """
        self.running = HALT


# Launch the virtual machine with the provided shellcode (in shellcode.py for better readability)
vm = VirtualMachine(shellcode)
