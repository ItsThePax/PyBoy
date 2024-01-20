import debug


#static masks for easy bit manipulation
setBitMasks = bytes([
    0x1, 0x2, 0x4, 0x8, 
    0x10, 0x20, 0x40, 0x80])
resetBitMasks = bytes([
    0xfe, 0xfd, 0xfb, 0xf7, 
    0xef, 0xdf, 0xbf, 0x7f]) 


#flag mappings
flagZero = 0x80
flagSub = 0x40
flagHalfCarry = 0x20
flagCarry = 0x10
flagNone = 0x0


#type 0 for native 16 bit, type 1 for 8 bit register pair
class Register16bit:
    def __init__(self, regType):
        if regType == 0:
            self.read = self.read16
            self.load = self.load16
            self.value = bytearray([0, 0])
        elif regType == 1:
            self.high = Register8bit()
            self.low = Register8bit()
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

    #add 1, never uses flags
    def inc(self):#TODO write better
        self.rawAdd(1)

    #sub 1, never uses flags
    def dec(self,):#TODO write better
        self.rawSub(1)


class Register8bit:
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
        flagMask <<= 4
        oldFlags = flags.read()
        newFlags = flagHalfCarry
        if self.value[0] & setBitMasks[bitNumber] == 0:
            newFlags += flagZero
        newFlags &= flagMask
        oldFlags &= (flagMask ^ 0xff)
        flags.load(newFlags | oldFlags)

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

    def adc(self, add, flags, flagMask): 
        flagMask <<= 4
        oldFlags = flags.read()
        newFlags = 0
        if (add & 0xf) + (self.value[0] & 0xf) > 0xf:
            newFlags += flagHalfCarry
        temp = add + self.value[0]
        if oldFlags & flagCarry:
            temp += 1
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

    def sbc(self, sub, flags, flagMask):
        flagMask <<= 4
        oldFlags = flags.read()
        newFlags = flagSub
        if (self.value[0] & 0xf) - (sub & 0xf) < 0:
            newFlags += flagHalfCarry
        temp = self.value[0] - sub
        if oldFlags & flagCarry:
            temp -= 1 
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

    def band(self, binAnd, flags): #always use all flags
        self.value[0] &= binAnd
        if self.value[0] == 0:
            flags.load(flagZero | flagHalfCarry)
        else:
            flags.load(flagHalfCarry)
        
    def bxor(self, binXor, flags): #always use all flags
        self.value[0] ^= binXor
        if self.value[0] == 0:
            flags.load(flagZero)
        else:
            flags.load(flagNone)

    def bor(self, binOr, flags): #always use all flags
        self.value[0] |= binOr
        if self.value[0] == 0:
            flags.load(flagZero)
        else:
            flags.load(flagNone)
    
    def cp(self, sub, flags):
        newFlags = flagSub
        if (self.value[0] & 0xf) - (sub & 0xf) < 0:
            newFlags += flagHalfCarry
        temp = self.value[0] - sub 
        if temp < 0:
            newFlags += flagCarry
            temp &= 0xff
        if temp == 0:
            newFlags += flagZero
        flags.load(newFlags)

    def rlca(self, flags):
        temp = self.value[0] << 1
        if temp >= 256:
            flags.load(flagCarry)
            self.value[0] = temp  & 0xff
        else:
            flags.load(flagNone)
            self.value[0] = temp

    def rl(self, flags):
        newFlags = 0
        c = flags.read() & flagCarry
        if self.value[0] & 0x80:
            newFlags += flagCarry
            self.value[0] &= resetBitMasks[7]
        self.value[0] <<= 1
        if c:
            self.value[0] += 1
        if self.value[0] == 0:
            newFlags += flagZero
        flags.load(newFlags)

    def rlc(self, flags):
        newFlags = 0
        c = self.value[0] & 0x80
        if c:
            newFlags |= flagCarry
            self.value[0] = (self.value[0] - 0x80) << 1
            self.value[0] += 1
        else:
            self.value[0] <<=1
            if self.value[0] == 0:
                newFlags |= flagZero
        flags.load(newFlags)

    def rla(self, flags):
        c = flags.read() & flagCarry
        if self.value[0] & 0x80:
            flags.load(flagCarry)
            self.value[0] &= resetBitMasks[7]
        else:
            flags.load(flagNone)
        self.value[0] <<= 1
        if c:
            self.value[0] += 1
            
    def rrca(self, flags):
        temp = 0
        if self.value[0] & 0x1:
            temp = 0x80
            flags.load(flagCarry)
        else:
            flags.load(flagNone)
        self.value[0] >>= 1
        self.value[0] += temp

    def rrc(self, flags):
        newFlags = 0
        c = self.value[0] & 0x1
        self.value[0] >>= 1
        if c:
            newFlags |= flagCarry
            self.value[0] += 0x80
        else:
            if self.value[0] == 0:
                newFlags |= flagZero
        flags.load(newFlags)
               
    def rra(self, flags):
        c = flags.read() & flagCarry
        if self.value[0] & 0x1:
            flags.load(flagCarry)
        else:
            flags.load(flagNone)
        self.value[0] >>= 1
        if c:
            self.value[0] |= setBitMasks[7]

    def rr(self, flags):
        c = flags.read() & flagCarry
        newFlags = 0
        if self.value[0] & 0x1:
            newFlags |= flagCarry
        self.value[0] >>= 1
        if c:
            self.value[0] += 0x80
        if self.value[0] == 0:
            newFlags |= flagZero
        flags.load(newFlags)

    def sla(self, flags):
        newFlags = 0
        if self.value[0] & 0x80:
            self.value[0] -= 0x80
            newFlags |= flagCarry
        self.value[0] <<= 1
        if self.value[0] == 0:
            newFlags |= flagZero
        flags.load(newFlags)

    def sra(self, flags):
        newFlags = 0
        if self.value[0] & 0x1:
            newFlags |= flagCarry
        bit7 = self.value[0] & 0x80
        self.value[0] >>= 1
        self.value[0] += bit7
        if self.value[0] == 0:
            newFlags |= flagZero
        flags.load(newFlags)

    def srl(self, flags):
        newFlags = 0
        if self.value[0] & 0x1:
            newFlags |= flagCarry
        self.value[0] >>= 1
        if self.value[0] == 0:
            newFlags |= flagZero
        flags.load(newFlags)

    def swap(self, flags):
        temp = (self.value[0] & 0xf) << 4
        self.value[0] >>= 4
        self.value[0] += temp
        if self.value[0] == 0:
            flags.load(flagZero)
        else:
            flags.load(flagNone)

    def DAA(self, flags):
        oldFlags = flags.read()
        newFlags = oldFlags & 0x50 
        temp = 0
        if oldFlags & 0x40:
            if oldFlags & 0x10:
                temp += 0x60
            if oldFlags & 0x20:
                temp += 0x6
            self.rawSub(temp)
        else:
            if self.value[0] > 0x99 or oldFlags & 0x10:
                temp += 0x60
                newFlags |= 0x10
            if (self.value[0] & 0xf) > 0x9 or oldFlags & 0x20:
                temp += 0x6
            self.rawAdd(temp)
        if self.value[0] == 0:
            newFlags |= 0x80
        flags.load(newFlags)        

