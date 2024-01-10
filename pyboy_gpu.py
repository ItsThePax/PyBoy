class DMG_gpu():
    def __init__(self):
        self.mmu = []

    line = 0
    dot = 0

    def reset(self): #might not need this fucntion
        pass

    def printStaus(self):
        print(f"0xff40:0x{self.mmu.read(0xff40):02x} 0xff44:0x{self.mmu.read(0xff44):02x}")
        

    def step(self, clock):
        self.dot = clock % 456
        self.line = clock // 456
        self.mmu.write(0xff44, self.line)
        if self.line > 143:
            self.updateLCDMode(1)
        else:
            if self.dot < 80:
                self.updateLCDMode(2)
            elif self.dot < 230:
                self.updateLCDMode(3)
            elif self.dot >= 230:
                self.updateLCDMode(0)


    def updateLCDMode(self, mode):
        value = self.mmu.read(0xff41)
        value &= 0xfa #clear last 2 bits
        self.mmu.write(0xff41, value | mode) #write back with new mode
    

