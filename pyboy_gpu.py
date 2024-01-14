import numpy as np
import pygame
import time


interruptVblank = 0x01
interruptLCDC = 0x02
bitMasks = bytes([0x80, 0x40, 0x20, 0x10, 0x8, 0x4, 0x2, 0x1])
valueToColorMapping = bytes([0xff, 0x56, 0x29, 0x0])
setBitMasks = bytes([0x1, 0x2, 0x4, 0x8, 0x10, 0x20, 0x40, 0x80])
resetBitMasks = bytes([0xfe, 0xfd, 0xfb,  0xf7, 0xef, 0xdf, 0xbf, 0x7f])


class DMG_gpu():
    def __init__(self, mmu):
        self.mmu = mmu
        self.lcdModeFunctions = [self.lcdMode0, self.lcdMode1, 
                                 self.lcdMode2, self.lcdMode3]
        self.screen = pygame.display.set_mode((160, 144), depth=8)
        self.clock = pygame.time.Clock()
        self.formatIndexTable = {
            0x8000: self.formatIndexU,
            0x8800: self.formatIndexS
        }

    FPS = 60
    frame = 0
    linePosition = 0
    lineNumber = 0    
    mode = 2
    t0 = time.time()
    t1 = time.time()

    frameBuffer = bytearray([0] * (160 * 144))

    def formatIndexU(self, index):
        return index

    def formatIndexS(self, index):
        index &= 0xff
        return (index ^ 0x80) - 0x80

    def reset(self): #might not need this fucntion
        self.screen = pygame.display.set_mode((160, 144), depth=8)


    def printStatus(self):
        print(f"0xff40:0x{self.mmu.read(0xff40):02x}"
              f"0xff44:0x{self.mmu.read(0xff44):02x}")
    

    def step(self, ticks):
        if self.mmu.read(0xff40) & 0x80:
            self.linePosition += ticks
            self.lcdModeFunctions[self.mode]()

    def lcdMode0(self):
        if self.linePosition > 455:
            self.linePosition %= 456
            self.lineNumber += 1
            self.mmu.write(0xff44, self.lineNumber)
            if self.lineNumber == 144:
                self.updateLCDMode(1)
                self.vBlank() 
            else:
                self.updateLCDMode(2)


    def lcdMode1(self):
        if self.linePosition > 455:
            self.linePosition %= 456
            self.lineNumber += 1
            self.mmu.write(0xff44, self.lineNumber)
            if self.lineNumber == 153:
                self.lineNumber = 0
                self.updateLCDMode(2)
            

    def lcdMode2(self):
        if self.linePosition > 79:
            self.updateLCDMode(3)


    def lcdMode3(self):
        if self.linePosition > 230: #HBLANK
            self.updateLCDMode(0)
            self.hBlank()


    def updateLCDMode(self, mode):
        self.mode = mode
        value = self.mmu.read(0xff41)
        value &= 0xfa #clear last 2 bits
        self.mmu.write(0xff41, value | mode) #write back with new mode


    def hBlank(self):
        lineData = self.renderLine(self.lineNumber)
        for i in range(160):
            self.frameBuffer.append(lineData[i])

    def vBlank(self):
        b = np.array(self.frameBuffer)
        b.resize((144, 160))
        surf = pygame.surfarray.make_surface(np.flipud(np.rot90(b)))
        self.screen.blit(surf, ((0, 0)))
        self.clock.tick(self.FPS)
        pygame.display.update()
        self.getControls()
        self.frameBuffer = bytearray([])
        self.frame += 1
        if self.frame % 60 == 0:
            self.t1 = time.time()
            #print((1/(self.t1 - self.t0)) * 60)
            self.t0 = time.time()
        self.mmu.write(0xff0f, self.mmu.read(0xff0f) | interruptVblank)


    def renderLine(self, lineNumber):
        lcdc = self.mmu.read(0xff40)
        scrollY = self.mmu.read(0xff42)
        scrollX = self.mmu.read(0xff43)
        winX = self.mmu.read(0xffa4)
        winY = self.mmu.read(0xffa5)
        bgPallet = self.mmu.read(0xff47)
        bgColorMap = bytearray([0, 0, 0, 0])
        for i in range (4):
            bgColorMap[i] = (bgPallet >> (i*2)) & 0x3
        #bg
        bgIndexLocation = 0x9800 + (lcdc & 0x8 * 0x80)
        bgDataLocation = 0x8000 + (lcdc & 0x10 * 0x80)
        self.formatIndex = self.formatIndexTable[bgDataLocation]
        tileY = (((lineNumber + scrollY) >> 3) * 32) % 1024
        lineInTile = (lineNumber + scrollY) % 8
        colorData = bytearray([0] * 512)
        startByte = scrollX // 8
        for i in range(startByte, startByte + 42, 2):
            tileIndex = self.formatIndex(self.mmu.read(bgIndexLocation 
                                                        + (tileY + (i >> 1))))
            colorByteLow = self.mmu.read(bgDataLocation 
                                          + (tileIndex << 4) 
                                          + (lineInTile << 1))
            colorByteHigh = self.mmu.read(bgDataLocation 
                                         + (tileIndex << 4) 
                                         + (lineInTile << 1)
                                         + 1)
            for j in range(8):
                temp = 0
                if colorByteHigh & bitMasks[j]:
                    temp += 2
                if colorByteLow & bitMasks[j]:
                    temp += 1
                colorData[(i * 4) + j] = valueToColorMapping[bgColorMap[temp]]
        return np.roll(colorData, scrollX)[0:160] 
    

    def renderLineDB(self, lineNumber):
        lcdc = self.mmu.read(0xff40)
        scrollY = self.mmu.read(0xff42)
        scrollX = self.mmu.read(0xff43)
        winX = self.mmu.read(0xffa4)
        winY = self.mmu.read(0xffa5)
        bgPallet = self.mmu.read(0xff47)
        bgColorMap = bytearray([0, 0, 0, 0])
        for i in range (4):
            bgColorMap[i] = (bgPallet >> (i*2)) & 0x3
        #bg
        bgIndexLocation = 0x9800 + (lcdc & 0x8 * 0x80)
        print(f"bgIndexLocation: {bgIndexLocation:04x}")
        bgDataLocation = 0x8000 + (lcdc & 0x10 * 0x80)
        print(f"bgDataLocation: {bgDataLocation:04x}")
        self.formatIndex = self.formatIndexTable[bgDataLocation]
        tileY = (((lineNumber + scrollY) >> 3) * 32) % 1024
        print(f"tileY: {tileY}")
        lineInTile = (lineNumber + scrollY) % 8
        print(f"lineInTile: {lineInTile}")
        colorData = bytearray([0] * 512)
        startByte = scrollX // 8
        for i in range(startByte, startByte + 42, 2):
            print(f"tile index pointer: "
                  f"{bgIndexLocation + (tileY + (i >> 1)):04x}")
            tileIndex = self.formatIndex(self.mmu.read(bgIndexLocation 
                                                        + (tileY + (i >> 1))))
            print(f"tile Index: {tileIndex}")
            print(f"color byte low pointer: "
                  f"{bgDataLocation + (tileIndex << 4) + (lineInTile << 1):04x}")
            print(f"color byte high pointer: "
                  f"{bgDataLocation + (tileIndex << 4) + (lineInTile << 1) + 1:04x}")
            colorByteLow = self.mmu.read(bgDataLocation 
                                          + (tileIndex << 4) 
                                          + (lineInTile << 1))
            colorByteHigh = self.mmu.read(bgDataLocation 
                                         + (tileIndex << 4) 
                                         + (lineInTile << 1)
                                         + 1)
            print(f"colorbyte low:  {colorByteLow:08b}")
            print(f"colorbyte high: {colorByteHigh:08b}")
            byteColorData = []
            for j in range(8):
                temp = 0
                if colorByteHigh & bitMasks[j]:
                    temp += 2
                if colorByteLow & bitMasks[j]:
                    temp += 1
                colorData[(i * 4) + j] = valueToColorMapping[bgColorMap[temp]]
                byteColorData.append(valueToColorMapping[bgColorMap[temp]])
            print(byteColorData)
            print("")
        return np.roll(colorData, scrollX)[0:160] 
       
    

    def getControls(self):
        events = pygame.event.get()
        for event in events:
            if event.type == 768:
                if event.key == 97: #a
                    self.mmu.buttons &= resetBitMasks[0]
                    print (f"pressed a, {self.mmu.buttons}")
                elif event.key == 115: #b
                    print (f"pressed b, {self.mmu.buttons}")
                    self.mmu.buttons &= resetBitMasks[1]
                elif event.key == 32: #select
                    print (f"pressed select, {self.mmu.buttons}")
                    self.mmu.buttons &= resetBitMasks[2]
                elif event.key == 13: #start
                    print (f"pressed start, {self.mmu.buttons}")
                    self.mmu.buttons &= resetBitMasks[3]
                elif event.key == 1073741903: #right
                    print (f"pressed right, {self.mmu.dpad}")
                    self.mmu.dpad &= resetBitMasks[0]
                elif event.key == 1073741904: #left
                    print (f"pressed left, {self.mmu.dpad}")
                    self.mmu.dpad &= resetBitMasks[1]
                elif event.key == 1073741906: #up
                    print (f"pressed up, {self.mmu.dpad}")
                    self.mmu.dpad &= resetBitMasks[2]
                elif event.key == 1073741905: #down
                    print (f"pressed down, {self.mmu.dpad}")
                    self.mmu.dpad &= resetBitMasks[3]
                self.mmu.write(0xff0f,  self.mmu.read(0xff0f) | 0x10)
            elif event.type == 769:
                if event.key == 97: #a
                    print (f"released a, {self.mmu.buttons}")
                    self.mmu.buttons |= setBitMasks[0]
                elif event.key == 115: #b
                    print (f"released b, {self.mmu.buttons}")
                    self.mmu.buttons |= setBitMasks[1]
                elif event.key == 32: #select
                    print (f"released select, {self.mmu.buttons}")
                    self.mmu.buttons |= setBitMasks[2]
                elif event.key == 13: #start
                    print (f"released start, {self.mmu.buttons}")
                    self.mmu.buttons |= setBitMasks[3]
                elif event.key == 1073741903: #right
                    print (f"released right, {self.mmu.dpad}")
                    self.mmu.dpad |= setBitMasks[0]
                elif event.key == 1073741904: #left
                    print (f"released left, {self.mmu.dpad}")
                    self.mmu.dpad |= setBitMasks[1]
                elif event.key == 1073741906: #up
                    print (f"released up, {self.mmu.dpad}")
                    self.mmu.dpad |= setBitMasks[2]
                elif event.key == 1073741905: #down
                    print (f"released down, {self.mmu.dpad}")
                    self.mmu.dpad |= setBitMasks[3]    

    def printVramDB(self):
        vram = []
        for i in range(0x8000, 0xa000):  
            vram.append(self.mmu.read(i))
        for i in range(0, len(vram), 16):
            print(f"0x{i + 0x8000:04x}: "
                  f"{vram[i + 0]:02x} {vram[i + 1]:02x} {vram[i + 2]:02x} "
                  f"{vram[i + 3]:02x} {vram[i + 4]:02x} {vram[i + 5]:02x} "
                  f"{vram[i + 6]:02x} {vram[i + 7]:02x} {vram[i + 8]:02x} "
                  f"{vram[i + 9]:02x} {vram[i + 10]:02x} {vram[i + 11]:02x} "
                  f"{vram[i + 12]:02x} {vram[i + 13]:02x} {vram[i + 14]:02x} " 
                  f"{vram[i + 15]:02x}")
            
    def renederCurrentFrameDB(self):
        for i in range(144):
            self.renderLine(i)
        b = np.array(self.frameBuffer)
        b.resize((144, 160))
        surf = pygame.surfarray.make_surface(np.flipud(np.rot90(b)))
        self.screen.blit(surf, ((0, 0)))
        self.clock.tick(self.FPS)
        pygame.display.update()
        pygame.event.get()