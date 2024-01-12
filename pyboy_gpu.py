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
        self.lcdModeFunctions = [self.lcdMode0, self.lcdMode1, self.lcdMode2, self.lcdMode3]
        self.screen = pygame.display.set_mode((160, 144), depth=8)
        self.clock = pygame.time.Clock()

    FPS = 60
    frame = 0
    linePosition = 0
    lineNumber = 0    
    mode = 2
    t0 = time.time()
    t1 = time.time()

    frameBuffer = bytearray([0] * (160 * 144))


    def reset(self): #might not need this fucntion
        self.screen = pygame.display.set_mode((160, 144), depth=8)


    def printStatus(self):
        print(f"0xff40:0x{self.mmu.read(0xff40):02x} 0xff44:0x{self.mmu.read(0xff44):02x}")
    

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
        self.frameBuffer[self.lineNumber * 160:(self.lineNumber * 160) + 159] = self.renderLine(self.lineNumber)


    def vBlank(self):
        b = np.array(self.frameBuffer)
        b.resize((144, 160))
        surf = pygame.surfarray.make_surface(np.flipud(np.rot90(b)))
        self.screen.blit(surf, ((0, 0)))
        self.clock.tick(self.FPS)
        pygame.display.update()
        self.getControls()
        self.frame += 1
        if self.frame % 60 == 0:
            self.t1 = time.time()
            print((1/(self.t1 - self.t0)) * 60)
            self.t0 = time.time()
        self.mmu.write(0xff0f, self.mmu.read(0xff0f) | interruptVblank)


    def renderLine(self, lineNumber):
        pixelData = bytearray(64)
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
        tileY = (((lineNumber + scrollY) >> 3) * 32)
        lineInTile = (lineNumber + scrollY) % 8
        colorData = bytearray([0] * 512)
        for i in range(0, 40, 2):
            tileIndex = self.mmu.read(bgIndexLocation + (tileY + (i >> 1)))
            colorByteHigh = self.mmu.read(bgDataLocation + (tileIndex << 4) + (lineInTile << 1))
            colorByteLow = self.mmu.read(bgDataLocation + (tileIndex << 4) + 1)
            for j in range(8):
                temp = 0
                if colorByteHigh & bitMasks[j]:
                    temp += 2
                if colorByteLow & bitMasks[j]:
                    temp += 1
                colorData[(i * 4) + j] = valueToColorMapping[bgColorMap[temp]]
        return colorData[0:160]   
       

    def renderLineDB(self, lineNumber):
        pixelData = bytearray(64)
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
        tileY = (((lineNumber + scrollY) >> 3) * 32)
        print(f'tileY is {tileY}')
        lineInTile = (lineNumber + scrollY) % 8
        print(f'line in tile {lineInTile}')
        colorData = bytearray([0] * 512)
        for i in range(0, 40, 2):
            print(f'tile index pointer is {hex(bgIndexLocation + (tileY + (i >> 1)))}')
            tileIndex = self.mmu.read(bgIndexLocation + (tileY + (i >> 1)))
            print(f'tile index is {tileIndex}')
            print(f'high color byte is at {hex(bgDataLocation + (tileIndex << 4))}')
            print(f' low color byte is at {hex(bgDataLocation + (tileIndex << 4) + 1)}')
            colorByteHigh = self.mmu.read(bgDataLocation + (tileIndex << 4) + (lineInTile << 1))
            colorByteLow = self.mmu.read(bgDataLocation + (tileIndex << 4) + 1)
            print(f'color byte high is {hex(colorByteHigh)}')
            print(f'color byte  low is {hex(colorByteLow)}')
            for j in range(8):
                temp = 0
                if colorByteHigh & bitMasks[j]:
                    temp += 2
                if colorByteLow & bitMasks[j]:
                    temp += 1
                colorData[(i * 4) + j] = valueToColorMapping[bgColorMap[temp]]
            print(f'color data this tile is {colorData[i * 4:(i * 4) + 4]}')
        return colorData[0:160]   


    def getControls(self):
        events = pygame.event.get()
        for event in events:
            if event.type == 768:
                if event.key == 97: #a
                    self.mmu.buttons &= resetBitMasks[0]
                    print (f"detected A, {self.mmu.buttons}")
                elif event.key == 115: #b
                    self.mmu.buttons &= resetBitMasks[1]
                elif event.key == 32: #select
                    self.mmu.buttons &= resetBitMasks[2]
                elif event.key == 13: #start
                    self.mmu.buttons &= resetBitMasks[3]
                elif event.key == 1073741903: #right
                    self.mmu.Dpad &= resetBitMasks[0]
                elif event.key == 1073741904: #left
                    self.mmu.Dpad &= resetBitMasks[1]
                elif event.key == 1073741906: #up
                    self.mmu.Dpad &= resetBitMasks[2]
                elif event.key == 1073741905: #down
                    self.mmu.Dpad &= resetBitMasks[3]
                self.mmu.write(0xff0f,  self.mmu.read(0xff0f) | 0x10)
            elif event.type == 769:
                if event.key == 97: #a
                    self.mmu.buttons |= setBitMasks[0]
                elif event.key == 115: #b
                    self.mmu.buttons |= setBitMasks[1]
                elif event.key == 32: #select
                    self.mmu.buttons |= setBitMasks[2]
                elif event.key == 13: #start
                    self.mmu.buttons |= setBitMasks[3]
                elif event.key == 1073741903: #right
                    self.mmu.Dpad |= setBitMasks[0]
                elif event.key == 1073741904: #left
                    self.mmu.Dpad |= setBitMasks[1]
                elif event.key == 1073741906: #up
                    self.mmu.Dpad |= setBitMasks[2]
                elif event.key == 1073741905: #down
                    self.mmu.Dpad |= setBitMasks[3]    