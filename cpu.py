import mmu
import cb
import codecs
import interrupts

run = 1

def load(file):
    f = open(file, "rb")
    i = 0
    byte = f.read(1)
    while bool(byte) is not False:
        byte = int(codecs.encode(byte, 'hex'), 16)   
        mmu.cart[i] = byte
        byte = f.read(1)
        i += 1
    f.close()
    print(hex(mmu.cart[0x0147]))
    if mmu.cart[0x0147] in [0, 8]:
        mmu.cartrage_type = 0
    elif mmu.cart[0x0147] in [1, 2, 3]:
        mmu.cartrage_type = 1
    elif 0xf <= mmu.cart[0x0147] in [12, 13]:
        mmu.cartrage_type = 3
    mmu.rom_size = mmu.cart[0x0148]
    mmu.ram_size = mmu.cart[0x0149]


def loadboot(file):
    f = open(file, "rb")
    i = 0
    byte = f.read(1)
    while bool(byte) is not False:
        byte = int(codecs.encode(byte, 'hex'), 16)   
        mmu.bootloader.append(byte)
        byte = f.read(1)
        i += 1
    f.close()

def op_00(register, b, interrupts):
    return 4


def op_01(register, b, interrupts):
    register['b'] = b[2]
    register['c'] = b[1]
    return 12


def op_02(register, b, interrupts):
    bc = register['b'] << 8 | register['c']
    mmu.write(register['clock'], bc, register['a'], )
    return 8


def op_03(register, b, interrupts):
    bc = (register['b'] << 8) + register['c']
    bc += 1
    register['b'] = (bc >> 8) & 0xff
    register['c'] = bc & 0xff
    return 8


def op_04(register, b, interrupts):
    h = register['b']
    register['b'] = (register['b'] + 1) & 0xff
    if register['b'] == 0x0:
        register['f'] &= ~0x80
    else:
        register['f'] |= 0x80
    register['f'] &= ~0x40
    if (h & 0xf) + (register['b'] & 0xf) > 0xf:
        register['f'] |= 0x20
    else:
        register['f'] &= ~0x20
    register['b'] &= 0xff
    return 4


def op_05(register, b, interrupts):
    h = register['b']
    register['b'] -= 1
    if register['b'] == 0x0:
        register['f'] |= 0x80
    else:
        register['f'] &= ~0x80
    register['f'] |= 0x40
    if ((h & 0xf) < (register['b'] & 0xf)):
        register['f'] |= 0x20
    else:
        register['f'] &= ~0x20
    if register['b'] < 0:
        register['b'] += 0x100
    return 4


def op_06(register, b, interrupts):
    register['b'] = b[1]
    return 8


def op_07(register, b, interrupts):
    """temp = register['a'] & 0x80
    register['a'] <<= 1
    register['a'] &= 0xff
    if temp:
        register['f'] = 0x10
    else:
        register['f'] = 0x0
    return 4"""
    register['f'] = 0
    register['a'] <<= 1
    if register['a'] > 0xff:
        register['f'] |= 0x10
        register['a'] += 1
        register['a'] &= 0xff
    return 4

def op_08(register, b, interrupts):
    temp = b[2] << 8 | b[1]
    mmu.write(register['clock'], temp, register['sp'] & 0xff)
    mmu.write(register['clock'], temp + 1, register['sp'] >> 8)
    return 20


def op_09(register, b, interrupts):
    hl = register['h'] << 8 | register['l']
    bc = (register['b'] << 8) | register['c']
    temp = hl
    hl += bc
    register['f'] &= 0x80
    if (temp & 0xfff) + (hl & 0xfff) > 0xfff:
        register['f'] |= 0x20
    if hl > 0xffff:
        register['f'] |= 0x10
    hl &= 0xffff
    register['h'] = hl >> 8
    register['l'] = hl & 0xff
    return 8


def op_0a(register, b, interrupts):
    bc = (register['b'] << 8) | register['c']
    register['a'] = mmu.read(bc)
    return 8


def op_0b(register, b, interrupts):
    bc = register ['b'] << 8 | register['c']
    bc -= 1
    if bc < 0:
        bc += 0x10000
    register['b'] = bc >> 8
    register['c'] = bc & 0xff
    return 8


def op_0c(register, b, interrupts):
    h = register['c']
    register['c'] = (register['c'] + 1) & 0xff
    if register['c'] == 0x0:
        register['f'] &= ~0x80
    else:
        register['f'] |= 0x80
    register['f'] &= ~0x40
    if (h & 0xf) + (register['c'] & 0xf) > 0xf:
        register['f'] |= 0x20
    else:
        register['f'] &= ~0x20
    return 4


def op_0d(register, b, interrupts):
    h = register['c']
    register['c'] -= 1
    register['f'] = 0x40
    if register['c'] == 0:
        register['f'] |= 0x80
    elif register['c'] < 0:
        register['f'] |= 0x10
        register ['c'] += 0x100
    if (h & 0xf) - (register['c'] & 0xf) < 0:
        register['f'] |= 0x20
    return 4


def op_0f(register, b, interrupts):
    """if register['a'] & 1:
        register['f'] = 0x10
        register['a'] += 0x100
    else:
        register['f'] = 0
    register['a'] >>= 1
    return 4"""
    register['f'] = 0
    temp = register['a'] & 0x1
    register['a'] >>= 1
    if temp:
        register['a'] += 0x80
        register['f'] = 0x10
    return 4


def op_0e(register, b, interrupts):
    register['c'] = b[1]
    return 8



def op_10(register, b, interrupts):
    while True:
        print('STOP 0')


def op_11(register, b, interrupts):
    register['d'] = b[2]
    register['e'] = b[1]
    return 12


def op_12(register, b, interrupts):
    de = register['d'] << 8 | register['e']
    mmu.write(register['clock'], de, register['a'])
    return 8    


def op_13(register, b, interrupts):
    de = (register['d'] << 8) + register['e']
    de += 1
    register['d'] = (de >> 8) & 0xff
    register['e'] = de & 0xff
    return 8


def op_14(register, b, interrupts):
    h = register['d']
    register['d'] = (register['d'] + 1) & 0xff
    if register['d'] == 0x0:
        register['f'] &= ~0x80
    else:
        register['f'] |= 0x80
    register['f'] &= ~0x40
    if (h & 0xf) + (register['d'] & 0xf) > 0xf:
        register['f'] |= 0x20
    else:
        register['f'] &= ~0x20
    return 4


def op_15(register, b, interrupts):
    h = register['d']
    register['d'] -= 1
    register['f'] = 0x40
    if register['d'] == 0:
        register['f'] |= 0x80
    elif register['d'] < 0:
        register['f'] |= 0x10
        register ['d'] += 0x100
    if (h & 0xf) - (register['d'] & 0xf) < 0:
        register['f'] |= 0x20
    return 4


def op_16(register, b, interrupts):
    register['d'] = b[1]
    return 8


def op_17(register, b, interrupts):
    temp = (register['f'] & 0x10) >> 4
    register['a'] <<= 1
    if register['a'] > 0xff:
        register['f'] = 0x10
    else:
        register['f'] = 0
    register['a'] &= 0xff
    register['a'] += temp
    return 4


def op_18(register, b, interrupts):
    if b[1] > 127:
        b[1] = ~(255 - b[1])
    register['pc'] += b[1]
    return 12


def op_19(register, b, interrupts):
    hl = register['h'] << 8 | register['l']
    de = (register['d'] << 8) | register['e']
    temp = hl
    hl += de
    register['f'] &= 0x80
    if (temp & 0xf00) + (de & 0xf00) > 0xf00:
        register['f'] |= 0x20
    if hl > 0xffff:
        register['f'] |= 0x10
    hl &= 0xffff
    register['h'] = hl >> 8
    register['l'] = hl & 0xff
    return 8
    
    
def op_1a(register, b, interrupts):
    de = (register['d'] << 8) | register['e']
    register['a'] = mmu.read(de)
    return 8


def op_1b(register, b, interrupts):
    de = register ['d'] << 8 | register['e']
    de -= 1
    if de < 0:
        de += 0x10000
    register['d'] = de >> 8
    register['e'] = de & 0xff
    return 8


def op_1c(register, b, interrupts):
    register['f'] &= ~0x40
    if register['e'] & 0xf == 0xf:
        register['f'] |= 0x20
    else:
        register['f'] &= ~0x20
    if register['e'] == 0xff:
        register['e'] = 0
        register['f'] |= 0x80
    else:
        register['f'] &= ~0x80
        register['e'] += 1
    return 4

    
##    h = register['e']
##    register['e'] = (register['e'] + 1) & 0xff
##    if register['e'] == 0x0:
##        register['f'] &= ~0x80
##    else:
##        register['f'] |= 0x80
##    register['f'] &= ~0x40
##    if (h & 0xf) + (register['e'] & 0xf) > 0xf:
##        register['f'] |= 0x20
##    else:
##        register['f'] &= ~0x20  
##    return 4
    
    
def op_1d(register, b, interrupts):
    h = register['e']
    register['e'] -= 1
    register['f'] = 0x40
    if register['e'] == 0:
        register['f'] |= 0x80
    elif register['e'] < 0:
        register['f'] |= 0x10
        register ['e'] += 0x100
    if (h & 0xf) - (register['e'] & 0xf) < 0:
        register['f'] |= 0x20
    return 4


def op_1e(register, b, interrupts):
    register['e'] = b[1]
    return 8


