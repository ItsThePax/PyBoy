import pygame
import numpy as np

bitMasks = bytes([0x80, 0x40, 0x20, 0x10, 0x8, 0x4, 0x2, 0x1])
valueToColorMapping = bytes([0xff, 0x56, 0x29, 0x0])

setBitMasks = bytes([0x80, 0x40, 0x20, 0x10, 0x8, 0x4, 0x2, 0x1])

opcodeNames = {
    0x00: 'NOP',          0x01: 'LD BC,{0}', 0x02: 'LD (BC),A',   0x03: 'INC BC',    
    0x04: 'INC B',        0x05: 'DEC B',     0x06: 'LD B,{0}',    0x07: 'RCLA',
    0x08: 'LD ({0}),SP',  0x09: 'ADD HL,BC', 0x0a: 'LD A,(BC)',   0x0b: 'DEC BC',
    0x0c: 'INC C',        0x0d: 'DEC C',     0x0e: 'LD C,{0}',    0x0f: 'RRCA',
    0x10: 'STOP 0',       0x11: 'LD DE,{0}', 0x12: 'LD (DE),A',   0x13: 'INC DE',    
    0x14: 'INC D',        0x15: 'DEC D',     0x16: 'LD D,{0}',    0x17: 'RLA',
    0x18: 'JR {0}',       0x19: 'ADD HL,DE', 0x1a: 'LD A,(DE)',   0x1b: 'DEC DE',   
    0x1c: 'INC E',        0x1d: 'DEC E',     0x1e: 'LD E,{0}',    0x1f: 'RRA',
    0x20: 'JR NZ,{0}',    0x21: 'LD HL,{0}', 0x22: 'LD (HL+),A',  0x23: 'INC HL',    
    0x24: 'INC H',        0x25: 'DEC H',     0x26: 'LD H,{0}',    0x27: 'DAA',
    0x28: 'JR Z,{0}',     0x29: 'ADD HL,HL', 0x2a: 'LD A,(HL+)',  0x2b: 'DEC HL',    
    0x2c: 'INC L',        0x2d: 'DEC L',     0x2e: 'LD L,{0}',    0x2f: 'CPL',
    0x30: 'JR NC,{0}',    0x31: 'LD SP,{0}', 0x32: 'LD (HL-),A',  0x33: 'INC SP',    
    0x34: 'INC (HL)',     0x35: 'DEC (HL)',  0x36: 'LD (HL),{0}', 0x37: 'SCF',
    0x38: 'JR C,{0}',     0x39: 'ADD HL,SP', 0x3a: 'LD A,(HL-)',  0x3b: 'DEC SP',    
    0x3c: 'INC A',        0x3d: 'DEC A',     0x3e: 'LD A,{0}',    0x3f: 'CCF',
    0x40: 'LD B,B',       0x41: 'LD B,C',    0x42: 'LD B,D',      0x43: 'LD B,E',    
    0x44: 'LD B,H',       0x45: 'LD B,L',    0x46: 'LD B,(HL)',   0x47: 'LD B,A',
    0x48: 'LD C,B',       0x49: 'LD C,C',    0x4a: 'LD C,D',      0x4b: 'LD C,E',    
    0x4c: 'LD C,H',       0x4d: 'LD C,L',    0x4e: 'LD C,(HL)',   0x4f: 'LD C,A',
    0x50: 'LD D,B',       0x51: 'LD D,C',    0x52: 'LD D,D',      0x53: 'LD D,E',    
    0x54: 'LD D,H',       0x55: 'LD D,L',    0x56: 'LD D,(HL)',   0x57: 'LD D,A',
    0x58: 'LD E,B',       0x59: 'LD E,C',    0x5a: 'LD E,D',      0x5b: 'LD E,E',    
    0x5c: 'LD E,H',       0x5d: 'LD E,L',    0x5e: 'LD E,(HL)',   0x5f: 'LD E,A',
    0x60: 'LD H,B',       0x61: 'LD H,C',    0x62: 'LD H,D',      0x63: 'LD H,E',    
    0x64: 'LD H,H',       0x65: 'LD H,L',    0x66: 'LD H,(HL)',   0x67: 'LD H,A',
    0x68: 'LD L,B',       0x69: 'LD L,C',    0x6a: 'LD L,D',      0x6b: 'LD L,E',    
    0x6c: 'LD L,H',       0x6d: 'LD L,L',    0x6e: 'LD L,(HL)',   0x6f: 'LD L,A',
    0x70: 'LD (HL),B',    0x71: 'LD (HL),C', 0x72: 'LD (HL),D',   0x73: 'LD (HL),E', 
    0x74: 'LD (HL),H',    0x75: 'LD (HL),L', 0x76: 'HALT',        0x77: 'LD (HL),A',
    0x78: 'LD A,B',       0x79: 'LD A,C',    0x7a: 'LD A,D',      0x7b: 'LD A,E',    
    0x7c: 'LD A,H',       0x7d: 'LD A,L',    0x7e: 'LD A,(HL)',   0x7f: 'LD A,A',
    0x80: 'ADD A,B',      0x81: 'ADD A,C',   0x82: 'ADD A,D',     0x83: 'ADD A,E',   
    0x84: 'ADD A,H',      0x85: 'ADD A,L',   0x86: 'ADD A,(HL)',  0x87: 'ADD A,A',
    0x88: 'ADC A,B',      0x89: 'ADC A,C',   0x8a: 'ADC A,D',     0x8b: 'ADC A,E',   
    0x8c: 'ADC A,H',      0x8d: 'ADC A,L',   0x8e: 'ADC A,(HL)',  0x8f: 'ADC A,A',
    0x90: 'SUB B',        0x91: 'SUB C',     0x92: 'SUB D',       0x93: 'SUB E',     
    0x94: 'SUB H',        0x95: 'SUB L',     0x96: 'SUB (HL)',    0x97: 'SUB A',
    0x98: 'SBC A,B',      0x99: 'SBC A,C',   0x9a: 'SBC A,D',     0x9b: 'SBC A,E',   
    0x9c: 'SBC A,H',      0x9d: 'SBC A,L',   0x9e: 'SBC A,(HL)',  0x9f: 'SBC A,A',
    0xa0: 'AND B',        0xa1: 'AND C',     0xa2: 'AND D',       0xa3: 'AND E',     
    0xa4: 'AND H',        0xa5: 'AND L',     0xa6: 'AND (HL)',    0xa7: 'AND A',
    0xa8: 'XOR B',        0xa9: 'XOR C',     0xaa: 'XOR D',       0xab: 'XOR E',  
    0xac: 'XOR H',        0xad: 'XOR L',     0xae: 'XOR (HL)',    0xaf: 'XOR A',
    0xb0: 'OR B',         0xb1: 'OR C',      0xb2: 'OR D',        0xb3: 'OR E',      
    0xb4: 'OR H',         0xb5: 'OR L',      0xb6: 'OR (HL)',     0xb7: 'OR A',
    0xb8: 'CP B',         0xb9: 'CP C',      0xba: 'CP D',        0xbb: 'CP E',     
    0xbc: 'CP H',         0xbd: 'CP L',      0xbe: 'CP (HL)',     0xbf: 'CP A',
    0xc0: 'RET NZ',       0xc1: 'POP BC',    0xc2: 'JP NZ,{0}',   0xc3: 'JP {0}',    
    0xc4: 'CALL NZ,{0}',  0xc5: 'PUSH BC',   0xc6: 'ADD A,{0}',   0xc7: 'RST 00H',
    0xc8: 'RET Z',        0xc9: 'RET',       0xca: 'JP Z,{0}',    0xcb: 'PREFIX CB', 
    0xcc: 'CALL Z,{0}',   0xcd: 'CALL {0}',  0xce: 'ADC A,{0}',   0xcf: 'RST 08H',
    0xd0: 'RET NC',       0xd1: 'POP DE',    0xd2: 'JP NC,{0}',   0xd3: 'Invalid',   
    0xd4: 'CALL NC,{0}',  0xd5: 'PUSH DE',   0xd6: 'SUB {0}',     0xd7: 'RST 10H',
    0xd8: 'RET C',        0xd9: 'RETI',      0xda: 'JP C,{0}',    0xdb: 'Invalid',   
    0xdc: 'CALL C,{0}',   0xdd: 'Invalid',   0xde: 'SBC A,{0}',   0xdf:'RST 18H',
    0xe0: 'LDH ({0}),A',  0xe1: 'POP HL',    0xe2: 'LD (C),A',    0xe3: 'Invalid',   
    0xe4: 'Invalid',      0xe5: 'PUSH HL',   0xe6: 'AND {0}',     0xe7: 'RST 20H',
    0xe8: 'ADD SP,{0}',   0xe9: 'JP (HL)',   0xea: 'LD ({0}),A',  0xeb: 'Invalid',  
    0xec: 'Invalid',      0xed: 'Invalid',   0xee: 'XOR {0}',     0xef: 'RST 28H',
    0xf0: 'LDH A,({0})',  0xf1: 'POP AF',    0xf2: 'LD A,(C)',    0xf3: 'DI',        
    0xf4: 'Invalid',      0xf5: 'PUSH AF',   0xf6: 'OR {0}',      0xf7: 'RST 30H',
    0xf8: 'LD HL,SP+{0}', 0xf9: 'LD SP,HL',  0xfa: 'LD A,({0})',  0xfb: 'EI',        
    0xfc: 'Invalid',      0xfd: 'Invalid',   0xfe: 'CP {0}',      0xff: 'RST 38H'
    }


