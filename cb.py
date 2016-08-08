import mmu


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
    hl = register['h'] << 8 | register['e']
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


def cb_33(register):
    temp = register['e'] & 0xf
    register['e'] <<= 4
    register['e'] |= temp
    register['e'] &= 0xff
    register['f'] = 0
    if register['e'] == 0:
        register['f'] = 0x80
        

def cb_37(register):
    temp = register['a'] & 0xf0
    temp >>= 4
    register['a'] <<= 4
    register['a'] |= temp
    register['a'] &= 0xff
    register['f'] = 0
    if register['a'] == 0:
        register['f'] = 0x80

        
def cb_3f(register):
    if register['a'] & 0x80:
        register['f'] = 0x10
    else:
        register['f'] = 0
    register['a'] >>= 1
    if register['a'] == 0:
        register['f'] |= 0x80
        

def cb_40(register):
    if register['b'] & 1:
        register['f'] &= ~(1 << 7)
    else:
        register['f'] |= (1 << 7)
    register['f'] &= ~(1 << 6)
    register['f'] |= (1 << 5)

def cb_41(register):
    if register['c'] & 1:
        register['f'] &= ~(1 << 7)
    else:
        register['f'] |= (1 << 7)
    register['f'] &= ~(1 << 6)
    register['f'] |= (1 << 5)


def cb_42(register):
    if register['d'] & 1:
        register['f'] &= ~(1 << 7)
    else:
        register['f'] |= (1 << 7)
    register['f'] &= ~(1 << 6)
    register['f'] |= (1 << 5)


def cb_46(register):
    hl = register['h'] << 8 | register['l']
    value = mmu.read(hl)
    if value & 1:
        register['f'] &= ~(1 << 7)
    else:
        register['f'] |= (1 << 7)
    register['f'] &= ~(1 << 6)
    register['f'] |= (1 << 5)


def cb_47(register):
    if register['a'] & 1:
        register['f'] &= ~(1 << 7)
    else:
        register['f'] |= (1 << 7)
    register['f'] &= ~(1 << 6)
    register['f'] |= (1 << 5)
    

def cb_48(register):
    if register['b'] & (1 << 1):
        register['f'] &= ~(1 << 7)
    else:
        register['f'] |= (1 << 7)
    register['f'] &= ~(1 << 6)
    register['f'] |= (1 << 5)


def cb_4f(register):
    if register['a'] & 2:
        register['f'] &= ~(1 << 7)
    else:
        register['f'] |= (1 << 7)
    register['f'] &= ~(1 << 6)
    register['f'] |= (1 << 5)


def cb_50(register):
    if register['b'] & (1 << 2):
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


def cb_68(register):
    if register['b'] & (1 << 4):
        register['f'] &= ~(1 << 7)
    else:
        register['f'] |= (1 << 7)
    register['f'] &= ~(1 << 6)
    register['f'] |= (1 << 5)


def cb_69(register):
    if register['c'] & (1 << 5):
        register['f'] &= ~(1 << 7)
    else:
        register['f'] |= (1 << 7)
    register['f'] &= ~(1 << 6)
    register['f'] |= (1 << 5)


def cb_6f(register):
    if register['a'] & (1 << 5):
        register['f'] &= ~(1 << 7)
    else:
        register['f'] |= (1 << 7)
    register['f'] &= ~(1 << 6)
    register['f'] |= (1 << 5)


def cb_70(register):
    if register['b'] & (1 << 6):
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
    if register['b'] & (1 << 7):
        register['f'] &= ~(1 << 7)
    else:
        register['f'] |= (1 << 7)
    register['f'] &= ~(1 << 6)
    register['f'] |= (1 << 5)


def cb_7c(register):
    if register['h'] & (1 << 7):
        register['f'] &= ~(1 << 7)
    else:
        register['f'] |= (1 << 7)
    register['f'] &= ~(1 << 6)
    register['f'] |= (1 << 5)