class Cpu():
    def __init__(self, mmu):
        #registers
        #f: Z S H C X X X X        
        #a 0, f 1, b 2, c 3, d 4, e 5, h 6, l 7
        self.regAF = Register16bit(1)
        self.regBC = Register16bit(1)
        self.regDE = Register16bit(1)
        self.regHL = Register16bit(1)
        self.regSP = Register16bit(0)
        self.regPC = Register16bit(0)
        self.regA = self.regAF.high
        self.regF = self.regAF.low
        self.regB = self.regBC.high
        self.regC = self.regBC.low
        self.regD = self.regDE.high
        self.regE = self.regDE.low
        self.regH = self.regHL.high
        self.regL = self.regHL.low

        #used for opcodes operating on (HL)
        self.regDeRef = Register8bit()
        
        #table of function references
        self.opcodeFunctions = [
            self.op00, self.op01, self.op02, self.op03, 
            self.op04, self.op05, self.op06, self.op07, 
            self.op08, self.op09, self.op0a, self.op0b, 
            self.op0c, self.op0d, self.op0e, self.op0f, 
            self.op10, self.op11, self.op12, self.op13, 
            self.op14, self.op15, self.op16, self.op17, 
            self.op18, self.op19, self.op1a, self.op1b, 
            self.op1c, self.op1d, self.op1e, self.op1f, 
            self.op20, self.op21, self.op22, self.op23, 
            self.op24, self.op25, self.op26, self.op27, 
            self.op28, self.op29, self.op2a, self.op2b, 
            self.op2c, self.op2d, self.op2e, self.op2f, 
            self.op30, self.op31, self.op32, self.op33, 
            self.op34, self.op35, self.op36, self.op37, 
            self.op38, self.op39, self.op3a, self.op3b, 
            self.op3c, self.op3d, self.op3e, self.op3f, 
            self.op40, self.op41, self.op42, self.op43, 
            self.op44, self.op45, self.op46, self.op47, 
            self.op48, self.op49, self.op4a, self.op4b, 
            self.op4c, self.op4d, self.op4e, self.op4f, 
            self.op50, self.op51, self.op52, self.op53, 
            self.op54, self.op55, self.op56, self.op57, 
            self.op58, self.op59, self.op5a, self.op5b, 
            self.op5c, self.op5d, self.op5e, self.op5f, 
            self.op60, self.op61, self.op62, self.op63, 
            self.op64, self.op65, self.op66, self.op67, 
            self.op68, self.op69, self.op6a, self.op6b, 
            self.op6c, self.op6d, self.op6e, self.op6f, 
            self.op70, self.op71, self.op72, self.op73, 
            self.op74, self.op75, self.op76, self.op77, 
            self.op78, self.op79, self.op7a, self.op7b, 
            self.op7c, self.op7d, self.op7e, self.op7f, 
            self.op80, self.op81, self.op82, self.op83, 
            self.op84, self.op85, self.op86, self.op87, 
            self.op88, self.op89, self.op8a, self.op8b, 
            self.op8c, self.op8d, self.op8e, self.op8f, 
            self.op90, self.op91, self.op92, self.op93, 
            self.op94, self.op95, self.op96, self.op97, 
            self.op98, self.op99, self.op9a, self.op9b, 
            self.op9c, self.op9d, self.op9e, self.op9f, 
            self.opa0, self.opa1, self.opa2, self.opa3, 
            self.opa4, self.opa5, self.opa6, self.opa7, 
            self.opa8, self.opa9, self.opaa, self.opab, 
            self.opac, self.opad, self.opae, self.opaf, 
            self.opb0, self.opb1, self.opb2, self.opb3, 
            self.opb4, self.opb5, self.opb6, self.opb7, 
            self.opb8, self.opb9, self.opba, self.opbb, 
            self.opbc, self.opbd, self.opbe, self.opbf, 
            self.opc0, self.opc1, self.opc2, self.opc3, 
            self.opc4, self.opc5, self.opc6, self.opc7, 
            self.opc8, self.opc9, self.opca, self.opcb, 
            self.opcc, self.opcd, self.opce, self.opcf, 
            self.opd0, self.opd1, self.opd2, self.invalidOp, 
            self.opd4, self.opd5, self.opd6, self.opd7, 
            self.opd8, self.opd9, self.opda, self.invalidOp, 
            self.opdc, self.invalidOp, self.opde, self.opdf, 
            self.ope0, self.ope1, self.ope2, self.invalidOp, 
            self.invalidOp, self.ope5, self.ope6, self.ope7, 
            self.ope8, self.ope9, self.opea, self.invalidOp, 
            self.invalidOp, self.invalidOp, self.opee, self.opef, 
            self.opf0, self.opf1, self.opf2, self.opf3, 
            self.invalidOp, self.opf5, self.opf6, self.opf7, 
            self.opf8, self.opf9, self.opfa, self.opfb, 
            self.invalidOp, self.invalidOp, self.opfe, self.opff              
        ]

        #table of cb functions
        self.cbFunctions = [
            self.cb00, self.cb01, self.cb02, self.cb03, 
            self.cb04, self.cb05, self.cb06, self.cb07, 
            self.cb08, self.cb09, self.cb0a, self.cb0b, 
            self.cb0c, self.cb0d, self.cb0e, self.cb0f, 
            self.cb10, self.cb11, self.cb12, self.cb13, 
            self.cb14, self.cb15, self.cb16, self.cb17, 
            self.cb18, self.cb19, self.cb1a, self.cb1b, 
            self.cb1c, self.cb1d, self.cb1e, self.cb1f, 
            self.cb20, self.cb21, self.cb22, self.cb23, 
            self.cb24, self.cb25, self.cb26, self.cb27, 
            self.cb28, self.cb29, self.cb2a, self.cb2b, 
            self.cb2c, self.cb2d, self.cb2e, self.cb2f, 
            self.cb30, self.cb31, self.cb32, self.cb33, 
            self.cb34, self.cb35, self.cb36, self.cb37, 
            self.cb38, self.cb39, self.cb3a, self.cb3b, 
            self.cb3c, self.cb3d, self.cb3e, self.cb3f, 
            self.cb40, self.cb41, self.cb42, self.cb43, 
            self.cb44, self.cb45, self.cb46, self.cb47, 
            self.cb48, self.cb49, self.cb4a, self.cb4b, 
            self.cb4c, self.cb4d, self.cb4e, self.cb4f, 
            self.cb50, self.cb51, self.cb52, self.cb53, 
            self.cb54, self.cb55, self.cb56, self.cb57, 
            self.cb58, self.cb59, self.cb5a, self.cb5b, 
            self.cb5c, self.cb5d, self.cb5e, self.cb5f, 
            self.cb60, self.cb61, self.cb62, self.cb63, 
            self.cb64, self.cb65, self.cb66, self.cb67, 
            self.cb68, self.cb69, self.cb6a, self.cb6b, 
            self.cb6c, self.cb6d, self.cb6e, self.cb6f, 
            self.cb70, self.cb71, self.cb72, self.cb73, 
            self.cb74, self.cb75, self.cb76, self.cb77, 
            self.cb78, self.cb79, self.cb7a, self.cb7b, 
            self.cb7c, self.cb7d, self.cb7e, self.cb7f, 
            self.cb80, self.cb81, self.cb82, self.cb83, 
            self.cb84, self.cb85, self.cb86, self.cb87, 
            self.cb88, self.cb89, self.cb8a, self.cb8b, 
            self.cb8c, self.cb8d, self.cb8e, self.cb8f, 
            self.cb90, self.cb91, self.cb92, self.cb93, 
            self.cb94, self.cb95, self.cb96, self.cb97, 
            self.cb98, self.cb99, self.cb9a, self.cb9b, 
            self.cb9c, self.cb9d, self.cb9e, self.cb9f, 
            self.cba0, self.cba1, self.cba2, self.cba3, 
            self.cba4, self.cba5, self.cba6, self.cba7, 
            self.cba8, self.cba9, self.cbaa, self.cbab, 
            self.cbac, self.cbad, self.cbae, self.cbaf, 
            self.cbb0, self.cbb1, self.cbb2, self.cbb3, 
            self.cbb4, self.cbb5, self.cbb6, self.cbb7, 
            self.cbb8, self.cbb9, self.cbba, self.cbbb, 
            self.cbbc, self.cbbd, self.cbbe, self.cbbf, 
            self.cbc0, self.cbc1, self.cbc2, self.cbc3, 
            self.cbc4, self.cbc5, self.cbc6, self.cbc7, 
            self.cbc8, self.cbc9, self.cbca, self.cbcb, 
            self.cbcc, self.cbcd, self.cbce, self.cbcf, 
            self.cbd0, self.cbd1, self.cbd2, self.cbd3, 
            self.cbd4, self.cbd5, self.cbd6, self.cbd7, 
            self.cbd8, self.cbd9, self.cbda, self.cbdb, 
            self.cbdc, self.cbdd, self.cbde, self.cbdf, 
            self.cbe0, self.cbe1, self.cbe2, self.cbe3, 
            self.cbe4, self.cbe5, self.cbe6, self.cbe7, 
            self.cbe8, self.cbe9, self.cbea, self.cbeb, 
            self.cbec, self.cbed, self.cbee, self.cbef, 
            self.cbf0, self.cbf1, self.cbf2, self.cbf3, 
            self.cbf4, self.cbf5, self.cbf6, self.cbf7, 
            self.cbf8, self.cbf9, self.cbfa, self.cbfb, 
            self.cbfc, self.cbfd, self.cbfe, self.cbff]

        #table of opcodelengths
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

        #instruction fetch fucntions:
        self.fetch = [
            self.fetchNextInstruction, 
            self.haltBugFetchNextInstruction]

        #next instruction decode buffer
        self.nextInstruction = bytearray([0, 0, 0])
        
        #setup mmu
        self.mmu = mmu
        return
    
    #is the cpu in a running state
    run = 1
    stop = 0
    halt = 0
    haltBug = 0

    #interrupt master enable
    DI = 0
    EI = 0


    #debugging
    def reset(self):
        self.regAF.load(0)
        self.regBC.load(0)
        self.regDE.load(0)
        self.regHL.load(0)
        self.regSP.load(0)
        self.regPC.load(0)
        self.regDeRef.load(0)
        self.run = 1
        self.stop = 0
        self.halt = 0
        self.EI = 0
        self.DI = 0 

    def getState(self):
        return (
            f"A:0x{self.regA.read():02x} " 
            f"F:0x{self.regF.read():02x} "
            f"B:0x{self.regB.read():02x} "
            f"C:0x{self.regC.read():02x} " 
            f"D:0x{self.regD.read():02x} " 
            f"E:0x{self.regE.read():02x} " 
            f"H:0x{self.regH.read():02x} " 
            f"L:0x{self.regL.read():02x} " 
            f"SP:0x{self.regSP.read():04x} " 
            f"PC:0x{self.regPC.read():04x}"
        )
    
    #bit fiddleing
    def setCarryFlag(self):
        self.regF.setBit(4)

    def resetCarryFlag(self):
        self.regF.resetBit(4)

    def getCarryFlag(self):
        if self.regF.read() & flagCarry:
            return 1
        return 0

    def setHalfCarryFlag(self):
        self.regF.setBit(5)

    def resetHalfCarryFlag(self):
        self.regF.resetBit(5)

    def getHalfCarryFlag(self):
        if self.regF.read() & flagHalfCarry:
            return 1
        return 0

    def setSubtractionFlag(self):
        self.regF.setBit(6)

    def resetSubtractionFlag(self):
        self.regF.resetBit(6)

    def getSubtractionFlag(self):
        if self.regF.read() & flagSub:
            return 1
        return 0

    def setZeroFlag(self):
        self.regF.setBit(7)

    def resetZeroFlag(self):
        self.regF.resetBit(7)
    
    def getZeroFlag(self):
        if self.regF.read() & flagZero:
            return 1
        return 0

    def clearFlags(self):
        self.regF.load(0)

    def toSigned(self, value): #stolen from gengkev on stackoverflow
        value &= 0xff
        return (value ^ 0x80) - 0x80
    
    #functions for running the CPU
    def printState(self):
        print (self.getState())
    ps = printState

    def printNextInstruction(self):
        print("")
        pc = self.regPC.read()
        print(f'PC is at:{hex(pc)}', end=" --- ")
        temp = []
        for i in range(self.opcodeLength[self.mmu.read(pc)]):
            print (hex(self.mmu.read(pc + i)), end=" ")
            temp.append(self.mmu.read(pc + i))
        registers = [self.regSP.read(), self.regPC.read()]
        opcodeString = debug.formatOpcodeName(
            temp, 
            self.opcodeLength[temp[0]], 
            registers)
        print(f'--- {opcodeString}')
    pni = printNextInstruction
    
    def executeNextInstruction(self):
        self.regPC.rawAdd(self.opcodeLength[self.nextInstruction[0]])
        opcodeFunction = self.opcodeFunctions[self.nextInstruction[0]]
        cycles = opcodeFunction(self.nextInstruction)
        return cycles
    eni = executeNextInstruction
    
    def fetchNextInstruction(self):
        pc = self.regPC.read()
        instruction = bytearray([
            self.mmu.read(pc), 
            self.mmu.read(pc + 1), 
            self.mmu.read(pc + 2)
            ])
        self.nextInstruction = instruction
    fni = fetchNextInstruction

    def fetchAndExecuteNextInstruction(self):
        self.fetch[self.haltBug]()
        return self.executeNextInstruction()
    feni = fetchAndExecuteNextInstruction
    step = fetchAndExecuteNextInstruction

    def serviceInterrupt(self, vector):
        sp = self.regSP.read()
        pch, pcl = self.splitShort(self.regPC.read())
        self.mmu.write(sp - 1, pch)
        self.mmu.write(sp - 2, pcl)
        self.regPC.load(vector)
        self.regSP.rawSub(2)
        return 16
    
    def haltBugFetchNextInstruction(self):
        pc = self.regPC.read()
        instruction = bytearray([
            self.mmu.read(pc), 
            self.mmu.read(pc), 
            self.mmu.read(pc + 1)
            ])
        self.nextInstruction = instruction
        self.haltBug = 0

    
    #combine 2 char into short
    def combineTwoChar(self, highChar, lowChar):
        temp = highChar * 0x100
        temp += lowChar
        return temp
    
    #split 16 bit value and return upper and lower char
    def splitShort(self, short):
        return short >> 8, short & 0xff  

    #cpu intruction functions
    def op00(self, instruction):
        return 4
    
    def op01(self, instruction):
        value = self.combineTwoChar(instruction[2], instruction[1])
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
        self.regA.rlca(self.regF)
        return 4

    def op08(self, instruction):
        address = self.combineTwoChar(instruction[2], instruction[1])
        sp = self.regSP.read()
        sph, spl = self.splitShort(sp)
        self.mmu.write(address, spl)
        self.mmu.write(address + 1, sph)
        return 20

    def op09(self, instruction):
        self.regHL.add(self.regBC.read(), self.regF, 0x7)
        return 8
    
    def op0a(self, instruction):
        self.regA.load(self.mmu.read(self.regBC.read()))
        return 8

    def op0b(self, instruction):
        self.regBC.dec()
        return 8

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
        self.regA.rrca(self.regF)
        return 4

    def op10(self, instruction):
        self.stop = 1
        #print("STOP")
        return 4

    def op11(self, instruction):
        value = self.combineTwoChar(instruction[2], instruction[1])
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
        self.regA.rla(self.regF)
        return 4

    # this is a little janky, but register.add() wont work reliable 
    # with negative numbers ##TODO test this it might be bad
    def op18(self, instruction): 
        if instruction[1] & 0x80: # number is negative and we must sub
            self.regPC.rawSub(abs(self.toSigned(instruction[1])))
        else: # number is positive and we must add
            self.regPC.rawAdd(instruction[1])
        return 12

    def op19(self, instruction):
        self.regHL.add(self.regDE.read(), self.regF, 0x7)
        return 8

    def op1a(self, instruction):
        self.regA.load(self.mmu.read(self.regDE.read()))
        return 8

    def op1b(self, instruction):
        self.regDE.dec()
        return 8

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
        self.regA.rra(self.regF)
        return 4

    def op20(self, instruction):
        #this is a little janky, but register.add() wont work 
        #reliable with negative numbers ##TODO test this it might be bad
        if self.getZeroFlag() == 0:
            if instruction[1] & 0x80: #number is negative and we must sub
                self.regPC.rawSub(abs(self.toSigned(instruction[1])))
            else: #number is positive and we must add
                self.regPC.rawAdd(instruction[1])
            return 12
        return 8

    def op21(self, instruction):
        value = instruction[2] << 8 | instruction[1]
        self.regHL.load(value)
        return 12

    def op22(self, instruction):
        addr = self.regHL.read()
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
        self.regA.DAA(self.regF)
        return 4

    def op28(self, instruction):
        if self.getZeroFlag() == 1:
            if instruction[1] & 0x80: #number is negative and we must sub
                self.regPC.rawSub(abs(self.toSigned(instruction[1])))
            else: #number is positive and we must add
                self.regPC.rawAdd(instruction[1])
            return 12
        return 8

    def op29(self, instruction):
        self.regHL.add(self.regHL.read(), self.regF, 0x7)
        return 8

    def op2a(self, instruction):
        self.regA.load(self.mmu.read(self.regHL.read()))
        self.regHL.inc()
        return 8

    def op2b(self, instruction):
        self.regHL.dec()
        return 8

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
        self.regA.load(self.regA.read() ^ 0xff)
        return 4

    def op30(self, instruction):
        if self.getCarryFlag() == 0:
            if instruction[1] & 0x80: #number is negative and we must sub
                self.regPC.rawSub(abs(self.toSigned(instruction[1])))
            else: #number is positive and we must add
                self.regPC.rawAdd(instruction[1])
            return 12
        return 8

    def op31(self, instruction):
        value = instruction[2] << 8 | instruction[1]
        self.regSP.load(value)
        return 12

    def op32(self, instruction):
        addr = self.regHL.read()
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
        return 12

    def op37(self, instruction):
        self.setCarryFlag()
        return 4

    def op38(self, instruction):
        if self.getCarryFlag() == 1:
            if instruction[0] & 0x80: #number is negative and we must sub
                self.regPC.rawSub(abs(self.toSigned(instruction[1])))
            else: #number is positive and we must add
                self.regPC.rawAdd(instruction[1])
            return 12
        return 8

    def op39(self, instruction):
        self.regHL.add(self.regSP.read(), self.regF, 0x7)
        return 8

    def op3a(self, instruction):
        self.regA.load(self.mmu.read(self.regHL.read()))
        self.regHL.dec()
        return 8

    def op3b(self, instruction):
        self.regSP.dec()
        return 8

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
        self.resetSubtractionFlag()
        self.resetHalfCarryFlag()
        self.regF.load(self.regF.read() ^ flagCarry)
        return 4

    def op40(self, instruction):
        self.regB.load(self.regB.read())
        return 4

    def op41(self, instruction):
        self.regB.load(self.regC.read())
        return 4

    def op42(self, instruction):
        self.regB.load(self.regD.read())
        return 4

    def op43(self, instruction):
        self.regB.load(self.regE.read())
        return 4

    def op44(self, instruction):
        self.regB.load(self.regH.read())
        return 4

    def op45(self, instruction):
        self.regB.load(self.regL.read())
        return 4

    def op46(self, instruction):
        self.regB.load(self.mmu.read(self.regHL.read()))
        return 8

    def op47(self, instruction):
        self.regB.load(self.regA.read())
        return 4

    def op48(self, instruction):
        self.regC.load(self.regB.read())
        return 4

    def op49(self, instruction):
        self.regC.load(self.regC.read())
        return 4

    def op4a(self, instruction):
        self.regC.load(self.regD.read())
        return 4

    def op4b(self, instruction):
        self.regC.load(self.regE.read())
        return 4

    def op4c(self, instruction):
        self.regC.load(self.regH.read())
        return 4

    def op4d(self, instruction):
        self.regC.load(self.regL.read())
        return 4

    def op4e(self, instruction):
        self.regC.load(self.mmu.read(self.regHL.read()))
        return 8

    def op4f(self, instruction):
        self.regC.load(self.regA.read())
        return 4

    def op50(self, instruction):
        self.regD.load(self.regB.read())
        return 4

    def op51(self, instruction):
        self.regD.load(self.regC.read())
        return 4

    def op52(self, instruction):
        self.regD.load(self.regD.read())
        return 4

    def op53(self, instruction):
        self.regD.load(self.regE.read())
        return 4

    def op54(self, instruction):
        self.regD.load(self.regH.read())
        return 4

    def op55(self, instruction):
        self.regD.load(self.regL.read())
        return 4

    def op56(self, instruction):
        self.regD.load(self.mmu.read(self.regHL.read()))
        return 8

    def op57(self, instruction):
        self.regD.load(self.regA.read())
        return 4

    def op58(self, instruction):
        self.regE.load(self.regB.read())
        return 4

    def op59(self, instruction):
        self.regE.load(self.regC.read())
        return 4

    def op5a(self, instruction):
        self.regE.load(self.regD.read())
        return 4

    def op5b(self, instruction):
        self.regE.load(self.regE.read())
        return 4

    def op5c(self, instruction):
        self.regE.load(self.regH.read())
        return 4

    def op5d(self, instruction):
        self.regE.load(self.regL.read())
        return 4

    def op5e(self, instruction):
        self.regE.load(self.mmu.read(self.regHL.read()))
        return 8

    def op5f(self, instruction):
        self.regE.load(self.regA.read())
        return 4

    def op60(self, instruction):
        self.regH.load(self.regB.read())
        return 4

    def op61(self, instruction):
        self.regH.load(self.regC.read())
        return 4

    def op62(self, instruction):
        self.regH.load(self.regD.read())
        return 4

    def op63(self, instruction):
        self.regH.load(self.regE.read())
        return 4

    def op64(self, instruction):
        self.regH.load(self.regH.read())
        return 4

    def op65(self, instruction):
        self.regH.load(self.regL.read())
        return 4

    def op66(self, instruction):
        self.regH.load(self.mmu.read(self.regHL.read()))
        return 8

    def op67(self, instruction):
        self.regH.load(self.regA.read())
        return 4

    def op68(self, instruction):
        self.regL.load(self.regB.read())
        return 4

    def op69(self, instruction):
        self.regL.load(self.regC.read())
        return 4

    def op6a(self, instruction):
        self.regL.load(self.regD.read())
        return 4

    def op6b(self, instruction):
        self.regL.load(self.regE.read())
        return 4

    def op6c(self, instruction):
        self.regL.load(self.regH.read())
        return 4

    def op6d(self, instruction):
        self.regL.load(self.regL.read())
        return 4

    def op6e(self, instruction):
        self.regL.load(self.mmu.read(self.regHL.read()))
        return 8

    def op6f(self, instruction):
        self.regL.load(self.regA.read())
        return 4

    def op70(self, instruction):
        self.mmu.write(self.regHL.read(), self.regB.read())
        return 8

    def op71(self, instruction):
        self.mmu.write(self.regHL.read(), self.regC.read())
        return 8

    def op72(self, instruction):
        self.mmu.write(self.regHL.read(), self.regD.read())
        return 8

    def op73(self, instruction):
        self.mmu.write(self.regHL.read(), self.regE.read())
        return 8

    def op74(self, instruction):
        self.mmu.write(self.regHL.read(), self.regH.read())
        return 8

    def op75(self, instruction):
        self.mmu.write(self.regHL.read(), self.regL.read())
        return 8

    def op76(self, instruction):
        if self.interrupts.IME == 0:
            if self.mmu.read(0xff0f) & self.mmu.read(0xffff):
                print("HALT BUG")
                self.haltBug = 1
                return 4

            
        self.run = 0
        return 4

    def op77(self, instruction):
        self.mmu.write(self.regHL.read(), self.regA.read())
        return 8

    def op78(self, instruction):
        self.regA.load(self.regB.read())
        return 4

    def op79(self, instruction):
        self.regA.load(self.regC.read())
        return 4

    def op7a(self, instruction):
        self.regA.load(self.regD.read())
        return 4

    def op7b(self, instruction):
        self.regA.load(self.regE.read())
        return 4

    def op7c(self, instruction):
        self.regA.load(self.regH.read())
        return 4

    def op7d(self, instruction):
        self.regA.load(self.regL.read())
        return 4

    def op7e(self, instruction):
        self.regA.load(self.mmu.read(self.regHL.read()))
        return 8

    def op7f(self, instruction):
        self.regA.load(self.regA.read())
        return 4

    def op80(self, instruction):
        self.regA.add(self.regB.read(), self.regF, 0xf)
        return 4

    def op81(self, instruction):
        self.regA.add(self.regC.read(), self.regF, 0xf)
        return 4

    def op82(self, instruction):
        self.regA.add(self.regD.read(), self.regF, 0xf)
        return 4

    def op83(self, instruction):
        self.regA.add(self.regE.read(), self.regF, 0xf)
        return 4

    def op84(self, instruction):
        self.regA.add(self.regH.read(), self.regF, 0xf)
        return 4

    def op85(self, instruction):
        self.regA.add(self.regL.read(), self.regF, 0xf)
        return 4

    def op86(self, instruction):
        self.regA.add(self.mmu.read(self.regHL.read()), self.regF, 0xf)
        return 8

    def op87(self, instruction):
        self.regA.add(self.regA.read(), self.regF, 0xf)
        return 4

    def op88(self, instruction):
        self.regA.adc(self.regB.read(), self.regF, 0xf)
        return 4

    def op89(self, instruction):
        self.regA.adc(self.regC.read(), self.regF, 0xf)
        return 4

    def op8a(self, instruction):
        self.regA.adc(self.regD.read(), self.regF, 0xf)
        return 4

    def op8b(self, instruction):
        self.regA.adc(self.regE.read(), self.regF, 0xf)
        return 4

    def op8c(self, instruction):
        self.regA.adc(self.regH.read(), self.regF, 0xf)
        return 4

    def op8d(self, instruction):
        self.regA.adc(self.regL.read(), self.regF, 0xf)
        return 4

    def op8e(self, instruction):
        self.regA.adc(self.mmu.read(self.regHL.read()), self.regF, 0xf)
        return 8

    def op8f(self, instruction):
        self.regA.adc(self.regA.read(), self.regF, 0xf)
        return 4

    def op90(self, instruction):
        self.regA.sub(self.regB.read(), self.regF, 0xf)
        return 4

    def op91(self, instruction):
        self.regA.sub(self.regC.read(), self.regF, 0xf)
        return 4

    def op92(self, instruction):
        self.regA.sub(self.regD.read(), self.regF, 0xf)
        return 4

    def op93(self, instruction):
        self.regA.sub(self.regE.read(), self.regF, 0xf)
        return 4

    def op94(self, instruction):
        self.regA.sub(self.regH.read(), self.regF, 0xf)
        return 4

    def op95(self, instruction):
        self.regA.sub(self.regL.read(), self.regF, 0xf)
        return 4

    def op96(self, instruction):
        self.regA.sub(self.mmu.read(self.regHL.read()), self.regF, 0xf)
        return 4

    def op97(self, instruction):
        self.regA.sub(self.regA.read(), self.regF, 0xf)
        return 4

    def op98(self, instruction):
        self.regA.sbc(self.regB.read(), self.regF, 0xf)
        return 4

    def op99(self, instruction):
        self.regA.sbc(self.regC.read(), self.regF, 0xf)
        return 4

    def op9a(self, instruction):
        self.regA.sbc(self.regD.read(), self.regF, 0xf)
        return 4

    def op9b(self, instruction):
        self.regA.sbc(self.regE.read(), self.regF, 0xf)
        return 4

    def op9c(self, instruction):
        self.regA.sbc(self.regH.read(), self.regF, 0xf)
        return 4

    def op9d(self, instruction):
        self.regA.sbc(self.regL.read(), self.regF, 0xf)
        return 4

    def op9e(self, instruction):
        self.regA.sbc(self.mmu.read(self.regHL.read()), self.regF, 0xf)
        return 4

    def op9f(self, instruction):
        self.regA.sbc(self.regA.read(), self.regF, 0xf)
        return 4
    
    def opa0(self, instruction):
        self.regA.band(self.regB.read(), self.regF)
        return 4

    def opa1(self, instruction):
        self.regA.band(self.regC.read(), self.regF)
        return 4

    def opa2(self, instruction):
        self.regA.band(self.regD.read(), self.regF)
        return 4

    def opa3(self, instruction):
        self.regA.band(self.regE.read(), self.regF)
        return 4

    def opa4(self, instruction):
        self.regA.band(self.regH.read(), self.regF)
        return 4

    def opa5(self, instruction):
        self.regA.band(self.regL.read(), self.regF)
        return 4

    def opa6(self, instruction):
        self.regA.band(self.mmu.read(self.regHL.read()), self.regF)
        return 8

    def opa7(self, instruction):
        self.regA.band(self.regA.read(), self.regF)
        return 4

    def opa8(self, instruction):
        self.regA.bxor(self.regB.read(), self.regF)
        return 4

    def opa9(self, instruction):
        self.regA.bxor(self.regC.read(), self.regF)
        return 4

    def opaa(self, instruction):
        self.regA.bxor(self.regD.read(), self.regF)
        return 4

    def opab(self, instruction):
        self.regA.bxor(self.regE.read(), self.regF)
        return 4

    def opac(self, instruction):
        self.regA.bxor(self.regH.read(), self.regF)
        return 4

    def opad(self, instruction):
        self.regA.bxor(self.regL.read(), self.regF)
        return 4

    def opae(self, instruction):
        self.regA.bxor(self.mmu.read(self.regHL.read()), self.regF)
        return 8

    def opaf(self, instruction):
        self.regA.bxor(self.regA.read(), self.regF)
        return 4
    
    def opb0(self, instruction):
        self.regA.bor(self.regB.read(), self.regF)
        return 4

    def opb1(self, instruction):
        self.regA.bor(self.regC.read(), self.regF)
        return 4

    def opb2(self, instruction):
        self.regA.bor(self.regD.read(), self.regF)
        return 4

    def opb3(self, instruction):
        self.regA.bor(self.regE.read(), self.regF)
        return 4

    def opb4(self, instruction):
        self.regA.bor(self.regH.read(), self.regF)
        return 4

    def opb5(self, instruction):
        self.regA.bor(self.regL.read(), self.regF)
        return 4

    def opb6(self, instruction):
        self.regA.bor(self.mmu.read(self.regHL.read()), self.regF)
        return 8

    def opb7(self, instruction):
        self.regA.bor(self.regA.read(), self.regF)
        return 4

    def opb8(self, instruction):
        self.regA.cp(self.regB.read(), self.regF)
        return 4

    def opb9(self, instruction):
        self.regA.cp(self.regC.read(), self.regF)
        return 4

    def opba(self, instruction):
        self.regA.cp(self.regD.read(), self.regF)
        return 4

    def opbb(self, instruction):
        self.regA.cp(self.regE.read(), self.regF)
        return 4

    def opbc(self, instruction):
        self.regA.cp(self.regH.read(), self.regF)
        return 4

    def opbd(self, instruction):
        self.regA.cp(self.regL.read(), self.regF)
        return 4

    def opbe(self, instruction):
        self.regA.cp(self.mmu.read(self.regHL.read()), self.regF)
        return 8

    def opbf(self, instruction):
        self.regA.cp(self.regA.read(), self.regF)
        return 4

    def opc0(self, instruction):
        if self.getZeroFlag() == 0:
            sp = self.regSP.read()
            self.regPC.load(self.combineTwoChar(self.mmu.read(sp + 1), 
                                                self.mmu.read(sp)))
            self.regSP.rawAdd(2)
            return 20
        else:
            return 8

    def opc1(self, instruction):
        sp = self.regSP.read()
        self.regBC.load(self.combineTwoChar(self.mmu.read(sp + 1), 
                                            self.mmu.read(sp)))
        self.regSP.rawAdd(2)
        return 12

    def opc2(self, instruction):
        if self.getZeroFlag() == 0:
            self.regPC.load(self.combineTwoChar(instruction[2], 
                                                instruction[1]))
            return 16
        else:
            return 12

    def opc3(self, instruction):
        self.regPC.load(self.combineTwoChar(instruction[2], 
                                            instruction[1]))
        return 16

    def opc4(self, instruction):
        if self.getZeroFlag() == 0:
            sp = self.regSP.read()
            pch, pcl = self.splitShort(self.regPC.read())
            self.mmu.write(sp - 1, pch)
            self.mmu.write(sp - 2, pcl)
            self.regPC.load(self.combineTwoChar(instruction[2], 
                                                instruction[1]))
            self.regSP.rawSub(2)
            return 24
        else:
            return 12

    def opc5(self, instruction):
        h, l = self.splitShort(self.regBC.read())
        sp = self.regSP.read()
        self.mmu.write(sp - 1, h)
        self.mmu.write(sp - 2, l)
        self.regSP.rawSub(2)
        return 16

    def opc6(self, instruction):
        self.regA.add(instruction[1], self.regF, 0xf)
        return 8

    def opc7(self, instruction):
        sp = self.regSP.read()
        pch, pcl = self.splitShort(self.regPC.read())
        self.mmu.write(sp - 1, pch)
        self.mmu.write(sp - 2, pcl)
        self.regPC.load(0)
        self.regSP.rawSub(2)
        return 16


    def opc8(self, instruction):
        if self.getZeroFlag() == 1:
            sp = self.regSP.read()
            self.regPC.load(self.combineTwoChar(self.mmu.read(sp + 1), 
                                                self.mmu.read(sp)))
            self.regSP.rawAdd(2)
            return 20
        else:
            return 8

    def opc9(self, instruction):
        sp = self.regSP.read()
        self.regPC.load(self.combineTwoChar(self.mmu.read(sp + 1), 
                                            self.mmu.read(sp)))
        self.regSP.rawAdd(2)
        return 16

    def opca(self, instruction):
        if self.getZeroFlag() == 1:
            self.regPC.load(self.combineTwoChar(instruction[2], 
                                                instruction[1]))
            return 16
        else:
            return 12

    def opcb(self, instruction):
        self.cbFunctions[instruction[1]]()
        if instruction[1] % 8 == 6:
            return 16
        return 8

    def opcc(self, instruction):
        if self.getZeroFlag() == 1:
            sp = self.regSP.read()
            pch, pcl = self.splitShort(self.regPC.read())
            self.mmu.write(sp - 1, pch)
            self.mmu.write(sp - 2, pcl)
            self.regPC.load(self.combineTwoChar(instruction[2], 
                                                instruction[1]))
            self.regSP.rawSub(2)
            return 24
        else:
            return 12
    
    def opcd(self, instruction):
        sp = self.regSP.read()
        pch, pcl = self.splitShort(self.regPC.read())
        self.mmu.write(sp - 1, pch)
        self.mmu.write(sp - 2, pcl)
        self.regPC.load(self.combineTwoChar(instruction[2], 
                                            instruction[1]))
        self.regSP.rawSub(2)
        return 24

    def opce(self, instruction):
        self.regA.adc(instruction[1], self.regF, 0xf)
        return 8

    def opcf(self, instruction):
        sp = self.regSP.read()
        pch, pcl = self.splitShort(self.regPC.read())
        self.mmu.write(sp - 1, pch)
        self.mmu.write(sp - 2, pcl)
        self.regPC.load(0x8)
        self.regSP.rawSub(2)
        return 16

    def opd0(self, instruction):
        if self.getCarryFlag() == 0:
            sp = self.regSP.read()
            self.regPC.load(self.combineTwoChar(self.mmu.read(sp + 1), 
                                                self.mmu.read(sp)))
            self.regSP.rawAdd(2)
            return 20
        else:
            return 8

    def opd1(self, instruction):
        sp = self.regSP.read()
        self.regDE.load(self.combineTwoChar(self.mmu.read(sp + 1), 
                                            self.mmu.read(sp)))
        self.regSP.rawAdd(2)
        return 12

    def opd2(self, instruction):
        if self.getCarryFlag() == 0:
            self.regPC.load(self.combineTwoChar(instruction[2], 
                                                instruction[1]))
            return 16
        else:
            return 12

    def opd4(self, instruction):
        if self.getCarryFlag() == 0:
            sp = self.regSP.read()
            pch, pcl = self.splitShort(self.regPC.read())
            self.mmu.write(sp - 1, pch)
            self.mmu.write(sp - 2, pcl)
            self.regPC.load(self.combineTwoChar(instruction[2], 
                                                instruction[1]))
            self.regSP.rawSub(2)
            return 24
        else:
            return 12

    def opd5(self, instruction):
        h, l = self.splitShort(self.regDE.read())
        sp = self.regSP.read()
        self.mmu.write(sp - 1, h)
        self.mmu.write(sp - 2, l)
        self.regSP.rawSub(2)
        return 16

    def opd6(self, instruction):
        self.regA.sub(instruction[1], self.regF, 0xf)
        return 8

    def opd7(self, instruction):
        sp = self.regSP.read()
        pch, pcl = self.splitShort(self.regPC.read())
        self.mmu.write(sp - 1, pch)
        self.mmu.write(sp - 2, pcl)
        self.regPC.load(0x10)
        self.regSP.rawSub(2)
        return 16

    def opd8(self, instruction):
        if self.getCarryFlag() == 1:
            sp = self.regSP.read()
            self.regPC.load(self.combineTwoChar(self.mmu.read(sp + 1), 
                                                self.mmu.read(sp)))
            self.regSP.rawAdd(2)
            return 20
        else:
            return 8

    def opd9(self, instruction):
        sp = self.regSP.read()
        self.regPC.load(self.combineTwoChar(self.mmu.read(sp + 1), 
                                            self.mmu.read(sp)))
        self.regSP.rawAdd(2)
        self.interrupts.IME = 1
        return 16

    def opda(self, instruction):
        if self.getCarryFlag() == 1:
            self.regPC.load(self.combineTwoChar(instruction[2], 
                                                instruction[1]))
            return 16
        else:
            return 12

    def opdc(self, instruction):
        if self.getCarryFlag() == 1:
            sp = self.regSP.read()
            pch, pcl = self.splitShort(self.regPC.read())
            self.mmu.write(sp - 1, pch)
            self.mmu.write(sp - 2, pcl)
            self.regPC.load(self.combineTwoChar(instruction[2], 
                                                instruction[1]))
            self.regSP.rawSub(2)
            return 24
        else:
            return 12

    def opde(self, instruction):
        self.regA.sbc(instruction[1], self.regF, 0xf)
        return 8

    def opdf(self, instruction):
        sp = self.regSP.read()
        pch, pcl = self.splitShort(self.regPC.read())
        self.mmu.write(sp - 1, pch)
        self.mmu.write(sp - 2, pcl)
        self.regPC.load(0x18)
        self.regSP.rawSub(2)
        return 16

    def ope0(self, instruction):
        self.mmu.write(0xff00 + instruction[1], self.regA.read())
        return 12

    def ope1(self, instruction):
        sp = self.regSP.read()
        self.regHL.load(self.combineTwoChar(self.mmu.read(sp + 1), 
                                            self.mmu.read(sp)))
        self.regSP.rawAdd(2)
        return 12

    def ope2(self, instruction):
        self.mmu.write(0xff00 + self.regC.read(), self.regA.read())
        return 8

    def ope5(self, instruction):
        h, l = self.splitShort(self.regHL.read())
        sp = self.regSP.read()
        self.mmu.write(sp - 1, h)
        self.mmu.write(sp - 2, l)
        self.regSP.rawSub(2)
        return 16

    def ope6(self, instruction):
        self.regA.band(instruction[1], self.regF)
        return 8

    def ope7(self, instruction):
        sp = self.regSP.read()
        pch, pcl = self.splitShort(self.regPC.read())
        self.mmu.write(sp - 1, pch)
        self.mmu.write(sp - 2, pcl)
        self.regPC.load(0x20)
        self.regSP.rawSub(2)
        return 16

    def ope8(self, instruction):
        if instruction[1] & 0x80: #number is negative and we must sub
            self.regSP.sub(abs(self.toSigned(instruction[1])), self.regF, 0x3)
        else: #number is positive and we must add
            self.regSP.add(instruction[1], self.regF, 0x3)
        self.resetSubtractionFlag()
        self.resetZeroFlag()
        return 16

    def ope9(self, instruction):
        self.regPC.load(self.regHL.read())
        return 4

    def opea(self, instruction):
        self.mmu.write(self.combineTwoChar(instruction[2], instruction[1]), 
                       self.regA.read())
        return 16

    def opee(self, instruction):
        self.regA.bxor(instruction[1], self.regF)
        return 8

    def opef(self, instruction):
        sp = self.regSP.read()
        pch, pcl = self.splitShort(self.regPC.read())
        self.mmu.write(sp - 1, pch)
        self.mmu.write(sp - 2, pcl)
        self.regPC.load(0x28)
        self.regSP.rawSub(2)
        return 16

    def opf0(self, instruction):
        self.regA.load(self.mmu.read(0xff00 + instruction[1]))
        return 12

    def opf1(self, instruction):
        sp = self.regSP.read()
        self.regAF.load(self.combineTwoChar(self.mmu.read(sp + 1), 
                                            self.mmu.read(sp)))
        self.regSP.rawAdd(2)
        return 12

    def opf2(self, instruction):
        self.regA.load(self.mmu.read(0xff00 + self.regC.read()))
        return 12

    def opf3(self, instruction):
        self.DI = 1
        return 4

    def opf5(self, instruction):
        h, l = self.splitShort(self.regAF.read())
        sp = self.regSP.read()
        self.mmu.write(sp - 1, h)
        self.mmu.write(sp - 2, l & 0xf0)
        self.regSP.rawSub(2)
        return 16

    def opf6(self, instruction):
        self.regA.bor(instruction[1], self.regF)
        return 8

    def opf7(self, instruction):
        sp = self.regSP.read()
        pch, pcl = self.splitShort(self.regPC.read())
        self.mmu.write(sp - 1, pch)
        self.mmu.write(sp - 2, pcl)
        self.regPC.load(0x30)
        self.regSP.rawSub(2)
        return 16

    #this is a janky solution, save sp, add value to get flags 
    #and result, copy to HL, then put original value back in sp
    #TODO check if flags are set on SP + r8, or SP + HL
    def opf8(self, instruction):
        sp = self.regSP.read()
        if instruction[1] & 0x80: #number is negative and we must sub
            self.regSP.sub(abs(self.toSigned(instruction[1])), self.regF, 0x3)
        else: #number is positive and we must add
            self.regSP.add(instruction[1], self.regF, 0x3)
        self.resetSubtractionFlag()
        self.resetZeroFlag()
        self.regHL.load(self.regSP.read())
        self.regSP.load(sp)
        return 12

    def opf9(self, instruction): 
        self.regSP.load(self.regHL.read())
        return 8

    def opfa(self, instruction):
        self.regA.load(self.mmu.read(self.combineTwoChar(instruction[2], 
                                                         instruction[1])))
        return 16

    def opfb(self, instruction):
        self.EI = 1
        return 4

    def opfe(self, instruction):
        self.regA.cp(instruction[1], self.regF)
        return 8

    def opff(self, instruction):
        sp = self.regSP.read()
        pch, pcl = self.splitShort(self.regPC.read())
        self.mmu.write(sp - 1, pch)
        self.mmu.write(sp - 2, pcl)
        self.regPC.load(0x38)
        self.regSP.rawSub(2)
        return 16
    
    def invalidOp(self, instruction):
        print(f"invalid Opcode called"
              f"{hex(instruction[0])}" 
              f"{hex(instruction[1])}" 
              f"{hex(instruction[2])}")
        self.run = 0
        return None
    

    #CB opcode functions
    def cb00(self):
        self.regB.rlc(self.regF)

    def cb01(self):
        self.regC.rlc(self.regF)

    def cb02(self):
        self.regD.rlc(self.regF)

    def cb03(self):
        self.regE.rlc(self.regF)

    def cb04(self):
        self.regH.rlc(self.regF)

    def cb05(self):
        self.regL.rlc(self.regF)

    def cb06(self):
        self.regDeRef.load(self.mmu.read(self.regHL.read()))
        self.regDeRef.rlc(self.regF)
        self.mmu.write(self.regHL.read(), self.regDeRef.read())

    def cb07(self):
        self.regA.rlc(self.regF)

    def cb08(self):
        self.regB.rrc(self.regF)

    def cb09(self):
        self.regC.rrc(self.regF)

    def cb0a(self):
        self.regD.rrc(self.regF)

    def cb0b(self):
        self.regE.rrc(self.regF)

    def cb0c(self):
        self.regH.rrc(self.regF)

    def cb0d(self):
        self.regL.rrc(self.regF)

    def cb0e(self):
        self.regDeRef.load(self.mmu.read(self.regHL.read()))
        self.regDeRef.rrc(self.regF)
        self.mmu.write(self.regHL.read(), self.regDeRef.read())

    def cb0f(self):
        self.regA.rrc(self.regF)

    def cb10(self):
        self.regB.rl(self.regF)

    def cb11(self):
        self.regC.rl(self.regF)

    def cb12(self):
        self.regD.rl(self.regF)

    def cb13(self):
        self.regE.rl(self.regF)

    def cb14(self):
        self.regH.rl(self.regF)

    def cb15(self):
        self.regL.rl(self.regF)

    def cb16(self):
        self.regDeRef.load(self.mmu.read(self.regHL.read()))
        self.regDeRef.rl(self.regF)
        self.mmu.write(self.regHL.read(), self.regDeRef.read())

    def cb17(self):
        self.regA.rl(self.regF)

    def cb18(self):
        self.regB.rr(self.regF)

    def cb19(self):
        self.regC.rr(self.regF)

    def cb1a(self):
        self.regD.rr(self.regF)

    def cb1b(self):
        self.regE.rr(self.regF)

    def cb1c(self):
        self.regH.rr(self.regF)

    def cb1d(self):
        self.regL.rr(self.regF)

    def cb1e(self):
        self.regDeRef.load(self.mmu.read(self.regHL.read()))
        self.regDeRef.rr(self.regF)
        self.mmu.write(self.regHL.read(), self.regDeRef.read())

    def cb1f(self):
        self.regA.rr(self.regF)

    def cb20(self):
        self.regB.sla(self.regF)

    def cb21(self):
        self.regC.sla(self.regF)

    def cb22(self):
        self.regD.sla(self.regF)

    def cb23(self):
        self.regE.sla(self.regF)

    def cb24(self):
        self.regH.sla(self.regF)

    def cb25(self):
        self.regL.sla(self.regF)

    def cb26(self):
        self.regDeRef.load(self.mmu.read(self.regHL.read()))
        self.regDeRef.sla(self.regF)
        self.mmu.write(self.regHL.read(), self.regDeRef.read())

    def cb27(self):
        self.regA.sla(self.regF)

    def cb28(self):
        self.regB.sra(self.regF)

    def cb29(self):
        self.regC.sra(self.regF)

    def cb2a(self):
        self.regD.sra(self.regF)

    def cb2b(self):
        self.regE.sra(self.regF)

    def cb2c(self):
        self.regH.sra(self.regF)

    def cb2d(self):
        self.regL.sra(self.regF)

    def cb2e(self):
        self.regDeRef.load(self.mmu.read(self.regHL.read()))
        self.regDeRef.sra(self.regF)
        self.mmu.write(self.regHL.read(), self.regDeRef.read())

    def cb2f(self):
        self.regA.sra(self.regF)

    def cb30(self):
        self.regB.swap(self.regF)

    def cb31(self):
        self.regC.swap(self.regF)

    def cb32(self):
        self.regD.swap(self.regF)

    def cb33(self):
        self.regE.swap(self.regF)

    def cb34(self):
        self.regH.swap(self.regF)

    def cb35(self):
        self.regL.swap(self.regF)

    def cb36(self):
        self.regDeRef.load(self.mmu.read(self.regHL.read()))
        self.regDeRef.swap(self.regF)
        self.mmu.write(self.regHL.read(), self.regDeRef.read())

    def cb37(self):
        self.regA.swap(self.regF)

    def cb38(self):
        self.regB.srl(self.regF)

    def cb39(self):
        self.regC.srl(self.regF)

    def cb3a(self):
        self.regD.srl(self.regF)

    def cb3b(self):
        self.regE.srl(self.regF)

    def cb3c(self):
        self.regH.srl(self.regF)

    def cb3d(self):
        self.regL.srl(self.regF)

    def cb3e(self):
        self.regDeRef.load(self.mmu.read(self.regHL.read()))
        self.regDeRef.srl(self.regF)
        self.mmu.write(self.regHL.read(), self.regDeRef.read())

    def cb3f(self):
        self.regA.srl(self.regF)

    def cb40(self):
        self.regB.getBit(0, self.regF, 0xe)

    def cb41(self):
        self.regC.getBit(0, self.regF, 0xe)

    def cb42(self):
        self.regD.getBit(0, self.regF, 0xe)

    def cb43(self):
        self.regE.getBit(0, self.regF, 0xe)

    def cb44(self):
        self.regH.getBit(0, self.regF, 0xe)

    def cb45(self):
        self.regL.getBit(0, self.regF, 0xe)

    def cb46(self):
        self.regDeRef.load(self.mmu.read(self.regHL.read()))
        self.regDeRef.getBit(0, self.regF, 0xe)
        self.mmu.write(self.regHL.read(), self.regDeRef.read())

    def cb47(self):
        self.regA.getBit(0, self.regF, 0xe)

    def cb48(self):
        self.regB.getBit(1, self.regF, 0xe)

    def cb49(self):
        self.regC.getBit(1, self.regF, 0xe)

    def cb4a(self):
        self.regD.getBit(1, self.regF, 0xe)

    def cb4b(self):
        self.regE.getBit(1, self.regF, 0xe)

    def cb4c(self):
        self.regH.getBit(1, self.regF, 0xe)

    def cb4d(self):
        self.regL.getBit(1, self.regF, 0xe)

    def cb4e(self):
        self.regDeRef.load(self.mmu.read(self.regHL.read()))
        self.regDeRef.getBit(1, self.regF, 0xe)
        self.mmu.write(self.regHL.read(), self.regDeRef.read())

    def cb4f(self):
        self.regA.getBit(1, self.regF, 0xe)

    def cb50(self):
        self.regB.getBit(2, self.regF, 0xe)

    def cb51(self):
        self.regC.getBit(2, self.regF, 0xe)

    def cb52(self):
        self.regD.getBit(2, self.regF, 0xe)

    def cb53(self):
        self.regE.getBit(2, self.regF, 0xe)

    def cb54(self):
        self.regH.getBit(2, self.regF, 0xe)

    def cb55(self):
        self.regL.getBit(2, self.regF, 0xe)

    def cb56(self):
        self.regDeRef.load(self.mmu.read(self.regHL.read()))
        self.regDeRef.getBit(2, self.regF, 0xe)
        self.mmu.write(self.regHL.read(), self.regDeRef.read())

    def cb57(self):
        self.regA.getBit(2, self.regF, 0xe)

    def cb58(self):
        self.regB.getBit(3, self.regF, 0xe)

    def cb59(self):
        self.regC.getBit(3, self.regF, 0xe)

    def cb5a(self):
        self.regD.getBit(3, self.regF, 0xe)

    def cb5b(self):
        self.regE.getBit(3, self.regF, 0xe)

    def cb5c(self):
        self.regH.getBit(3, self.regF, 0xe)

    def cb5d(self):
        self.regL.getBit(3, self.regF, 0xe)

    def cb5e(self):
        self.regDeRef.load(self.mmu.read(self.regHL.read()))
        self.regDeRef.getBit(3, self.regF, 0xe)
        self.mmu.write(self.regHL.read(), self.regDeRef.read())

    def cb5f(self):
        self.regA.getBit(3, self.regF, 0xe)

    def cb60(self):
        self.regB.getBit(4, self.regF, 0xe)

    def cb61(self):
        self.regC.getBit(4, self.regF, 0xe)

    def cb62(self):
        self.regD.getBit(4, self.regF, 0xe)

    def cb63(self):
        self.regE.getBit(4, self.regF, 0xe)

    def cb64(self):
        self.regH.getBit(4, self.regF, 0xe)

    def cb65(self):
        self.regL.getBit(4, self.regF, 0xe)

    def cb66(self):
        self.regDeRef.load(self.mmu.read(self.regHL.read()))
        self.regDeRef.getBit(4, self.regF, 0xe)
        self.mmu.write(self.regHL.read(), self.regDeRef.read())

    def cb67(self):
        self.regA.getBit(4, self.regF, 0xe)

    def cb68(self):
        self.regB.getBit(5, self.regF, 0xe)

    def cb69(self):
        self.regC.getBit(5, self.regF, 0xe)

    def cb6a(self):
        self.regD.getBit(5, self.regF, 0xe)

    def cb6b(self):
        self.regE.getBit(5, self.regF, 0xe)

    def cb6c(self):
        self.regH.getBit(5, self.regF, 0xe)

    def cb6d(self):
        self.regL.getBit(5, self.regF, 0xe)

    def cb6e(self):
        self.regDeRef.load(self.mmu.read(self.regHL.read()))
        self.regDeRef.getBit(5, self.regF, 0xe)
        self.mmu.write(self.regHL.read(), self.regDeRef.read())

    def cb6f(self):
        self.regA.getBit(5, self.regF, 0xe)

    def cb70(self):
        self.regB.getBit(6, self.regF, 0xe)

    def cb71(self):
        self.regC.getBit(6, self.regF, 0xe)

    def cb72(self):
        self.regD.getBit(6, self.regF, 0xe)

    def cb73(self):
        self.regE.getBit(6, self.regF, 0xe)

    def cb74(self):
        self.regH.getBit(6, self.regF, 0xe)

    def cb75(self):
        self.regL.getBit(6, self.regF, 0xe)

    def cb76(self):
        self.regDeRef.load(self.mmu.read(self.regHL.read()))
        self.regDeRef.getBit(6, self.regF, 0xe)
        self.mmu.write(self.regHL.read(), self.regDeRef.read())

    def cb77(self):
        self.regA.getBit(6, self.regF, 0xe)

    def cb78(self):
        self.regB.getBit(7, self.regF, 0xe)

    def cb79(self):
        self.regC.getBit(7, self.regF, 0xe)

    def cb7a(self):
        self.regD.getBit(7, self.regF, 0xe)

    def cb7b(self):
        self.regE.getBit(7, self.regF, 0xe)

    def cb7c(self):
        self.regH.getBit(7, self.regF, 0xe)

    def cb7d(self):
        self.regL.getBit(7, self.regF, 0xe)

    def cb7e(self):
        self.regDeRef.load(self.mmu.read(self.regHL.read()))
        self.regDeRef.getBit(7, self.regF, 0xe)
        self.mmu.write(self.regHL.read(), self.regDeRef.read())

    def cb7f(self):
        self.regA.getBit(7, self.regF, 0xe)

    def cb80(self):
        self.regB.resetBit(0)

    def cb81(self):
        self.regC.resetBit(0)

    def cb82(self):
        self.regD.resetBit(0)

    def cb83(self):
        self.regE.resetBit(0)

    def cb84(self):
        self.regH.resetBit(0)

    def cb85(self):
        self.regL.resetBit(0)

    def cb86(self):
        self.regDeRef.load(self.mmu.read(self.regHL.read()))
        self.regDeRef.resetBit(0)
        self.mmu.write(self.regHL.read(), self.regDeRef.read())

    def cb87(self):
        self.regA.resetBit(0)

    def cb88(self):
        self.regB.resetBit(1)

    def cb89(self):
        self.regC.resetBit(1)

    def cb8a(self):
        self.regD.resetBit(1)

    def cb8b(self):
        self.regE.resetBit(1)

    def cb8c(self):
        self.regH.resetBit(1)

    def cb8d(self):
        self.regL.resetBit(1)

    def cb8e(self):
        self.regDeRef.load(self.mmu.read(self.regHL.read()))
        self.regDeRef.resetBit(1)
        self.mmu.write(self.regHL.read(), self.regDeRef.read())

    def cb8f(self):
        self.regA.resetBit(1)

    def cb90(self):
        self.regB.resetBit(2)

    def cb91(self):
        self.regC.resetBit(2)

    def cb92(self):
        self.regD.resetBit(2)

    def cb93(self):
        self.regE.resetBit(2)

    def cb94(self):
        self.regH.resetBit(2)

    def cb95(self):
        self.regL.resetBit(2)

    def cb96(self):
        self.regDeRef.load(self.mmu.read(self.regHL.read()))
        self.regDeRef.resetBit(2)
        self.mmu.write(self.regHL.read(), self.regDeRef.read())

    def cb97(self):
        self.regA.resetBit(2)

    def cb98(self):
        self.regB.resetBit(3)

    def cb99(self):
        self.regC.resetBit(3)

    def cb9a(self):
        self.regD.resetBit(3)

    def cb9b(self):
        self.regE.resetBit(3)

    def cb9c(self):
        self.regH.resetBit(3)

    def cb9d(self):
        self.regL.resetBit(3)

    def cb9e(self):
        self.regDeRef.load(self.mmu.read(self.regHL.read()))
        self.regDeRef.resetBit(3)
        self.mmu.write(self.regHL.read(), self.regDeRef.read())

    def cb9f(self):
        self.regA.resetBit(3)

    def cba0(self):
        self.regB.resetBit(4)

    def cba1(self):
        self.regC.resetBit(4)

    def cba2(self):
        self.regD.resetBit(4)

    def cba3(self):
        self.regE.resetBit(4)

    def cba4(self):
        self.regH.resetBit(4)

    def cba5(self):
        self.regL.resetBit(4)

    def cba6(self):
        self.regDeRef.load(self.mmu.read(self.regHL.read()))
        self.regDeRef.resetBit(4)
        self.mmu.write(self.regHL.read(), self.regDeRef.read())

    def cba7(self):
        self.regA.resetBit(4)

    def cba8(self):
        self.regB.resetBit(5)

    def cba9(self):
        self.regC.resetBit(5)

    def cbaa(self):
        self.regD.resetBit(5)

    def cbab(self):
        self.regE.resetBit(5)

    def cbac(self):
        self.regH.resetBit(5)

    def cbad(self):
        self.regL.resetBit(5)

    def cbae(self):
        self.regDeRef.load(self.mmu.read(self.regHL.read()))
        self.regDeRef.resetBit(5)
        self.mmu.write(self.regHL.read(), self.regDeRef.read())

    def cbaf(self):
        self.regA.resetBit(5)

    def cbb0(self):
        self.regB.resetBit(6)

    def cbb1(self):
        self.regC.resetBit(6)

    def cbb2(self):
        self.regD.resetBit(6)

    def cbb3(self):
        self.regE.resetBit(6)

    def cbb4(self):
        self.regH.resetBit(6)

    def cbb5(self):
        self.regL.resetBit(6)

    def cbb6(self):
        self.regDeRef.load(self.mmu.read(self.regHL.read()))
        self.regDeRef.resetBit(6)
        self.mmu.write(self.regHL.read(), self.regDeRef.read())

    def cbb7(self):
        self.regA.resetBit(6)

    def cbb8(self):
        self.regB.resetBit(7)

    def cbb9(self):
        self.regC.resetBit(7)

    def cbba(self):
        self.regD.resetBit(7)

    def cbbb(self):
        self.regE.resetBit(7)

    def cbbc(self):
        self.regH.resetBit(7)

    def cbbd(self):
        self.regL.resetBit(7)

    def cbbe(self):
        self.regDeRef.load(self.mmu.read(self.regHL.read()))
        self.regDeRef.resetBit(7)
        self.mmu.write(self.regHL.read(), self.regDeRef.read())

    def cbbf(self):
        self.regA.resetBit(7)

    def cbc0(self):
        self.regB.setBit(0)

    def cbc1(self):
        self.regC.setBit(0)

    def cbc2(self):
        self.regD.setBit(0)

    def cbc3(self):
        self.regE.setBit(0)

    def cbc4(self):
        self.regH.setBit(0)

    def cbc5(self):
        self.regL.setBit(0)

    def cbc6(self):
        self.regDeRef.load(self.mmu.read(self.regHL.read()))
        self.regDeRef.setBit(0)
        self.mmu.write(self.regHL.read(), self.regDeRef.read())

    def cbc7(self):
        self.regA.setBit(0)

    def cbc8(self):
        self.regB.setBit(1)

    def cbc9(self):
        self.regC.setBit(1)

    def cbca(self):
        self.regD.setBit(1)

    def cbcb(self):
        self.regE.setBit(1)

    def cbcc(self):
        self.regH.setBit(1)

    def cbcd(self):
        self.regL.setBit(1)

    def cbce(self):
        self.regDeRef.load(self.mmu.read(self.regHL.read()))
        self.regDeRef.setBit(1)
        self.mmu.write(self.regHL.read(), self.regDeRef.read())

    def cbcf(self):
        self.regA.setBit(1)

    def cbd0(self):
        self.regB.setBit(2)

    def cbd1(self):
        self.regC.setBit(2)

    def cbd2(self):
        self.regD.setBit(2)

    def cbd3(self):
        self.regE.setBit(2)

    def cbd4(self):
        self.regH.setBit(2)

    def cbd5(self):
        self.regL.setBit(2)

    def cbd6(self):
        self.regDeRef.load(self.mmu.read(self.regHL.read()))
        self.regDeRef.setBit(2)
        self.mmu.write(self.regHL.read(), self.regDeRef.read())

    def cbd7(self):
        self.regA.setBit(2)

    def cbd8(self):
        self.regB.setBit(3)

    def cbd9(self):
        self.regC.setBit(3)

    def cbda(self):
        self.regD.setBit(3)

    def cbdb(self):
        self.regE.setBit(3)

    def cbdc(self):
        self.regH.setBit(3)

    def cbdd(self):
        self.regL.setBit(3)

    def cbde(self):
        self.regDeRef.load(self.mmu.read(self.regHL.read()))
        self.regDeRef.setBit(3)
        self.mmu.write(self.regHL.read(), self.regDeRef.read())

    def cbdf(self):
        self.regA.setBit(3)

    def cbe0(self):
        self.regB.setBit(4)

    def cbe1(self):
        self.regC.setBit(4)

    def cbe2(self):
        self.regD.setBit(4)

    def cbe3(self):
        self.regE.setBit(4)

    def cbe4(self):
        self.regH.setBit(4)

    def cbe5(self):
        self.regL.setBit(4)

    def cbe6(self):
        self.regDeRef.load(self.mmu.read(self.regHL.read()))
        self.regDeRef.setBit(4)
        self.mmu.write(self.regHL.read(), self.regDeRef.read())

    def cbe7(self):
        self.regA.setBit(4)

    def cbe8(self):
        self.regB.setBit(5)

    def cbe9(self):
        self.regC.setBit(5)

    def cbea(self):
        self.regD.setBit(5)

    def cbeb(self):
        self.regE.setBit(5)

    def cbec(self):
        self.regH.setBit(5)

    def cbed(self):
        self.regL.setBit(5)

    def cbee(self):
        self.regDeRef.load(self.mmu.read(self.regHL.read()))
        self.regDeRef.setBit(5)
        self.mmu.write(self.regHL.read(), self.regDeRef.read())

    def cbef(self):
        self.regA.setBit(5)

    def cbf0(self):
        self.regB.setBit(6)

    def cbf1(self):
        self.regC.setBit(6)

    def cbf2(self):
        self.regD.setBit(6)

    def cbf3(self):
        self.regE.setBit(6)

    def cbf4(self):
        self.regH.setBit(6)

    def cbf5(self):
        self.regL.setBit(6)

    def cbf6(self):
        self.regDeRef.load(self.mmu.read(self.regHL.read()))
        self.regDeRef.setBit(6)
        self.mmu.write(self.regHL.read(), self.regDeRef.read())

    def cbf7(self):
        self.regA.setBit(6)

    def cbf8(self):
        self.regB.setBit(7)

    def cbf9(self):
        self.regC.setBit(7)

    def cbfa(self):
        self.regD.setBit(7)

    def cbfb(self):
        self.regE.setBit(7)

    def cbfc(self):
        self.regH.setBit(7)

    def cbfd(self):
        self.regL.setBit(7)

    def cbfe(self):
        self.regDeRef.load(self.mmu.read(self.regHL.read()))
        self.regDeRef.setBit(7)
        self.mmu.write(self.regHL.read(), self.regDeRef.read())

    def cbff(self):
        self.regA.setBit(7)
        