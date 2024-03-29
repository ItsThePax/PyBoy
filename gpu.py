import pygame
import cpu
import time
import os
import debug

frame = 0
old_clock = 0
new_clock = 0
line = 0
color = {0x3: ((0, 0, 0)), 0x2: ((100, 100, 100)), 0x1: ((180, 180, 180)), 0x0: ((240, 240, 240))}
t0 = 0
t1 = 0
t2 = 0
t3 = 0
unique_addr = []


def get_controls():
    events = pygame.event.get()
    for event in events:
        if event.type == 768:
            if event.key == 97:
                cpu.mmu.a = 1
            elif event.key == 115:
                cpu.mmu.b = 1
            elif event.key == 1073741904:
                cpu.mmu.left = 1
            elif event.key == 1073741906:
                cpu.mmu.up = 1
            elif event.key == 1073741905:
                cpu.mmu.down = 1
            elif event.key == 1073741903:
                cpu.mmu.right = 1
            elif event.key == 13:
                cpu.mmu.start = 1
            elif event.key == 32:
                cpu.mmu.select = 1
            cpu.mmu.memory[0xff0f] |= 0x10
        elif event.type == 769:
            if event.key == 97:
                cpu.mmu.a = 0
            elif event.key == 115:
                cpu.mmu.b = 0
            elif event.key == 1073741904:
                cpu.mmu.left = 0
            elif event.key == 1073741906:
                cpu.mmu.up = 0
            elif event.key == 1073741905:
                cpu.mmu.down = 0
            elif event.key == 1073741903:
                cpu.mmu.right = 0
            elif event.key == 13:
                cpu.mmu.start = 0
            elif event.key == 32:
                cpu.mmu.select = 0
                

