interruptVblank = 0x01
interruptLCDC = 0x02
interruptTimer = 0x04
interruptSerial = 0x08
interruptControls = 0x10

resetVblank = 0xfe
resetLCDC = 0xfd
resetTimer = 0xfb
resetSerial = 0xf7
resetControls = 0xef


vectorVblank = 0x40
vectorLCDC = 0x48
vectorTimer = 0x50
vectorSerial = 0x58
vectorControls = 0x60

#static masks for easy bit manipulation
resetBitMasks = bytes([0xfe, 0xfd, 0xfb, 0xf7, 
                       0xef, 0xdf, 0xbf, 0x7f])


class InterruptHandler:
    def __init__(self, cpu, mmu):
        self.cpu = cpu 
        self.mmu = mmu

    IME = 0
    
    def reset(self):
        self.IME = 0

    def step(self):
        interruptTriggered = (self.mmu.interruptEnabled 
                              & self.mmu.registers[0x0f])
        if self.IME:
            if interruptTriggered:
                self.cpu.run = 1
                self.IME = 0
                if interruptTriggered & interruptVblank:
                    self.mmu.registers[0x0f]  &= resetVblank
                    return self.cpu.serviceInterrupt(vectorVblank)
                if interruptTriggered & interruptLCDC:
                    self.mmu.registers[0x0f]  &= resetLCDC
                    return self.cpu.serviceInterrupt(vectorLCDC)
                if interruptTriggered & interruptTimer:
                    self.mmu.registers[0x0f]  &= resetTimer
                    return self.cpu.serviceInterrupt(vectorTimer)
                if interruptTriggered & interruptSerial:
                    self.mmu.registers[0x0f]  &= resetSerial
                    return self.cpu.serviceInterrupt(vectorSerial)
                if interruptTriggered & interruptControls:
                    self.mmu.registers[0x0f]  &= resetControls
                    return self.cpu.serviceInterrupt(vectorControls)
        else:
            if interruptTriggered:
                self.cpu.run = 1
        if self.cpu.DI:
            if self.cpu.DI == 2:
                self.IME = 0
                self.cpu.DI = 0
                return 0
            self.cpu.DI = 2
        if self.cpu.EI:
            if self.cpu.EI == 2:
                self.IME = 1
                self.cpu.EI = 0
                return 0
            self.cpu.EI = 2
        return 0
