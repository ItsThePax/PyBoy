import mmu
import debug
IME = 0
EI = 0
DI = 0


def interrupts(running, register):
    global EI, DI, IME
    if debug.level > 0:
        debug.l.write('EL:{0} DI:{1} IME:{2}\n' .format(EI, DI, IME))
    if EI > 0:
        if debug.level > 0:
            debug.l.write('EI triggered: {0}\n' .format(EI))
        if EI > 1:
            IME = 1
            EI = 0
            if debug.level > 0:
                debug.l.write('IME enabled: {0}\n' .format(IME))
        else:
            EI += 1
    if DI > 0:
        if debug.level > 0:
            debug.l.write('DI triggered: {0}\n' .format(DI))
        if DI > 1:
            IME = 0
            DI = 0
            if debug.level > 0:
                debug.l.write('IME enabled: {0}\n' .format(IME))
        else:
            DI += 1
    if mmu.memory[0xff0f] & 0x1:
        if mmu.memory[0xffff] & 0x1:
            if IME:
                if debug.level > 0:
                    debug.l.write('IME enabled, ***vblank interrupt***\n\n')
                IME = 0
                mmu.write(0xff0f, 0)
                mmu.write(register['sp'] - 1, (register['pc'] >> 8))
                mmu.write(register['sp'] - 2, (register['pc'] & 0xff))
                register['sp'] -= 2
                register['pc'] = 0x40
                register['clock'] += 16
                
            else:
                if running == 0:
                    running == 1

    if mmu.memory[0xff0f] & 0x2:
        if mmu.memory[0xffff] & 0x2:
            if IME:
                if debug.level > 0:
                    print('***LCDC interrupt***')
                    debug.l.write('IME enabled, ***LCDC interrupt***')
                IME = 0
                mmu.write(0xff0f, 0)
                mmu.write(register['sp'] - 1, (register['pc'] >> 8))
                mmu.write(register['sp'] - 2, (register['pc'] & 0xff))
                register['sp'] -= 2
                register['pc'] = 0x48
                register['clock'] += 16
                
            else:
                if running == 0:
                    running == 1

    if mmu.memory[0xff0f] & 0x4:
        if mmu.memory[0xffff] & 0x4:
            if IME:
                if debug.level > 0:
                    print('***timer interrupt***')
                    debug.l.write('IME enabled, ***timer interrupt***')
                IME = 0
                mmu.write(0xff0f, 0)
                mmu.write(register['sp'] - 1, (register['pc'] >> 8))
                mmu.write(register['sp'] - 2, (register['pc'] & 0xff))
                register['sp'] -= 2
                register['pc'] = 0x50
                register['clock'] += 16
                
            else:
                if running == 0:
                    running == 1

    if mmu.memory[0xff0f] & 0x8:
        if mmu.memory[0xffff] & 0x8:
            if IME:
                if debug.level > 0:
                    print('***serial IO interrupt***')
                    debug.l.write('IME enabled, ***serial IO interrupt***')
                IME = 0
                mmu.write(0xff0f, 0)
                mmu.write(register['sp'] - 1, (register['pc'] >> 8))
                mmu.write(register['sp'] - 2, (register['pc'] & 0xff))
                register['sp'] -= 2
                register['pc'] = 0x58
                register['clock'] += 16
                
            else:
                if running == 0:
                    running == 1

    if mmu.memory[0xff0f] & 0x16:
        if mmu.memory[0xffff] & 0x16:
            if IME:
                if debug.level > 0:
                    print('***input interrupt***')
                    debug.l.write('IME enabled, ***input interrupt***')
                IME = 0
                mmu.write(0xff0f, 0)
                mmu.write(register['sp'] - 1, (register['pc'] >> 8))
                mmu.write(register['sp'] - 2, (register['pc'] & 0xff))
                register['sp'] -= 2
                register['pc'] = 0x60
                register['clock'] += 16
                
            else:
                if running == 0:
                    running == 1
                    
