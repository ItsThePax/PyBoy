import random

random.seed()

class Mmu:
    mmuType = 0

    #opens a file and returns the entire contents ~~DONT ABUSE~~
    def loadFile(self, filename):
        with open(filename, 'rb') as f:
            return f.read()

    #direct read access to cartridgeRom   
    def rawReadCartridge(self, address):
        return self.cartridgeRom[address]
    
    #direct write access to cartridgeRom
    def rawWriteCartridge(self, address, value):
        self.cartridgeRom[address] = value & 0xff
    
    #MC0
    #use this fucntion to read while bios is active
    def readMemoryController0WithBios(self, address):
        if address < 0x100:
            return self.biosRom[address]
        else:
            return self.readMemoryControler0(address)
    
    #use this function to read after bios has been disabled
    def readMemoryControler0(self, address):
        if address & 0x8000:
            if address & 0xe000 == 0xa000:
                return 0xff
            else:
                return self.memory[address]
        else:
            return self.cartridgeRom[address]
        
    #write to mc0 #TOTO make this not suck later
    def writeMemoryController0(self, address, value):
        if value > 0xff:
            print("WARNING: something tried to write {0} to address {1}".format(hex(value), hex(address)))
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
            if address == 0xff50:
                self.read = self.readMemoryControler0
            else:
                self.memory[address] = value

   

    def __init__(self, cartridgeRomPath, biosRomPath):
        #set up randomized memory
        self.memory = bytearray([])
        for i in range(0x10000):
            self.memory.append(random.randint(0x0, 0xff))
        
        #load cartridge and bios files
        self.cartridgeRom = bytes(self.loadFile(cartridgeRomPath))
        self.biosRom = bytes(self.loadFile(biosRomPath))

        #set up functions for correct memory controller version
        self.readWriteFunctionMapping = {
            0: {"read":self.readMemoryController0WithBios, "write":self.writeMemoryController0},
            1: {"read":None, "write":None} #placeholder
        }

        self.mmuType = self.rawReadCartridge(0x147)
        self.read = self.readWriteFunctionMapping[self.mmuType]["read"]
        self.write = self.readWriteFunctionMapping[self.mmuType]["write"]