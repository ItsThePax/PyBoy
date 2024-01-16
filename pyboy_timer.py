dividers = [1024, 16, 64, 256]
interruptTimer = 0x04


class Timer:
    def __init__(self, mmu):
        self.mmu = mmu

    timerRaw = 0
    run = 0
    mode = 0    

    divL = 0
    divH = 0
    tima = 0
    tma = 0
    tac = 0

    def step(self, ticks):
        self.divL += ticks
        if self.divL > 0xff:
            self.divL %= 256
            self.divH += 1
            self.mmu.rawWriteMemory(0xff04, self.divH)
        if self.run:
            self.timerRaw += ticks
            if self.timerRaw > dividers[self.mode]:
                self.timerRaw %= dividers[self.mode]
                if self.tima == 0xff:
                    self.mmu.write(0xff05, self.tima)
                    self.mmu.write(0xff0f, self.mmu.read(0xff0f) 
                                   | interruptTimer)
                else:
                    self.mmu.write(0xff05, self.tima + 1)

    def printStatus(self):
        print(f"Enabled: {self.run}, Div: {self.divH} {self.divL}, "
              f"internal timer: {self.timerRaw}, mode: {self.mode}, "
              f"timer divider: {dividers[self.mode]}, "
              f"0xff04: {self.mmu.read(0xff04)}, "
              f"0xff05: {self.mmu.read(0xff05)}")
    ps = printStatus
    