def draw_screen(s):
    t0 = time.time()
    scrolly = cpu.mmu.memory[0xff42]
    scrollx = cpu.mmu.memory[0xff43]
    winy = cpu.mmu.memory[0xff4a]
    winx = cpu.mmu.memory[0xff4b]
    bg_pallet = cpu.mmu.memory[0xff47]
    spallet0 = cpu.mmu.memory[0xff48]
    spallet1 = cpu.mmu.memory[0xff49]                                                                  
    #BG and window
    if cpu.mmu.memory[0xff40] & 1:
        tile_data_loc = 0x8800
        tile_map_loc = 0x9800
        window_map_loc = 0x9800
        if cpu.mmu.memory[0xff40] & 0x10:
            tile_data_loc = 0x8000
        if cpu.mmu.memory[0xff40] & 0x8:
            tile_map_loc = 0x9c00
        if cpu.mmu.memory[0xff40] & 0x40:
            window_map_loc = 0x9c00
        #window
        if cpu.mmu.memory[0xff40] & 0x20:
            for j in range(winy, 144):
                tile_y = int(((scrolly + j) % 256) / 8)
                pixel_y = (scrolly + j) % 8
                pixel2_y = pixel_y * 2
                for i in range((winx - 7), 160):
                    pixel_x = (scrollx + i) % 8
                    tile_x = int(((scrollx + i) % 256) / 8)
                    tile = (tile_y * 32) + tile_x
                    if tile_data_loc == 0x8800:
                        temp = cpu.mmu.memory[window_map_loc + tile]
                        if temp > 127:
                            temp -= 0x100
                        tile_loc = 0x9000 + (temp * 0x10)
                    else:
                        tile_loc = tile_data_loc + (cpu.mmu.memory[tile_map_loc + tile] * 0x10)
                    byte_h = cpu.mmu.memory[tile_loc + pixel2_y]
                    byte_l = cpu.mmu.memory[tile_loc + pixel2_y + 1]
                    raw_u = (byte_h >> (7 - pixel_x)) & 1
                    raw_l = (byte_l >> (7 - pixel_x) & 1) << 1
                    raw_color = raw_u | raw_l 
                    actual_color = (bg_pallet >> (raw_color * 2)) & 0x3
                    s[i][j] = color[actual_color]
                    
        else:
            winy = 144
            winx = 167
    #bg
        for j in range(winy):
            tile_y = int(((scrolly + j) % 256) / 8)
            pixel_y = (scrolly + j) % 8
            pixel2_y = pixel_y * 2
            for i in range(winx - 7):
                pixel_x = (scrollx + i) % 8
                tile_x = int(((scrollx + i) % 256) / 8)
                tile = (tile_y * 32) + tile_x
                if tile_data_loc == 0x8800:
                    temp = cpu.mmu.memory[tile_map_loc + tile]
                    if temp > 127:
                        temp -= 0x100
                    tile_loc = 0x9000 + (temp * 0x10)
                else:
                    tile_loc = tile_data_loc + (cpu.mmu.memory[tile_map_loc + tile] * 0x10)
                byte_h = cpu.mmu.memory[tile_loc + pixel2_y]
                byte_l = cpu.mmu.memory[tile_loc + pixel2_y + 1]
                raw_u = (byte_h >> (7 - pixel_x)) & 1
                raw_l = (byte_l >> (7 - pixel_x) & 1) << 1
                raw_color = raw_u | raw_l 
                actual_color = (bg_pallet >> (raw_color * 2)) & 0x3
                s[i][j] = color[actual_color]
                
                
    #Sprites with priority > 0 
    if cpu.mmu.memory[0xff40] & (1 << 1): #sprites enabled
        if cpu.mmu.memory[0xff40] & (1 << 2):
            #render sprites 8*16 mode
            pass
        else:
            #render sprites 8*8 mode
            for i in range(40):
                offset = i * 4
                oam_loc = 0xfe00 + offset
                if ~(cpu.mmu.memory[oam_loc + 3] & (1 << 7)):
                    pixel_x = 0
                    pixel_y = 0
                    y = cpu.mmu.memory[oam_loc]
                    x = cpu.mmu.memory[oam_loc + 1]
                    sprite_pattern = cpu.mmu.memory[oam_loc + 2]
                    sprite_data = 0x8000 + (sprite_pattern * 0x10)
                    if cpu.mmu.memory[oam_loc + 3] & (1 << 4):
                        pallet = spallet1
                    else:
                        pallet = spallet0
                    if cpu.mmu.memory[oam_loc + 3] & (1 << 6): 
                        if cpu.mmu.memory[oam_loc + 3] & (1 << 5): # x flip and y flip
                            for pixel_y in range (8):
                                y_pos = y + pixel_y + scrolly - 16
                                if 0 <= y_pos < 144:
                                    for pixel_x in range (8):
                                        x_pos = x + pixel_x + scrollx - 8
                                        if 0 <= x_pos < 160:
                                            raw_color = ((cpu.mmu.memory[sprite_data + ((7 - pixel_y) * 2)] >> (pixel_x)) & 1) |\
                                                        (((cpu.mmu.memory[sprite_data + (((7 - pixel_y) * 2) + 1)] >> (pixel_x)) & 1) << 1)
                                            actual_color = (pallet >> (raw_color * 2)) & 0x3
                                            if actual_color != 0:
                                                s[x_pos][y_pos] = color[actual_color]
                                            
                        else:   #y flip
                            for pixel_y in range (8):
                                y_pos = y + pixel_y + scrolly - 16
                                if 0 <= y_pos < 144:
                                    for pixel_x in range (8):
                                        x_pos = x + pixel_x + scrollx - 8
                                        if 0 <= x_pos < 160:
                                            raw_color = ((cpu.mmu.memory[sprite_data + ((7 - pixel_y) * 2)] >> (7 - pixel_x)) & 1) |\
                                                        (((cpu.mmu.memory[sprite_data + (((7 - pixel_y) * 2) + 1)] >> (7 - pixel_x)) & 1) << 1)
                                            actual_color = (pallet >> (raw_color * 2)) & 0x3
                                            if actual_color != 0:
                                                s[x_pos][y_pos] = color[actual_color]
                                            
                    else: #x flip
                        if cpu.mmu.memory[oam_loc + 3] & (1 << 5):
                            for pixel_y in range (8):
                                y_pos = y + pixel_y + scrolly - 16
                                if 0 <= y_pos < 144:
                                    for pixel_x in range (8):
                                        x_pos = x + pixel_x + scrollx - 8
                                        if 0 <= x_pos < 160:
                                            raw_color = ((cpu.mmu.memory[sprite_data + (pixel_y * 2)] >> (pixel_x)) & 1) |\
                                                        (((cpu.mmu.memory[sprite_data + ((pixel_y * 2) + 1)] >> (pixel_x)) & 1) << 1)
                                            actual_color = (pallet >> (raw_color * 2)) & 0x3
                                            if actual_color != 0:
                                                s[x_pos][y_pos] = color[actual_color]
                                            
                        else: # no flip
                            for pixel_y in range (8):
                                y_pos = y + pixel_y + scrolly - 16
                                if 0 <= y_pos < 144:
                                    for pixel_x in range (8):
                                        x_pos = x + pixel_x + scrollx - 8
                                        if 0 <= x_pos < 160:
                                            if cpu.mmu.memory[oam_loc + 3] & (1 << 7) and s[x_pos][y_pos] != 0:
                                                raw_color = ((cpu.mmu.memory[sprite_data + (pixel_y * 2)] >> (7 - pixel_x)) & 1) |\
                                                            (((cpu.mmu.memory[sprite_data + ((pixel_y * 2) + 1)] >> (7 - pixel_x)) & 1) << 1)
                                                if raw_color != 0:
                                                    actual_color = (pallet >> (raw_color * 2)) & 0x3
                                                    s[x_pos][y_pos] = color[actual_color]
                                            elif cpu.mmu.memory[oam_loc + 3] & (1 << 7) == 0:
                                                raw_color = ((cpu.mmu.memory[sprite_data + (pixel_y * 2)] >> (7 - pixel_x)) & 1) |\
                                                            (((cpu.mmu.memory[sprite_data + ((pixel_y * 2) + 1)] >> (7 - pixel_x)) & 1) << 1)
                                                if raw_color != 0:
                                                    actual_color = (pallet >> (raw_color * 2)) & 0x3
                                                    s[x_pos][y_pos] = color[actual_color] 
                                                      
        #TODO sprites priority 0
                    



  
