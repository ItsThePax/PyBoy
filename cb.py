import mmu

def cb_00(register):
    register['f'] = 0
    register['b'] <<= 1
    if register['b'] == 0:
        register['f'] |= 0x80
    elif register['b'] > 0xff:
        register['f'] |= 0x10
        register['b'] += 1
        register['b'] &= 0xff


def cb_01(register):
    register['f'] = 0
    register['c'] <<= 1
    if register['c'] == 0:
        register['f'] |= 0x80
    elif register['c'] > 0xff:
        register['f'] |= 0x10
        register['c'] += 1
        register['c'] &= 0xff

        
def cb_02(register):
    register['f'] = 0
    register['d'] <<= 1
    if register['d'] == 0:
        register['f'] |= 0x80
    elif register['d'] > 0xff:
        register['f'] |= 0x10
        register['d'] += 1
        register['d'] &= 0xff

        
def cb_03(register):
    register['f'] = 0
    register['e'] <<= 1
    if register['e'] == 0:
        register['f'] |= 0x80
    elif register['e'] > 0xff:
        register['f'] |= 0x10
        register['e'] += 1
        register['e'] &= 0xff

        
def cb_04(register):
    register['f'] = 0
    register['h'] <<= 1
    if register['h'] == 0:
        register['f'] |= 0x80
    elif register['h'] > 0xff:
        register['f'] |= 0x10
        register['h'] += 1
        register['h'] &= 0xff

        
def cb_05(register):
    register['f'] = 0
    register['l'] <<= 1
    if register['l'] == 0:
        register['f'] |= 0x80
    elif register['l'] > 0xff:
        register['f'] |= 0x10
        register['l'] += 1
        register['l'] &= 0xff

        
def cb_06(register):
    hl = register['h'] << 8 | register['l']
    temp = mmu.read(hl)
    register['f'] = 0
    temp <<= 1
    if temp == 0:
        register['f'] |= 0x80
    elif temp > 0xff:
        temp |= 0x10
        temp += 1
        temp &= 0xff
    mmu.write(hl, temp)

        
def cb_07(register):
    hl = register['h'] << 8 | register['l']
    temp = mmu.read(hl)
    register['f'] = 0
    register['a'] <<= 1
    if register['a'] == 0:
        register['f'] |= 0x80
    elif register['a'] > 0xff:
        register['f'] |= 0x10
        register['a'] += 1
        register['a'] &= 0xff
    mmu.write(hl, temp)

    
def cb_08(register):
    c = register['b'] & 1
    register['b'] >>= 1
    register['f'] = 0
    if c:
        register['b'] += 0x80
        register['f'] = 0x10
    if register['b'] == 0:
        register['f'] |= 0x80


def cb_09(register):
    c = register['c'] & 1
    register['c'] >>= 1
    register['f'] = 0
    if c:
        register['c'] += 0x80
        register['f'] = 0x10
    if register['c'] == 0:
        register['f'] |= 0x80


def cb_0a(register):
    c = register['d'] & 1
    register['d'] >>= 1
    register['f'] = 0
    if c:
        register['d'] += 0x80
        register['f'] = 0x10
    if register['d'] == 0:
        register['f'] |= 0x80


def cb_0b(register):
    c = register['e'] & 1
    register['e'] >>= 1
    register['f'] = 0
    if c:
        register['e'] += 0x80
        register['f'] = 0x10
    if register['e'] == 0:
        register['f'] |= 0x80


def cb_0c(register):
    c = register['h'] & 1
    register['h'] >>= 1
    register['f'] = 0
    if c:
        register['h'] += 0x80
        register['f'] = 0x10
    if register['h'] == 0:
        register['f'] |= 0x80


def cb_0d(register):
    c = register['l'] & 1
    register['l'] >>= 1
    register['f'] = 0
    if c:
        register['l'] += 0x80
        register['f'] = 0x10
    if register['l'] == 0:
        register['f'] |= 0x80


def cb_0e(register):
    hl = register['h'] << 8 | register['l']
    temp = mmu.read(hl)
    c = temp & 1
    temp >>= 1
    register['f'] = 0
    if c:
        temp += 0x80
        register['f'] = 0x10
    if temp == 0:
        register['f'] |= 0x80
    mmu.write(hl, temp)


def cb_0f(register):
    c = register['a'] & 1
    register['a'] >>= 1
    register['f'] = 0
    if c:
        register['a'] += 0x80
        register['f'] = 0x10
    if register['a'] == 0:
        register['f'] |= 0x80


def cb_10(register):
    register['f'] = 0
    register['a'] <<= 1
    if register['a'] >= 0x100:
        register['f'] |= 0x10
    register['a'] &= 0xff
    if register['a'] == 0:
        register['f'] |= 0x80
    

def cb_11(register):
    if register['c'] & 0x80:
        register['f'] = 0x10
    else:
        register['f'] = 0
    register['c'] <<= 1
    register['c'] &= 0xff
    if register['c'] == 0:
        register['f'] |= 0x80


def cb_12(register):
    if register['d'] & 0x80:
        register['f'] = 0x10
    else:
        register['f'] = 0
    register['d'] <<= 1
    register['d'] &= 0xff
    if register['d'] == 0:
        register['f'] |= 0x80
        
def cb_13(register):
    if register['e'] & 0x80:
        register['f'] = 0x10
    else:
        register['f'] = 0
    register['e'] <<= 1
    register['e'] &= 0xff
    if register['e'] == 0:
        register['f'] |= 0x80
        

def cb_14(register):
    if register['h'] & 0x80:
        register['f'] = 0x10
    else:
        register['f'] = 0
    register['h'] <<= 1
    register['h'] &= 0xff
    if register['h'] == 0:
        register['f'] |= 0x80
        