def op_1f(register, b, interrupts):
    if register['f'] & 0x10:
        register['a'] += 0x100
    if register['a'] & 1:
        register['f'] = 0x10
    else:
        register['f'] = 0
    register['a'] >>= 1
    return 4


def op_20(register, b, interrupts):
    if register['f'] & 0x80:
        return 8
    else:
        if b[1] > 127:
            b[1] = ~(255 - b[1])
        register['pc'] += b[1]
        return 12


def op_21(register, b, interrupts):
    register['h'] = b[2]
    register['l'] = b[1]
    return 12


def op_22(register, b, interrupts):
    hl = (register['h'] << 8) | register['l']
    mmu.write(register['clock'], hl, register['a'])
    hl += 1
    register['h'] = hl >> 8
    register['l'] = hl & 0xff
    return 8


def op_23(register, b, interrupts):
    hl = (register['h'] << 8) | register['l']
    hl += 1
    register['h'] = (hl >> 8) & 0xff
    register['l'] = hl & 0xff
    return 8


def op_24(register, b, interrupts):
    e = register['h']
    register['h'] = (register['h'] + 1) & 0xff
    if register['h'] == 0x0:
        register['f'] &= ~0x80
    else:
        register['f'] |= 0x80
    register['f'] &= ~0x40
    if (e & 0xf) + (register['h'] & 0xf) > 0xf:
        register['f'] |= 0x20
    else:
        register['f'] &= ~0x20
    return 4


def op_25(register, b, interrupts):
    h = register['h']
    register['h'] -= 1
    if register['h'] < 0:
        register['h'] += 0x100
    if register['h'] == 0x0:
        register['f'] &= ~0x80
    else:
        register['f'] |= 0x80
    register['f'] |= 0x40
    if (h & 0xf) + (register['h'] & 0xf) > 0xf:
        register['f'] |= 0x20
    else:
        register['f'] &= ~0x20
    return 4


def op_26(register, b, interrupts):
    register['h'] = b[1]
    return 8


#def daa(x, c, h, n):
#    if c:
#        c = 1
#    if h:
#        h = 1
#    if n:
#        n = 1
#    hnib = x >> 4
#    lnib = x & 0xf
#    if n == 0:
#        if (c == 0 and 0 <= hnib <=9 and h == 0 and 0 <= lnib <= 9):
#            return [x + 0x00, 0]
#        
#        elif (c == 0 and 0 <= hnib <=8 and h == 0 and 0xa <= lnib <= 0xf):
#            return [x + 0x06, 0]
#        elif (c == 0 and 0 <= hnib <=9 and h == 1 and 0 <= lnib <= 3):
#            return [x + 0x06, 0]
#        elif (c == 0 and 0xa <= hnib <=0xf and h == 0 and 0 <= lnib <= 9):
#            return [x + 0x60, 1]
#        elif (c == 0 and 9 <= hnib <=0xf and h == 0 and 0x8 <= lnib <= 0xf):
#            return [x + 0x66, 1]
#        elif (c == 0 and 0xa <= hnib <=0xf and h == 1 and 0 <= lnib <= 3):
#            return [x + 0x66, 1]
#        elif (c == 1 and 0 <= hnib <=2 and h == 0 and 0 <= lnib <= 9):
#            return [x + 0x60, 1]
#        elif (c == 1 and 0 <= hnib <=2 and h == 0 and 0x0a <= lnib <= 0xf):
#            return [x + 0x66, 1]
#        elif (c == 1 and 0 <= hnib <=3 and h == 1 and 0 <= lnib <= 3):
#            return [x + 0x66, 1]
#        else:
#            return None

#    if n == 1:
#        if (c == 0 and 0 <= hnib <=9 and h == 0 and 0 <= lnib <= 9):
#            return [x, 0]
#        elif (c == 0 and 0 <= hnib <=8 and h == 1 and 6 <= lnib <= 0xf):
#            return [x + 0xfa, 0]
#        elif (c == 1 and 7 <= hnib <=0xf and h == 0 and 0 <= lnib <= 9):
#            return [x + 0xa0, 1]
#        elif (c == 1 and 6 <= hnib <=0xf and h == 1 and 6 <= lnib <= 0xf):
#            return [x + 0x9a, 1]
#        else:
#            return None
        

def daa(x, flags):
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
        return [x, flags[3]]
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
        return [x, flags[3]]


def op_27(register, b, interrupts):
    n = register['f'] & 0x40
    if n:
        n - 1
    h = register['f'] & 0x20
    if h:
        h = 1
    c = register['f'] & 0x10
    if c:
        c = 1
    #print(hex(register['a']), c, h, n, hex(register['pc']))
    num = daa(register['a'], [0, n, h, c])
    register['f'] &= 0x40
    if num[1]:
        register['f'] |= 0x10
    register['a'] = num[0] & 0xff
    if register['a'] == 0:
        register['f'] |= 0x80
    return 4

##    ah = register['a'] >> 4
##    al = register['a'] | 0xf
##    register['f'] &= 0x40
##    if n == 0:
##        if c == 0:
##            if h == 0:
##                if ah < 0x9 and al <= 0x9:
##                    register['a'] += 0
##                elif ah <= 0x8 and al >= 0xa:
##                    register['a'] += 0x6
##                elif ah >= 0xa and al <= 0x9:
##                    register['a'] += 0x60
##                    register['f'] |= 0x10
##                elif ah >= 0x9 and al >= 0xa:
##                    register['a'] += 0x66
##                    register['f'] |= 0x10
##            else:
##                if ah <= 0x9 and al <= 0x3:
##                    register['a'] += 0x6
##                elif ah >= 0xa and al <= 0x4:
##                    register['a'] += 0x66
##                    register['f'] |= 0x10
##        else:
##            if h == 0:
##                if al >= 0x9:
##                    register['a'] += 0x60
##                    register['f'] |= 0x10
##                else:
##                    register['a'] += 0x66
##                    register['f'] |= 0x10
##            else:
##                register['a'] += 0x66
##                register['f'] |= 0x10
##    else:
##        if c == 0:
##            if h == 0:
##                register['a'] += 0
##            else:
##                register['a'] += 0xfa
##        else:
##            if h == 0:
##                register['a'] += 0xa0
##                register['f'] |= 0x10
##            else:
##                register['a'] += 0x9a
##                register['f'] |= 0x10
##    register['a'] &= 0xff
##    if register['a'] == 0:
##        register['f'] |= 0x80
##    return 4


def op_28(register, b, interrupts):
    if register['f'] & 0x80:
        if b[1] > 127:
            b[1] = ~(255 - b[1])
        register['pc'] += b[1]
        return 12
    else:
        return 8


def op_29(register, b, interrupts):
    hl = register['h'] << 8 | register['l']
    temp = hl
    hl += hl
    register['f'] &= 0x80
    if (temp & 0xfff) + (temp & 0xfff) > 0xf00:
        register['f'] |= 0x20
    if hl > 0xffff:
        register['f'] |= 0x10
    hl &= 0xffff
    register['h'] = hl >> 8
    register['l'] = hl & 0xff
    return 8


def op_2a(register, b, interrupts):
    hl = (register['h'] << 8) | register['l']
    register['a'] = mmu.read(hl)
    hl += 1
    hl &= 0xffff
    register['h'] = hl >> 8
    register['l'] = hl & 0xff
    return 8


def op_2b(register, b, interrupts):
    hl = register ['h'] << 8 | register['l']
    hl -= 1
    if hl < 0:
        hl += 0x10000
    register['h'] = hl >> 8
    register['l'] = hl & 0xff
    return 8


def op_2c(register, b, interrupts):
    h = register['l']
    register['l'] = (register['l'] + 1) & 0xff
    if register['l'] == 0x0:
        register['f'] |= 0x80
    else:
        register['f'] &= ~0x80
    register['f'] &= ~0x40
    if (h & 0xf) + (register['l'] & 0xf) > 0xf:
        register['f'] |= 0x20
    else:
        register['f'] &= ~0x20  
    return 4


def op_2d(register, b, interrupts):
    h = register['l']
    register['l'] -= 1
    if register['l'] == 0x0:
        register['f'] |= 0x80
    else:
        register['f'] &= ~0x80
    register['f'] |= 0x40
    if ((h & 0xf) < (register['l'] & 0xf)):
        register['f'] |= 0x20
    else:
        register['f'] &= ~0x20
    return 4


def op_2e(register, b, interrupts):
    register['l'] = b[1]
    return 4

def op_2f(register, b, interrupts):
    register['a'] = ~register['a'] + 256
    register['f'] |= 0x60
    return 4


def op_30(register, b, interrupts):
    if register['f'] & 0x10:
        return 8
    else:
        if b[1] > 127:
            b[1] = ~(255 - b[1])
        register['pc'] += b[1]
        return 12


def op_31(register, b, interrupts):
    register['sp'] = b[2] << 8
    register['sp'] = register['sp'] | b[1]
    return 12


def op_32(register, b, interrupts):
    hl = (register['h'] << 8) | register['l']
    mmu.write(register['clock'], hl, register['a'])
    hl -= 1
    if hl < 0:
        hl += 0x10000
    register['h'] = hl >> 8
    register['l'] = hl & 0xff
    return 8


def op_33(register, b, interrupts):
    register['sp'] += 1 & 0xffff
    return 8


