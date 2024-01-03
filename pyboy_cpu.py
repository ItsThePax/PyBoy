import pyboy_mmu

class Cpu():
    def __init__(self, cartridgeRomPath, biosRomPath):
        #registers
        #f: Z S C H X X X X        
        #a 0, f 1, b 2, c 3, d 4, e 5, h 6, l 7
        self.registers = bytearray([0, 0, 0, 0, 0, 0, 0, 0])
        self.regA = self.registers[0]
        self.regF = self.registers[1]
        self.regB = self.registers[2]
        self.regC = self.registers[3]
        self.regD = self.registers[4]
        self.regE = self.registers[5]
        self.regH = self.registers[6]
        self.regL = self.registers[7]
        self.regSP = 0
        self.regPC = 0


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
            self.opd0, self.opd1, self.opd2, self.opd3, self.opd4, self.opd5, self.opd6, self.opd7, 
            self.opd8, self.opd9, self.opda, self.opdb, self.opdc, self.opdd, self.opde, self.opdf, 
            self.ope0, self.ope1, self.ope2, self.ope3, self.ope4, self.ope5, self.ope6, self.ope7, 
            self.ope8, self.ope9, self.opea, self.opeb, self.opec, self.oped, self.opee, self.opef, 
            self.opf0, self.opf1, self.opf2, self.opf3, self.opf4, self.opf5, self.opf6, self.opf7, 
            self.opf8, self.opf9, self.opfa, self.opfb, self.opfc, self.opfd, self.opfe, self.opff
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


        #static masks for easy bit manupulation
        self.setBitMasks = bytes([0x1, 0x2, 0x4, 0x8, 0x10, 0x20, 0x40, 0x80])
        self.resetBitMasks = bytes([0xfe, 0xfd, 0xfb,  0xf7, 0xef, 0xdf, 0xbf, 0x7f])
        
        #next instruction decode buffer
        self.nextInstruction = bytearray([0, 0, 0])
        
        #setup mmu
        self.mmu = pyboy_mmu.Mmu(biosRomPath, cartridgeRomPath)
        return
    

    def getState(self):
        return "A:{} F:{} B:{} C:{} D:{} E:{} H:{} L:{} SP:{} PC:{}".format(
                hex(self.regA), hex(self.regF), hex(self.regB), hex(self.regC),
                hex(self.regD), hex(self.regE), hex(self.regH), hex(self.regL), 
                hex(self.regSP), hex(self.regPC))
    

    def setCarryFlag(self):
        self.setBitInByte(self.regF, 4)


    def resetCarryFlag(self):
        self.resetBitInByte(self.regF, 4)


    def setHalfCarryFlag(self):
        self.setBitInByte(self.regF, 5)


    def resetHalfCarryFlag(self):
        self.resetBitInByte(self.regF, 5)


    def setSubtractionFlag(self):
        self.setBitInByte(self.regF, 6)


    def resetSubtractionFlag(self):
        self.resetBitInByte(self.regF, 6)


    def setZeroFlag(self):
        self.setBitInByte(self.regF, 7)


    def resetZeroFlag(self):
        self.resetBitInByte(self.regF, 7)


    def clearFlags(self):
        self.regF = 0
    

    def setBitInByte(self, target, bit):
        target |= self.setBitMasks[bit]

    
    def resetBitInByte(self, target, bit):
        target &= self.resetBitMasks[bit]


    def getBitSetInByte(self, target, bit):
        result = 0
        if target & self.setBitMasks[bit]:
            result += 1
        return result


    def unpackFlags(self):
        flags = bytearray([0, 0, 0, 0])
        for i in range(0, 3,):
            flags[i] = self.getBitSetInByte(self.regF, 7 - i)
        return flags
    
    # should be passed lenth 4 array/list ordered Z N H C
    def packFlags(self, flags):
        temp = 0
        for i in range(4):
            if flags[i]:
                temp += self.setBitMasks[7- i]
        return temp




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
        self.registers[9] += self.opcodeLength[self.nextInstruction[0]]
        return ticks
    eni = executeNextInstruction
    

    def fetchNextInstruction(self):
        instruction = bytearray([0, 0, 0])
        for i in range(3): 
            instruction[i] = self.mmu.read(self.regPC + i)
        self.nextInstruction = instruction
    fni = fetchNextInstruction

    def fetchAndExecuteNextInstruction(self):
        self.fetchNextInstruction()
        return self.executeNextInstruction()
    feni = fetchAndExecuteNextInstruction
    
    
    #DAA instruction logic. I hate this ##TODO## make me not hate this
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
            self.regF = self.packFlags(flags)
            return x


    #combine 2 char into short
    def combineTwoChar(self, highChar, lowChar):
        temp = highChar * 0x100
        temp += lowChar
        return temp
    

    #split 16 bit value and return upper and lower char
    def splitShort(self, short):
        return bytes(short >> 8, short & 0xff)


    def increment8bitRegisterPairAs16bitValue(self, registerHigh, registerLow):
        temp = self.combineTwoChar(registerHigh, registerLow)
        if temp == 0xffff:
            return 0, 0
        return self.splitShort(temp + 1)
    

    def decrement8bitRegisterPairAs16bitValue(self, registerHigh, registerLow):
        temp = self.combineTwoChar(registerHigh, registerLow)
        if temp == 0:
            return 0xff, 0xff
        return self.splitShort(temp - 1)
    

    def increment8bitRegister(self, register):
        self.resetSubtractionFlag()
        if register &0xf == 0xf:
            self.setHalfCarryFlag()
        else:
            self.resetHalfCarryFlag()
        if register == 0xff:
            self.setZeroFlag()
            return 0
        else:
            self.resetZeroFlag()
            return register + 1

            
    

    #cpu intruction functions
    def op00(self, instruction):
        return 4
    
    def op01(self, instruction):
        self.regB = instruction[2]
        self.regC = instruction[1]
        return 12
    
    def op02(self, instruction):
        self.mmu.write(self.combineTwoChar(self.regB, self.regC), self.regA)
        return 8

    def op03(self, instruction):
        self.regB, self.regC = self.increment8bitRegisterPairAs16bitValue(self.regB, self.regC)
        return 8

    def op04(self, instruction):
        return None

    def op05(self, instruction):
        return None

    def op06(self, instruction):
        return None

    def op07(self, instruction):
        return None

    def op08(self, instruction):
        return None

    def op09(self, instruction):
        return None

    def op0a(self, instruction):
        return None

    def op0b(self, instruction):
        return None

    def op0c(self, instruction):
        return None

    def op0d(self, instruction):
        return None

    def op0e(self, instruction):
        return None

    def op0f(self, instruction):
        return None

    def op10(self, instruction):
        return None

    def op11(self, instruction):
        self.regD = instruction[2]
        self.regE = instruction[1]
        return 12

    def op12(self, instruction):
        self.mmu.write(self.combineTwoChar(self.regD, self.regE), self.regA)
        return 8

    def op13(self, instruction):
        self.regD, self.regE = self.increment8bitRegisterPairAs16bitValue(self.regD, self.regE)
        return 8

    def op14(self, instruction):
        return None

    def op15(self, instruction):
        return None

    def op16(self, instruction):
        return None

    def op17(self, instruction):
        return None

    def op18(self, instruction):
        return None

    def op19(self, instruction):
        return None

    def op1a(self, instruction):
        return None

    def op1b(self, instruction):
        return None

    def op1c(self, instruction):
        return None

    def op1d(self, instruction):
        return None

    def op1e(self, instruction):
        return None

    def op1f(self, instruction):
        return None

    def op20(self, instruction):
        return None

    def op21(self, instruction):
        self.regH = instruction[2]
        self.regL = instruction[1]
        return 12

    def op22(self, instruction):
        self.mmu.write(self.combineTwoChar(self.regH, self.regL), self.regA)
        self.RegH, self.RegL = self.increment8bitRegisterPairAs16bitValue(self.regH, self.regL)
        return 8

    def op23(self, instruction):
        self.regH, self.regL = self.increment8bitRegisterPairAs16bitValue(self.regH, self.regL)
        return 8

    def op24(self, instruction):
        return None

    def op25(self, instruction):
        return None

    def op26(self, instruction):
        return None

    def op27(self, instruction):
        self.regA = self.DAA(self.regA)
        return 4

    def op28(self, instruction):
        return None

    def op29(self, instruction):
        return None

    def op2a(self, instruction):
        return None

    def op2b(self, instruction):
        return None

    def op2c(self, instruction):
        return None

    def op2d(self, instruction):
        return None

    def op2e(self, instruction):
        return None

    def op2f(self, instruction):
        return None

    def op30(self, instruction):
        return None

    def op31(self, instruction):
        self.regSP = self.combineTwoChar(instruction[2], instruction[1])
        return 12

    def op32(self, instruction):
        self.mmu.write(self.combineTwoChar(self.regH, self.regL), self.regA)
        self.RegH, self.RegL = self.decrement8bitRegisterPairAs16bitValue(self.regH, self.regL)
        return 8

    def op33(self, instruction):
        self.regSP += 1
        return 8

    def op34(self, instruction):
        return None

    def op35(self, instruction):
        return None

    def op36(self, instruction):
        return None

    def op37(self, instruction):
        return None

    def op38(self, instruction):
        return None

    def op39(self, instruction):
        return None

    def op3a(self, instruction):
        return None

    def op3b(self, instruction):
        return None

    def op3c(self, instruction):
        return None

    def op3d(self, instruction):
        return None

    def op3e(self, instruction):
        return None

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
    
    


    



      


    
    