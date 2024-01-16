
import random

random.seed()

cartMbcMap = {
    0x00:0,
    0x01:2, 0x02:2, 0x03:2,
    0x05:2, 0x06:2,
    0x08:1, 0x09:1,
    0x0f:3, 0x10:3, 0x11:3, 0x12:3, 0x13:3 
}

romBankSize = 0x4000
romMode = {
    0x00: 0, 0x01: 4, 0x02: 8, 0x03: 16, 0x04: 32, 0x05: 64, 0x06: 128,
    0x07: 256, 0x08: 512, 0x52: 72, 0x53: 80, 0x54: 96
}

ramPageSize = 0x2000
ramMode = {
    0x0: 0
}

class Mmu:
    def __init__(self, cartridgeRomPath, biosRomPath):
        #set up randomized memory
        self.memory = bytearray([])
        for i in range(0x10000):
            #self.memory.append(random.randint(0x0, 0xff))
            self.memory.append(0)
        
        #load cartridge and bios files
        self.cartridgeRom = bytes(self.loadFile(cartridgeRomPath))
        self.biosRom = bytes(self.loadFile(biosRomPath))

        #set up functions for correct memory controller version
        self.readWriteFunction = {
            0: {
                    "read":self.readRomOnlyWithBios, 
                    "write":self.writeRomOnly
            },
            #1: {
            #        "read":self.readRomAndRamWithBios, 
            #        "write":self.writeRomAndRam
            #}  
            2: {    "read":self.readMC1WithBios,
                    "write":self.writeMC1
            
            
            }
        }

        self.mmuType = self.rawReadCartridge(0x147)
        self.romType = self.rawReadCartridge(0x148)
        self.ramType = self.rawReadCartridge(0x149)
        self.ram = bytearray([0] * (ramPageSize * ramMode[self.ramType]))
        self.read = self.readWriteFunction[cartMbcMap[self.mmuType]]["read"]
        self.write = self.readWriteFunction[cartMbcMap[self.mmuType]]["write"]
    
    # 0 controls rom, 1 controlls ram
    MC1RomRamSelector = 0

    mmuType = 0
    romType = 0
    ramType = 0 
    romBank = 1
    RamBank = 0
    ramWriteProtect = 1

    #controls
    buttons = 0xf
    dpad = 0xf

    #reset mmu to power-on state
    def reset(self):
        self.MC1RomRamSelector = 0
        self.romBank = 1
        self.ramBank = 0
        self.ramWriteProtect = 1
        self.buttons = 0xf
        self.dpad = 0xf
        self.read = self.readWriteFunction[cartMbcMap[self.mmuType]]["read"]
        self.write = self.readWriteFunction[cartMbcMap[self.mmuType]]["write"]
        self.memory = bytearray([])
        for i in range(0x10000):
            self.memory.append(random.randint(0x0, 0xff))

    #returns contents of controlls register 0xff00
    def getControls(self):
        controls = self.memory[0xff00]
        if controls & 0x2f == 20:
            return controls | self.dpad
        if controls & 0x1f == 0x10:
            return controls | self.buttons
        return controls | 0xf

    #opens a file and returns the entire contents ~~DONT ABUSE~~
    def loadFile(self, filename):
        with open(filename, 'rb') as f:
            return f.read()
            
    #direct read access to cartridgeRom
    def rawReadCartridge(self, address):
        return self.cartridgeRom[address]
    
     # raw memory read
    def rawReadMemory(self, address):
        return self.memory[address]
        
    # raw memory write
    def rawWriteMemory(self, address, value):
        self.memory[address] = value & 0xff    
    
    #ROM only
    #use this fucntion to read while bios is active
    def readRomOnlyWithBios(self, address):
        if address < 0x100:
            return self.biosRom[address]
        else:
            return self.readRomOnly(address)
    
    #use this function to read after bios has been disabled
    def readRomOnly(self, address):
        if address > 0x7fff:
            if address & 0xe000 == 0xa000:
                return 0xff
            else:
                if address == 0xff00:
                    return self.getControls()
                else:
                    return self.memory[address]
        else:
            return self.cartridgeRom[address]
        
    #write to Rom only #TODO make this not suck later
    def writeRomOnly(self, address, value):
        if value > 0xff:
            print(f"WARNING: something tried to write "
                  f"{hex(value)} to address {hex(address)}")
            value &= 0xff
        if 0x8000 <= address < 0xa000:
            self.memory[address] = value
        elif 0xc000 <= address < 0xde00:
            self.memory[address] = value
            self.memory[address + 0x2000] = value
        elif 0xde00 <= address < 0xe000:
            self.memory[address] = value
        elif 0xe000 <= address < 0xfe00:
            self.memory[address] = value
            self.memory[address - 0x2000] = value
        elif 0xfe00 <= address < 0xfea0:
            self.memory[address] = value
        elif 0xff00 <= address < 0x10000:
            if address == 0xff00:
                self.memory[0xff00] = value & 0xf0
            elif address == 0xff04:
                self.memory[address] = 0
                self.timer.divH  = 0
            elif address == 0xff05:
                self.memory[address] = value
                self.timer.tima = value
            elif address == 0xff06:
                self.memory[address] = value
                self.timer.tma = value
            elif address == 0xff07:
                self.memory[address] = value
                self.timer.run = value & 0x4
                self.timer.mode = value & 0x3
            elif address == 0xff40:
                self.memory[address] = value
                self.gpu.lcdc = value
                if value & 0x80 == 0:
                    self.write(0xff44, 0)
            elif address == 0xff41:
                self.memory[address] = value
                self.gpu.stat = value
                self.gpu.mode = value & 0x3
            elif address == 0xff42:
                self.memory[address] = value
                self.gpu.scy = value
            elif address == 0xff43:
                self.memory[address] = value
                self.gpu.scx = value
            elif address == 0xff44:
                self.memory[address] = value
                self.gpu.ly = value
            elif address == 0xff45:
                self.memory[address] = value
                self.gpu.lyc = value
            elif address == 0xff46:
                # do dma
                pass
            elif address == 0xff47:
                self.memory[address] = value
                self.gpu.bgPallet = value
            elif address == 0xff48:
                self.memory[address] = value
                self.gpu.obPallet0 = value
            elif address == 0xff49:
                self.memory[address] = value
                self.gpu.obPallet1 = value
            elif address == 0xff4a:
                self.memory[address] = value
                self.gpu.wy = value
            elif address == 0xff4b:
                self.memory[address] = value
                self.gpu.wx = value
            elif address == 0xff50:
                self.read = self.readRomOnly
            else:
                self.memory[address] = value

    
    
    
    
    
    
    
    
    
    
    
    
    
    #MC1
    #use this fucntion to read while bios is active
    def readMC1WithBios(self, address):
        if address < 0x100:
            return self.biosRom[address]
        else:
            return self.readMC1(address)
    
    #use this function to read after bios has been disabled
    def readMC1(self, address):
        if address > 0x7fff:
            if address & 0xe000 == 0xa000:
                return 0xff
            else:
                return self.memory[address]
        else:
            if address < 0x4000:
                return self.cartridgeRom[address]
            else:
                return self.cartridgeRom[
                    (romBankSize * self.romBank) 
                    + (address & 0x3fff)]

    #write to mc1 #TODO make this not suck later
    def writeMC1(self, address, value):
        if value > 0xff:
            print(f"WARNING: something tried to write "
                  f"{hex(value)} to address {hex(address)}")
            value &= 0xff
        if 0x0 <= address < 0x8000:
            if address < 0x2000:
                if value == 0xa:
                    self.writeProtect = 0
                else:
                    self.writeProtect = 1
            elif address < 0x4000:
                self.romBank = (self.romBank & 0xe0) | value 
            elif address < 0x6000:
                if self.MC1RomRamSelector == 0:
                    self.romBank = (self.romBank & 0x1f) | (value << 5)
                else:
                    self.ramBank = value
            else:
                self.MC1RomRamSelector = value
        elif 0x8000 <= address < 0xa000:
            self.memory[address] = value
        elif 0xc000 <= address < 0xde00:
            self.memory[address] = value
            self.memory[address + 0x2000] = value
        elif 0xde00 <= address < 0xe000:
            self.memory[address] = value
        elif 0xe000 <= address < 0xfe00:
            self.memory[address] = value
            self.memory[address - 0x2000] = value
        elif 0xfe00 <= address < 0xfea0:
            self.memory[address] = value
        elif 0xff00 <= address < 0x10000:
            if address == 0xff00:
                self.memory[0xff00] = value & 0xf0
            if address == 0xff50:
                self.read = self.readMC1
            else:
                self.memory[address] = value