def op_34(register, b, interrupts):
    hl = register['h'] << 8 | register['l']
    h = mmu.read(hl)
    value = h + 1
    value &= 0xff
    mmu.write(register['clock'], hl, value)
    if (value) == 0x0:
        register['f'] |= 0x80
    else:
        register['f'] &= ~0x80
    register['f'] &= ~0x40
    if (h & 0xf) + (value & 0xf) > 0xf:
        register['f'] |= 0x20
    else:
        register['f'] &= ~0x20
    return 4


def op_35(register, b, interrupts):
    hl = register['h'] << 8 | register['l']
    value = mmu.read(hl)
    h = value
    value -= 1
    if value == 0x0:
        register['f'] |= 0x80
    else:
        register['f'] &= ~0x80
    register['f'] |= 0x40
    if ((h & 0xf) < (value & 0xf)):
        register['f'] |= 0x20
    else:
        register['f'] &= ~0x20
    if value < 0:
        value += 256
    mmu.write(register['clock'], hl, value)
    return 12


def op_36 (register, b, interrupts):
    hl = (register['h'] << 8) | register['l']
    mmu.write(register['clock'], hl, b[1])
    register['h'] = hl >> 8
    register['l'] = hl & 0xff
    return 12


def op_37(register, b, interrupts):
    register['f'] &= 0x80
    register['f'] += 1
    return 4


def op_38(register, b, interrupts):
    if register['f'] & 0x10:
        if b[1] > 127:
            b[1] = ~(255 - b[1])
        register['pc'] += b[1]
        return 12
    else:
        return 8


def op_39(register, b, interrupts):
    hl = register['h'] << 8 | register['l']
    temp = hl
    hl += register['sp']
    register['f'] &= 0x80
    if (temp & 0xfff) + (register['sp'] & 0xfff) > 0xfff:
        register['f'] |= 0x20
    if hl > 0xffff:
        register['f'] |= 0x10
    hl &= 0xffff
    register['h'] = hl >> 8
    register['l'] = hl & 0xff
    return 8


def op_3a(register, b, interrupts):
    hl = (register['h'] << 8) | register['l']
    register['a'] = mmu.read(hl)
    hl -= 1
    hl &= 0xffff
    register['h'] = hl >> 8
    register['l'] = hl & 0xff
    return 8


def op_3b(register, b, interrupts):
    register['sp'] -= 1
    if register['sp'] < 0:
        register['sp'] += 0x10000
    return 8


def op_3c(register, b, interrupts):
    register['f'] &= ~0x40
    register['f'] &= ~0x20
    if register['a'] == 0xff:
        register['a'] = 0
        register['f'] &= ~0x20
        register['f'] |= 0x80
    else:
        register['a'] += 1
        if register['a'] & 0x1f == 0x10:
           register['f'] |= 0x20
        register['f'] &= ~0x80
    return 4
    
##    h = register['a']
##    register['a'] += 1
##    if register['a'] == 0x0:
##        register['f'] |= 0x80
##    else:
##        register['f'] &= ~0x80
##    register['f'] &= ~0x40
##    if (h & 0xf) + (register['a'] & 0xf) > 0xf:
##        register['f'] |= 0x20
##    else:
##        register['f'] &= ~0x20
##    register['a'] &= 0xff
##    return 4

    
def op_3d(register, b, interrupts):
    h = register['a']
    register['a'] -= 1
    register['f'] = 0x40
    if register['a'] == 0:
        register['f'] |= 0x80
    elif register['a'] < 0:
        register['f'] |= 0x10
        register ['a'] += 0x100
    if (h & 0xf) - (register['a'] & 0xf) < 0:
        register['f'] |= 0x20
    return 4


def op_3e(register, b, interrupts):
    register['a'] = b[1]
    return 8


def op_3f(register, b, interrupts):
    register['f'] &= 0x9f
    if register['f'] & 0x10:
        register['f'] &= 0xef
    else:
        register['f'] |= 0x10
    return 4


def op_40(register, b, interrupts):
    register['b'] = register['b']
    return 4


def op_41(register, b, interrupts):
    register['b'] = register['c']
    return 4


def op_42(register, b, interrupts):
    register['b'] = register['d']
    return 4


def op_43(register, b, interrupts):
    register['b'] = register['e']
    return 4


def op_44(register, b, interrupts):
    register['b'] = register['h']
    return 4


def op_45(register, b, interrupts):
    register['b'] = register['l']
    return 4


def op_46(register, b, interrupts):
    hl = register['h'] << 8 | register['l']
    register['b'] = mmu.read(hl)
    return 8


def op_47(register, b, interrupts):
    register['b'] = register['a']
    return 4


def op_48(register, b, interrupts):
    register['c'] = register['b']
    return 4


def op_49(register, b, interrupts):
    register['c'] = register['c']
    return 4


def op_4a(register, b, interrupts):
    register['c'] = register['d']
    return 4


def op_4b(register, b, interrupts):
    register['c'] = register['e']
    return 4


def op_4c(register, b, interrupts):
    register['c'] = register['h']
    return 4


def op_4d(register, b, interrupts):
    register['c'] = register['l']
    return 4


def op_4e(register, b, interrupts):
    hl = register['h'] << 8 | register['l']
    register['c'] = mmu.read(hl)
    return 4


def op_4f(register, b, interrupts):
    register['c'] = register['a']
    return 4


def op_50(register, b, interrupts):
    register['d'] = register['b']
    return 4


def op_51(register, b, interrupts):
    register['d'] = register['c']
    return 4


def op_52(register, b, interrupts):
    register['d'] = register['d']
    return 4


def op_53(register, b, interrupts):
    register['d'] = register['e']
    return 4


def op_54(register, b, interrupts):
    register['d'] = register['h']
    return 4


def op_55(register, b, interrupts):
    register['d'] = register['l']
    return 4
    

def op_56(register, b, interrupts):
    hl = register['h'] << 8 | register['l']
    register['d'] = mmu.read(hl)
    return 4


def op_57(register, b, interrupts):
    register['d'] = register['a']
    return 4


def op_58(register, b, interrupts):
    register['e'] = register['b']
    return 4


def op_59(register, b, interrupts):
    register['e'] = register['c']
    return 4


def op_5a(register, b, interrupts):
    register['e'] = register['d']
    return 4


def op_5b(register, b, interrupts):
    register['e'] = register['e']
    return 4


def op_5c(register, b, interrupts):
    register['e'] = register['h']
    return 4


def op_5d(register, b, interrupts):
    register['e'] = register['l']
    return 4


def op_5e(register, b, interrupts):
    hl = register['h'] << 8 | register['l']
    register['e'] = mmu.read(hl)
    return 4


def op_5f(register, b, interrupts):
    register['e']= register['a']
    return 4


def op_60(register, b, interrupts):
    register['h'] = register['b']
    return 4
    

def op_61(register, b, interrupts):
    register['h'] = register['c']
    return 4
    

def op_62(register, b, interrupts):
    register['h'] = register['d']
    return 4
    

def op_63(register, b, interrupts):
    register['h'] = register['e']
    return 4
    

def op_64(register, b, interrupts):
    register['h'] = register['h']
    return 4
    

def op_65(register, b, interrupts):
    register['h'] = register['l']
    return 4
    

def op_66(register, b, interrupts):
    hl = register['h'] << 8 | register['l']
    register['h'] = mmu.read(hl)
    return 8
    

def op_67(register, b, interrupts):
    register['h'] = register['a']
    return 4
    

def op_68(register, b, interrupts):
    register['l'] = register['b']
    return 4
    

def op_69(register, b, interrupts):
    register['l'] = register['c']
    return 4
    

def op_6a(register, b, interrupts):
    register['l'] = register['d']
    return 4
    

def op_6b(register, b, interrupts):
    register['l'] = register['e']
    return 4
    

def op_6c(register, b, interrupts):
    register['l'] = register['h']
    return 4
    

def op_6d(register, b, interrupts):
    register['l'] = register['l']
    return 4
    

def op_6e(register, b, interrupts):
    hl = register['h'] << 8 | register['l']
    register['l'] = mmu.read(hl)
    return 8
    

def op_6f(register, b, interrupts):
    register['l'] = register['a']
    return 4


def op_70(register, b, interrupts):
    hl = (register['h'] << 8) | register['l']
    mmu.write(register['clock'], hl, register['b'])
    return 8


def op_71(register, b, interrupts):
    hl = (register['h'] << 8) | register['l']
    mmu.write(register['clock'], hl, register['c'])
    return 8


def op_72(register, b, interrupts):
    hl = (register['h'] << 8) | register['l']
    mmu.write(register['clock'], hl, register['d'])
    return 8


def op_73(register, b, interrupts):
    hl = (register['h'] << 8) | register['l']
    mmu.write(register['clock'], hl, register['e'])
    return 8


def op_74(register, b, interrupts):
    hl = (register['h'] << 8) | register['l']
    mmu.write(register['clock'], hl, register['h'])
    return 8
    

def op_75(register, b, interrupts):
    hl = (register['h'] << 8) | register['l']
    mmu.write(register['clock'], hl, register['l'])
    return 8


def op_76 (register, b, interrupts):
    global run
    run = 0
    return 4

def op_77(register, b, interrupts):
    hl = (register['h'] << 8) | register['l']
    mmu.write(register['clock'], hl, register['a'])
    return 8


def op_78(register, b, interrupts):
    register['a'] = register['b']
    return 4


def op_79(register, b, interrupts):
    register['a'] = register['c']
    return 4


def op_7a(register, b, interrupts):
    register['a'] = register['d']
    return 4


