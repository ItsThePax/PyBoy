import sys
import random
import pyboy_cpu
import pyboy_gpu
import pyboy_interrupt
import pyboy_timer

random.seed()

biosFile = "DMG_rom.bin"
cartridgeFile = "tetris.gb"


class Pyboy:
    def __init__(self, cartridgeFile, biosFile):
        self.cpu = pyboy_cpu.Cpu(cartridgeFile, biosFile)
        self.mmu = self.cpu.mmu
        self.gpu = pyboy_gpu.DMG_gpu(self.mmu)
        self.interrupts = pyboy_interrupt.InterruptHandler(self.cpu, self.mmu)
        self.timer = pyboy_timer.Timer(self.mmu)
        self.cpu.interrupts = self.interrupts
        self.mmu.timer = self.timer
        self.mmu.gpu = self.gpu
    
    def run(self):
        while (True):  # run forever until error or break
            self.step()
    
    def runDB(self):
            while True:
                self.step()
                self.cpu.ps()

    def runTo(self, target):  # must match pc exactly
        if self.cpu.regPC.read() == target:
            self.step()
        while self.cpu.regPC.read() != target:
            self.step()
        self.cpu.ps()

    def runToDB(self, target):  # must match pc exactly
        if self.cpu.regPC.read() == target:
            self.step()
            self.cpu.ps()
        while self.cpu.regPC.read() != target:
            self.step()
            self.cpu.ps()

    def step(self):
        ticks = self.interrupts.step()
        if self.cpu.run == 1:
            ticks += self.cpu.step()
        else:
            ticks += 4
        self.timer.step(ticks)
        self.gpu.step(ticks)

    def stepOver(self):
        if self.cpu.nextInstruction[0] in [0x18, 0xc3, 0xc7, 0xcf, 0xd7, 
                                           0xdf, 0xe7, 0xef, 0xf7, 0xff]:
            self.step()
        else:
            self.runTo(self.cpu.regPC.read() 
                       + self.cpu.opcodeLength[self.cpu.nextInstruction[0]])

    def stepDB(self):
        self.cpu.fni() # fetch next instruction
        self.cpu.pni() # print next instruction
        self.step()
        self.cpu.ps()

    def stepOverDB(self):
        self.cpu.fni() # fetch next instruction
        self.cpu.pni() # print next instruction
        if self.cpu.nextInstruction[0] in [0x18, 0xc3, 0xc7, 0xcf, 0xd7, 
                                           0xdf, 0xe7, 0xef, 0xf7, 0xff]:
            self.step()
        else:
            self.runTo(self.cpu.regPC.read() 
                       + self.cpu.opcodeLength[self.cpu.nextInstruction[0]])
        self.cpu.ps()

    def reset(self):
        self.cpu.reset()
        self.mmu.reset()
        self.gpu.reset()
        self.interrupts.reset()

    def memDump(self):
        mem = bytearray([])
        for i in range(0x10000):
            mem.append(self.mmu.read(i))
        with open("memdump.bin", "wb") as f:
            f.write(mem)
    

def main(cartridgeFile, biosFile):
    a = Pyboy(cartridgeFile, biosFile)
    a.run()
    

def create(cartridgeFile, biosFile):
    return Pyboy (cartridgeFile, biosFile,)


def cd(): #CreateDefault
    global cartridgeFile, biosFile
    return Pyboy(cartridgeFile, biosFile)


def runQuickTest():
    a = cd()
    print ("Testing Cpu Functions:")
    for i in range(256):
        print(i)
        a.cpu.opcodeFunctions[i]([i, 0, 0])
    print("testing cb functions")
    for i in range(256):
        print(i)
        a.cpu.cbFunctions[i]


def fuzz():
    a = cd()
    a.cpu.regPC.load(0x8000)
    a.cpu.regSP.load(0x8000)
    while True:
        if a.cpu.regSP.read() < 5 or a.cpu.regSP.read() > 0xfff8:
            a.cpu.regSP.load(0x8000)
        if a.cpu.regPC.read() < 5 or a.cpu.regPC.read() > 0xfff8:
            a.cpu.regPC.load(0x8000)
        a.cpu.nextInstruction[0] = random.randint(0, 255)
        a.cpu.nextInstruction[1] = random.randint(0, 255)
        a.cpu.nextInstruction[2] = random.randint(0, 255)
        a.cpu.ps()
        a.cpu.eni()






if __name__ == "__main__":
   sys.exit(main(cartridgeFile, biosFile))   