def cb_15(register):
    if register['l'] & 0x80:
        register['f'] = 0x10
    else:
        register['f'] = 0
    register['l'] <<= 1
    register['l'] &= 0xff
    if register['l'] == 0:
        register['f'] |= 0x80
        

def cb_16(register):
    hl = register['h'] << 8 | register['l']
    temp = mmu.read(hl)
    if temp & 0x80:
        register['f'] = 0x10
    else:
        register['f'] = 0
    temp <<= 1
    temp &= 0xff
    if temp == 0:
        register['f'] |= 0x80
    mmu.write(hl, temp)
        

def cb_17(register):
    if register['a'] & 0x80:
        register['f'] = 0x10
    else:
        register['f'] = 0
    register['a'] <<= 1
    register['a'] &= 0xff
    if register['a'] == 0:
        register['f'] |= 0x80
        

def cb_18(register):
    if register['b'] & 1:
        register['f'] = 0x10
    else:
        register['f'] = 0
    register['b'] >>= 1
    if register['b'] == 0:
        register['f'] |= 0x80


def cb_19(register):
    if register['c'] & 1:
        register['f'] = 0x10
    else:
        register['f'] = 0
    register['c'] >>= 1
    if register['c'] == 0:
        register['f'] |= 0x80


def cb_1a(register):
    if register['d'] & 1:
        register['f'] = 0x10
    else:
        register['f'] = 0
    register['d'] >>= 1
    if register['d'] == 0:
        register['f'] |= 0x80


def cb_1b(register):
    if register['e'] & 1:
        register['f'] = 0x10
    else:
        register['f'] = 0
    register['e'] >>= 1
    if register['e'] == 0:
        register['f'] |= 0x80


def cb_1c(register):
    if register['h'] & 1:
        register['f'] = 0x10
    else:
        register['f'] = 0
    register['h'] >>= 1
    if register['h'] == 0:
        register['f'] |= 0x80


def cb_1d(register):
    if register['l'] & 1:
        register['f'] = 0x10
    else:
        register['f'] = 0
    register['l'] >>= 1
    if register['l'] == 0:
        register['f'] |= 0x80


def cb_1e(register):
    hl = register['h'] << 8 | register['l']
    temp = mmu.read(hl)
    if temp & 1:
        register['f'] = 0x10
    else:
        register['f'] = 0
    temp >>= 1
    if temp == 0:
        register['f'] |= 0x80
    mmu.write(hl, temp)


def cb_1f(register):
    if register['a'] & 1:
        register['f'] = 0x10
    else:
        register['f'] = 0
    register['a'] >>= 1
    if register['a'] == 0:
        register['f'] |= 0x80


def cb_20(register):
    register['b'] <<= 1
    register['f'] = 0
    if register['b'] > 0xff:
        register['f'] |= 0x10
    register['b'] &= 0xff
    if register['b'] == 0:
        register['f'] |= 0x80


def cb_21(register):
    register['c'] <<= 1
    register['f'] = 0
    if register['c'] > 0xff:
        register['f'] |= 0x10
    register['c'] &= 0xff
    if register['c'] == 0:
        register['f'] |= 0x80


def cb_22(register):
    register['d'] <<= 1
    register['f'] = 0
    if register['d'] > 0xff:
        register['f'] |= 0x10
    register['d'] &= 0xff
    if register['d'] == 0:
        register['f'] |= 0x80


def cb_23(register):
    register['e'] <<= 1
    register['f'] = 0
    if register['e'] > 0xff:
        register['f'] |= 0x10
    register['e'] &= 0xff
    if register['e'] == 0:
        register['f'] |= 0x80


def cb_24(register):
    register['h'] <<= 1
    register['f'] = 0
    if register['h'] > 0xff:
        register['f'] |= 0x10
    register['h'] &= 0xff
    if register['h'] == 0:
        register['f'] |= 0x80


def cb_25(register):
    register['l'] <<= 1
    register['f'] = 0
    if register['l'] > 0xff:
        register['f'] |= 0x10
    register['l'] &= 0xff
    if register['l'] == 0:
        register['f'] |= 0x80


def cb_26(register):
    hl = register['h'] << 8 | register['l']
    temp = mmu.read(hl)
    temp <<= 1
    register['f'] = 0
    if temp > 0xff:
        register['f'] |= 0x10
    temp &= 0xff
    if temp == 0:
        register['f'] |= 0x80
    mmu.write(hl, temp)


def cb_27(register):
    register['a'] <<= 1
    register['f'] = 0x0
    if register ['a'] > 0xff:
        register['f'] |= 0x10
    register['a'] &= 0xff
    if register['a'] == 0:
        register['f'] |= 0x80


def cb_28(register):
    register['f'] = 0
    temp = register['b'] & 0x80
    if register['b'] & 0x1:
        register['f'] = 0x10
    register['b'] >>= 1
    register['b'] |= temp


def cb_29(register):
    register['f'] = 0
    temp = register['c'] & 0x80
    if register['c'] & 0x1:
        register['f'] = 0x10
    register['c'] >>= 1
    register['c'] |= temp


def cb_2a(register):
    register['f'] = 0
    temp = register['d'] & 0x80
    if register['d'] & 0x1:
        register['f'] = 0x10
    register['d'] >>= 1
    register['d'] |= temp


def cb_2b(register):
    register['f'] = 0
    temp = register['e'] & 0x80
    if register['e'] & 0x1:
        register['f'] = 0x10
    register['e'] >>= 1
    register['e'] |= temp


def cb_2c(register):
    register['f'] = 0
    temp = register['h'] & 0x80
    if register['h'] & 0x1:
        register['f'] = 0x10
    register['h'] >>= 1
    register['h'] |= temp