def op_7b(register, b, interrupts):
    register['a'] = register['e']
    return 4

def op_7c(register, b, interrupts):
    register['a'] = register['h']
    return 4


def op_7d(register, b, interrupts):
    register['a'] = register['l']
    return 4


def op_7e(register, b, interrupts):
    hl = register['h'] << 8 | register['l']
    register['a'] = mmu.read(hl)
    return 4


def op_7f(register, b, interrupts):
    register['a'] = register['a']
    return 4


def op_80(register, b, interrupts):
    h = register['a']
    register['f'] = 0
    register['a'] += register['b']
    if register['a'] > 0xff:
        register['f'] |= 0x10
    register['a'] &= 0xff
    if (h & 0xf) + (register['b'] & 0xf) > 0xf:
        register['f'] |= 0x20
    if register['a'] == 0:
        register['f'] |= 0x80
    return 4


def op_81(register, b, interrupts):
    h = register['a']
    register['f'] = 0
    register['a'] += register['c']
    if register['a'] > 0xff:
        register['f'] |= 0x10
    register['a'] &= 0xff
    if (h & 0xf) + (register['c'] & 0xf) > 0xf:
        register['f'] |= 0x20
    if register['a'] == 0:
        register['f'] |= 0x80
    return 4


def op_82(register, b, interrupts):
    h = register['a']
    register['f'] = 0
    register['a'] += register['d']
    if register['a'] > 0xff:
        register['f'] |= 0x10
    register['a'] &= 0xff
    if (h & 0xf) + (register['d'] & 0xf) > 0xf:
        register['f'] |= 0x20
    if register['a'] == 0:
        register['f'] |= 0x80
    return 4


def op_83(register, b, interrupts):
    h = register['a']
    register['a'] += register['e']
    if register['a'] > 0xff:
        register['f'] |= 0x10
    register['a'] &= 0xff
    register['f'] = 0
    if (h & 0xf) + (register['e'] & 0xf) > 0xf:
        register['f'] |= 0x20
    if register['a'] == 0:
        register['f'] |= 0x80
    return 4


def op_84(register, b, interrupts):
    h = register['a']
    register['a'] += register['h']
    if register['a'] > 0xff:
        register['f'] |= 0x10
    register['a'] &= 0xff
    register['f'] = 0
    if (h & 0xf) + (register['h'] & 0xf) > 0xf:
        register['f'] |= 0x20
    if register['a'] == 0:
        register['f'] |= 0x80
    return 4
    

def op_85(register, b, interrupts):
    h = register['a']
    register['f'] = 0
    register['a'] += register['l']
    if register['a'] > 0xff:
        register['f'] |= 0x10
    register['a'] &= 0xff
    if (h & 0xf) + (register['l'] & 0xf) > 0xf:
        register['f'] |= 0x20
    if register['a'] == 0:
        register['f'] |= 0x80
    return 4


def op_86(register, b, interrupts):
    hl = (register['h'] << 8) | register['l']
    h = mmu.read(hl)
    register['f'] = 0
    if ((register['a'] & 0xf) + (h & 0xf)) >= 0x10:
        register['f'] |= 0x20
    register['a'] += h
    if register['a'] >= 0x100:
        register['f'] |= 0x10
    else:
        register['f'] &= ~0x10
    register['a'] &= 0xff
    if register['a'] == 0:
        register['f'] |= 0x80
    #print (hex(register['a']), hex(register['f']), hex(h), hex(register['pc']))
    return 8
    
##    register['f'] &= ~0x40
##    if (h & 0xf) + (register['a'] & 0xf) > 0xf:
##        register['f'] |= 0x20
##    if register['a'] > 255:
##        register['f'] |= 0x10
##        register['a'] &= 0xff
##    if register['a'] == 0x0:
##        register['f'] |= 0x80
    return 8



def op_87(register, b, interrupts):
    h = register['a']
    register['a'] += register['a']
    register['f'] = 0
    if register['a'] > 0xff:
        register['f'] |= 0x10
    register['a'] &= 0xff
    if (h & 0xf) + (register['a'] & 0xf) > 0xf:
        register['f'] |= 0x20
    if register['a'] == 0:
        register['f'] |= 0x80
    return 4


def op_88(register, b, interrupts):
    h = register['a']
    register['a'] += register['b']
    register['f'] = 0
    if register['a'] > 0xff:
        register['f'] |= 0x10
    register['a'] &= 0xff
    if (h & 0xf) + (register['b'] & 0xf) > 0xf:
        register['f'] |= 0x20
    if register['a'] == 0:
        register['f'] |= 0x80
    return 4


def op_89(register, b, interrupts):
    h = register['a']
    if register['f'] & 0x10:
        register['a'] += 1
    register['a'] += register['c']
    register['f'] = 0
    if register['a'] > 0xff:
        register['f'] |= 0x10
    register['a'] &= 0xff
    if (h & 0xf) + (register['c'] & 0xf) > 0xf:
        register['f'] |= 0x20
    if register['a'] == 0:
        register['f'] |= 0x80
    return 4


def op_8a(register, b, interrupts):
    h = register['a']
    if register['f'] & 0x10:
        register['a'] += 1
    register['a'] += register['d']
    register['f'] = 0
    if register['a'] > 0xff:
        register['f'] |= 0x10
    register['a'] &= 0xff
    if (h & 0xf) + (register['d'] & 0xf) > 0xf:
        register['f'] |= 0x20
    if register['a'] == 0:
        register['f'] |= 0x80
    return 4


def op_8b(register, b, interrupts):
    h = register['a']
    if register['f'] & 0x10:
        register['a'] += 1
    register['a'] += register['e']
    register['f'] = 0
    if register['a'] > 0xff:
        register['f'] |= 0x10
    register['a'] &= 0xff
    if (h & 0xf) + (register['e'] & 0xf) > 0xf:
        register['f'] |= 0x20
    if register['a'] == 0:
        register['f'] |= 0x80
    return 4


def op_8c(register, b, interrupts):
    h = register['a']
    if register['f'] & 0x10:
        register['a'] += 1
    register['a'] += register['h']
    register['f'] = 0
    if register['a'] > 0xff:
        register['f'] |= 0x10
    register['a'] &= 0xff
    if (h & 0xf) + (register['h'] & 0xf) > 0xf:
        register['f'] |= 0x20
    if register['a'] == 0:
        register['f'] |= 0x80
    return 4

def op_8d(register, b, interrupts):
    h = register['a']
    if register['f'] & 0x10:
        register['a'] += 1
    register['a'] += register['l']
    register['f'] = 0
    if register['a'] > 0xff:
        register['f'] |= 0x10
    register['a'] &= 0xff
    if (h & 0xf) + (register['l'] & 0xf) > 0xf:
        register['f'] |= 0x20
    if register['a'] == 0:
        register['f'] |= 0x80
    return 4


def op_8e(register, b, interrupts):
    hl = register['h'] << 8 | register['l']
    temp = mmu.read(hl)
    h = register['a']
    if register['f'] & 0x10:
        register['a'] += 1
    register['a'] += temp
    register['f'] = 0
    if register['a'] > 0xff:
        register['f'] |= 0x10
    register['a'] &= 0xff
    if (h & 0xf) + (temp & 0xf) > 0xf:
        register['f'] |= 0x20
    if register['a'] == 0:
        register['f'] |= 0x80
    return 4


def op_8f(register, b, interrupts):
    h = register['a']
    if register['f'] & 0x10:
        register['a'] += 1
    register['a'] += register['a']
    register['f'] = 0
    if register['a'] > 0xff:
        register['f'] |= 0x10
    register['a'] &= 0xff
    if (h & 0xf) + (register['a'] & 0xf) > 0xf:
        register['f'] |= 0x20
    if register['a'] == 0:
        register['f'] |= 0x80
    return 4
    
    
def op_90(register, b, interrupts):
    h = register['a']
    register['f'] = 0x40
    register['a'] -= register['b']
    if register['a'] < 0:
        register['f'] |= 0x10
        register['a'] += 0x100
    elif register['a'] == 0:
        register['f'] |= 0x80
    if (h & 0xf) - (register['b'] & 0xf) < 0:
        register['f'] |= 0x20
    return 4

def op_91(register, b, interrupts):
    h = register['a']
    register['f'] = 0x40
    register['a'] -= register['c']
    if register['a'] < 0:
        register['f'] |= 0x10
        register['a'] += 0x100
    elif register['a'] == 0:
        register['f'] |= 0x80
    if (h & 0xf) - (register['c'] & 0xf) < 0:
        register['f'] |= 0x20
    return 4


def op_92(register, b, interrupts):
    h = register['a']
    register['f'] = 0x40
    register['a'] -= register['d']
    if register['a'] < 0:
        register['f'] |= 0x10
        register['a'] += 0x100
    elif register['a'] == 0:
        register['f'] |= 0x80
    if (h & 0xf) - (register['d'] & 0xf) < 0:
        register['f'] |= 0x20
    return 4


def op_93(register, b, interrupts):
    h = register['a']
    register['f'] = 0x40
    register['a'] -= register['e']
    if register['a'] < 0:
        register['f'] |= 0x10
        register['a'] += 0x100
    elif register['a'] == 0:
        register['f'] |= 0x80
    if (h & 0xf) - (register['e'] & 0xf) < 0:
        register['f'] |= 0x20
    return 4


