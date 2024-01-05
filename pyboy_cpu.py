import pyboy_mmu

#static masks for easy bit manipulation
setBitMasks = bytes([0x1, 0x2, 0x4, 0x8, 0x10, 0x20, 0x40, 0x80])
resetBitMasks = bytes([0xfe, 0xfd, 0xfb,  0xf7, 0xef, 0xdf, 0xbf, 0x7f])
flagBitMasks = bytes([0x00, 0x10, 0x20, 0x30, 0x40, 0x50, 0x60, 0x70, 0x80, 0x90, 0xa0, 0xb0, 0xc0, 0xd0, 0xe0, 0xf0])

#flag mappings
flagZero = 0x80
flagSub = 0x40
flagHalfCarry = 0x20
flagCarry = 0x10
flagNone = 0x0


#type 0 for native 16 bit, type 1 for 8 bit register pair
class register16bit:
    def __init__(self, type):
        if type == 0:
            self.read = self.read16
            self.load = self.load16
            self.value = bytearray([0, 0])
        elif type == 1:
            self.high = register8bit()
            self.low = register8bit()
            self.read = self.readPair
            self.load = self.loadPair

    
    def readPair(self):
        return self.high.read() << 8 | self.low.read()
    
    def loadPair(self, newValue):
        self.high.load(newValue >> 8)
        self.low.load(newValue & 0xff)
    
    def read16(self):
        return self.value[0] << 8 | self.value[1]
    
    def load16(self, newValue):
        self.value[0] = newValue >> 8
        self.value[1] = newValue & 0xff
    
    #add with flag logic
    def add(self, add, flags, flagMask):
        flagMask <<= 4
        oldFlags = flags.read()
        newFlags = 0
        value = self.read()
        if (value & 0xfff) + (add & 0xfff) > 0xfff:
            newFlags += flagHalfCarry
        value += add
        if value > 0xffff:
            newFlags += flagCarry
            value &= 0xffff
        self.load(value)
        newFlags &= flagMask
        oldFlags &= (flagMask ^ 0xff)
        flags.load(newFlags | oldFlags)

    #add without flag logic
    def rawAdd(self, add):
        self.load((self.read() + add) & 0xffff)

    #sub with flag logic
    def sub(self, sub, flags, flagMask):
        self.rawSub(sub)#TODO fix

    #sub without flag logic
    def rawSub(self, sub):
        self.load((self.read() - sub) & 0xffff)

    def inc(self):#TODO write better
        self.rawAdd(1)

    def dec(self,):#TODO write better
        self.rawSub(1)


class register8bit:
    def __init__(self):
        self.value = bytearray([0])

    def read(self):
        return self.value[0]
    
    def load(self, newValue):
        self.value[0] = newValue

    def setBit(self, bitNumber):
        self.value[0] |= setBitMasks[bitNumber]

    def resetBit(self, bitNumber):
        self.value[0] &= resetBitMasks[bitNumber]


    def getBit(self, bitNumber, flags, flagMask):
        flagMask >>= 4
        oldFlags = flags.read()
        newFlags = flagHalfCarry
        if self.value[0] & setBitMasks[bitNumber] == 0:
            newFlags += flagZero
        newFlags &= flagMask
        oldFlags &= (flagMask ^ 0xff)
        flags.load(newFlags | oldFlags)


    def swap(self, flags): #no flag mask, alsways affects all flags
        temp = self.value[0] & 0xf << 4
        self.value[0] >>= 4
        self.value[0] += temp
        if self.value[0] == 0:
            flags.write(flagZero)
        else:
            flags.write(flagNone)


    def add(self, add, flags, flagMask): 
        flagMask <<= 4
        oldFlags = flags.read()
        newFlags = 0
        if (add & 0xf) + (self.value[0] & 0xf) > 0xf:
            newFlags += flagHalfCarry
        temp = add + self.value[0]
        if temp > 0xff:
            newFlags += flagCarry
            temp &= 0xff
        if temp == 0:
            newFlags += flagZero
        self.value[0] = temp
        newFlags &= flagMask
        oldFlags &= (flagMask ^ 0xff)
        flags.load(newFlags | oldFlags)


    def rawAdd(self, add): #no flag logic
        temp = self.value[0] + add
        self.value[0] = temp & 0xff


    def sub(self, sub, flags, flagMask):
        flagMask <<= 4
        oldFlags = flags.read()
        newFlags = flagSub
        if (self.value[0] & 0xf) - (sub & 0xf) < 0:
            newFlags += flagHalfCarry
        temp = self.value[0] - sub
        if temp < 0:
            newFlags += flagCarry
            temp &= 0xff
        if temp == 0:
            newFlags += flagZero
        self.value[0] = temp
        newFlags &= flagMask
        oldFlags &= (flagMask ^ 0xff)
        flags.load(newFlags | oldFlags)


    def rawSub(self, sub):#no flag logic
        temp = self.value[0] - sub
        self.value[0] = temp & 0xff


    def inc(self, flags, flagMask):#todo write dedicated function
        self.add(1, flags, flagMask)


    def dec(self, flags, flagMask):#todo write dedicated function
        self.sub(1, flags, flagMask)
        