def cb_2d(register):
    register['f'] = 0
    temp = register['l'] & 0x80
    if register['l'] & 0x1:
        register['f'] = 0x10
    register['l'] >>= 1
    register['l'] |= temp


def cb_2e(register):
    hl = register['h'] << 8 | register['l']
    temp = mmu.read(hl)
    register['f'] = 0
    h = temp & 0x80
    if temp & 0x1:
        register['f'] = 0x10
    temp >>= 1
    temp |= h
    mmu.write(hl, temp)


def cb_2f(register):
    register['f'] = 0
    temp = register['a'] & 0x80
    if register['a'] & 0x1:
        register['f'] = 0x10
    register['a'] >>= 1
    register['a'] |= temp
        

def cb_30(register):
    if register['b'] == 0:
        register['f'] = 0x80
        return
    temp = register['b'] & 0xf
    temp <<= 4
    register['b'] >>= 4
    register['b'] |= temp
    register['f'] = 0


def cb_31(register):
    if register['c'] == 0:
        register['f'] = 0x80
        return
    temp = register['c'] & 0xf
    temp <<= 4
    register['c'] >>= 4
    register['c'] |= temp
    register['f'] = 0


def cb_32(register):
    if register['d'] == 0:
        register['f'] = 0x80
        return
    temp = register['d'] & 0xf
    temp <<= 4
    register['d'] >>= 4
    register['d'] |= temp
    register['f'] = 0


def cb_33(register):
    if register['e'] == 0:
        register['f'] = 0x80
        return
    temp = register['e'] & 0xf
    temp <<= 4
    register['e'] >>= 4
    register['e'] |= temp
    register['f'] = 0


def cb_34(register):
    if register['h'] == 0:
        register['f'] = 0x80
        return
    temp = register['h'] & 0xf
    temp <<= 4
    register['h'] >>= 4
    register['h'] |= temp
    register['f'] = 0


def cb_35(register):
    if register['l'] == 0:
        register['f'] = 0x80
        return
    temp = register['l'] & 0xf
    temp <<= 4
    register['l'] >>= 4
    register['l'] |= temp
    register['f'] = 0


def cb_36(register):
    hl = register['h'] << 8 | register ['l']
    temp = mmu.read(hl)
    if temp == 0:
        register['f'] = 0x80
        return
    n = temp & 0xf
    temp <<= 4
    temp >>= 4
    temp |= n
    register['f'] = 0
    mmu.write(hl, temp)
        

def cb_37(register):
    if register['a'] == 0:
        register['f'] = 0x80
        return
    temp = register['a'] & 0xf
    temp <<= 4
    register['a'] >>= 4
    register['a'] |= temp
    register['f'] = 0


def cb_38(register):
    if register['b'] & 0x80:
        register['f'] = 0x10
    else:
        register['f'] = 0
    register['b'] >>= 1
    if register['b'] == 0:
        register['f'] |= 0x80
        

def cb_39(register):
    if register['c'] & 0x80:
        register['f'] = 0x10
    else:
        register['f'] = 0
    register['c'] >>= 1
    if register['c'] == 0:
        register['f'] |= 0x80
        

def cb_3a(register):
    if register['d'] & 0x80:
        register['f'] = 0x10
    else:
        register['f'] = 0
    register['d'] >>= 1
    if register['d'] == 0:
        register['f'] |= 0x80
        

def cb_3b(register):
    if register['e'] & 0x80:
        register['f'] = 0x10
    else:
        register['f'] = 0
    register['e'] >>= 1
    if register['e'] == 0:
        register['f'] |= 0x80
        

def cb_3c(register):
    if register['h'] & 0x80:
        register['f'] = 0x10
    else:
        register['f'] = 0
    register['h'] >>= 1
    if register['h'] == 0:
        register['f'] |= 0x80
        

def cb_3d(register):
    if register['l'] & 0x80:
        register['f'] = 0x10
    else:
        register['f'] = 0
    register['l'] >>= 1
    if register['l'] == 0:
        register['f'] |= 0x80
        

def cb_3e(register):
    hl = register['h'] << 8 | register ['l']
    temp = mmu.read(hl)
    if temp & 0x80:
        register['f'] = 0x10
    else:
        register['f'] = 0
    temp >>= 1
    if temp == 0:
        register['f'] |= 0x80
    mmu.write(hl, temp)
        

def cb_3f(register):
    if register['a'] & 0x80:
        register['f'] = 0x10
    else:
        register['f'] = 0
    register['a'] >>= 1
    if register['a'] == 0:
        register['f'] |= 0x80
        

def cb_40(register):
    register['f'] &= 0x20
    if register['b'] & 0x1 == 0:
        register['f'] |= 0x80


def cb_41(register):
    register['f'] &= 0x20
    if register['c'] & 0x1 == 0:
        register['f'] |= 0x80


def cb_42(register):
    register['f'] &= 0x20
    if register['d'] & 0x1 == 0:
        register['f'] |= 0x80


def cb_43(register):
    register['f'] &= 0x20
    if register['e'] & 0x1 == 0:
        register['f'] |= 0x80


def cb_44(register):
    register['f'] &= 0x20
    if register['h'] & 0x1 == 0:
        register['f'] |= 0x80


def cb_45(register):
    register['f'] &= 0x20
    if register['l'] & 0x1 == 0:
        register['f'] |= 0x80


def cb_46(register):
    hl = register['h'] << 8 | register['l']
    value = mmu.read(hl)
    register['f'] &= 0x20
    if value & 0x1 == 0:
        register['f'] |= 0x80


def cb_47(register):
    register['f'] &= 0x20
    if register['b'] & 0x1 == 0:
        register['f'] |= 0x80
    