def op_94(register, b, interrupts):
    h = register['a']
    register['f'] = 0x40
    register['a'] -= register['h']
    if register['a'] < 0:
        register['f'] |= 0x10
        register['a'] += 0x100
    elif register['a'] == 0:
        register['f'] |= 0x80
    if (h & 0xf) - (register['h'] & 0xf) < 0:
        register['f'] |= 0x20
    return 4


def op_95(register, b, interrupts):
    h = register['a']
    register['f'] = 0x40
    register['a'] -= register['l']
    if register['a'] < 0:
        register['f'] |= 0x10
        register['a'] += 0x100
    elif register['a'] == 0:
        register['f'] |= 0x80
    if (h & 0xf) - (register['l'] & 0xf) < 0:
        register['f'] |= 0x20
    return 4


def op_96(register, b, interrupts):
    hl = register['h'] << 8 | register['l']
    temp = mmu.read(hl)
    h = register['a']
    register['f'] = 0x40
    register['a'] -= temp
    if register['a'] < 0:
        register['f'] |= 0x10
        register['a'] += 0x100
    elif register['a'] == 0:
        register['f'] |= 0x80
    if (h & 0xf) - (temp & 0xf) < 0:
        register['f'] |= 0x20
    return 8


def op_97(register, b, interrupts):
    h = register['a']
    register['f'] = 0x40
    register['a'] -= register['a']
    if register['a'] < 0:
        register['f'] |= 0x10
        register['a'] += 0x100
    elif register['a'] == 0:
        register['f'] |= 0x80
    if (h & 0xf) - (register['a'] & 0xf) < 0:
        register['f'] |= 0x20
    return 4


def op_98(register, b, interrupts):
    h = register['a']
    register['a'] -= register['b']
    if register['f'] & 0x10:
        register['a'] -= 1
    register['f'] = 0x40
    if register['a'] < 0:
        register['f'] |= 0x10
        register['a'] += 0x100
    elif register['a'] == 0:
        register['f'] |= 0x80
    if (h & 0xf) - (register['b'] & 0xf) < 0:
        register['f'] |= 0x20
    return 4


def op_99(register, b, interrupts):
    h = register['a']
    register['a'] -= register['c']
    if register['f'] & 0x10:
        register['a'] -= 1
    register['f'] = 0x40
    if register['a'] < 0:
        register['f'] |= 0x10
        register['a'] += 0x100
    elif register['a'] == 0:
        register['f'] |= 0x80
    if (h & 0xf) - (register['c'] & 0xf) < 0:
        register['f'] |= 0x20
    return 4


def op_9a(register, b, interrupts):
    h = register['a']
    register['a'] -= register['d']
    if register['f'] & 0x10:
        register['a'] -= 1
    register['f'] = 0x40
    if register['a'] < 0:
        register['f'] |= 0x10
        register['a'] += 0x100
    elif register['a'] == 0:
        register['f'] |= 0x80
    if (h & 0xf) - (register['d'] & 0xf) < 0:
        register['f'] |= 0x20
    return 4


def op_9b(register, b, interrupts):
    h = register['a']
    register['a'] -= register['e']
    if register['f'] & 0x10:
        register['a'] -= 1
    register['f'] = 0x40
    if register['a'] < 0:
        register['f'] |= 0x10
        register['a'] += 0x100
    elif register['a'] == 0:
        register['f'] |= 0x80
    if (h & 0xf) - (register['e'] & 0xf) < 0:
        register['f'] |= 0x20
    return 4


def op_9c(register, b, interrupts):
    h = register['a']
    register['a'] -= register['h']
    if register['f'] & 0x10:
        register['a'] -= 1
    register['f'] = 0x40
    if register['a'] < 0:
        register['f'] |= 0x10
        register['a'] += 0x100
    elif register['a'] == 0:
        register['f'] |= 0x80
    if (h & 0xf) - (register['h'] & 0xf) < 0:
        register['f'] |= 0x20
    return 4


def op_9d(register, b, interrupts):
    h = register['a']
    register['a'] -= register['l']
    if register['f'] & 0x10:
        register['a'] -= 1
    register['f'] = 0x40
    if register['a'] < 0:
        register['f'] |= 0x10
        register['a'] += 0x100
    elif register['a'] == 0:
        register['f'] |= 0x80
    if (h & 0xf) - (register['l'] & 0xf) < 0:
        register['f'] |= 0x20
    return 4


def op_9e(register, b, interrupts):
    hl = register['h'] << 8 | register['l']
    temp = mmu.read(hl)
    h = register['a']
    register['a'] -= temp
    if register['f'] & 0x10:
        register['a'] -= 1
    register['f'] = 0x40
    if register['a'] < 0:
        register['f'] |= 0x10
        register['a'] += 0x100
    elif register['a'] == 0:
        register['f'] |= 0x80
    if (h & 0xf) - (temp & 0xf) < 0:
        register['f'] |= 0x20
    return 8


def op_9f(register, b, interrupts):
    h = register['a']
    register['a'] -= register['a']
    if register['f'] & 0x10:
        register['a'] -= 1
    register['f'] = 0x40
    if register['a'] < 0:
        register['f'] |= 0x10
        register['a'] += 0x100
    elif register['a'] == 0:
        register['f'] |= 0x80
    if (h & 0xf) - (register['a'] & 0xf) < 0:
        register['f'] |= 0x20
    return 4


def op_a0(register, b, interrupts):
    register['a'] &= register['b']
    register['f'] = 0x20
    if register['a'] == 0:
        register['f'] = 0xa0
    return 4


def op_a1(register, b, interrupts):
    register['a'] &= register['c']
    register['f'] = 0x20
    if register['a'] == 0:
        register['f'] = 0xa0
    return 4


def op_a2(register, b, interrupts):
    register['a'] &= register['d']
    register['f'] = 0x20
    if register['a'] == 0:
        register['f'] = 0xa0
    return 4


def op_a3(register, b, interrupts):
    register['a'] &= register['e']
    register['f'] = 0x20
    if register['a'] == 0:
        register['f'] = 0xa0
    return 4


def op_a4(register, b, interrupts):
    register['a'] &= register['h']
    register['f'] = 0x20
    if register['a'] == 0:
        register['f'] = 0xa0
    return 4


def op_a5(register, b, interrupts):
    register['a'] &= register['l']
    register['f'] = 0x20
    if register['a'] == 0:
        register['f'] = 0xa0
    return 4


def op_a6(register, b, interrupts):
    hl = register['h'] << 8 | register['l']
    temp = mmu.read(hl)
    register['a'] &= temp
    register['f'] = 0x20
    if register['a'] == 0:
        register['f'] = 0xa0
    return 4


def op_a7(register, b, interrupts):
    register['a'] &= register['a']
    register['f'] = 0x20
    if register['a'] == 0:
        register['f'] = 0xa0
    return 4


def op_a8(register, b, interrupts):
    register['a'] ^= register['b']
    register['f'] = 0
    if register['a'] == 0:
        register['f'] = 0x80
    return 4


def op_a9(register, b, interrupts):
    register['a'] ^= register['c']
    register['f'] = 0
    if register['a'] == 0:
        register['f'] = 0x80
    return 4


def op_aa(register, b, interrupts):
    register['a'] ^= register['d']
    register['f'] = 0
    if register['a'] == 0:
        register['f'] = 0x80
    return 4


def op_ab(register, b, interrupts):
    register['a'] ^= register['e']
    register['f'] = 0
    if register['a'] == 0:
        register['f'] = 0x80
    return 4


def op_ac(register, b, interrupts):
    register['a'] ^= register['h']
    register['f'] = 0
    if register['a'] == 0:
        register['f'] = 0x80
    return 4


def op_ad(register, b, interrupts):
    register['a'] ^= register['l']
    register['f'] = 0
    if register['a'] == 0:
        register['f'] = 0x80
    return 4


def op_ae(register, b, interrupts):
    hl = register['h'] << 8 | register['l']
    temp = mmu.read(hl)
    register['a'] ^= temp
    register['f'] = 0
    if register['a'] == 0:
        register['f'] = 0x80
    return 4
 

def op_af(register, b, interrupts):
    register['a'] ^= register['a']
    register['f'] = 0
    if register['a'] == 0:
        register['f'] = 0x80
    return 4


def op_b0(register, b, interrupts):
    register['a'] |= register['b']
    if register['a'] == 0:
        register['f'] = 0x80
    else:
        register['f'] = 0x00
    return 4


def op_b1(register, b, interrupts):
    register['a'] |= register['c']
    if register['a'] == 0:
        register['f'] = 0x80
    else:
        register['f'] = 0x00
    return 4


def op_b2(register, b, interrupts):
    register['a'] |= register['d']
    if register['a'] == 0:
        register['f'] = 0x80
    else:
        register['f'] = 0x00
    return 4


def op_b3(register, b, interrupts):
    register['a'] |= register['e']
    if register['a'] == 0:
        register['f'] = 0x80
    else:
        register['f'] = 0x00
    return 4


def op_b4(register, b, interrupts):
    register['a'] |= register['d']
    if register['a'] == 0:
        register['f'] = 0x80
    else:
        register['f'] = 0x00
    return 4


def op_b5(register, b, interrupts):
    register['a'] |= register['e']
    if register['a'] == 0:
        register['f'] = 0x80
    else:
        register['f'] = 0x00
    return 4


def op_b6(register, b, interrupts):
    hl = register['h'] << 8 | register['l']
    temp = mmu.read(hl)
    register['a'] |= temp
    if register['a'] == 0:
        register['f'] = 0x80
    else:
        register['f'] = 0x00
    return 4