class Cpu():
    def __init__(self, cartridgeRomPath, biosRomPath):
        #registers
        #f: Z S H C X X X X        
        #a 0, f 1, b 2, c 3, d 4, e 5, h 6, l 7
        self.regAF = register16bit(1)
        self.regBC = register16bit(1)
        self.regDE = register16bit(1)
        self.regHL = register16bit(1)
        self.regSP = register16bit(0)
        self.regPC = register16bit(0)
        self.regA = self.regAF.high
        self.regF = self.regAF.low
        self.regB = self.regBC.high
        self.regC = self.regBC.low
        self.regD = self.regDE.high
        self.regE = self.regDE.low
        self.regH = self.regHL.high
        self.regL = self.regHL.low

        #used for opcodes operating on (HL)
        self.regDeRef = register8bit()
        

        #table of function references
        self.opcodeFunctions = [
            self.op00, self.op01, self.op02, self.op03, self.op04, self.op05, self.op06, self.op07, 
            self.op08, self.op09, self.op0a, self.op0b, self.op0c, self.op0d, self.op0e, self.op0f, 
            self.op10, self.op11, self.op12, self.op13, self.op14, self.op15, self.op16, self.op17, 
            self.op18, self.op19, self.op1a, self.op1b, self.op1c, self.op1d, self.op1e, self.op1f, 
            self.op20, self.op21, self.op22, self.op23, self.op24, self.op25, self.op26, self.op27, 
            self.op28, self.op29, self.op2a, self.op2b, self.op2c, self.op2d, self.op2e, self.op2f, 
            self.op30, self.op31, self.op32, self.op33, self.op34, self.op35, self.op36, self.op37, 
            self.op38, self.op39, self.op3a, self.op3b, self.op3c, self.op3d, self.op3e, self.op3f, 
            self.op40, self.op41, self.op42, self.op43, self.op44, self.op45, self.op46, self.op47, 
            self.op48, self.op49, self.op4a, self.op4b, self.op4c, self.op4d, self.op4e, self.op4f, 
            self.op50, self.op51, self.op52, self.op53, self.op54, self.op55, self.op56, self.op57, 
            self.op58, self.op59, self.op5a, self.op5b, self.op5c, self.op5d, self.op5e, self.op5f, 
            self.op60, self.op61, self.op62, self.op63, self.op64, self.op65, self.op66, self.op67, 
            self.op68, self.op69, self.op6a, self.op6b, self.op6c, self.op6d, self.op6e, self.op6f, 
            self.op70, self.op71, self.op72, self.op73, self.op74, self.op75, self.op76, self.op77, 
            self.op78, self.op79, self.op7a, self.op7b, self.op7c, self.op7d, self.op7e, self.op7f, 
            self.op80, self.op81, self.op82, self.op83, self.op84, self.op85, self.op86, self.op87, 
            self.op88, self.op89, self.op8a, self.op8b, self.op8c, self.op8d, self.op8e, self.op8f, 
            self.op90, self.op91, self.op92, self.op93, self.op94, self.op95, self.op96, self.op97, 
            self.op98, self.op99, self.op9a, self.op9b, self.op9c, self.op9d, self.op9e, self.op9f, 
            self.opa0, self.opa1, self.opa2, self.opa3, self.opa4, self.opa5, self.opa6, self.opa7, 
            self.opa8, self.opa9, self.opaa, self.opab, self.opac, self.opad, self.opae, self.opaf, 
            self.opb0, self.opb1, self.opb2, self.opb3, self.opb4, self.opb5, self.opb6, self.opb7, 
            self.opb8, self.opb9, self.opba, self.opbb, self.opbc, self.opbd, self.opbe, self.opbf, 
            self.opc0, self.opc1, self.opc2, self.opc3, self.opc4, self.opc5, self.opc6, self.opc7, 
            self.opc8, self.opc9, self.opca, self.opcb, self.opcc, self.opcd, self.opce, self.opcf, 
            self.opd0, self.opd1, self.opd2, self.invalidOp, self.opd4, self.opd5, self.opd6, self.opd7, 
            self.opd8, self.opd9, self.opda, self.invalidOp, self.opdc, self.invalidOp, self.opde, self.opdf, 
            self.ope0, self.ope1, self.ope2, self.invalidOp, self.invalidOp, self.ope5, self.ope6, self.ope7, 
            self.ope8, self.ope9, self.opea, self.invalidOp, self.invalidOp, self.invalidOp, self.opee, self.opef, 
            self.opf0, self.opf1, self.opf2, self.opf3, self.invalidOp, self.opf5, self.opf6, self.opf7, 
            self.opf8, self.opf9, self.opfa, self.opfb, self.invalidOp, self.invalidOp, self.opfe, self.opff
        ]


        self.opcodeLength = [
            1, 3, 1, 1, 1, 1, 2, 1, 3, 1, 1, 1, 1, 1, 2, 1,
            1, 3, 1, 1, 1, 1, 2, 1, 2, 1, 1, 1, 1, 1, 2, 1,
            2, 3, 1, 1, 1, 1, 2, 1, 2, 1, 1, 1, 1, 1, 2, 1,
            2, 3, 1, 1, 1, 1, 2, 1, 2, 1, 1, 1, 1, 1, 2, 1,
            1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
            1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
            1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
            1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
            1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
            1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
            1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
            1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
            1, 1, 3, 3, 3, 1, 2, 1, 1, 1, 3, 2, 3, 3, 2, 1,
            1, 1, 3, 4, 3, 1, 2, 1, 1, 1, 3, 4, 3, 4, 2, 1,
            2, 1, 1, 4, 4, 1, 2, 1, 2, 1, 3, 4, 4, 4, 2, 1,
            2, 1, 1, 1, 4, 1, 2, 1, 2, 1, 3, 1, 4, 4, 2, 1
        ]

    
      
        
        
        #next instruction decode buffer
        self.nextInstruction = bytearray([0, 0, 0])
        
        #setup mmu
        self.mmu = pyboy_mmu.Mmu(biosRomPath, cartridgeRomPath)
        return
    

    run = 1


    def reset(self):
        self.regAF.load(0)
        self.regBC.load(0)
        self.regDE.load(0)
        self.regHL.load(0)
        self.regSP.load(0)
        self.regPC.load(0)
        self.regDeRef.load(0)


    def getState(self):
        return "A:{} F:{} B:{} C:{} D:{} E:{} H:{} L:{} SP:{} PC:{}".format(
                hex(self.regA.read()), hex(self.regF.read()), hex(self.regB.read()), hex(self.regC.read()),
                hex(self.regD.read()), hex(self.regE.read()), hex(self.regH.read()), hex(self.regL.read()), 
                hex(self.regSP.read()), hex(self.regPC.read()))
    

    def setCarryFlag(self):
        self.regF.setBit(4)


    def resetCarryFlag(self):
        self.regF.resetBit(4)


    def setHalfCarryFlag(self):
        self.regF.setBit(5)


    def resetHalfCarryFlag(self):
        self.regF.resetBit(5)


    def setSubtractionFlag(self):
        self.regF.setBit(6)


    def resetSubtractionFlag(self):
        self.regF.resetBit(6)


    def setZeroFlag(self):
        self.regF.setBit(7)


    def resetZeroFlag(self):
        self.regF.resetBit(7)


    def clearFlags(self):
        self.regF.load(0)


    #legacy fucntion, still used by DAA
    def unpackFlags(self):
        fValue = self.regF.read()
        flags = bytearray([0, 0, 0, 0])
        for i in range(0, 3,):
            if fValue & setBitMasks[7 - i]:
                flags[i] = 1
        return flags
    

    #legacy function, still used by DAA
    # should be passed lenth 4 array/list ordered Z N H C
    def packFlags(self, flags):
        fValue = 0
        for i in range(4):
            if flags[i]:
                fValue += setBitMasks[7- i]
        return fValue


    def toSigned(value): #stolen from gengkev on stackoverflow
        value &= 0xff
        return (value ^ 0x80) - 0x80
    

    def printState(self):
        print (self.getState())
    ps = printState


    def printNextInstruction(self):
        for i in range(self.opcodeLength[self.nextInstruction[0]]):
            print (hex(self.nextInstruction[i]), end=" ")
        print("")
    pni = printNextInstruction

    
    def executeNextInstruction(self):
        ticks = self.opcodeFunctions[self.nextInstruction[0]](self.nextInstruction)
        self.regPC.rawAdd(self.opcodeLength[self.nextInstruction[0]])
        return ticks
    eni = executeNextInstruction
    

    def fetchNextInstruction(self):
        pc = self.regPC.read()
        instruction = bytearray([0, 0, 0])
        for i in range(3): 
            instruction[i] = self.mmu.read(pc + i)
        self.nextInstruction = instruction
    fni = fetchNextInstruction


    def fetchAndExecuteNextInstruction(self):
        self.fetchNextInstruction()
        return self.executeNextInstruction()
    feni = fetchAndExecuteNextInstruction
    
    
    #DAA instruction logic. I hate this ##TODO## make me not hate this
    #legacy function writeen before implementing flag masks, handles own flag logic so flag mask not needed
    def DAA(self, x):
        flags = self.unpackFlags()
        flags[0] = 0
        xLowNibble = x & 0xf
        xHighNibble = x >> 4
        if flags[1] == 0:
            if flags[3] == 0 and 0x0 <= xHighNibble <= 0x9 and flags[2] == 0 and 0x0 <= xLowNibble <= 0x9:
                pass
            elif flags[3] == 0 and 0x0 <= xHighNibble <= 0x8 and flags[2] == 0 and 0xa <= xLowNibble <= 0xf:
                x += 0x6
            elif flags[3] == 0 and 0x0 <= xHighNibble <= 0x9 and flags[2] == 1 and 0x0 <= xLowNibble <= 0x3:
                x += 0x6
            elif flags[3] == 0 and 0xa <= xHighNibble <= 0xf and flags[2] == 0 and 0x0 <= xLowNibble <= 0x9:
                x += 0x60
                flags[3] = 1
            elif flags[3] == 0 and 0x9 <= xHighNibble <= 0xf and flags[2] == 0 and 0xa <= xLowNibble <= 0xf:
                x += 0x66
                flags[3] = 1
            elif flags[3] == 0 and 0xa <= xHighNibble <= 0xf and flags[2] == 1 and 0x0 <= xLowNibble <= 0x3:
                x += 0x66
                flags[3] = 1
            elif flags[3] == 1 and 0x0 <= xHighNibble <= 0x2 and flags[2] == 0 and 0x0 <= xLowNibble <= 0x9:
                x += 0x60
                flags[3] = 1
            elif flags[3] == 1 and 0x0 <= xHighNibble <= 0x2 and flags[2] == 0 and 0xa <= xLowNibble <= 0xf:
                x += 0x66
                flags[3] = 1
            elif flags[3] == 1 and 0x0 <= xHighNibble <= 0x3 and flags[2] == 1 and 0x0 <= xLowNibble <= 0x3:
                x += 0x66
                flags[3] = 1
            x &= 0xff
            if x == 0:
                flags[0] = 1
            return x
        else:
            if flags[3] == 0 and 0x0 <= xHighNibble <= 0x9 and flags[2] == 0 and 0x0 <= xLowNibble <= 0x9:
                pass
            elif flags[3] == 0 and 0x0 <= xHighNibble <= 0x8 and flags[2] == 1 and 0x6 <= xLowNibble <= 0xf:
                x += 0xfa
            elif flags[3] == 1 and 0x7 <= xHighNibble <= 0xf and flags[2] == 0 and 0x0 <= xLowNibble <= 0x9:
                x += 0xa0
            elif flags[3] == 1 and 0x6 <= xHighNibble <= 0xf and flags[2] == 1 and 0x6 <= xLowNibble <= 0xf:
                x += 0x9a
            x &= 0xff
            if x == 0:
                flags[0] = 1
            self.regF.write(self.packFlags(flags))
            return x


    #combine 2 char into short
    def combineTwoChar(self, highChar, lowChar):
        temp = highChar * 0x100
        temp += lowChar
        return temp
    

    #split 16 bit value and return upper and lower char
    def splitShort(self, short):
        return bytes(short >> 8, short & 0xff)  


    #cpu intruction functions
    def op00(self, instruction):
        return 4
    
    def op01(self, instruction):
        value = instruction[2] << 8 | instruction[1]
        self.regBC.load(value)
        return 12
    
    def op02(self, instruction):
        addr = self.regBC.read()
        self.mmu.write(addr, self.regA.read())
        return 8

    def op03(self, instruction):
        self.regBC.inc()
        return 8

    def op04(self, instruction):
        self.regB.inc(self.regF, 0xe)
        return 4

    def op05(self, instruction):
        self.regB.dec(self.regF, 0xe)
        return 4

    def op06(self, instruction):
        self.regB.load(instruction[1])
        return 8

    def op07(self, instruction):
        return None

    def op08(self, instruction):
        address = instruction[2] << 8 | instruction[1]
        sp = self.regSP.read()
        self.mmu.write(address, sp & 0xff)
        self.mmu.write(address + 1, sp >> 8)
        self.regSP.rawSub(2)
        return 20

    def op09(self, instruction):
        self.regHL.add(self.regBC.read(), self.regF, 0x7)
        return 8
    
    def op0a(self, instruction):
        self.regA.load(self.mmu.read(self.regBC.read()))
        return 8

    def op0b(self, instruction):
        self.regBC.dec()
        return 0

    def op0c(self, instruction):
        self.regC.inc(self.regF, 0xe)
        return 4

    def op0d(self, instruction):
        self.regC.dec(self.regF, 0xe)
        return 4

    def op0e(self, instruction):
        self.regC.load(instruction[1])
        return 8

    def op0f(self, instruction):
        return None

    def op10(self, instruction):
        self.run = 0
        print("STOP")
        return 4

    def op11(self, instruction):
        value = instruction[2] << 8 | instruction[1]
        self.regDE.load(value)
        return 12

    def op12(self, instruction):
        addr = self.regDE.read()
        self.mmu.write(addr, self.regA.read())
        return 8

    def op13(self, instruction):
        self.regDE.inc()
        return 8

    def op14(self, instruction):
        self.regD.inc(self.regF, 0xe)
        return 4

    def op15(self, instruction):
        self.regD.dec(self.regF, 0xe)
        return 4

    def op16(self, instruction):
        self.regD.load(instruction[1])
        return 8

    def op17(self, instruction):
        return None

    def op18(self, instruction): #this is a little janky, but register.add() wont work reliable with negative numbers ##TODO test this is might be bad
        if instruction[0] & 0x80: #number is negative and we must sub
            self.regPC.rawSub(abs(self.toSigned(instruction[1])))
        else: #number is positive and we must add
            self.regPC.rawAdd(instruction[1])
        return 12

    def op19(self, instruction):
        self.regHL.add(self.regDE.read(), self.regF, 0x7)
        return 8

    def op1a(self, instruction):
        self.regA.load(self.mmu.read(self.regDE.read()))
        return 8

    def op1b(self, instruction):
        return None

    def op1c(self, instruction):
        self.regE.inc(self.regF, 0xe)
        return 4

    def op1d(self, instruction):
        self.regE.dec(self.regF, 0xe)
        return 4

    def op1e(self, instruction):
        self.regE.load(instruction[1])
        return 8

    def op1f(self, instruction):
        return None

    def op20(self, instruction):
        return None

    def op21(self, instruction):
        value = instruction[2] << 8 | instruction[1]
        self.regHL.load(value)
        return 12

    def op22(self, instruction):
        addr = self.regDE.read()
        self.mmu.write(addr, self.regA.read())
        self.regHL.inc()
        return 8

    def op23(self, instruction):
        self.regHL.inc()
        return 8

    def op24(self, instruction):
        self.regH.inc(self.regF, 0xe)
        return 4

    def op25(self, instruction):
        self.regH.dec(self.regF, 0xe)
        return 4

    def op26(self, instruction):
        self.regH.load(instruction[1])
        return 8

    def op27(self, instruction):
        return None

    def op28(self, instruction):
        return None

    def op29(self, instruction):
        self.regHL.add(self.regHL.read(), self.regF, 0x7)
        return 8

    def op2a(self, instruction):
        self.regA.load(self.mmu.read(self.regHL.read()))
        self.regHL.inc()
        return 8

    def op2b(self, instruction):
        return None

    def op2c(self, instruction):
        self.regL.inc(self.regF, 0xe)
        return 4

    def op2d(self, instruction):
        self.regL.dec(self.regF, 0xe)
        return 4

    def op2e(self, instruction):
        self.regL.load(instruction[1])
        return 8

    def op2f(self, instruction):
        return None

    def op30(self, instruction):
        return None

    def op31(self, instruction):
        value = instruction[2] << 8 | instruction[1]
        self.regSP.load(value)
        return 12

    def op32(self, instruction):
        addr = self.regDE.read()
        self.mmu.write(addr, self.regA.read())
        self.regHL.dec()
        return 8

    def op33(self, instruction):
        self.regSP.inc()
        return 8

    def op34(self, instruction):
        self.regDeRef.load(self.mmu.read(self.regHL.read()))
        self.regDeRef.inc(self.regF, 0xe)
        self.mmu.write(self.regHL.read(), self.regDeRef.read())
        return 12
    
    def op35(self, instruction):
        self.regDeRef.load(self.mmu.read(self.regHL.read()))
        self.regDeRef.dec(self.regF, 0xe)
        self.mmu.write(self.regHL.read(), self.regDeRef.read())
        return 12

    def op36(self, instruction):
        self.mmu.write(self.regHL.read(), instruction[1])
        return 

    def op37(self, instruction):
        return None

    def op38(self, instruction):
        return None

    def op39(self, instruction):
        self.regHL.add(self.regSP.read(), self.regF, 0x7)
        return 8

    def op3a(self, instruction):
        self.regA.load(self.mmu.read(self.regHL.read()))
        self.regHL.dec()
        return 8

    def op3b(self, instruction):
        return None

    def op3c(self, instruction):
        self.regA.inc(self.regF, 0xe)
        return 4

    def op3d(self, instruction):
        self.regA.dec(self.regF, 0xe)
        return 4

    def op3e(self, instruction):
        self.regA.load(instruction[1])
        return 8

    def op3f(self, instruction):
        return None

    def op40(self, instruction):
        return None

    def op41(self, instruction):
        return None

    def op42(self, instruction):
        return None

    def op43(self, instruction):
        return None

    def op44(self, instruction):
        return None

    def op45(self, instruction):
        return None

    def op46(self, instruction):
        return None

    def op47(self, instruction):
        return None

    def op48(self, instruction):
        return None

    def op49(self, instruction):
        return None

    def op4a(self, instruction):
        return None

    def op4b(self, instruction):
        return None

    def op4c(self, instruction):
        return None

    def op4d(self, instruction):
        return None

    def op4e(self, instruction):
        return None

    def op4f(self, instruction):
        return None

    def op50(self, instruction):
        return None

    def op51(self, instruction):
        return None

    def op52(self, instruction):
        return None

    def op53(self, instruction):
        return None

    def op54(self, instruction):
        return None

    def op55(self, instruction):
        return None

    def op56(self, instruction):
        return None

    def op57(self, instruction):
        return None

    def op58(self, instruction):
        return None

    def op59(self, instruction):
        return None

    def op5a(self, instruction):
        return None

    def op5b(self, instruction):
        return None

    def op5c(self, instruction):
        return None

    def op5d(self, instruction):
        return None

    def op5e(self, instruction):
        return None

    def op5f(self, instruction):
        return None

    def op60(self, instruction):
        return None

    def op61(self, instruction):
        return None

    def op62(self, instruction):
        return None

    def op63(self, instruction):
        return None

    def op64(self, instruction):
        return None

    def op65(self, instruction):
        return None

    def op66(self, instruction):
        return None

    def op67(self, instruction):
        return None

    def op68(self, instruction):
        return None

    def op69(self, instruction):
        return None

    def op6a(self, instruction):
        return None

    def op6b(self, instruction):
        return None

    def op6c(self, instruction):
        return None

    def op6d(self, instruction):
        return None

    def op6e(self, instruction):
        return None

    def op6f(self, instruction):
        return None

    def op70(self, instruction):
        return None

    def op71(self, instruction):
        return None

    def op72(self, instruction):
        return None

    def op73(self, instruction):
        return None

    def op74(self, instruction):
        return None

    def op75(self, instruction):
        return None

    def op76(self, instruction):
        return None

    def op77(self, instruction):
        return None

    def op78(self, instruction):
        return None

    def op79(self, instruction):
        return None

    def op7a(self, instruction):
        return None

    def op7b(self, instruction):
        return None

    def op7c(self, instruction):
        return None

    def op7d(self, instruction):
        return None

    def op7e(self, instruction):
        return None

    def op7f(self, instruction):
        return None

    def op80(self, instruction):
        return None

    def op81(self, instruction):
        return None

    def op82(self, instruction):
        return None

    def op83(self, instruction):
        return None

    def op84(self, instruction):
        return None

    def op85(self, instruction):
        return None

    def op86(self, instruction):
        return None

    def op87(self, instruction):
        return None

    def op88(self, instruction):
        return None

    def op89(self, instruction):
        return None

    def op8a(self, instruction):
        return None

    def op8b(self, instruction):
        return None

    def op8c(self, instruction):
        return None

    def op8d(self, instruction):
        return None

    def op8e(self, instruction):
        return None

    def op8f(self, instruction):
        return None

    def op90(self, instruction):
        return None

    def op91(self, instruction):
        return None

    def op92(self, instruction):
        return None

    def op93(self, instruction):
        return None

    def op94(self, instruction):
        return None

    def op95(self, instruction):
        return None

    def op96(self, instruction):
        return None

    def op97(self, instruction):
        return None

    def op98(self, instruction):
        return None

    def op99(self, instruction):
        return None

    def op9a(self, instruction):
        return None

    def op9b(self, instruction):
        return None

    def op9c(self, instruction):
        return None

    def op9d(self, instruction):
        return None

    def op9e(self, instruction):
        return None

    def op9f(self, instruction):
        return None

    def opa0(self, instruction):
        return None

    def opa1(self, instruction):
        return None

    def opa2(self, instruction):
        return None

    def opa3(self, instruction):
        return None

    def opa4(self, instruction):
        return None

    def opa5(self, instruction):
        return None

    def opa6(self, instruction):
        return None

    def opa7(self, instruction):
        return None

    def opa8(self, instruction):
        return None

    def opa9(self, instruction):
        return None

    def opaa(self, instruction):
        return None

    def opab(self, instruction):
        return None

    def opac(self, instruction):
        return None

    def opad(self, instruction):
        return None

    def opae(self, instruction):
        return None

    def opaf(self, instruction):
        return None
    
    def opb0(self, instruction):
        return None

    def opb1(self, instruction):
        return None

    def opb2(self, instruction):
        return None

    def opb3(self, instruction):
        return None

    def opb4(self, instruction):
        return None

    def opb5(self, instruction):
        return None

    def opb6(self, instruction):
        return None

    def opb7(self, instruction):
        return None

    def opb8(self, instruction):
        return None

    def opb9(self, instruction):
        return None

    def opba(self, instruction):
        return None

    def opbb(self, instruction):
        return None

    def opbc(self, instruction):
        return None

    def opbd(self, instruction):
        return None

    def opbe(self, instruction):
        return None

    def opbf(self, instruction):
        return None

    def opc0(self, instruction):
        return None

    def opc1(self, instruction):
        return None

    def opc2(self, instruction):
        return None

    def opc3(self, instruction):
        return None

    def opc4(self, instruction):
        return None

    def opc5(self, instruction):
        return None

    def opc6(self, instruction):
        return None

    def opc7(self, instruction):
        return None

    def opc8(self, instruction):
        return None

    def opc9(self, instruction):
        return None

    def opca(self, instruction):
        return None

    def opcb(self, instruction):
        return None

    def opcc(self, instruction):
        return None

    def opcd(self, instruction):
        return None

    def opce(self, instruction):
        return None

    def opcf(self, instruction):
        return None

    def opd0(self, instruction):
        return None

    def opd1(self, instruction):
        return None

    def opd2(self, instruction):
        return None

    def opd3(self, instruction):
        return None

    def opd4(self, instruction):
        return None

    def opd5(self, instruction):
        return None

    def opd6(self, instruction):
        return None

    def opd7(self, instruction):
        return None

    def opd8(self, instruction):
        return None

    def opd9(self, instruction):
        return None

    def opda(self, instruction):
        return None

    def opdb(self, instruction):
        return None

    def opdc(self, instruction):
        return None

    def opdd(self, instruction):
        return None

    def opde(self, instruction):
        return None

    def opdf(self, instruction):
        return None

    def ope0(self, instruction):
        return None

    def ope1(self, instruction):
        return None

    def ope2(self, instruction):
        return None

    def ope3(self, instruction):
        return None

    def ope4(self, instruction):
        return None

    def ope5(self, instruction):
        return None

    def ope6(self, instruction):
        return None

    def ope7(self, instruction):
        return None

    def ope8(self, instruction):
        return None

    def ope9(self, instruction):
        return None

    def opea(self, instruction):
        return None

    def opeb(self, instruction):
        return None

    def opec(self, instruction):
        return None

    def oped(self, instruction):
        return None

    def opee(self, instruction):
        return None

    def opef(self, instruction):
        return None

    def opf0(self, instruction):
        return None

    def opf1(self, instruction):
        return None

    def opf2(self, instruction):
        return None

    def opf3(self, instruction):
        return None

    def opf4(self, instruction):
        return None

    def opf5(self, instruction):
        return None

    def opf6(self, instruction):
        return None

    def opf7(self, instruction):
        return None

    def opf8(self, instruction):
        return None

    def opf9(self, instruction):
        return None

    def opfa(self, instruction):
        return None

    def opfb(self, instruction):
        return None

    def opfc(self, instruction):
        return None

    def opfd(self, instruction):
        return None

    def opfe(self, instruction):
        return None

    def opff(self, instruction):
        return None
    
    def invalidOp(self, instruction):
        print("invalid Opcode called")
        self.run = 0
        return None
    