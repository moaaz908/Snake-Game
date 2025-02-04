import pygame
import random
import math
import sys
from tkinter import *
from tkinter import messagebox
from pygame import mixer
from array import array

WIDTH = 800
HEIGHT = 600
CELL_SIZE = 20
FPS = 15 c

# Initialize Pygame
pygame.init()
def generate_sound(frequency=440, duration=0.1, wave_type='square', volume=0.5):
    sample_rate = 44100
    period = int(sample_rate / frequency)
    amplitude = 2 ** (abs(mixer.get_init()[2]) - 1) - 1
    samples = []
    
    for i in range(int(duration * sample_rate)):
        if wave_type == 'square':
            value = int(amplitude * volume) if (i % period) < (period // 2) else -int(amplitude * volume)
        elif wave_type == 'sine':
            value = int(amplitude * volume * math.sin(2 * math.pi * frequency * i / sample_rate))
        samples.append(value)
    
    return pygame.mixer.Sound(array('h', samples))

# تهيئة الأصوات
mixer.init(frequency=44100, size=-16, channels=1)
eat_sound = generate_sound(784, 0.1, 'square', 0.3)
level_up_sound = generate_sound(1568, 0.3, 'sine', 0.5)
game_over_sound = generate_sound(220, 0.8, 'square', 0.4)

# -----------------------------------------------------------------
# كل ما يلي يبقى كما هو بدون أي تعديلات
# -----------------------------------------------------------------
