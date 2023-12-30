level = 0

l = open('log.txt', 'w')


def debug_log(l, log, b, register):
    
    log.write('a:')
    log.write(str(hex(register['a'])))
    log.write(' ')
    log.write('b:')
    log.write(str(hex(register['b'])))
    log.write(' ')
    log.write('c:')
    log.write(str(hex(register['c'])))
    log.write(' ')
    log.write('d:')
    log.write(str(hex(register['d'])))
    log.write(' ')
    log.write('e:')
    log.write(str(hex(register['e'])))
    log.write(' ')
    log.write('f:')
    log.write(str(hex(register['f'])))
    log.write(' ')
    log.write('h:')
    log.write(str(hex(register['h'])))
    log.write(' ')
    log.write('l:')
    log.write(str(hex(register['l'])))
    log.write(' ')
    log.write('pc:')
    log.write(str(hex(register['pc'])))
    log.write(' ')
    log.write('sp:')
    log.write(str(hex(register['sp'])))
    log.write(' ')
    log.write('clock:')
    log.write(str(register['clock']))
    log.write('\n')
    for i in range(l):
        log.write(hex(b[i]))
        log.write(' ')
    log.write('\n')