def toSigned(value): #stolen from gengkev on stackoverflow
        value &= 0xff
        return (value ^ 0x80) - 0x80


def formatOpcodeName(instructions, length, registers):
    if length == 1:
        return opcodeNames[instructions[0]]
    elif length == 2:
        if instructions[0] in [0x18, 0x20, 0x28, 0x30, 0x38, 0xe8, 0xf8]:
            offset = toSigned(instructions[1])
            if instructions[0] in [0xe8, 0xf8]:
                 return opcodeNames[instructions[0]].format(
                        hex(registers[0] + offset))
            return opcodeNames[instructions[0]].format(
                    hex(registers[1] + offset + 2))
        elif instructions[0] in [0xcb, 0x20]:
            return opcodeNames[instructions[0]]
        elif instructions[0] in [0xe0, 0xe2, 0xf0, 0xf2]:
            return opcodeNames[instructions[0]].format(
                    hex(0xff00 + instructions[1]))
        else:
             return opcodeNames[instructions[0]].format(
                    hex(instructions[1]))
    elif length == 3:
         return opcodeNames[instructions[0]].format(
                hex(instructions[2] << 8 | instructions[1]))




def renderTileViewer(rom, offset, screen, pallet):
    scalingFactor = 4 # hardcoded dont change
    mem = []
    for i in range(1024):
        mem.append(rom[(i + offset) % len(rom)])
    frameData = []
    for i in range(8): #tile y
        for j in range(8): # line in tile
            lineData = []
            for k in range(8): #tile X
                #print(f"i = {i}, j = {j}, k = {k}")
                colorByteLowIndex = (i * 128) + (j * 2) + (k * 16)
                colorByteHighIndex = colorByteLowIndex + 1
                #print (colorByteLowIndex, colorByteHighIndex)          
                for l in range(8): #for every color bit pair
                    temp = 0
                    if mem[colorByteHighIndex] & bitMasks[l]:
                        temp += 2
                    if mem[colorByteLowIndex] & bitMasks[l]:
                        temp += 1
                    for m in range(scalingFactor):
                        lineData.append(valueToColorMapping[pallet[temp]])
                #print(f"lenLineData: {len(lineData)}")
            for x in range(scalingFactor):
                frameData.append(lineData)
                #print(len(frameData))
    b = np.array(frameData)
    surf = pygame.surfarray.make_surface(np.flipud(np.rot90(b)))
    screen.blit(surf, ((0, 0)))
    pygame.display.update()


