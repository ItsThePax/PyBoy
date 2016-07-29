# PyBoy
Gameboy emulator in python.

A fun project to work on in my free time, still far from finished.  I'm using this to teach myself how to code, hence weird naming schemes and formatting.

Requires Pygame 1.9.2, runs in 2.7 and 3.5

Current implementation is slow, is being used for prototyping. Currently in the process of rewriting in C with libSDL2

Current status as of 26JUL2016:
Display:
    background:
        - fully functional
    sprites:
        - sprites 8*8 with priority 1 working
        - sprites with priority 0 not implemented
        - sprites 16*8 not implemented
    window:
        - not yet implemented
        
Memory controllers:
    -32k roms functional
    -all other MC units not yet implemented
    
CPU instructions:
    -adding instructions as I go, many are buggy, especially with flag handeling.  Planning to do major rewrite of all opcode functions in the future
    
Sound:
    -not implemented yet
    
Controls:
    -very buggy
    
