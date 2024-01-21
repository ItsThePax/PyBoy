
import random

random.seed()

cartMbcMap = {
    0x00:0,
    0x01:1, 0x02:1, 0x03:1,
    0x05:2, 0x06:2,
    0x08:0, 0x09:0,
    0x0f:3, 0x10:3, 0x11:3, 0x12:3, 0x13:3 
}

romBankSize = 0x4000
romMode = {
    0x00: 0, 0x01: 4, 0x02: 8, 0x03: 16, 0x04: 32, 0x05: 64, 0x06: 128,
    0x07: 256, 0x08: 512, 0x52: 72, 0x53: 80, 0x54: 96
}

ramPageSize = 0x2000
ramMode = {
    0x0: 0,
    0x2: 1,
    0x3: 4
}

class Mmu:
    def __init__(self, cartridgeRomPath, biosRomPath):
        #load cartridge and bios files
        self.cartridgeRom = bytes(self.loadFile(cartridgeRomPath))
        self.biosRom = bytes(self.loadFile(biosRomPath))
        
        #set up memory
        self.vram = bytearray([0] * 0x2000)
        self.internalRam = bytearray([0] * 0x2000)
        self.oam = bytearray([0] * 0xa0)
        self.hiRam = bytearray([0] * 0x80)

        #set up control registers
        self.registers = bytearray([
            #controls
            0,

            #serial
            0xff, 0xff, 
            
            #none
            0xff,

            #timer
            0, 0, 0, 0,  
            
            #none
            0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 
            
            #interrupts
            0, 

            #sound
            0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 
            0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 
            0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 
            0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 
            0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 
            0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff,
            
            #gpu
            0, 0, 0, 
            0, 0, 0, 
            
            #dma
            0xff, 

            #gpu 
            0, 0, 0, 
            0, 0, 
            
            #none
            0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 
            0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 
            0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 
            0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 
            0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 
            0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 
            0xff, 0xff, 0xff, 0xff
        ])

        #masks for setting disabled bits on registers
        self.registerMasks = bytearray([
            #controls
            0xcf,

            #serial
            0x0, 0x7e,
            
            #none
            0xff,

            #timer
            0x0, 0x0, 0x0, 0xf8,  
            
            #none
            0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 
            
            #interrupts
            0xe0, 

            #sound #TODO
            0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 
            0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 
            0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 
            0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 
            0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 
            0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff,
            
            #gpu
            0x0, 0x80, 0x0, 
            0x0, 0x0, 0x0,
            
            #dma
            0xff, 

            #gpu 
            0x0, 0x0, 0x0, 0x0, 0x0,
            
            #none
            0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 
            0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 
            0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 
            0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 
            0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 
            0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 
            0xff, 0xff, 0xff, 0xff
        ])

        self.interruptEnabled = 0
        
        #set up functions for correct memory controller version
        self.mmuType = self.rawReadCartridge(0x147)
        print ( f"mmuType: {self.mmuType}")
        self.romType = self.rawReadCartridge(0x148)
        self.ramType = self.rawReadCartridge(0x149)
        if cartMbcMap[self.mmuType] == 2:
            self.externalRam = bytearray([0] * 512)
        else:
            self.externalRam = bytearray([0] * (ramPageSize * ramMode[self.ramType]))

        self.MCWriteFuncs = [
           self.writeMemControlerNone,
           self.writeMemControlerMC1,
           self.writeMemControlerMC2,
           self.writeMemControlerMC3
        ] 

        self.read = self.readWithBios

        if self.ramType == 0:
            self.readExternalRam = self.readExternalRamNone
            self.writeExternalRam = self.writeExternalRamNone
        if cartMbcMap[self.mmuType] == 2:
            self.readExternalRam = self.readExternalRamMC2
            self.writeExternalRam = self.writeExternalRamMC2
        else:
            self.readExternalRam = self.readExternalRamBanked
            self.writeExternalRam = self.writeExternalRamBanked
        
        if self.romType == 0:
            self.readCart = self.readCartNoBanks
        else:
            self.readCart = self.readCartBanked 
        
        self.writeMemControler = self.MCWriteFuncs[cartMbcMap[self.mmuType]]
        

    #mc1 specific
    mc1Mode = 0

    #generic
    mmuType = 0
    romType = 0
    ramType = 0 
    romBank = 1
    ramBank = 0
    ramWriteProtect = 1

    #controls
    buttons = 0xf
    dpad = 0xf

    #returns contents of controlls register 0xff00
    def getControls(self):
        controls = self.registers[0] & 0xf0
        if controls & 0x30 == 0x20:
            return controls | self.dpad
        if controls & 0x30 == 0x10:
            return controls | self.buttons
        return controls | 0xf

    #opens a file and returns the entire contents ~~DONT ABUSE~~
    def loadFile(self, filename):
        with open(filename, 'rb') as f:
            return f.read()
            
    #direct read access to cartridgeRom
    def rawReadCartridge(self, address):
        return self.cartridgeRom[address]
    
     # raw memory read #TODO rewrite
    def rawReadMemory(self, address):
        return self.memory[address]
        
    # raw memory write #TODO rewrite
    def rawWriteMemory(self, address, value):
        self.memory[address] = value & 0xff 

    def readWithBios(self, address):
        if address < 0x100:
            return self.biosRom[address]
        return self.readWithoutBios(address)

    def readWithoutBios(self, address):
        if address < 0x8000:
            return self.readCart(address)
        if address >= 0xff00:                                #0x8000 - 0xffff
            if address == 0xffff:                               #0xffff
                return self.interruptEnabled                
            if address >= 0xff80:               
                return self.hiRam[address % 0x80]
            if address == 0xff00:                       #0xff80 - 0xfffe
                    return self.getControls() 
            return self.registers[address % 0x80]           #0xff00 - 0xff7f
        if address < 0xa000:
            return self.vram[address % 0x2000]              #0x8000 - 0x9fff
        if address < 0xc000:
            return self.readExternalRam(address % 0x2000)   #0xa000 - 0xbfff
        if address < 0xfe00:
            return self.internalRam[address % 0x2000]
        if address < 0xfea0:
            return self.oam[address % 0x100]
        return 0xff
    
    def write(self, address, value):
        if address < 0x8000:
            return self.writeMemControler(address, value)
        if address >= 0xff00:                                         
            if address >= 0xff80:                            
                if address == 0xffff:                              
                    self.interruptEnabled = value
                    return
                self.hiRam[address % 0x80] = value
                return
            
            address %= 0x80
            if address == 0x50:
                self.read = self.readWithoutBios
                return
            
            elif address == 4:
                self.registers[0x4] = 0
                return
            
            elif address == 0x40:
                if value & 0x80 == 0:
                    self.registers[0x44] = 0
                    self.gpu.linePosition = 0
                    self.gpu.mode = 0
                    self.registers[0x41] &= 0xfc
                if value & 0x80:
                    if self.registers[0x40] & 0x80 == 0:
                        self.gpu.mode == 2
                        self.registers[0x41] &= 0xfc
                        self.registers[0x41] |= 2
            
            elif address == 0x41:
                value &= 0x78 # mask off read only bits
                self.registers[0x41] == value | 0x80  
                return
            
            elif address == 0x44:
                return
            elif address == 0x50:
                self.read = self.readWithoutBios
            self.registers[address] = value | self.registerMasks[address]          #0xff00 - 0xff7f
            return
        if address < 0xa000:
            self.vram[address % 0x2000] = value              #0x8000 - 0x9fff
            return
        if address < 0xc000:
            self.writeExternalRam(address % 0x2000, value)   #0xa000 - 0xbfff
            return
        if address < 0xfe00:
            self.internalRam[address % 0x2000] = value
            return
        if address < 0xfea0:
            self.oam[address % 0x100] = value
            return
    

    def readCartNoBanks(self, address):
        return self.cartridgeRom[address] 
    
    def readExternalRamNone(self, address):
        return 0xff
    
    def writeExternalRamNone(self, address, value):
        return
    
    def readCartBanked(self, address):
        if address < 0x4000:
            return self.cartridgeRom[address]
        else:
            return self.cartridgeRom[
                (self.romBank * 0x4000) + (address % 0x4000)]
    
    def readExternalRamBanked(self, address):
        address %= 0x2000
        return self.externalRam[(self.ramBank * 0x2000) + address]
    
    def readExternalRamMC2(self, address):
        address %= 0x200
        return self.externalRam[address]
    
    def writeExternalRamMC2(self, address, value):
        if self.ramWriteProtect == 0:
            address %= 0x200
            self.externalRam[address] = value & 0xf
    
    def writeExternalRamBanked(self, address, value):
        if self.ramWriteProtect == 0:
            address %= 0x2000
            self.externalRam[(self.ramBank * 0x2000) + address] = value
        return

    def writeMemControlerNone(self, address, value):
        return
    
    def writeMemControlerMC1(self, address, value):
        if address < 0x2000:
            if value == 0x0a:
                self.ramWriteProtect = 0
            else:
                self.ramWriteProtect = 1
            return
        elif 0x2000 <= address <= 0x4000:
            self.romBank = value
            return
        elif 0x4000 <= address < 0x6000:
            if self.mc1Mode:
                self.ramBank = value
            else:
                self.romBank &= 0xf
                self.romBank |= (value << 4)
        elif 0x6000 <= address:
            self.mc1Mode = value

    def writeMemControlerMC2(self, address, value):
        if address < 0x1000:
            if value == 0x0a:
                self.ramWriteProtect = 0
            else:
                self.ramWriteProtect = 1
            return
        elif 0x2100 <= address <= 0x2200:
            self.romBank = value
        return
    
    def writeMemControlerMC3(self, address, value):
        if address < 0x2000:
            if value == 0x0a:
                self.ramWriteProtect = 0
            else:
                self.ramWriteProtect = 1
        elif address < 0x4000:
            if 1 <= value < 0x80:
                self.romBank = value
                return
        elif address < 0x6000:
            if 0 <= value < 4:
                self.ramBank = value
            #TODO rtc registers
        else:
            pass
            #TODO rtc latching
        return