def op_b7(register, b, interrupts):
    register['a'] |= register['a']
    if register['a'] == 0:
        register['f'] = 0x80
    else:
        register['f'] = 0x00
    return 4


def op_b8(register, b, interrupts):
    register['f'] = 0
    if register['a'] - register['b'] == 0:
        register['f'] |= 0x80
    register['f'] |= 0x40
    if (register['a'] & 0xf) < (register['b'] & 0xf):
        register['f'] |= 0x20
    if register['a'] < register['b']:
        register['f'] &= ~0x10
    else:
        register['f'] |= 0x10
    return 8


def op_b9(register, b, interrupts):
    register['f'] = 0
    if register['a'] - register['c'] == 0:
        register['f'] |= 0x80
    register['f'] |= 0x40
    if (register['a'] & 0xf) < (register['c'] & 0xf):
        register['f'] |= 0x20
    if register['a'] < register['c']:
        register['f'] &= ~0x10
    else:
        register['f'] |= 0x10
    return 8


def op_ba(register, b, interrupts):
    register['f'] = 0
    if register['a'] - register['d'] == 0:
        register['f'] |= 0x80
    register['f'] |= 0x40
    if (register['a'] & 0xf) < (register['d'] & 0xf):
        register['f'] |= 0x20
    if register['a'] < register['d']:
        register['f'] &= ~0x10
    else:
        register['f'] |= 0x10
    return 8


def op_bb(register, b, interrupts):
    register['f'] = 0
    if register['a'] - register['e'] == 0:
        register['f'] |= 0x80
    register['f'] |= 0x40
    if (register['a'] & 0xf) < (register['e'] & 0xf):
        register['f'] |= 0x20
    if register['a'] < register['e']:
        register['f'] &= ~0x10
    else:
        register['f'] |= 0x10
    return 8


def op_bc(register, b, interrupts):
    register['f'] = 0
    if register['a'] - register['h'] == 0:
        register['f'] |= 0x80
    register['f'] |= 0x40
    if (register['a'] & 0xf) < (register['h'] & 0xf):
        register['f'] |= 0x20
    if register['a'] < register['h']:
        register['f'] &= ~0x10
    else:
        register['f'] |= 0x10
    return 8


def op_bd(register, b, interrupts):
    register['f'] = 0
    if register['a'] - register['l'] == 0:
        register['f'] |= 0x80
    register['f'] |= 0x40
    if (register['a'] & 0xf) < (register['l'] & 0xf):
        register['f'] |= 0x20
    if register['a'] < register['l']:
        register['f'] &= ~0x10
    else:
        register['f'] |= 0x10
    return 8


def op_be(register, b, interrupts):
    register['f'] = 0
    hl = (register['h'] << 8) | register['l']
    if register['a'] - mmu.read(hl) == 0:
        register['f'] |= 0x80
    register['f'] |= 0x40
    if (register['a'] & 0xf) < (mmu.read(hl) & 0xf):
        register['f'] |= 0x20
    if register['a'] < mmu.read(hl):
        register['f'] &= ~0x10
    else:
        register['f'] |= 0x10
    return 8


def op_bf(register, b, interrupts):
    register['f'] = 0
    if register['a'] - register['a'] == 0:
        register['f'] |= 0x80
    register['f'] |= 0x40
    if (register['a'] & 0xf) < (register['a'] & 0xf):
        register['f'] |= 0x20
    if register['a'] < register['a']:
        register['f'] &= ~0x10
    else:
        register['f'] |= 0x10
    return 8


def op_c0(register, b, interrupts):
    if register['f'] & 0x80:
        return 8
    else:
        register['pc'] = mmu.read(register['sp'])
        register['pc'] += (mmu.read(register['sp'] + 1) << 8)
        register['sp'] += 2
        return 20
        
    
def op_c1(register, b, interrupts):
    register['c'] = mmu.read(register['sp'])
    register['b'] = mmu.read(register['sp'] + 1)
    register['sp'] += 2                         
    return 12


def op_c2(register, b, interrupts):
    if register['f'] & 0x80:
        return 12
    else:
        register['pc'] = b[2] << 8 | b[1]
        return 16


def op_c3(register, b, interrupts):
    register['pc'] = b[2] << 8 | b[1]
    return 16


def op_c4(register, b, interrupts):
    if register['f'] & 0x80:
        return 12
    else:
        mmu.write(register['clock'], register['sp'] - 1, register['pc'] >> 8)
        mmu.write(register['clock'], register['sp'] - 2, register['pc'] & 0xff)
        register['pc'] = (b[2] << 8) + b[1]
        register['sp'] -= 2
        return 24


def op_c5(register, b, interrupts):
    mmu.write(register['clock'], register['sp'] - 1, register['b'])
    mmu.write(register['clock'], register['sp'] - 2, register['c'])
    register['sp'] -= 2
    return 16


def op_c6(register, b, interrupts):
    h = register['a']
    register['a'] += b[1]
    if register['a'] > 0xff:
        register['f'] |= 0x10
    register['a'] &= 0xff
    register['f'] = 0
    if ~((h & 0xf) < (register['a'] & 0xf)):
        register['f'] |= 0x20
    if register['a'] == 0:
        register['f'] |= 0x80
    return 4


def op_c7(register, b, interrupts):
    mmu.write(register['clock'], register['sp'] - 1, register['pc'] >> 8)
    mmu.write(register['clock'], register['sp'] - 2, register['pc'] & 0xff)
    register['sp'] -= 2
    register['pc'] = 0
    return 16


def op_c8(register, b, interrupts):
    if register['f'] & 0x80:
        register['pc'] = mmu.read(register['sp'])
        register['pc'] += (mmu.read(register['sp'] + 1) << 8)
        register['sp'] += 2
        return 20
    else:
        return 8
        

def op_c9(register, b, interrupts):
    register['pc'] = mmu.read(register['sp'])
    register['pc'] += (mmu.read(register['sp'] + 1) << 8)
    register['sp'] += 2
    return 16


def op_ca(register, b, interrupts):
    if register['f'] & 0x80:
        register['pc'] = b[2] << 8 | b[1]
        return 16
    else:
        return 12


def op_cb(register, b, interrupts):
    cb.cb_lookup[int(b[1])](register)
    return 8


def op_cc(register, b, interrupts):
    if register['f'] & 0x80:
        mmu.write(register['clock'], register['sp'] - 1, register['pc'] >> 8)
        mmu.write(register['clock'], register['sp'] - 2, register['pc'] & 0xff)
        register['pc'] = (b[2] << 8) + b[1]
        register['sp'] -= 2
        return 24
    else:
        return 12


def op_cd(register, b, interrupts):
    mmu.write(register['clock'], register['sp'] - 1, register['pc'] >> 8)
    mmu.write(register['clock'], register['sp'] - 2, register['pc'] & 0xff)
    register['pc'] = (b[2] << 8) + b[1]
    register['sp'] -= 2
    return 24


def op_ce(register, b, interrupts):
    h = register['a']
    if register['f'] & 0x10:
        register['a'] += 1
    register['a'] += b[1]
    register['f'] = 0
    if register['a'] > 0xff:
        register['f'] |= 0x10
    register['a'] &= 0xff
    if (h & 0xf) + (b[1] & 0xf) > 0xf:
        register['f'] |= 0x20
    if register['a'] == 0:
        register['f'] |= 0x80
    return 4


def op_cf(register, b, interrupts):
    mmu.write(register['clock'], register['sp'] - 1, register['pc'] >> 8)
    mmu.write(register['clock'], register['sp'] - 2, register['pc'] & 0xff)
    register['sp'] -= 2
    register['pc'] = 0x8
    return 16


def op_d0(register, b, interrupts):
    if register['f'] & 0x10:
        return 8
    else:
        register['pc'] = mmu.read(register['sp'])
        register['pc'] += (mmu.read(register['sp'] + 1) << 8)
        register['sp'] += 2
        return 20


def op_d1(register, b, interrupts):
    register['e'] = mmu.read(register['sp'])
    register['d'] = mmu.read(register['sp'] + 1)
    register['sp'] += 2                         
    return 12


def op_d2(register, b, interrupts):
    if register['f'] & 0x10:
        return 12
    else:
        register['pc'] = b[2] << 8 | b[1]
        return 16


def op_d4(register, b, interrupts):
    if register['f'] & 0x10:
        return 12
    else:
        mmu.write(register['clock'], register['sp'] - 1, register['pc'] >> 8)
        mmu.write(register['clock'], register['sp'] - 2, register['pc'] & 0xff)
        register['pc'] = (b[2] << 8) + b[1]
        register['sp'] -= 2
        return 24


def op_d5(register, b, interrupts):
    mmu.write(register['clock'], register['sp'] - 1, register['d'])
    mmu.write(register['clock'], register['sp'] - 2, register['e'])
    register['sp'] -= 2
    return 16


def op_d6(register, b, interrupts):
    h = register['a']
    register['f'] = 0x40
    register['a'] -= b[1]
    if register['a'] < 0:
        register['f'] |= 0x10
        register['a'] += 0x100
    elif register['a'] == 0:
        register['f'] |= 0x80
    if (h & 0xf) - (b[1] & 0xf) < 0:
        register['f'] |= 0x20
    return 4


