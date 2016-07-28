import cpu
import struct
import pygame
import gpu
import time
import interrupts
import debug

t0, t1 = 0, 0
screen = pygame.display.set_mode((160, 144))
start_logging = 0x100
last_instruction = 0
run = 1
div = 0
timer = 0


filename = 'Tetris (World).gb'


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
        clock = cpu.opcode_lookup[int(b0)](cpu.reg)
    elif length == 2:
        b1 = cpu.mmu.read(cpu.reg['pc'] + 1)
        cpu.reg['pc'] += 2
        clock = cpu.opcode_lookup[int(b0)](cpu.reg, b1)
    else:
        b1 = cpu.mmu.read(cpu.reg['pc'] + 1)
        b2 = cpu.mmu.read(cpu.reg['pc'] + 2)
        cpu.reg['pc'] += 3
        clock = cpu.opcode_lookup[int(b0)](cpu.reg, b1, b2)
    if debug.level > 0:
        debug.debug_log(length, debug.l, b0, b1, b2, cpu.reg)
    return clock

    
def do_interrupts(run, reg):
    interrupts.interrupts(run, reg)


def do_timing(clock):
    global div, timer
    cpu.reg['clock'] += clock
    if cpu.reg['clock'] >= 70224:
        cpu.reg['clock'] -= 70224
    div += clock
    if div >= 256:
        div -= 256
        cpu.mmu.memory[0xff04] += 1
        if cpu.mmu.memory[0xff04] >= 256:
            cpu.mmu.memory[0xff04] -= 256
    if cpu.mmu.memory[0xff07] & 0x4:
        timer += clock
        if cpu.mmu.memory[0xff07] & 0x3 == 0:
            if timer >= 1000:
                cpu.mmu.memory[0xff05] += 1
                if cpu.mmu.memory[0xff05] >= 256:
                    cpu.mmumemory[0xff05] -= 256
                    cpu.mmu.memory[0xff0f] |= 0x4
    elif cpu.mmu.memory[0xff07] & 0x4:
        timer += clock
        if cpu.mmu.memory[0xff07] & 0x3 == 1:
            if timer >= 16:
                cpu.mmu.memory[0xff05] += 1
                if cpu.mmu.memory[0xff05] >= 256:
                    cpu.mmu.memory[0xff05] -= 256
                    cpu.mmu.memory[0xff0f] |= 0x4
    elif cpu.mmu.memory[0xff07] & 0x4:
        timer += clock
        if cpu.mmu.memory[0xff07] & 0x3 == 2:
            if timer >= 64:
                cpu.mmu.memory[0xff05] += 1
                if cpu.mmu.memory[0xff05] >= 256:
                    cpu.mmumemory[0xff05] -= 256
                    cpu.mmu.memory[0xff0f] |= 0x4
    elif cpu.mmu.memory[0xff07] & 0x4:
        timer += clock
        if cpu.mmu.memory[0xff07] & 0x3 == 3:
            if timer >= 256:
                cpu.mmu.memory[0xff05] += 1
                if cpu.mmu.memory[0xff05] >= 256:
                    cpu.mmumemory[0xff05] -= 256
                    cpu.mmu.memory[0xff0f] |= 0x4

        
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
if cpu.mmu.customboot == 1:
    cpu.loadboot('quickboot.bin')
while 1:
    if cpu.reg['pc'] == start_logging:
        debug.level = 1
    do_interrupts(run, cpu.reg)
    if run == 1:
        try:
            clock = do_cpu()
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
    else:
        clock = 4
    do_timing(clock)
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
