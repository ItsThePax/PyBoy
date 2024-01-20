dividers = [1024, 16, 64, 256]
interruptTimer = 0x04
timerEnable = 0x4


class Timer:
    def __init__(self, mmu):
        self.mmu = mmu
        self.divH = self.mmu.registers[0x4]
        self.tima = self.mmu.registers[0x5]
        self.tma = self.mmu.registers[0x6]

    timerRaw = 0
    mode = 0    
    divL = 0

    def step(self, ticks):
        self.divL += ticks
        if self.divL > 0xff:
            self.divL %= 256
            self.mmu.registers[0x4] = (self.mmu.registers[0x4] + 1) % 256
        if self.mmu.registers[0x7] & timerEnable:
            self.timerRaw += ticks
            if self.timerRaw > dividers[self.mode]:
                self.timerRaw %= dividers[self.mode]
                if self.mmu.registers[0x5] == 0xff:
                    self.mmu.registers[0x5] = self.mmu.registers[0x6]
                    self.mmu.registers[0x0f] |= interruptTimer
                else:
                    self.mmu.registers[0x5] += 1

    def printStatus(self):
        print(f"Enabled: {self.run}, Div: {self.mmu.registers[0x4]} {self.divL}, "
              f"internal timer: {self.timerRaw}, mode: {self.mode}, "
              f"timer divider: {dividers[self.mode]}, "
              f"0xff04: {self.mmu.registers[0x4]}, "
              f"0xff05: {self.mmu.registers[0x5]}")
    ps = printStatus
    