def op_d7(register, b, interrupts):
    mmu.write(register['clock'], register['sp'] - 1, register['pc'] >> 8)
    mmu.write(register['clock'], register['sp'] - 2, register['pc'] & 0xff)
    register['sp'] -= 2
    register['pc'] = 0x10
    return 16


def op_d8(register, b, interrupts):
    if register['f'] & 0x10:
        register['pc'] = mmu.read(register['sp'])
        register['pc'] += (mmu.read(register['sp'] + 1) << 8)
        register['sp'] += 2
        return 20
    else:
        return 8


def op_d9(register, b, interrupts):
    register['pc'] = mmu.read(register['sp'])
    register['pc'] += (mmu.read(register['sp'] + 1) << 8)
    register['sp'] += 2
    interrupts[0] = 1
    return 16


def op_da(register, b, interrupts):
    if register['f'] & 0x10:
        register['pc'] = b[2] << 8 | b[1]
        return 16
    else:
        return 12


def op_dc(register, b, interrupts):
    if register['f'] & 0x10:
        mmu.write(register['clock'], register['sp'] - 1, register['pc'] >> 8)
        mmu.write(register['clock'], register['sp'] - 2, register['pc'] & 0xff)
        register['pc'] = (b[2] << 8) + b[1]
        register['sp'] -= 2
        return 24
    else:
        return 12


def op_de(register, b, interrupts):
    h = register['a']
    register['a'] -= b[1]
    if register['f'] & 0x10:
        register['a'] -= 1
    register['f'] = 0x40
    if register['a'] < 0:
        register['f'] |= 0x10
        register['a'] += 0x100
    elif register['a'] == 0:
        register['f'] |= 0x80
    if (h & 0xf) - (b[1] & 0xf) < 0:
        register['f'] |= 0x20
    return 4


def op_df(register, b, interrupts):
    mmu.write(register['clock'], register['sp'] - 1, register['pc'] >> 8)
    mmu.write(register['clock'], register['sp'] - 2, register['pc'] & 0xff)
    register['sp'] -= 2
    register['pc'] = 0x18
    return 16


def op_e0(register, b, interrupts):
    b[1] += 0xff00
    mmu.write(register['clock'], b[1], register['a'])
    return 12


def op_e1(register, b, interrupts):
    register['l'] = mmu.read(register['sp'])
    register['h'] = mmu.read(register['sp'] + 1)
    register['sp'] += 2                         
    return 12


def op_e2(register, b, interrupts):
    temp = register['c'] + 0xff00
    mmu.write(register['clock'], temp, register['a'])
    return 8


def op_e5(register, b, interrupts):
    mmu.write(register['clock'], register['sp'] - 1, register['h'])
    mmu.write(register['clock'], register['sp'] - 2, register['l'])
    register['sp'] -= 2
    return 16


def op_e6(register, b, interrupts):
    register['a'] &= b[1]
    if register['a'] == 0:
        register['f'] = 0xa0
    else:
        register['f'] = 0x20
    return 8


def op_e7(register, b, interrupts):
    mmu.write(register['clock'], register['sp'] - 1, register['pc'] >> 8)
    mmu.write(register['clock'], register['sp'] - 2, register['pc'] & 0xff)
    register['sp'] -= 2
    register['pc'] = 0x20
    return 16


def op_e8(register, b, interrupts):
    if b[1] > 127:
        b[1] = ~(255 - b[1])
    h = register['sp']
    if (h & 0xf) + (register['sp'] & 0xf) > 0xf:
        register['f'] = 0x10
    else :
        register['f'] = 0
        register['sp'] += b[1]
        if (register['sp'] & 0xff) + h > 0xff:
            register['f'] |= 0x80
    return 16
    
    
def op_e9(register, b, interrupts):
    hl = register['h'] << 8 | register['l']
    register['pc'] = hl
    #print(hex(hl))
    return 4


def op_ea(register, b, interrupts):
    mmu.write(register['clock'], (b[2] << 8) + b[1], register['a'])
    return 16


def op_ee(register, b, interrupts):
    register['a'] ^= b[1]
    register['f'] = 0
    if register['a'] == 0:
        register['f'] = 0x80
    return 8


def op_ef(register, b, interrupts):
    mmu.write(register['clock'], register['sp'] - 1, register['pc'] >> 8)
    mmu.write(register['clock'], register['sp'] - 2, register['pc'] & 0xff)
    register['sp'] -= 2
    register['pc'] = 0x28
    return 16
    


def op_f0(register, b, interrupts):
    b[1] += 0xff00
    register['a'] = mmu.read(b[1])
    return 12


def op_f1(register, b, interrupts):
    register['f'] = mmu.read(register['sp'])
    register['a'] = mmu.read(register['sp'] + 1)
    register['sp'] += 2                         
    return 12


def op_f2(register, b, interrupts):
    temp = register['c'] + 0xff00
    register['a'] = mmu.read(temp)
    return 8


def op_f3(register, b, interrupts):
    interrupts[1] = 1
    return 4


def op_f5(register, b, interrupts):
    mmu.write(register['clock'], register['sp'] - 1, register['a'])
    mmu.write(register['clock'], register['sp'] - 2, register['f'])
    register['sp'] -= 2
    return 16


def op_f6(register, b, interrupts):
    register['a'] |= b[1]
    if register['a'] == 0:
        register['f'] = 0x80
    else:
        register['f'] = 0x00
    return 8


def op_f7(register, b, interrupts):
    mmu.write(register['clock'], register['sp'] - 1, register['pc'] >> 8)
    mmu.write(register['clock'], register['sp'] - 2, register['pc'] & 0xff)
    register['sp'] -= 2
    register['pc'] = 0x30
    return 16


def op_f8(register, b, interrupts):
    if b[1] > 127:
            temp = ~(255 - b[1])
    hl = register['sp'] + b[1]
    register['f'] = 0
    if hl > 0xffff:
        register['f'] |= 0x10
        hl -= 0x10000
    elif hl < 0:
        register['f'] += 0x10
        hl += 0x10000
    hl &= 0xffff
    register['h'] = hl >> 8
    register['l'] = hl & 0xff
    temp = (register['sp'] &  0xf00) + (b[1] & 0xf00)
    if temp > 0xf | temp < 0:
        register['f'] |= 0x20
    return 12


def op_f9(register, b, interrupts):
    hl = register['h'] << 8 | register['l']
    register['sp'] = hl
    return 8
    

def op_fa(register, b, interrupts):
    register['a'] = mmu.read(b[2] << 8 | b[1])
    return 16


def op_fb(register, b, interrupts):
    interrupts[0] = 1
    return 4


def op_fe(register, b, interrupts):
    register['f'] = 0
    if register['a'] - b[1] == 0:
        register['f'] |= 0x80
    register['f'] |= 0x40
    if (register['a'] & 0xf) - (b[1] & 0xf) < 0:
        register['f'] |= 0x20
    if register['a'] < b[1]:
        register['f'] |= 0x10
    return 8

def op_ff(register, b, interrupts):
    mmu.write(register['clock'], register['sp'] - 1, register['pc'] >> 8)
    mmu.write(register['clock'], register['sp'] - 2, register['pc'] & 0xff)
    register['sp'] -= 2
    register['pc'] = 0x38
    return 16

    