def cb_7e(register):
    hl = register['h'] << 8 | register['l']
    value = mmu.read(hl)
    if value & (1 << 7):
        register['f'] &= ~(1 << 7)
    else:
        register['f'] |= (1 << 7)
    register['f'] &= ~(1 << 6)
    register['f'] |= (1 << 5)


def cb_7f(register):
    if register['a'] & (1 << 7):
        register['f'] &= ~(1 << 7)
    else:
        register['f'] |= (1 << 7)
    register['f'] &= ~(1 << 6)
    register['f'] |= (1 << 5)


def cb_86(register):
    hl = register['h'] << 8 | register['l']
    temp = mmu.read(hl)
    temp &= 0xfe
    mmu.write(hl, temp)
    

def cb_87(register):
    register['a'] &= 0xfe


def cb_8f(register):
    register['a'] &= 0xfd


def cb_97(register):
    register['a'] &= 0xfb


def cb_9e(register):
    hl = register['h'] << 8 | register['e']
    temp = mmu.read(hl)
    temp &= 0xf7
    mmu.write(hl, temp)


def cb_a6(register):
    register['b'] &= 0xef

    
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
    

def cb_be(register):
    hl = register['h'] << 8 | register['l']
    temp = mmu.read(hl)
    temp &= 0x7f
    mmu.write(hl, temp)


def cb_d6(register):
    hl = register['h'] << 8 | register['l']
    temp = mmu.read(hl)
    temp |= 0x2
    mmu.write(hl, temp)


def cb_de(register):
    hl = register['h'] << 8 | register['l']
    temp = mmu.read(hl)
    temp |= 0x8
    mmu.write(hl, temp)


def cb_ed(register):
    register['l'] |= 0x20


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
    hl = register['h'] << 8 | register['e']
    temp = mmu.read(hl)
    temp |= 0x80
    mmu.write(hl, temp)


def cb_ff(register):
    register['a'] |= 0x80


cb_lookup = {
    0x10: cb_10, 0x11: cb_11, 0x12: cb_12, 0x13: cb_13, 0x14: cb_14, 0x15: cb_15, 0x16: cb_16, 0x17: cb_17,
    0x1a: cb_1a, 0x1b: cb_1b,
    0x20: cb_20, 0x21: cb_21, 0x22: cb_22, 0x23: cb_23, 0x24: cb_24, 0x25: cb_25, 0x26: cb_26, 0x27: cb_27, 
    0x27: cb_27,
    0x33: cb_33,
    0x37: cb_37, 0x3f: cb_3f,
    0x40: cb_40, 0x41: cb_41, 0x42: cb_42, 0x46: cb_46, 0x47: cb_47,
    0x48: cb_48, 0x4f: cb_4f, 
    0x50: cb_50, 0x57: cb_57,
    0x58: cb_58, 0x5f: cb_5f,
    0x60: cb_60, 0x61: cb_61,
    0x68: cb_68, 0x69: cb_69, 0x6f: cb_6f,
    0x70: cb_70, 
    0x77: cb_77, 0x78: cb_78, 0x7c: cb_7c, 0x7e: cb_7e, 0x7f: cb_7f, 
    0x86: cb_86, 0x87: cb_87,
    0x8f: cb_8f,
    0x97: cb_97,
    0x9e: cb_9e,
    0xa6: cb_a6,
    0xa8: cb_a8, 0xa9: cb_a9, 0xaa: cb_aa, 0xab: cb_ab, 0xac: cb_ac, 0xad: cb_ad, 0xae: cb_ae, 0xaf: cb_af, 
    0xbe: cb_be,
    0xd6: cb_d6,
    0xde: cb_de,
    0xed: cb_ed,
    0xf0: cb_f0, 0xf1: cb_f1, 0xf2: cb_f2, 0xf3: cb_f3, 0xf4: cb_f4, 0xf5: cb_f5, 0xf6: cb_f6, 0xf7: cb_f7,
    0xf8: cb_f8, 0xf9: cb_f9, 0xfa: cb_fa, 0xfb: cb_fb, 0xfc: cb_fc, 0xfd: cb_fd, 0xfe: cb_fe, 0xff: cb_ff, 
}
