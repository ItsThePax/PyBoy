import cpu
import struct
import pygame
import gpu
import time
import interrupts
import debug

t0, t1 = 0, 0
screen = pygame.display.set_mode((160, 144))
start_logging = 0x48c
last_instruction = 0
run = 1
new_div = 0


filename = 'roms/Tetris (World).gb'


def do_cpu():
    global last_instruction
    b1, b2 = 0, 0
    b0 = cpu.mmu.read(cpu.reg['pc'])
    length = cpu.length_lookup[int(b0)]
    last_instruction = cpu.reg['pc']
    if debug.level > 0:
        debug.l.write('\nAt address: ')
        debug.l.write(hex(cpu.reg['pc']))
        debug.l.write('\n')
    if length == 1:
        cpu.reg['pc'] += 1
        cpu.opcode_lookup[int(b0)](cpu.reg)
    elif length == 2:
        b1 = cpu.mmu.read(cpu.reg['pc'] + 1)
        cpu.reg['pc'] += 2
        cpu.opcode_lookup[int(b0)](cpu.reg, b1)
    else:
        b1 = cpu.mmu.read(cpu.reg['pc'] + 1)
        b2 = cpu.mmu.read(cpu.reg['pc'] + 2)
        cpu.reg['pc'] += 3
        cpu.opcode_lookup[int(b0)](cpu.reg, b1, b2)
    if debug.level > 0:
        debug.debug_log(length, debug.l, b0, b1, b2, cpu.reg) 

    
def do_interrupts(run, reg):
    interrupts.interrupts(run, reg)


def get_controls():    
    for event in pygame.event.get():
        if event.type == 2:
            if event.key == 97:
                cpu.mmu.a = 1
            elif event.key == 115:
                cpu.mmu.b = 1
            elif event.key == 276:
                cpu.mmu.left = 1
            elif event.key == 273:
                cpu.mmu.up = 1
            elif event.key == 274:
                cpu.mmu.down = 1
            elif event.key == 275:
                cpu.mmu.right = 1
            elif event.key == 13:
                cpu.mmu.start = 1
            elif event.key == 32:
                cpu.mmu.select = 1
            cpu.mmu.memory[0xff0f] |= 0x10
        elif event.type == 3:
            if event.key == 97:
                cpu.mmu.a = 0
            elif event.key == 115:
                cpu.mmu.b = 0
            elif event.key == 276:
                cpu.mmu.left = 0
            elif event.key == 273:
                cpu.mmu.up = 0
            elif event.key == 274:
                cpu.mmu.down = 0
            elif event.key == 275:
                cpu.mmu.right = 0
            elif event.key == 13:
                cpu.mmu.start = 0
            elif event.key == 32:
                cpu.mmu.select = 0


cpu.load(filename)
while 1:
    if cpu.reg['pc'] == start_logging:
        debug.level = 1
    do_interrupts(run, cpu.reg)
    if run == 1:
        try:
            do_cpu()
        except KeyError:
            if 0xcb == last_instruction:
                print("Need to implement the following *CB* command:")
                print(hex(cpu.mmu.read(last_instruction)))
                if debug.level > 0:
                    debug.l.write("Need to implement the following *CB* command:")
                    debug.l.write(str(hex(cpu.mmu.read(last_instruction))))
                    debug.l.write('\n')
            else:
                print("Need to implement the following command:")
                print(hex(cpu.mmu.read(last_instruction)))
                if debug.level > 0:
                    debug.l.write("Need to implement the following command:")
                    debug.l.write(str(hex(cpu.mmu.read(last_instruction))))
                    debug.l.write('\n')
            break
        if cpu.mmu.memory[0xff40] & (1 << 7):
            if debug.level > 0:
                debug.l.write('At line: {0}\n' .format(cpu.mmu.memory[0xff44]))
    if run == 0:
        cpu.reg['clock'] += 4
    if cpu.reg['clock'] >= 70224:
        cpu.reg['clock'] -= 70224
    old_div = cpu.reg['clock'] % 256
    if old_div <= new_div:
        cpu.mmu.memory[0xff04] += 1
        cpu.mmu.memory[0xff04] &= 0xff
        new_div = old_div
    gpu.do_gpu(screen)
    get_controls()
    
     
print("The PC is currently at:")
print(hex(last_instruction))
if debug.level > 0:
    debug.l.write("The PC is currently at:")
    debug.l.write(hex(last_instruction))
    debug.l.write('\n')
    g = open('memdump.bin', 'wb')
    i = 0x0
    while i <= 0xffff:
        g.write(struct.pack("B", cpu.mmu.memory[i]))
        if i % 0x1000 == 0:
            print(hex(i))
        i += 1
    time.sleep(10)
    g.close()
debug.l.close()
