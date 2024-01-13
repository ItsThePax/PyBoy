interruptVblank = 0x01
interruptLCDC = 0x02
interruptTimer = 0x04
interruptSerial = 0x08
interruptControls = 0x10


vectorVblank = 0x40
vectorLCDC = 0x48
vectorTimer = 0x50
vectorSerial = 0x58
vectorControls = 0x60


class InterruptHandler:
    def __init__(self, cpu, mmu):
        self.cpu = cpu 
        self.mmu = mmu

    IME = 0

    def reset(self):
        self.IME = 0
    

    def step(self):
        if self.IME:
            interruptTriggered = self.mmu.read(0xff0f) & self.mmu.read(0xffff)
            if interruptTriggered:
                self.cpu.run = 1
                if interruptTriggered & interruptVblank:
                    self.mmu.write(
                        0xff0f, 
                        self.mmu.read(0xff0f) & ~interruptVblank
                        )
                    return self.cpu.serviceInterrupt(vectorVblank)
                if interruptTriggered & interruptLCDC:
                    self.mmu.write(
                        0xff0f, 
                        self.mmu.read(0xff0f) & ~interruptLCDC
                        )
                    return self.cpu.serviceInterrupt(vectorLCDC)
                if interruptTriggered & interruptTimer:
                    self.mmu.write(
                        0xff0f, 
                        self.mmu.read(0xff0f) & ~interruptTimer 
                        )
                    return self.cpu.serviceInterrupt(vectorTimer)
                if interruptTriggered & interruptSerial:
                    self.mmu.write(
                        0xff0f, 
                        self.mmu.read(0xff0f) & ~interruptSerial
                        )
                    return self.cpu.serviceInterrupt(vectorSerial)
                if interruptTriggered & interruptControls:
                    self.mmu.write(
                        0xff0f, 
                        self.mmu.read(0xff0f) & ~interruptControls
                        )
                    return self.cpu.serviceInterrupt(vectorControls)
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