def cb_48(register):
    register['f'] &= 0x20
    if register['b'] & 0x2 == 0:
        register['f'] |= 0x80


def cb_49(register):
    register['f'] &= 0x20
    if register['c'] & 0x2 == 0:
        register['f'] |= 0x80


def cb_4a(register):
    register['f'] &= 0x20
    if register['d'] & 0x2 == 0:
        register['f'] |= 0x80


def cb_4b(register):
    register['f'] &= 0x20
    if register['e'] & 0x2 == 0:
        register['f'] |= 0x80


def cb_4c(register):
    register['f'] &= 0x20
    if register['h'] & 0x2 == 0:
        register['f'] |= 0x80


def cb_4d(register):
    register['f'] &= 0x20
    if register['h'] & 0x2 == 0:
        register['f'] |= 0x80


def cb_4e(register):
    hl = register['h'] << 8 | register ['l']
    temp = mmu.read(hl)
    register['f'] &= 0x20
    if temp & 0x2 == 0:
        register['f'] |= 0x80


def cb_4f(register):
    register['f'] &= 0x20
    if register['a'] & 0x2 == 0:
        register['f'] |= 0x80


def cb_50(register):
    if register['b'] & (1 << 2):
        register['f'] &= ~(1 << 7)
    else:
        register['f'] |= (1 << 7)
    register['f'] &= ~(1 << 6)
    register['f'] |= (1 << 5)


def cb_51(register):
    if register['c'] & (1 << 2):
        register['f'] &= ~(1 << 7)
    else:
        register['f'] |= (1 << 7)
    register['f'] &= ~(1 << 6)
    register['f'] |= (1 << 5)


def cb_52(register):
    if register['d'] & (1 << 2):
        register['f'] &= ~(1 << 7)
    else:
        register['f'] |= (1 << 7)
    register['f'] &= ~(1 << 6)
    register['f'] |= (1 << 5)


def cb_53(register):
    if register['e'] & (1 << 2):
        register['f'] &= ~(1 << 7)
    else:
        register['f'] |= (1 << 7)
    register['f'] &= ~(1 << 6)
    register['f'] |= (1 << 5)


def cb_54(register):
    if register['h'] & (1 << 2):
        register['f'] &= ~(1 << 7)
    else:
        register['f'] |= (1 << 7)
    register['f'] &= ~(1 << 6)
    register['f'] |= (1 << 5)


def cb_55(register):
    if register['l'] & (1 << 2):
        register['f'] &= ~(1 << 7)
    else:
        register['f'] |= (1 << 7)
    register['f'] &= ~(1 << 6)
    register['f'] |= (1 << 5)


def cb_56(register):
    hl = register['h'] << 8 | register ['l']
    temp = mmu.read(hl)
    if temp & (1 << 2):
        register['f'] &= ~(1 << 7)
    else:
        register['f'] |= (1 << 7)
    register['f'] &= ~(1 << 6)
    register['f'] |= (1 << 5)


def cb_57(register):
    if register['a'] & (1 << 2):
        register['f'] &= ~(1 << 7)
    else:
        register['f'] |= (1 << 7)
    register['f'] &= ~(1 << 6)
    register['f'] |= (1 << 5)


def cb_58(register):
    if register['b'] & (1 << 3):
        register['f'] &= ~(1 << 7)
    else:
        register['f'] |= (1 << 7)
    register['f'] &= ~(1 << 6)
    register['f'] |= (1 << 5)


def cb_58(register):
    if register['b'] & (1 << 3):
        register['f'] &= ~(1 << 7)
    else:
        register['f'] |= (1 << 7)
    register['f'] &= ~(1 << 6)
    register['f'] |= (1 << 5)


def cb_59(register):
    if register['c'] & (1 << 3):
        register['f'] &= ~(1 << 7)
    else:
        register['f'] |= (1 << 7)
    register['f'] &= ~(1 << 6)
    register['f'] |= (1 << 5)


def cb_5a(register):
    if register['d'] & (1 << 3):
        register['f'] &= ~(1 << 7)
    else:
        register['f'] |= (1 << 7)
    register['f'] &= ~(1 << 6)
    register['f'] |= (1 << 5)


def cb_5b(register):
    if register['e'] & (1 << 3):
        register['f'] &= ~(1 << 7)
    else:
        register['f'] |= (1 << 7)
    register['f'] &= ~(1 << 6)
    register['f'] |= (1 << 5)


def cb_5c(register):
    if register['h'] & (1 << 3):
        register['f'] &= ~(1 << 7)
    else:
        register['f'] |= (1 << 7)
    register['f'] &= ~(1 << 6)
    register['f'] |= (1 << 5)


def cb_5d(register):
    if register['l'] & (1 << 3):
        register['f'] &= ~(1 << 7)
    else:
        register['f'] |= (1 << 7)
    register['f'] &= ~(1 << 6)
    register['f'] |= (1 << 5)


def cb_5e(register):
    hl = register['h'] << 8 | register['l']
    temp = mmu.read(hl)
    if temp & (1 << 3):
        register['f'] &= ~(1 << 7)
    else:
        register['f'] |= (1 << 7)
    register['f'] &= ~(1 << 6)
    register['f'] |= (1 << 5)


def cb_5f(register):
    if register['a'] & (1 << 3):
        register['f'] &= ~(1 << 7)
    else:
        register['f'] |= (1 << 7)
    register['f'] &= ~(1 << 6)
    register['f'] |= (1 << 5)


def cb_60(register):
    if register['b'] & (1 << 4):
        register['f'] &= ~(1 << 7)
    else:
        register['f'] |= (1 << 7)
    register['f'] &= ~(1 << 6)
    register['f'] |= (1 << 5)


