import pygame
import sys
import pyboy_cpu

biosFile = "DMG_ROM.bin"
cartridgeFile = "tetris.gb"


def main(biosFile,  cartridgeFile):
    a = pyboy_cpu.Cpu (biosFile,  cartridgeFile)


def create(biosFile,  cartridgeFile):
    return pyboy_cpu.Cpu (biosFile,  cartridgeFile)

def cd():
    return pyboy_cpu.Cpu ("DMG_ROM.bin",  "tetris.gb")


if __name__ == "__main__":
   sys.exit(main(biosFile, cartridgeFile))   
