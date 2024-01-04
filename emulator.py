import cpu
import struct
import gpu
import time
import interrupts
import debug
import pygame


def do_cpu(reg, interrupts):
    b = [0, 0, 0]
    length = cpu.length_lookup[cpu.mmu.read(reg['pc'])]
    for i in range(length):
        b[i] = cpu.mmu.read(reg['pc'] + i)
    if debug.level > 0:
        debug.l.write('\nAt address: ')
        debug.l.write(hex(reg['pc']))
        debug.l.write(' Cartridge address: ')
        if 0x0000 <= reg['pc'] < 0x4000:
            debug.l.write(hex(reg['pc']))
        elif 0x4000 <= reg['pc'] < 0x8000:
            addr = (reg['pc'] - 0x4000) + (0x4000 * cpu.mmu.rom_bank)
            debug.l.write(hex(addr))
        else:
            debug.l.write("N\A ")
        debug.l.write(f'Rom Bank:{hex(cpu.mmu.rom_bank)} Ram bank:{hex(cpu.mmu.ram_bank)}')
        debug.l.write('\n')
        debug.debug_log(length, debug.l, b, reg)
    reg['pc'] += length
    clock = cpu.opcode_lookup[int(b[0])](reg, b, interrupts)
    return clock

    
def do_interrupts(run, reg, state):
    return interrupts.interrupts(run, reg, state)


def do_timing(clock, timer, div, reg):
    reg['clock'] += clock
    if reg['clock'] >= 70224:
        reg['clock'] -= 70224
    div += clock
    if div >= 256:
        div -= 256
        if cpu.mmu.memory[0xff04] == 255:
            cpu.mmu.memory[0xff04] = 0
        else:
            cpu.mmu.memory[0xff04] += 1
    if cpu.mmu.memory[0xff07] & 0x4:
        timer += clock
        if cpu.mmu.memory[0xff07] & 0x3 == 0:
            if timer >= 1000:
                if cpu.mmu.memory[0xff05] == 255:
                    cpu.mmu.memory[0xff05] = 0
                    cpu.mmu.memory[0xff0f] |= 0x4
                else:
                    cpu.mmu.memory[0xff05] += 1
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
                    cpu.mmu.memory[0xff05] -= 256
                    cpu.mmu.memory[0xff0f] |= 0x4
    elif cpu.mmu.memory[0xff07] & 0x4:
        timer += clock
        if cpu.mmu.memory[0xff07] & 0x3 == 3:
            if timer >= 256:
                cpu.mmu.memory[0xff05] += 1
                if cpu.mmu.memory[0xff05] >= 256:
                    cpu.mmu.memory[0xff05] -= 256
                    cpu.mmu.memory[0xff0f] |= 0x4
    return timer, div

        
def get_controls():
    events = pygame.event.get()
    for event in events:
        if event.type == 678:
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
        elif event.type == 679:
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


def main():
    t0, t1 = 0, 0
    screen = pygame.display.set_mode((160, 144))
    start_logging = 0x100000
    div = 0
    timer = 0
    boot_loader = 'DMG_quickboot.bin'
    filename = 'tetris.gb'
    cpu.loadboot(boot_loader)
    cpu.load(filename)
    gpu.frame = 0
    cpu.run = 1
    global reg
    reg = {'a': 0, 'f': 0, 'b': 0, 'c': 0, 'd': 0, 'e': 0, 'h': 0, 'l': 0, 'sp': 0, 'pc': 0, 'clock': 0}
    interrupt_state = [0, 0, 0]
    while 1:
        if gpu.frame == 1200:
            break
        if gpu.frame == 1100:
            debug.level = 1
        if reg['pc'] == start_logging:
            debug.level = 1
        cpu.run = do_interrupts(cpu.run, reg, interrupt_state)
        if cpu.run == 1:
            try:
                last_instruction = reg['pc']
                clock = do_cpu(reg, interrupt_state)
            except (IndexError, KeyError, ValueError):
                print (hex(reg['pc']))
                if cpu.mmu.read(last_instruction) == 0xcb:
                    print("Need to implement the following *CB* command:")
                    print(hex(cpu.mmu.read(last_instruction + 1)))
                    if debug.level > 0:
                        debug.l.write("Need to implement the following *CB* command:")
                        debug.l.write(str(hex(cpu.mmu.read(last_instruction + 1))))
                        debug.l.write('\n')
                else:
                    print("Need to implement the following command:")
                    print(hex(cpu.mmu.read(last_instruction)))
                    if debug.level > 0:
                        debug.l.write("Need to implement the following command:")
                        debug.l.write(str(hex(cpu.mmu.read(last_instruction))))
                        debug.l.write('\n')
                break
        else:
            clock = 4
        timer, div = do_timing(clock, timer, div, reg)
        gpu.do_gpu(screen, reg)

    print("The PC is currently at:")
    print(hex(last_instruction))
    print(cpu.mmu.rom_bank)
    debug.level = 1
    if debug.level > 0:
        debug.l.write("The PC is currently at:")
        debug.l.write(hex(last_instruction))
        debug.l.write('\n')
        g = open('memdump.bin', 'wb')
        i = 0x0
        for i in range(len(cpu.mmu.memory)):
            g.write(struct.pack("B", cpu.mmu.memory[i]))
            if i % 0x1000 == 0:
                print(hex(i))
            i += 1
        time.sleep(10)
        g.close()
        g = open('ramdump.bin', 'wb')
        i = 0x0
        for i in range(len(cpu.mmu.ram)):
            g.write(struct.pack("B", cpu.mmu.ram[i]))
            if i % 0x1000 == 0:
                print(hex(i))
            i += 1
        time.sleep(10)
        g.close()
    debug.l.close()

main()