def cb_61(register):
    if register['c'] & (1 << 4):
        register['f'] &= ~(1 << 7)
    else:
        register['f'] |= (1 << 7)
    register['f'] &= ~(1 << 6)
    register['f'] |= (1 << 5)


def cb_62(register):
    if register['d'] & (1 << 4):
        register['f'] &= ~(1 << 7)
    else:
        register['f'] |= (1 << 7)
    register['f'] &= ~(1 << 6)
    register['f'] |= (1 << 5)


def cb_63(register):
    if register['e'] & (1 << 4):
        register['f'] &= ~(1 << 7)
    else:
        register['f'] |= (1 << 7)
    register['f'] &= ~(1 << 6)
    register['f'] |= (1 << 5)


def cb_64(register):
    if register['h'] & (1 << 4):
        register['f'] &= ~(1 << 7)
    else:
        register['f'] |= (1 << 7)
    register['f'] &= ~(1 << 6)
    register['f'] |= (1 << 5)


def cb_65(register):
    if register['l'] & (1 << 4):
        register['f'] &= ~(1 << 7)
    else:
        register['f'] |= (1 << 7)
    register['f'] &= ~(1 << 6)
    register['f'] |= (1 << 5)


def cb_66(register):
    hl = register['h'] << 8 | register ['l']
    temp = mmu.read(hl)
    if temp & (1 << 4):
        register['f'] &= ~(1 << 7)
    else:
        register['f'] |= (1 << 7)
    register['f'] &= ~(1 << 6)
    register['f'] |= (1 << 5)


def cb_67(register):
    if register['a'] & (1 << 4):
        register['f'] &= ~(1 << 7)
    else:
        register['f'] |= (1 << 7)
    register['f'] &= ~(1 << 6)
    register['f'] |= (1 << 5)
    

def cb_68(register):
    register['f'] &= 0x20
    if register['b'] & 0x20 == 0:
        register['f'] |= 0x80


def cb_69(register):
    register['f'] &= 0x20
    if register['c'] & 0x20 == 0:
        register['f'] |= 0x80


def cb_6a(register):
    register['f'] &= 0x20
    if register['d'] & 0x20 == 0:
        register['f'] |= 0x80


def cb_6b(register):
    register['f'] &= 0x20
    if register['e'] & 0x20 == 0:
        register['f'] |= 0x80


def cb_6c(register):
    register['f'] &= 0x20
    if register['h'] & 0x20 == 0:
        register['f'] |= 0x80


def cb_6d(register):
    register['f'] &= 0x20
    if register['h'] & 0x20 == 0:
        register['f'] |= 0x80


def cb_6e(register):
    hl = register['h'] << 8 | register ['l']
    temp = mmu.read(hl)
    register['f'] &= 0x20
    if temp & 0x20 == 0:
        register['f'] |= 0x80


def cb_6f(register):
    register['f'] &= 0x20
    if register['a'] & 0x20 == 0:
        register['f'] |= 0x80


def cb_70(register):
    if register['b'] & (1 << 6):
        register['f'] &= ~(1 << 7)
    else:
        register['f'] |= (1 << 7)
    register['f'] &= ~(1 << 6)
    register['f'] |= (1 << 5)


def cb_71(register):
    if register['c'] & (1 << 6):
        register['f'] &= ~(1 << 7)
    else:
        register['f'] |= (1 << 7)
    register['f'] &= ~(1 << 6)
    register['f'] |= (1 << 5)


def cb_72(register):
    if register['d'] & (1 << 6):
        register['f'] &= ~(1 << 7)
    else:
        register['f'] |= (1 << 7)
    register['f'] &= ~(1 << 6)
    register['f'] |= (1 << 5)


def cb_73(register):
    if register['e'] & (1 << 6):
        register['f'] &= ~(1 << 7)
    else:
        register['f'] |= (1 << 7)
    register['f'] &= ~(1 << 6)
    register['f'] |= (1 << 5)


def cb_74(register):
    if register['h'] & (1 << 6):
        register['f'] &= ~(1 << 7)
    else:
        register['f'] |= (1 << 7)
    register['f'] &= ~(1 << 6)
    register['f'] |= (1 << 5)


def cb_75(register):
    if register['l'] & (1 << 6):
        register['f'] &= ~(1 << 7)
    else:
        register['f'] |= (1 << 7)
    register['f'] &= ~(1 << 6)
    register['f'] |= (1 << 5)


def cb_76(register):
    hl = register['h'] << 8 | register ['l']
    temp = mmu.read(hl)
    if temp & (1 << 6):
        register['f'] &= ~(1 << 7)
    else:
        register['f'] |= (1 << 7)
    register['f'] &= ~(1 << 6)
    register['f'] |= (1 << 5)
    


def cb_77(register):
    if register['a'] & (1 << 6):
        register['f'] &= ~(1 << 7)
    else:
        register['f'] |= (1 << 7)
    register['f'] &= ~(1 << 6)
    register['f'] |= (1 << 5)
    

def cb_78(register):
    register['f'] &= 0x20
    if register['b'] & 0x80 == 0:
        register['f'] |= 0x80


def cb_79(register):
    register['f'] &= 0x20
    if register['c'] & 0x80 == 0:
        register['f'] |= 0x80


def cb_7a(register):
    register['f'] &= 0x20
    if register['d'] & 0x80 == 0:
        register['f'] |= 0x80


def cb_7b(register):
    register['f'] &= 0x20
    if register['e'] & 0x80 == 0:
        register['f'] |= 0x80


def cb_7c(register):
    register['f'] &= 0x20
    if register['h'] & 0x80 == 0:
        register['f'] |= 0x80


