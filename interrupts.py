import mmu
import cpu
import debug



def interrupts(running, register, state):
    if debug.level > 0:
        debug.l.write('EI:{0} DI:{1} IME:{2}\n' .format(state[0], state[1], state[2]))
    if state[0] > 0:
        if debug.level > 0:
            debug.l.write('EI triggered: {0}\n' .format(state[0]))
        if state[0] > 1:
            state[2] = 1
            state[0] = 0
            if debug.level > 0:
                debug.l.write('IME enabled: {0}\n' .format(state[2]))
        else:
            state[0] += 1
    elif state[1] > 0:
        if debug.level > 0:
            debug.l.write('DI triggered: {0}\n' .format(state[1]))
        if state[1] > 1:
            state[2] = 0
            state[1] = 0
            if debug.level > 0:
                debug.l.write('IME enabled: {0}\n' .format(state[2]))
        else:
            state[1] += 1
    if mmu.memory[0xff0f] & 0x1:
        if mmu.memory[0xffff] & 0x1:
            if state[2]:
                if debug.level > 0:
                    debug.l.write('IME enabled, ***vblank interrupt***\n\n')
                state[2] = 0
                running = 1
                mmu.write(register['clock'], 0xff0f, 0)
                mmu.write(register['clock'], register['sp'] - 1, (register['pc'] >> 8))
                mmu.write(register['clock'], register['sp'] - 2, (register['pc'] & 0xff))
                register['sp'] -= 2
                register['pc'] = 0x40
                register['clock'] += 16 
    elif mmu.memory[0xff0f] & 0x2:
        if mmu.memory[0xffff] & 0x2:
            if state[2]:
                if debug.level > 0:
                    debug.l.write('IME enabled, ***LCDC interrupt***\n\n')
                state[2] = 0
                running = 1
                mmu.write(register['clock'], 0xff0f, 0)
                mmu.write(register['clock'], register['sp'] - 1, (register['pc'] >> 8))
                mmu.write(register['clock'], register['sp'] - 2, (register['pc'] & 0xff))
                register['sp'] -= 2
                register['pc'] = 0x48
                register['clock'] += 16
    elif mmu.memory[0xff0f] & 0x4:
        if mmu.memory[0xffff] & 0x4:
            if state[2]:
                if debug.level > 0:
                    debug.l.write('IME enabled, ***tstate[2]r interrupt***\n\n')
                state[2] = 0
                running = 1
                mmu.write(register['clock'], 0xff0f, 0)
                mmu.write(register['clock'], register['sp'] - 1, (register['pc'] >> 8))
                mmu.write(register['clock'], register['sp'] - 2, (register['pc'] & 0xff))
                register['sp'] -= 2
                register['pc'] = 0x50
                register['clock'] += 16
    elif mmu.memory[0xff0f] & 0x8:
        if mmu.memory[0xffff] & 0x8:
            if state[2]:
                if debug.level > 0:
                    debug.l.write('IME enabled, ***serial IO interrupt***\n\n')
                state[2] = 0
                running = 1
                mmu.write(register['clock'], 0xff0f, 0)
                mmu.write(register['clock'], register['sp'] - 1, (register['pc'] >> 8))
                mmu.write(register['clock'], register['sp'] - 2, (register['pc'] & 0xff))
                register['sp'] -= 2
                register['pc'] = 0x58
                register['clock'] += 16
    elif mmu.memory[0xff0f] & 0x16:
        if mmu.memory[0xffff] & 0x16:
            if state[2]:
                if debug.level > 0:
                    debug.l.write('IME enabled, ***input interrupt***\n\n')
                state[2] = 0
                running = 1
                mmu.write(register['clock'], 0xff0f, 0)
                mmu.write(register['clock'], register['sp'] - 1, (register['pc'] >> 8))
                mmu.write(register['clock'], register['sp'] - 2, (register['pc'] & 0xff))
                register['sp'] -= 2
                register['pc'] = 0x60
                register['clock'] += 16
    return running
    
