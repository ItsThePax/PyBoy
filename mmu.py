import cpu
import debug
import random

a, b, up, down, left, right, start, select = 0, 0, 0, 0, 0, 0, 0, 0

random.seed()

cartrage_type = 0
rom_size = 0
ram_size = 0

in_bios = 1
rom_bank = 0
ram_bank = 1
customboot = 0
write_protect = 1


bootloader = [
    0x31, 0xfe, 0xff, 0xaf, 0x21, 0xff, 0x9f, 0x32, 0xcb, 0x7c, 0x20, 0xfb, 0x21, 0x26, 0xff, 0x0e,
    0x11, 0x3e, 0x80, 0x32, 0xe2, 0x0c, 0x3e, 0xf3, 0xe2, 0x32, 0x3e, 0x77, 0x77, 0x3e, 0xfc, 0xe0,
    0x47, 0x11, 0x04, 0x01, 0x21, 0x10, 0x80, 0x1a, 0xcd, 0x95, 0x00, 0xcd, 0x96, 0x00, 0x13, 0x7b,
    0xfe, 0x34, 0x20, 0xf3, 0x11, 0xd8, 0x00, 0x06, 0x08, 0x1a, 0x13, 0x22, 0x23, 0x05, 0x20, 0xf9,
    0x3e, 0x19, 0xea, 0x10, 0x99, 0x21, 0x2f, 0x99, 0x0e, 0x0c, 0x3d, 0x28, 0x08, 0x32, 0x0d, 0x20,
    0xf9, 0x2e, 0x0f, 0x18, 0xf3, 0x67, 0x3e, 0x64, 0x57, 0xe0, 0x42, 0x3e, 0x91, 0xe0, 0x40, 0x04,
    0x1e, 0x02, 0x0e, 0x0c, 0xf0, 0x44, 0xfe, 0x90, 0x20, 0xfa, 0x0d, 0x20, 0xf7, 0x1d, 0x20, 0xf2,
    0x0e, 0x13, 0x24, 0x7c, 0x1e, 0x83, 0xfe, 0x62, 0x28, 0x06, 0x1e, 0xc1, 0xfe, 0x64, 0x20, 0x06,
    0x7b, 0xe2, 0x0c, 0x3e, 0x87, 0xe2, 0xf0, 0x42, 0x90, 0xe0, 0x42, 0x15, 0x20, 0xd2, 0x05, 0x20,
    0x4f, 0x16, 0x20, 0x18, 0xcb, 0x4f, 0x06, 0x04, 0xc5, 0xcb, 0x11, 0x17, 0xc1, 0xcb, 0x11, 0x17,
    0x05, 0x20, 0xf5, 0x22, 0x23, 0x22, 0x23, 0xc9, 0xce, 0xed, 0x66, 0x66, 0xcc, 0x0d, 0x00, 0x0b,
    0x03, 0x73, 0x00, 0x83, 0x00, 0x0c, 0x00, 0x0d, 0x00, 0x08, 0x11, 0x1f, 0x88, 0x89, 0x00, 0x0e,
    0xdc, 0xcc, 0x6e, 0xe6, 0xdd, 0xdd, 0xd9, 0x99, 0xbb, 0xbb, 0x67, 0x63, 0x6e, 0x0e, 0xec, 0xcc,
    0xdd, 0xdc, 0x99, 0x9f, 0xbb, 0xb9, 0x33, 0x3e, 0x3c, 0x42, 0xb9, 0xa5, 0xb9, 0xa5, 0x42, 0x3c,
    0x21, 0x04, 0x01, 0x11, 0xa8, 0x00, 0x1a, 0x13, 0xbe, 0x20, 0xfe, 0x23, 0x7d, 0xfe, 0x34, 0x20,
    0xf5, 0x06, 0x19, 0x78, 0x86, 0x23, 0x05, 0x20, 0xfb, 0x86, 0x20, 0xfe, 0x3e, 0x01, 0xe0, 0x50
]

externalbootloader = {}
memory = {}
cart = {}
ram = {}

i = 0
while i <= 0xffff:
    memory[i] = random.randint(0, 255)
    i += 1

while i <= 0xffff:
    ram[i] = random.randint(0, 255)
    i += 1

memory[0xff40] = 0    
memory[0xff43] = 0

i = 0
for i in range (0x100):
    externalbootloader[i] = 0


def get_controls():
    if memory[0xff00] & 0xf0 == 0x20:
        temp = 0x2f
        if right:
            debug.l.write('RIGHT')
            temp -= 0x1
            print('right')
        if left:
            temp -= 0x2
            print('left')
        if up:
            temp -= 0x4
            print('up')
        if down:
            temp -= 0x8
            print('down')
        return temp
    elif memory[0xff00] & 0xf0 == 0x10:
        temp = 0x1f
        if a:
            temp -= 0x1
            print('a')
        if b:
            temp -= 0x2
            print('b')
        if select:
            temp -= 0x4
            print('select')
        if start:
            temp -= 0x8
            print('start')
        return temp
    else:
       return memory[0xff00]


def read(addr):
    if cartrage_type == 0:
        return read_mc0(addr)
    elif 0xf <= cartrage_type < 0x14:
        return read_mc3(addr)


def write(addr, value):
    if cartrage_type == 0:
        return write_mc0(addr, value)
    elif 0xf <= cartrage_type < 0x14:
        return write_mc3(addr, value)
    

def read_mc0(addr):
    global a, b, up, down, left, right, start, select
    if 0 <= addr < 0x8000:
        if 0 <= addr < 256:
            if in_bios == 1:
                if customboot == 1:
                    return externalbootloader[addr]
                else:
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
        

def read_mc3(addr):
    global a, b, up, down, left, right, start, select, rom_bank
    if 0 <= addr < 0x8000:
        if 0 <= addr < 256:
            if in_bios == 1:
                if customboot == 1:
                    return externalbootloader[addr]
                else:
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


def do_dma(addr):
    global memory
    for i in range(0xA0):
        write(0xfe00 + i, read((addr * 0x100) + i))
        

def write_mc0(addr, value):
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
                    cpu.reg['clock'] = 0
            memory[addr] = value
        elif addr == 0xff44:
            memory[addr] = 0
            cpu.reg['clock'] = 0
        elif addr == 0xff46:
            do_dma(value)
        elif addr == 0xff50:
            in_bios = 0
        else:
            memory[addr] = value


def write_mc3(addr, value):
    global in_bios, write_protect, rom_bank, ram_bank
    if 0 <= addr < 0x2000:
        if value == 0x0a:
            write_protect = 0
        else:
            write_protect = 1
    elif 0x2000 <= addr <= 0x4000:
            rom_bank = value
    elif 0x4000 <= addr < 0x6000:
            ram_bank = value
    elif 0x6000 <= addr < 0x8000:
        return 0 #TODO implement RTC
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
                    cpu.reg['clock'] = 0
            memory[addr] = value
        elif addr == 0xff44:
            memory[addr] = 0
            cpu.reg['clock'] = 0
        elif addr == 0xff46:
            do_dma(value)
        elif addr == 0xff50:
            in_bios = 0
        else:
            memory[addr] = value





        
