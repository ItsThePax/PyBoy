import random

random.seed()

cartridgeTypeMbc = {
    0x00:0,
    0x01:2, 0x02:2, 0x03:2,
    0x05:2, 0x06:2,
    0x08:1, 0x09:1,
    0x0f:3, 0x10:3, 0x11:3, 0x12:3, 0x13:3 
}

romPageSize = 0x4000
romMode = {
    0x00: 0,
    0x01: 4,
    0x02: 8,
    0x03: 16,
    0x04: 32,
    0x05: 64,
    0x06: 128,
    0x07: 256,
    0x08: 512,
    0x52: 72,
    0x53: 80,
    0x54: 96
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
        if cartridgeTypeMbc[self.mmuType] == 1:
            self.romRAMSelector = 0 # 0 controls rom, 1 controlls ram
        self.romType = self.rawReadCartridge(0x148)
        self.ramType = self.rawReadCartridge(0x149)
        self.ram = bytearray([0] * (ramPageSize * ramMode[self.ramType]))
        self.read = self.readWriteFunction[cartridgeTypeMbc[self.mmuType]]["read"]
        self.write = self.readWriteFunction[cartridgeTypeMbc[self.mmuType]]["write"]
    

    mmuType = 0
    romType = 0
    RamType = 0 
    romBank = 1
    RamBank = 0
    ramWriteProtect = 1

    #controls
    buttons = 0xf
    Dpad = 0xf


    #reset mmu to power-on state
    def reset(self):
        self.buttons = 0xf
        self.Dpad = 0xf
        self.read = self.readWriteFunction[cartridgeTypeMbc[self.mmuType]]["read"]
        self.write = self.readWriteFunction[cartridgeTypeMbc[self.mmuType]]["write"]
        self.memory = bytearray([])
        for i in range(0x10000):
            self.memory.append(random.randint(0x0, 0xff))


    #opens a file and returns the entire contents ~~DONT ABUSE~~
    def loadFile(self, filename):
        with open(filename, 'rb') as f:
            return f.read()
        

    #status of control register
    def getControls(self):
        temp = self.memory[0xff00]
        if temp & 0x10:
            if temp & 0x20:
                return self.memory[0xff00] | 0xff
            return self.memory[0xff00] | self.Dpad
        return self.memory[0xff00] | self.buttons
            


    #direct read access to cartridgeRom   
    def rawReadCartridge(self, address):
        return self.cartridgeRom[address]
    
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
                return self.memory[address]
        else:
            if address > 0x4000:
                return self.cartridgeRom[address]
            else:
                return self.cartridgeRom[(romPageSize * self.romPage) + (address & 0x3fff)]


    #write to mc0 #TODO make this not suck later
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
            if address == 0xff50:
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
            return self.cartridgeRom[address]


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
                if self.romRAMSelector == 0:
                    self.romBank = (self.romBank & 0x1f) | (value << 5)
                else:
                    self.ramBank = value
            else:
                self.romRAMSelector = value
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