length_lookup = {
    0x00: 1, 0x01: 3, 0x02: 1, 0x03: 1, 0x04: 1, 0x05: 1, 0x06: 2, 0x07: 1,
    0x08: 3, 0x09: 1, 0x0a: 1, 0x0b: 1, 0x0c: 1, 0x0d: 1, 0x0e: 2, 0x0f: 1,
    0x10: 1, 0x11: 3, 0x12: 1, 0x13: 1, 0x14: 1, 0x15: 1, 0x16: 2, 0x17: 1,
    0x18: 2, 0x19: 1, 0x1a: 1, 0x1b: 1, 0x1c: 1, 0x1d: 1, 0x1e: 2, 0x1f: 1,
    0x20: 2, 0x21: 3, 0x22: 1, 0x23: 1, 0x24: 1, 0x25: 1, 0x26: 2, 0x27: 1,
    0x28: 2, 0x29: 1, 0x2a: 1, 0x2b: 1, 0x2c: 1, 0x2d: 1, 0x2e: 2, 0x2f: 1,
    0x30: 2, 0x31: 3, 0x32: 1, 0x33: 1, 0x34: 1, 0x35: 1, 0x36: 2, 0x37: 1,
    0x38: 2, 0x39: 1, 0x3a: 1, 0x3b: 1, 0x3c: 1, 0x3d: 1, 0x3e: 2, 0x3f: 1,
    0x40: 1, 0x41: 1, 0x42: 1, 0x43: 1, 0x44: 1, 0x45: 1, 0x46: 1, 0x47: 1,
    0x48: 1, 0x49: 1, 0x4a: 1, 0x4b: 1, 0x4c: 1, 0x4d: 1, 0x4e: 1, 0x4f: 1,
    0x50: 1, 0x51: 1, 0x52: 1, 0x53: 1, 0x54: 1, 0x55: 1, 0x56: 1, 0x57: 1,
    0x58: 1, 0x59: 1, 0x5a: 1, 0x5b: 1, 0x5c: 1, 0x5d: 1, 0x5e: 1, 0x5f: 1,
    0x60: 1, 0x61: 1, 0x62: 1, 0x63: 1, 0x64: 1, 0x65: 1, 0x66: 1, 0x67: 1,
    0x68: 1, 0x69: 1, 0x6a: 1, 0x6b: 1, 0x6c: 1, 0x6d: 1, 0x6e: 1, 0x6f: 1,
    0x70: 1, 0x71: 1, 0x72: 1, 0x73: 1, 0x74: 1, 0x75: 1, 0x76: 1, 0x77: 1,
    0x78: 1, 0x79: 1, 0x7a: 1, 0x7b: 1, 0x7c: 1, 0x7d: 1, 0x7e: 1, 0x7f: 1,
    0x80: 1, 0x81: 1, 0x82: 1, 0x83: 1, 0x84: 1, 0x85: 1, 0x86: 1, 0x87: 1,
    0x88: 1, 0x89: 1, 0x8a: 1, 0x8b: 1, 0x8c: 1, 0x8d: 1, 0x8e: 1, 0x8f: 1,
    0x90: 1, 0x91: 1, 0x92: 1, 0x93: 1, 0x94: 1, 0x95: 1, 0x96: 1, 0x97: 1,
    0x98: 1, 0x99: 1, 0x9a: 1, 0x9b: 1, 0x9c: 1, 0x9d: 1, 0x9e: 1, 0x9f: 1,
    0xa0: 1, 0xa1: 1, 0xa2: 1, 0xa3: 1, 0xa4: 1, 0xa5: 1, 0xa6: 1, 0xa7: 1,
    0xa8: 1, 0xa9: 1, 0xaa: 1, 0xab: 1, 0xac: 1, 0xad: 1, 0xae: 1, 0xaf: 1,
    0xb0: 1, 0xb1: 1, 0xb2: 1, 0xb3: 1, 0xb4: 1, 0xb5: 1, 0xb6: 1, 0xb7: 1,
    0xb8: 1, 0xb9: 1, 0xba: 1, 0xbb: 1, 0xbc: 1, 0xbd: 1, 0xbe: 1, 0xbf: 1,
    0xc0: 1, 0xc1: 1, 0xc2: 3, 0xc3: 3, 0xc4: 3, 0xc5: 1, 0xc6: 2, 0xc7: 1,
    0xc8: 1, 0xc9: 1, 0xca: 3, 0xcb: 2, 0xcc: 3, 0xcd: 3, 0xce: 2, 0xcf: 1,
    0xd0: 1, 0xd1: 1, 0xd2: 3, 0xd3: 4, 0xd4: 3, 0xd5: 1, 0xd6: 2, 0xd7: 1,
    0xd8: 1, 0xd9: 1, 0xda: 3, 0xdb: 4, 0xdc: 3, 0xdd: 4, 0xde: 2, 0xdf: 1,
    0xe0: 2, 0xe1: 1, 0xe2: 1, 0xe3: 4, 0xe4: 4, 0xe5: 1, 0xe6: 2, 0xe7: 1,
    0xe8: 2, 0xe9: 1, 0xea: 3, 0xeb: 4, 0xec: 4, 0xed: 4, 0xee: 2, 0xef: 1,
    0xf0: 2, 0xf1: 1, 0xf2: 1, 0xf3: 1, 0xf4: 4, 0xf5: 1, 0xf6: 2, 0xf7: 1,
    0xf8: 2, 0xf9: 1, 0xfa: 3, 0xfb: 1, 0xfc: 4, 0xfd: 4, 0xfe: 2, 0xff: 1,
}

opcode_lookup = {
    0x00: op_00, 0x01: op_01, 0x02: op_02, 0x03: op_03, 0x04: op_04, 0x05: op_05, 0x06: op_06, 0x07: op_07,
    0x08: op_08, 0x09: op_09, 0x0a: op_0a, 0x0b: op_0b, 0x0c: op_0c, 0x0d: op_0d, 0x0e: op_0e, 0x0f: op_0f,
    0x10: op_10, 0x11: op_11, 0x12: op_12, 0x13: op_13, 0x14: op_14, 0x15: op_15, 0x16: op_16, 0x17: op_17,
    0x18: op_18, 0x19: op_19, 0x1a: op_1a, 0x1b: op_1b, 0x1c: op_1c, 0x1d: op_1d, 0x1e: op_1e, 0x1f: op_1f,
    0x20: op_20, 0x21: op_21, 0x22: op_22, 0x23: op_23, 0x24: op_24, 0x25: op_25, 0x26: op_26, 0x27: op_27,
    0x28: op_28, 0x29: op_29, 0x2a: op_2a, 0x2b: op_2b, 0x2c: op_2c, 0x2d: op_2d, 0x2e: op_2e, 0x2f: op_2f,
    0x30: op_30, 0x31: op_31, 0x32: op_32, 0x33: op_33, 0x34: op_34, 0x35: op_35, 0x36: op_36, 0x37: op_37,
    0x38: op_38, 0x39: op_39, 0x3a: op_3a, 0x3b: op_3b, 0x3c: op_3c, 0x3d: op_3d, 0x3e: op_3e, 0x3f: op_3f,
    0x40: op_40, 0x41: op_41, 0x42: op_42, 0x43: op_43, 0x44: op_44, 0x45: op_45, 0x46: op_46, 0x47: op_47,
    0x48: op_48, 0x49: op_49, 0x4a: op_4a, 0x4b: op_4b, 0x4c: op_4c, 0x4d: op_4d, 0x4e: op_4e, 0x4f: op_4f, 
    0x50: op_50, 0x51: op_51, 0x52: op_52, 0x53: op_53, 0x54: op_54, 0x55: op_55, 0x56: op_56, 0x57: op_57,
    0x58: op_58, 0x59: op_59, 0x5a: op_5a, 0x5b: op_5b, 0x5c: op_5c, 0x5d: op_5d, 0x5e: op_5e, 0x5f: op_5f, 
    0x60: op_60, 0x61: op_61, 0x62: op_62, 0x63: op_63, 0x64: op_64, 0x65: op_65, 0x66: op_66, 0x67: op_67, 
    0x68: op_68, 0x69: op_69, 0x6a: op_6a, 0x6b: op_6b, 0x6c: op_6c, 0x6d: op_6d, 0x6e: op_6e, 0x6f: op_6f, 
    0x70: op_70, 0x71: op_71, 0x72: op_72, 0x73: op_73, 0x74: op_74, 0x75: op_75, 0x76: op_76, 0x77: op_77,
    0x78: op_78, 0x79: op_79, 0x7a: op_7a, 0x7b: op_7b, 0x7c: op_7c, 0x7d: op_7d, 0x7e: op_7e, 0x7f: op_7f, 
    0x80: op_80, 0x81: op_81, 0x82: op_82, 0x83: op_83, 0x84: op_84, 0x85: op_85, 0x86: op_86, 0x87: op_87,
    0x88: op_88, 0x89: op_89, 0x8a: op_8a, 0x8b: op_8b, 0x8c: op_8c, 0x8d: op_8d, 0x8e: op_8e, 0x8f: op_8f,
    0x90: op_90, 0x91: op_91, 0x92: op_92, 0x93: op_93, 0x94: op_94, 0x95: op_95, 0x96: op_96, 0x97: op_97, 
    0x98: op_98, 0x99: op_99, 0x9a: op_9a, 0x9b: op_9b, 0x9c: op_9c, 0x9d: op_9d, 0x9e: op_9e, 0x9f: op_9f, 
    0xa0: op_a0, 0xa1: op_a1, 0xa2: op_a2, 0xa3: op_a3, 0xa4: op_a4, 0xa5: op_a5, 0xa6: op_a6, 0xa7: op_a7,
    0xa8: op_a8, 0xa9: op_a9, 0xaa: op_aa, 0xab: op_ab, 0xac: op_ac, 0xad: op_ad, 0xae: op_ae, 0xaf: op_af,
    0xb0: op_b0, 0xb1: op_b1, 0xb2: op_b2, 0xb3: op_b3, 0xb4: op_b4, 0xb5: op_b5, 0xb6: op_b6, 0xb7: op_b7,
    0xb8: op_b8, 0xb9: op_b9, 0xba: op_ba, 0xbb: op_bb, 0xbc: op_bc, 0xbd: op_bd, 0xbe: op_be, 0xbf: op_bf,
    0xc0: op_c0, 0xc1: op_c1, 0xc2: op_c2, 0xc3: op_c3, 0xc4: op_c4, 0xc5: op_c5, 0xc6: op_c6, 0xc7: op_c7,
    0xc8: op_c8, 0xc9: op_c9, 0xca: op_ca, 0xcb: op_cb, 0xcc: op_cc, 0xcd: op_cd, 0xce: op_ce, 0xcf: op_cf,
    0xd0: op_d0, 0xd1: op_d1, 0xd2: op_d2, 0xd5: op_d5, 0xd6: op_d6, 0xd7: op_d7,
    0xd8: op_d8, 0xd9: op_d9, 0xda: op_da, 0xde: op_de,
    0xe0: op_e0, 0xe1: op_e1, 0xe2: op_e2, 0xe5: op_e5, 0xe6: op_e6, 0xe7: op_e7, 0xef: op_ef,
    0xe8: op_e8, 0xe9: op_e9, 0xea: op_ea, 0xee: op_ee, 0xef: op_ef,
    0xf0: op_f0, 0xf1: op_f1, 0xf2: op_f2, 0xf3: op_f3, 0xf5: op_f5, 0xf6: op_f6, 0xf7: op_f7, 
    0xf8: op_f8, 0xf9: op_f9, 0xfa: op_fa, 0xfb: op_fb, 0xfe: op_fe, 0xff: op_ff
}
