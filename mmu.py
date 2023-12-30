import debug
import random

a, b, up, down, left, right, start, select = 0, 0, 0, 0, 0, 0, 0, 0

random.seed()

cartrage_type = 0
rom_size = 0
ram_size = 0

in_bios = 1
rom_bank = 0
ram_bank = 0
write_protect = 1

bootloader = bytearray([])
memory = bytearray([])
for i in range(0x10000):
    memory.append(random.randint(0, 0xff))
cart = bytearray([])
for i in range(0x100000):
    cart.append(0)
ram = bytearray([])
for i in range(0x8000):
    ram.append(random.randint(0, 0xff))


    
memory[0xff40] = 0    
memory[0xff43] = 0


def get_controls():
    if memory[0xff00] & 0xf0 == 0x20:
        temp = 0x2f
        if right:
            temp -= 0x1
        if left:
            temp -= 0x2
        if up:
            temp -= 0x4
        if down:
            temp -= 0x8
        return temp
    elif memory[0xff00] & 0xf0 == 0x10:
        temp = 0x1f
        if a:
            temp -= 0x1
        if b:
            temp -= 0x2
        if select:
            temp -= 0x4
        if start:
            temp -= 0x8
        return temp
    else:
       return memory[0xff00]



def read(addr):
    global cartrage_type
    return mc_read_mapping[cartrage_type](addr)


def write(addr, value, reg):
    global cartrage_type
    return mc_write_mapping[cartrage_type](addr, value, reg)
    

def read_mc0(addr):
    global a, b, up, down, left, right, start, select
    if 0 <= addr < 0x8000:
        if 0 <= addr < 256:
            if in_bios == 1:
                return bootloader[addr]
            else:
                return cart[addr]
        else:
            return cart[addr]
    else:
        if 0xa000 <= addr < 0xc000:
            return 0xff
        if addr == 0xff00:
            return get_controls()
        else:
            return memory[addr]


def read_mc1(addr):
    global a, b, up, down, left, right, start, select, rom_bank
    if 0 <= addr < 0x8000:
        if 0 <= addr < 256:
            if in_bios == 1:
                return bootloader[addr]
            else:
                return cart[addr]
        elif 0x4000 <= addr < 0x8000:
            if rom_bank == 0:
                return cart[addr]
            return cart[(addr - 0x4000) + (0x4000 * rom_bank)]
        else:
            return cart[addr]
    else:
        if addr == 0xff00:
            return get_controls()
        else:
            return memory[addr]
        
        

def read_mc3(addr):
    global a, b, up, down, left, right, start, select, rom_bank
    if 0 <= addr < 0x8000:
        if 0 <= addr < 256:
            if in_bios == 1:
                return bootloader[addr]
            else:
                return cart[addr]
        elif 0x4000 <= addr < 0x8000:
            if rom_bank == 0:
                return cart[addr]
            return cart[(addr - 0x4000) + (0x4000 * rom_bank)]
        else:
            return cart[addr]
    elif 0xa000 <= addr < 0xc000:
        return ram[(ram_bank * 0x2000) + (addr - 0xa000)]
    else:
        if addr == 0xff00:
            return get_controls()
        else:
            return memory[addr]


def do_dma(addr):
    global memory
    for i in range(0xA0):
        write(0, 0xfe00 + i, read((addr * 0x100) + i))
        

def write_mc0(clock, addr, value):
    global in_bios
    if 0x8000 <= addr < 0xa000:
        memory[addr] = value
    elif 0xc000 <= addr < 0xde00:
        memory[addr] = value
        memory[addr + 0x2000] = value
    elif 0xde00 <= addr < 0xe000:
        memory[addr] = value
    elif 0xe000 <= addr < 0xfe00:
        memory[addr] = value
        memory[addr - 0x2000] = value
    elif 0xfe00 <= addr < 0xfea0:
        memory[addr] = value
    elif 0xff00 <= addr < 0x10000:
        if addr == 0xff00:
            memory[0xff00] = value | 0xf
        if addr == 0xff04:
            memory[0xff04] = 0
        elif addr == 0xff40:
            if memory[0xff40] & ~(1 << 7):
                if value & (1 << 7):
                    clock = 0
            memory[addr] = value
        elif addr == 0xff44:
            memory[addr] = 0
            clock = 0
        elif addr == 0xff46:
            do_dma(value)
        elif addr == 0xff50:
            in_bios = 0
        else:
            memory[addr] = value


def write_mc1(clock, addr, value):
    global in_bios, write_protect, rom_bank, ram_bank
    if 0x2000 <= addr <= 0x4000:
            rom_bank = value
    elif 0x8000 <= addr < 0xa000:
        memory[addr] = value
    elif 0xc000 <= addr < 0xde00:
        memory[addr] = value
        memory[addr + 0x2000] = value
    elif 0xde00 <= addr < 0xe000:
        memory[addr] = value
    elif 0xe000 <= addr < 0xfe00:
        memory[addr] = value
        memory[addr - 0x2000] = value
    elif 0xfe00 <= addr < 0xfea0:
        memory[addr] = value
    elif 0xff00 <= addr < 0x10000:
        if addr == 0xff00:
            memory[0xff00] = value | 0xf
        if addr == 0xff04:
            memory[0xff04] = 0
        elif addr == 0xff40:
            if memory[0xff40] & (1 << 7):
                if value & (1 << 7):
                    clock = 0
            memory[addr] = value
        elif addr == 0xff44:
            memory[addr] = 0
            clock = 0
        elif addr == 0xff46:
            do_dma(value)
        elif addr == 0xff50:
            in_bios = 0
        else:
            memory[addr] = value


def write_mc3(clock, addr, value):
    global in_bios, write_protect, rom_bank, ram_bank
    if 0 <= addr < 0x2000:
        if value == 0x0a:
            write_protect = 0
        else:
            write_protect = 1
    elif 0x2000 <= addr <= 0x4000:
            rom_bank = value
    elif 0x4000 <= addr < 0x6000:
            ram_bank = value % 3
    elif 0x6000 <= addr < 0x8000:
        return 0 #TODO implement RTC
    elif 0x8000 <= addr < 0xa000:
        memory[addr] = value
    elif 0xa000 <= addr < 0xc000:
        if write_protect == 0:
            ram[(ram_bank * 0x2000) + (addr - 0xa000)] = value
    elif 0xc000 <= addr < 0xde00:
        memory[addr] = value
        memory[addr + 0x2000] = value
    elif 0xde00 <= addr < 0xe000:
        memory[addr] = value
    elif 0xe000 <= addr < 0xfe00:
        memory[addr] = value
        memory[addr - 0x2000] = value
    elif 0xfe00 <= addr < 0xfea0:
        memory[addr] = value
    elif 0xff00 <= addr < 0x10000:
        if addr == 0xff00:
            memory[0xff00] = value | 0xf
        if addr == 0xff04:
            memory[0xff04] = 0
        elif addr == 0xff40:
            if memory[0xff40] & (1 << 7):
                if value & (1 << 7):
                    clock = 0
            memory[addr] = value
        elif addr == 0xff44:
            memory[addr] = 0
            clock = 0
        elif addr == 0xff46:
            do_dma(value)
        elif addr == 0xff50:
            in_bios = 0
        else:
            memory[addr] = value



mc_read_mapping = [read_mc0, read_mc1, None, read_mc3]
mc_write_mapping = [write_mc0, write_mc1, None, write_mc3]

        
