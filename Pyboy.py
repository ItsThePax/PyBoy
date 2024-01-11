import pygame
import sys
import pyboy_cpu
import pyboy_gpu
import random


random.seed()


biosFile = "DMG_rom.bin"
cartridgeFile = "tetris.gb"


class Pyboy:
    def __init__(self, model, cartridgeFile, biosFile):
        #for now model hard coding to DMG original monochrome gameboy
        model = "DMG"
        if model == "DMG":
            self.cpu = pyboy_cpu.Cpu(cartridgeFile, biosFile)
            self.mmu = self.cpu.mmu
            self.gpu = pyboy_gpu.DMG_gpu(self.mmu)
       
    
    def run(self):
        while (True): #run forever until error or break
            self.step()
    

    def runDB(self):
            while True:
                self.step()
                self.cpu.ps()

    
    def runto(self, target): #must match pc exactly
        if self.cpu.regPC.read() == target:
            self.step()
        while self.cpu.regPC.read() != target:
            self.step()


    def step(self):
        if self.cpu.run == 1:
            ticks = self.cpu.step()
        else:
            ticks = 4
        self.gpu.step(ticks)


    def stepDB(self):
        self.cpu.fni() #netch next instruction
        self.cpu.pni() #print next instruction
        self.step()
        self.cpu.ps()


    def reset(self):
        self.cpu.reset()
        self.mmu.reset()
        self.gpu.reset()


def main(cartridgeFile, biosFile):
    a = Pyboy("DMG", cartridgeFile, biosFile)
    a.run()
    

def create(biosFile,  cartridgeFile):
    return Pyboy (biosFile,  cartridgeFile)


def cd(): #CreateDefault
    global biosFile, cartridgeFile
    return Pyboy("DMG", biosFile,  cartridgeFile)


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
   sys.exit(main(biosFile, cartridgeFile))   
