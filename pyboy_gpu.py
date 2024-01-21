import numpy as np
import pygame
import time


interruptVblank = 0x01
interruptLCDC = 0x02
interruptControls = 0x10

lyMatchFlag = 0x4
lyMatchReset = 0xfb

inturruptModeLineMatch = 0x40
inturruptMode2 = 0x20
inturruptMode1 = 0x10
inturruptMode0 = 0x08
inturruptModeLookup = [0x20, 0x10, 0x08, 0]

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
        self.formatIndexTable = [
            self.formatIndexU,
            self.formatIndexS
        ]

    FPS = 60
    frame = 0
    linePosition = 0   
    mode = 0
    t0 = time.time()
    t1 = time.time()

    
    
    frameBuffer = bytearray([0] * (160 * 144))

    def formatIndexU(self, index):
        return index

    def formatIndexS(self, index):
        index &= 0xff
        return (index ^ 0x80) + 0x80

    def reset(self):
        self.screen = pygame.display.set_mode((160, 144), depth=8)

    def printStatus(self):
        print(f"lcdc:{hex(self.mmu.registers[0x40])} "
              f"stat:{hex(self.mmu.registers[0x41])} "
              f"scy:{hex(self.mmu.registers[0x42])} "
              f"scx:{hex(self.mmu.registers[0x43])} "
              f"ly:{hex(self.mmu.registers[0x44])} "
              f"lyc:{hex(self.mmu.registers[0x45])} "
              f"bgPallet:{hex(self.mmu.registers[0x47])} "
              f"obPallet0:{hex(self.mmu.registers[0x48])} "
              f"obPallet1:{hex(self.mmu.registers[0x49])} "
              f"WY:{hex(self.mmu.registers[0x4a])} "
              f"WX:{hex(self.mmu.registers[0x4b])} "
              f"linePosition: {self.linePosition} "
              f"mode: {self.mode}")
    ps = printStatus
    
    def step(self, ticks):
        if self.mmu.registers[0x40] & 0x80:
            self.linePosition += ticks
            self.lcdModeFunctions[self.mode]()

    def incrementLine(self):
        self.mmu.registers[0x44] += 1
        if self.mmu.registers[0x44] == self.mmu.registers[0x45]:
            self.mmu.registers[0x41] |= lyMatchFlag
            if self.mmu.registers[0x41] & inturruptModeLineMatch:
                self.interrupts.IF |= interruptLCDC
            else:
                self.mmu.registers[0x41] &= lyMatchReset

    def lcdMode0(self):
        if self.linePosition > 455:
            self.linePosition %= 456
            self.incrementLine()
            if self.mmu.registers[0x44] == 144:  # vblank
                self.updateLCDMode(1)
                self.vBlank()
            else:
                self.updateLCDMode(2)

    def lcdMode1(self):
        if self.linePosition > 455:
            self.linePosition %= 456
            self.incrementLine()
            if self.mmu.registers[0x44] == 154:
                self.mmu.registers[0x44] = 0
                self.updateLCDMode(2)
            
    def lcdMode2(self):
        if self.linePosition > 79:
            self.updateLCDMode(3)

    def lcdMode3(self):
        if self.linePosition > 230: #HBLANK
            self.updateLCDMode(0)
            self.hBlank()

    def updateLCDMode(self, mode):
        if inturruptModeLookup[mode] & self.mmu.registers[0x41]:
            self.interrupts.IF |= interruptLCDC
        self.mode = mode
        self.mmu.registers[0x41] = (self.mmu.registers[0x41] & 0xfc) | mode

    def hBlank(self):
        lineData = self.renderLine(self.mmu.registers[0x44])
        for i in range(160):
            self.frameBuffer.append(lineData[i])

    def vBlank(self):
        b = np.array(self.frameBuffer)
        b.resize((144, 160))
        surf = pygame.surfarray.make_surface(np.flipud(np.rot90(b)))
        self.screen.blit(surf, ((0, 0)))
        #self.clock.tick(self.FPS)
        pygame.display.update()
        self.getControls()
        self.frameBuffer = bytearray([])
        self.frame += 1
        if self.frame % 60 == 0:
            self.t1 = time.time()
            print((1/(self.t1 - self.t0)) * 60) # print approx fps
            self.t0 = time.time()
        self.mmu.registers[0x0f] |= interruptVblank

    def renderLine(self, lineNumber):
        bgColorMap = bytearray([0, 0, 0, 0])
        for i in range (4):
            bgColorMap[i] = (self.mmu.registers[0x47] >> (i*2)) & 0x3
        #bg
        bgIndexLocation = 0x9800 + (self.mmu.registers[0x40] & 0x8 * 0x80)
        bgDataLocation = 0x8000 + (self.mmu.registers[0x40] & 0x10 * 0x80)
        self.formatIndex = self.formatIndexTable[self.mmu.registers[0x40] & 0x10 >> 4]
        tileY = (((lineNumber + self.mmu.registers[0x42]) >> 3) * 32) % 1024
        lineInTile = (lineNumber + self.mmu.registers[0x42]) % 8
        colorData = bytearray([0] * 512)
        startByte = self.mmu.registers[0x43] // 8
        for i in range(startByte, startByte + 42, 2):
            tileIndex = self.formatIndex(
                self.mmu.read(
                    bgIndexLocation 
                     + (tileY + (i >> 1))))
            colorByteLow = self.mmu.read(
                bgDataLocation 
                 + (tileIndex << 4) 
                 + (lineInTile << 1))
            colorByteHigh = self.mmu.read(
                bgDataLocation 
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
        return np.roll(colorData, self.mmu.registers[0x43])[0:160] 

    def getControls(self):
        events = pygame.event.get()
        for event in events:
            if event.type == 768:
                if event.key == 97: #a
                    print (f"pressed a, {self.mmu.buttons}")
                    self.mmu.buttons &= resetBitMasks[0]
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
                self.mmu.registers[0x0f] |= interruptControls
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
            outString = f"0x{i + 0x8000:04x}: "
            for j in range(16):
                outString += f"{vram[i + j]:02x} "
            print(outString)
                
    