def cb_7d(register):
    register['f'] &= 0x20
    if register['h'] & 0x80 == 0:
        register['f'] |= 0x80


def cb_7e(register):
    hl = register['h'] << 8 | register ['l']
    temp = mmu.read(hl)
    register['f'] &= 0x80
    if temp & 0x20 == 0:
        register['f'] |= 0x80


def cb_7f(register):
    register['f'] &= 0x20
    if register['a'] & 0x80 == 0:
        register['f'] |= 0x80


def cb_80(register):
    register['b'] &= 0xfe


def cb_81(register):
    register['c'] &= 0xfe


def cb_82(register):
    register['d'] &= 0xfe


def cb_83(register):
    register['e'] &= 0xfe


def cb_84(register):
    register['h'] &= 0xfe


def cb_85(register):
    register['l'] &= 0xfe


def cb_86(register):
    hl = register['h'] << 8 | register['l']
    temp = mmu.read(hl)
    temp &= 0xfe
    mmu.write(hl, temp)
    

def cb_87(register):
    register['a'] &= 0xfe


def cb_88(register):
    register['b'] &= 0xfd


def cb_89(register):
    register['c'] &= 0xfd


def cb_8a(register):
    register['d'] &= 0xfd


def cb_8b(register):
    register['e'] &= 0xfd


def cb_8c(register):
    register['h'] &= 0xfd


def cb_8d(register):
    register['l'] &= 0xfd


def cb_8e(register):
    hl = register['h'] << 8 | register['l']
    temp = mmu.read(hl)
    temp &= 0xfd
    mmu.write(hl, temp)


def cb_8f(register):
    register['a'] &= 0xfd


def cb_90(register):
    register['b'] &= 0xfb


def cb_91(register):
    register['c'] &= 0xfb


def cb_92(register):
    register['d'] &= 0xfb


def cb_93(register):
    register['e'] &= 0xfb


def cb_94(register):
    register['h'] &= 0xfb


def cb_95(register):
    register['l'] &= 0xfb


def cb_96(register):
    hl = register['h'] << 8 | register['l']
    temp = mmu.read(hl)
    temp &= 0xfb
    mmu.write(hl, temp)


def cb_97(register):
    register['a'] &= 0xf7


def cb_98(register):
    register['b'] &= 0xf7


def cb_99(register):
    register['c'] &= 0xf7


def cb_9a(register):
    register['d'] &= 0xf7


def cb_9b(register):
    register['e'] &= 0xf7


def cb_9c(register):
    register['h'] &= 0xf7


def cb_9d(register):
    register['l'] &= 0xf7


def cb_9e(register):
    hl = register['h'] << 8 | register['l']
    temp = mmu.read(hl)
    temp &= 0xf7
    mmu.write(hl, temp)


def cb_9f(register):
    register['l'] &= 0xf7


def cb_a0(register):
    register['b'] &= 0xef


def cb_a1(register):
    register['c'] &= 0xef


def cb_a2(register):
    register['d'] &= 0xef


def cb_a3(register):
    register['e'] &= 0xef


def cb_a4(register):
    register['h'] &= 0xef


def cb_a5(register):
    register['l'] &= 0xef


def cb_a6(register):
    hl = register['h'] << 8 | register['l']
    temp = mmu.read(hl)
    temp &= 0xef
    mmu.write(hl, temp)


def cb_a7(register):
    register['a'] &= 0xef

    
def cb_a8(register):
    register['b'] &= 0xdf


def cb_a9(register):
    register['c'] &= 0xdf
    

def cb_aa(register):
    register['d'] &= 0xdf
    

def cb_ab(register):
    register['e'] &= 0xdf
    

def cb_ac(register):
    register['h'] &= 0xdf
    

def cb_ad(register):
    register['l'] &= 0xdf
    

def cb_ae(register):
    hl = register['h'] << 8 | register['l']
    temp = mmu.read(hl)
    temp &= 0xdf
    mmu.write(hl, temp)
    

def cb_af(register):
    register['a'] &= 0xdf


def cb_b0(register):
    register['b'] &= 0xdf


def cb_b1(register):
    register['c'] &= 0xdf


def cb_b2(register):
    register['d'] &= 0xdf


def cb_b3(register):
    register['e'] &= 0xdf


def cb_b4(register):
    register['h'] &= 0xdf


def cb_b5(register):
    register['l'] &= 0xdf


def cb_b6(register):
    hl = register['h'] << 8 | register['l']
    temp = mmu.read(hl)
    temp &= 0xdf
    mmu.write(hl, temp)


def cb_b7(register):
    register['a'] &= 0xdf
    

def cb_b8(register):
    register['b'] &= 0x7f


def cb_b9(register):
    register['c'] &= 0x7f


def cb_ba(register):
    register['d'] &= 0x7f


def cb_bb(register):
    register['e'] &= 0x7f


def cb_bc(register):
    register['h'] &= 0x7f


def cb_bd(register):
    register['l'] &= 0x7f


def cb_be(register):
    hl = register['h'] << 8 | register['l']
    temp = mmu.read(hl)
    temp &= 0x7f
    mmu.write(hl, temp)


def cb_bf(register):
    register['a'] &= 0x7f


def cb_c0(register):
    register['b'] |= 0x1


def cb_c1(register):
    register['c'] |= 0x1


def cb_c2(register):
    register['d'] |= 0x1


def cb_c3(register):
    register['e'] |= 0x1


def cb_c4(register):
    register['h'] |= 0x1


def cb_c5(register):
    register['l'] |= 0x1


def cb_c6(register):
    hl = register['h'] << 8 | register['l']
    temp = mmu.read(hl)
    temp |= 0x1
    mmu.write(hl, temp)