def tileViewer(rom, offset):
    print("U/D Shift by 1024")
    print("L/R Shift by 128")
    print("Shift + L/R shift by 1")
    print("1 2 3 4 Change pallet")
    shift = 0
    pallet = [0, 1, 2, 3]
    clock = pygame.time.Clock()
    #with open(rom, "rb") as f:
    #    rom = f.read()
    screen = pygame.display.set_mode((256, 256), depth=8)
    renderTileViewer(rom, offset, screen, pallet)
    print(hex(offset))
    while True:
        clock.tick(60)
        events = pygame.event.get()
        for event in events:
            if event.type == 768:
                if event.key == 113:
                    return
                elif event.key == 1073742049:
                    shift = 1
                elif event.key == 49:
                    pallet[0] = (pallet[0] + 1) % 4
                    print (pallet)
                    renderTileViewer(rom, offset, screen, pallet)
                elif event.key == 50:
                    pallet[1] = (pallet[1] + 1) % 4
                    print (pallet)
                    renderTileViewer(rom, offset, screen, pallet)
                elif event.key == 51:
                    pallet[2] = (pallet[2] + 1) % 4
                    print (pallet)
                    renderTileViewer(rom, offset, screen, pallet)
                elif event.key == 52:
                    pallet[3] = (pallet[3] + 1) % 4
                    print (pallet)
                    renderTileViewer(rom, offset, screen, pallet)
                elif event.key == 1073741906:
                    offset = (offset - 1024) % len(rom)
                    print (hex(offset))
                    renderTileViewer(rom, offset, screen, pallet)
                elif event.key == 1073741905:
                    offset = (offset + 1024) % len(rom)
                    print (hex(offset))
                    renderTileViewer(rom, offset, screen, pallet)
                elif event.key == 1073741904:
                    if shift:
                        offset = (offset - 1) % len(rom)
                    else:
                        offset = (offset - 128) % len(rom)
                    print (hex(offset))
                    renderTileViewer(rom, offset, screen, pallet)
                elif event.key == 1073741903:
                    if shift:
                        offset = (offset + 1) % len(rom)
                    else:
                        offset = (offset + 128) % len(rom)
                    print (hex(offset))
                    renderTileViewer(rom, offset, screen, pallet)
            elif event.type == 256:
                return
            elif event.type == 769:
                if event.key == 1073742049:
                    shift = 0

                

if __name__ == "__main__":
    import pyboy
    tileViewer(pyboy.cartridgeFile, 0)