def do_gpu(screen, reg):
    global old_clock, new_clock, t0, t1, t2, t3, frame
    new_clock = reg['clock']
    cpu.mmu.memory[0xff44] = int(new_clock / 456)
    if cpu.mmu.memory[0xff40] & 0x80:
        if cpu.mmu.memory[0xff44] < 144:
            if new_clock % 456 < 80:
                if cpu.mmu.memory[0xff41] & 0x3 != 2:
                    cpu.mmu.memory[0xff41] &= 0xfc
                    cpu.mmu.memory[0xff41] |= 2
            elif 80 <= new_clock % 456 < 252:
                if cpu.mmu.memory[0xff41] & 0x3 != 3:
                    cpu.mmu.memory[0xff41] &= 0xfc
                    cpu.mmu.memory[0xff41] |= 3
            elif new_clock % 456 >= 252:
                if cpu.mmu.memory[0xff41] & 0x3 != 0:
                    cpu.mmu.memory[0xff41] &= 0xfc
                    
        else :
            if cpu.mmu.memory[0xff41] & 0x3 != 1:
                cpu.mmu.memory[0xff41] &= 0xfc
                cpu.mmu.memory[0xff41] |= 1
                sb = pygame.PixelArray(screen)
                if cpu.mmu.memory[0xff40] & (1 << 7):
                    draw_screen(sb)
                    del sb
                pygame.display.update()
                t2 = time.time()
                #try:
                #    print(1/(t2 - t3))
                #except:
                #    pass
                t3 = time.time()
                cpu.mmu.memory[0xff0f] |= 0x1
                get_controls()
                frame += 1          
    else:
        reg['clock'] = 0
        cpu.mmu.memory[0xff41] = 0x3
            
            
    