def cb_c7(register):
    register['a'] |= 0x1
    

def cb_c8(register):
    register['b'] |= 0x2


def cb_c9(register):
    register['c'] |= 0x2


def cb_ca(register):
    register['d'] |= 0x2


def cb_cb(register):
    register['e'] |= 0x2


def cb_cc(register):
    register['h'] |= 0x2


def cb_cd(register):
    register['l'] |= 0x2


def cb_ce(register):
    hl = register['h'] << 8 | register['l']
    temp = mmu.read(hl)
    temp |= 0x2
    mmu.write(hl, temp)


def cb_cf(register):
    register['a'] |= 0x4


def cb_d0(register):
    register['b'] |= 0x4


def cb_d1(register):
    register['c'] |= 0x4


def cb_d2(register):
    register['d'] |= 0x4


def cb_d3(register):
    register['e'] |= 0x4


def cb_d4(register):
    register['h'] |= 0x4


def cb_d5(register):
    register['l'] |= 0x4


def cb_d6(register):
    hl = register['h'] << 8 | register['l']
    temp = mmu.read(hl)
    temp |= 0x4
    mmu.write(hl, temp)


def cb_d7(register):
    register['a'] |= 0x4
    

def cb_d8(register):
    register['b'] |= 0x8


def cb_d9(register):
    register['c'] |= 0x8


def cb_da(register):
    register['d'] |= 0x8


def cb_db(register):
    register['e'] |= 0x8


def cb_dc(register):
    register['h'] |= 0x8


def cb_dd(register):
    register['l'] |= 0x8


def cb_de(register):
    hl = register['h'] << 8 | register['l']
    temp = mmu.read(hl)
    temp |= 0x8
    mmu.write(hl, temp)


def cb_df(register):
    register['a'] |= 0x8


def cb_e0(register):
    register['b'] |= 0x10


def cb_e1(register):
    register['c'] |= 0x10


def cb_e2(register):
    register['d'] |= 0x10


def cb_e3(register):
    register['e'] |= 0x10


def cb_e4(register):
    register['h'] |= 0x10


def cb_e5(register):
    register['l'] |= 0x10


def cb_e6(register):
    hl = register['h'] << 8 | register['l']
    temp = mmu.read(hl)
    temp |= 0x10
    mmu.write(hl, temp)


def cb_e7(register):
    register['a'] |= 0x10
    

def cb_e8(register):
    register['b'] |= 0x20


def cb_e9(register):
    register['c'] |= 0x20


def cb_ea(register):
    register['d'] |= 0x20


def cb_eb(register):
    register['e'] |= 0x20


def cb_ec(register):
    register['h'] |= 0x20


def cb_ed(register):
    register['l'] |= 0x20


def cb_ee(register):
    hl = register['h'] << 8 | register['l']
    temp = mmu.read(hl)
    temp |= 0x20
    mmu.write(hl, temp)


def cb_ef(register):
    register['a'] |= 0x20


def cb_f0(register):
    register['b'] |= 0x40


def cb_f1(register):
    register['c'] |= 0x40


def cb_f2(register):
    register['d'] |= 0x40


def cb_f3(register):
    register['e'] |= 0x40


def cb_f4(register):
    register['h'] |= 0x40


def cb_f5(register):
    register['l'] |= 0x40


def cb_f6(register):
    hl = register['h'] << 8 | register['l']
    temp = mmu.read(hl)
    temp |= 0x40
    mmu.write(hl, temp)


def cb_f7(register):
    register['a'] |= 0x40


def cb_f8(register):
    register['b'] |= 0x80


def cb_f9(register):
    register['c'] |= 0x80


def cb_fa(register):
    register['d'] |= 0x80


def cb_fb(register):
    register['e'] |= 0x80


def cb_fc(register):
    register['h'] |= 0x80


def cb_fd(register):
    register['l'] |= 0x80


def cb_fe(register):
    hl = register['h'] << 8 | register['l']
    temp = mmu.read(hl)
    temp |= 0x80
    mmu.write(hl, temp)


def cb_ff(register):
    register['a'] |= 0x80


cb_lookup = {
    0x00: cb_00, 0x01: cb_01, 0x02: cb_02, 0x03: cb_03, 0x04: cb_04, 0x05: cb_05, 0x06: cb_06, 0x07: cb_07,
    0x08: cb_08, 0x09: cb_09, 0x0a: cb_0a, 0x0b: cb_0b, 0x0c: cb_0c, 0x0d: cb_0d, 0x0e: cb_0e, 0x0f: cb_0f, 
    0x10: cb_10, 0x11: cb_11, 0x12: cb_12, 0x13: cb_13, 0x14: cb_14, 0x15: cb_15, 0x16: cb_16, 0x17: cb_17,
    0x18: cb_18, 0x19: cb_19, 0x1a: cb_1a, 0x1b: cb_1b, 0x1c: cb_1c, 0x1d: cb_1d, 0x1e: cb_1e, 0x1f: cb_1f,
    0x20: cb_20, 0x21: cb_21, 0x22: cb_22, 0x23: cb_23, 0x24: cb_24, 0x25: cb_25, 0x26: cb_26, 0x27: cb_27, 
    0x28: cb_28, 0x29: cb_29, 0x2a: cb_2a, 0x2b: cb_2b, 0x2c: cb_2c, 0x2d: cb_2d, 0x2e: cb_2e, 0x2f: cb_2f, 
    0x30: cb_30, 0x31: cb_31, 0x32: cb_32, 0x33: cb_33, 0x34: cb_34, 0x35: cb_35, 0x36: cb_36, 0x37: cb_37,
    0x38: cb_38, 0x39: cb_39, 0x3a: cb_3a, 0x3b: cb_3b, 0x3c: cb_3c, 0x3d: cb_3d, 0x3e: cb_3e, 0x3f: cb_3f,
    0x40: cb_40, 0x41: cb_41, 0x42: cb_42, 0x43: cb_43, 0x44: cb_44, 0x45: cb_45, 0x46: cb_46, 0x47: cb_47,
    0x48: cb_48, 0x49: cb_49, 0x4a: cb_4a, 0x4b: cb_4b, 0x4c: cb_4c, 0x4d: cb_4d, 0x4e: cb_4e, 0x4f: cb_4f, 
    0x50: cb_50, 0x51: cb_51, 0x52: cb_52, 0x53: cb_53, 0x54: cb_54, 0x55: cb_55, 0x56: cb_56, 0x57: cb_57,
    0x58: cb_58, 0x59: cb_59, 0x5a: cb_5a, 0x5b: cb_5b, 0x5c: cb_5c, 0x5d: cb_5d, 0x5e: cb_5e, 0x5f: cb_5f,
    0x60: cb_60, 0x61: cb_61, 0x62: cb_62, 0x63: cb_63, 0x64: cb_64, 0x65: cb_65, 0x66: cb_66, 0x67: cb_67,
    0x68: cb_68, 0x69: cb_69, 0x6a: cb_6a, 0x6b: cb_6b, 0x6c: cb_6c, 0x6d: cb_6d, 0x6e: cb_6e, 0x6f: cb_6f,
    0x70: cb_70, 0x71: cb_71, 0x72: cb_72, 0x73: cb_73, 0x74: cb_74, 0x75: cb_75, 0x76: cb_76, 0x77: cb_77, 
    0x78: cb_78, 0x79: cb_79, 0x7a: cb_7a, 0x7b: cb_7b, 0x7c: cb_7c, 0x7d: cb_7d, 0x7e: cb_7e, 0x7f: cb_7f, 
    0x80: cb_80, 0x81: cb_81, 0x82: cb_82, 0x83: cb_83, 0x84: cb_84, 0x85: cb_85, 0x86: cb_86, 0x87: cb_87, 
    0x88: cb_88, 0x89: cb_89, 0x8a: cb_8a, 0x8b: cb_8b, 0x8c: cb_8c, 0x8d: cb_8d, 0x8e: cb_8e, 0x8f: cb_8f, 
    0x90: cb_90, 0x91: cb_91, 0x92: cb_92, 0x93: cb_93, 0x94: cb_94, 0x95: cb_95, 0x96: cb_96, 0x97: cb_97, 
    0x98: cb_98, 0x99: cb_99, 0x9a: cb_9a, 0x9b: cb_9b, 0x9c: cb_9c, 0x9d: cb_9d, 0x9e: cb_9e, 0x9f: cb_9f,
    0xa0: cb_a0, 0xa1: cb_a1, 0xa2: cb_a2, 0xa3: cb_a3, 0xa4: cb_a4, 0xa5: cb_a5, 0xa6: cb_a6, 0xa7: cb_a7, 
    0xa8: cb_a8, 0xa9: cb_a9, 0xaa: cb_aa, 0xab: cb_ab, 0xac: cb_ac, 0xad: cb_ad, 0xae: cb_ae, 0xaf: cb_af, 
    0xb0: cb_b0, 0xb1: cb_b1, 0xb2: cb_b2, 0xb3: cb_b3, 0xb4: cb_b4, 0xb5: cb_b5, 0xb6: cb_b6, 0xb7: cb_b7, 
    0xb8: cb_b8, 0xb9: cb_b9, 0xba: cb_ba, 0xbb: cb_bb, 0xbc: cb_bc, 0xbd: cb_bd, 0xbe: cb_be, 0xbf: cb_bf, 
    0xc0: cb_c0, 0xc1: cb_c1, 0xc2: cb_c2, 0xc3: cb_c3, 0xc4: cb_c4, 0xc5: cb_c5, 0xc6: cb_c6, 0xc7: cb_c7, 
    0xc8: cb_c8, 0xc9: cb_c9, 0xca: cb_ca, 0xcb: cb_cb, 0xcc: cb_cc, 0xcd: cb_cd, 0xce: cb_ce, 0xcf: cb_cf, 
    0xd0: cb_d0, 0xd1: cb_d1, 0xd2: cb_d2, 0xd3: cb_d3, 0xd4: cb_d4, 0xd5: cb_d5, 0xd6: cb_d6, 0xd7: cb_d7, 
    0xd8: cb_d8, 0xd9: cb_d9, 0xda: cb_da, 0xdb: cb_db, 0xdc: cb_dc, 0xdd: cb_dd, 0xde: cb_de, 0xdf: cb_df, 
    0xe0: cb_e0, 0xe1: cb_e1, 0xe2: cb_e2, 0xe3: cb_e3, 0xe4: cb_e4, 0xe5: cb_e5, 0xe6: cb_e6, 0xe7: cb_e7, 
    0xe8: cb_e8, 0xe9: cb_e9, 0xea: cb_ea, 0xeb: cb_eb, 0xec: cb_ec, 0xed: cb_ed, 0xee: cb_ee, 0xef: cb_ef, 
    0xf0: cb_f0, 0xf1: cb_f1, 0xf2: cb_f2, 0xf3: cb_f3, 0xf4: cb_f4, 0xf5: cb_f5, 0xf6: cb_f6, 0xf7: cb_f7,
    0xf8: cb_f8, 0xf9: cb_f9, 0xfa: cb_fa, 0xfb: cb_fb, 0xfc: cb_fc, 0xfd: cb_fd, 0xfe: cb_fe, 0xff: cb_ff, 
}
