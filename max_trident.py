# -*- coding: utf-8 -*-
"""
Created on Sat Oct  2 16:36:13 2021

@author: Healey
"""

"""Inspired by TopShed Pi Saber
https://github.com/topshed/Pi-Saber/blob/master/PiSaber.py

in combination with Adafruit Propmaker Light Saber Code

https://github.com/adafruit/Adafruit_Learning_System_Guides/blob/main/PropMaker_Lightsaber/code.py

But made for pizero_W
"""
# pylint: disable=bare-except

import time
import math
import gc
from digitalio import DigitalInOut, Direction, Pull
#import audioio
#import audiocore
#import busio
import board
#import neopixel
#import adafruit_lis3dh
import adafruit_dotstar as dotstar
import adafruit_adxl34x
from adafruit_led_animation.sequence import AnimationSequence
import adafruit_led_animation.animation.comet as comet_animation
import adafruit_led_animation.color as color

from board import *
import pygame as pg

# CUSTOMIZE YOUR COLOR HERE:
# (red, green, blue) -- each 0 (off) to 255 (brightest)
# COLOR = (255, 0, 0)  # red
# COLOR = (100, 0, 255)  # purple
# COLOR = (0, 100, 255) #cyan
COLOR = (0, 0, 255)  #blue
#COLOR = (0, 50, 255)  #greenblue

# CUSTOMIZE SENSITIVITY HERE: smaller numbers = more sensitive to motion
HIT_THRESHOLD = 350 # 250
SWING_THRESHOLD = 125

#Customize speaker voluem
SOUND_VOLUME = 0.2       #0.01 lowest, 0.99 is highest

NUM_PIXELS = 30
# NUM_PIXELS = 85
DOTS_PIN = board.D5
CLOCK_PIN = board.D6
POWER_PIN = board.D10
SWITCH_PIN = board.D26

enable = DigitalInOut(POWER_PIN)
enable.direction = Direction.OUTPUT
enable.value =False

# red_led = DigitalInOut(board.D11)
# red_led.direction = Direction.OUTPUT
# green_led = DigitalInOut(board.D12)
# green_led.direction = Direction.OUTPUT
# blue_led = DigitalInOut(board.D13)
# blue_led.direction = Direction.OUTPUT

#audio = audioio.AudioOut(board.A0)     # Speaker
pg.mixer.init()                         #speaker audio mixer initialize
mode = 0                               # Initial mode = OFF

strip = dotstar.DotStar(CLOCK_PIN, DOTS_PIN, 60, brightness=0.2, auto_write=False)
strip.fill(0)                          # NeoPixels off ASAP on startup
strip.show()

comet = comet_animation.Comet(strip, .005, color.CYAN, tail_length = 10, bounce=True)


switch = DigitalInOut(SWITCH_PIN)
switch.direction = Direction.INPUT
switch.pull = Pull.UP

time.sleep(0.1)

i2c = board.I2C()  # uses board.SCL and board.SDA
accel = adafruit_adxl34x.ADXL345(i2c)
accel.range = accel.range

# # Set up accelerometer on I2C bus, 4G range:
# i2c = busio.I2C(board.SCL, board.SDA)
# accel = adafruit_lis3dh.LIS3DH_I2C(i2c)
# accel.range = adafruit_lis3dh.RANGE_4_G

# "Idle" color is 1/4 brightness, "swinging" color is full brightness...
COLOR_IDLE = (int(COLOR[0] / 1), int(COLOR[1] / 1), int(COLOR[2] / 1))
COLOR_SWING = COLOR
COLOR_HIT = (255, 255, 255)  # "hit" color is white

def play_wav(name, loop=False):
    """
    Play a WAV file in the 'sounds' directory.
    @param name: partial file name string, complete name will be built around
                 this, e.g. passing 'foo' will play file 'sounds/foo.wav'.
    @param loop: if True, sound will repeat indefinitely (until interrupted
                 by another sound).
    """
    print("playing", name)
    try:
        soundtemp = pg.mixer.Sound('./sounds/' + name + '.wav')        
        soundtemp.set_volume(SOUND_VOLUME)
        if loop == True:
            
            soundtemp.play(loops = -1)   #pygame plays sound indefinitely
        else:
            soundtemp.play(loops = 0)    #pygame plays sound once
        #wave_file = open('sounds/' + name + '.wav', 'rb')
        #wave = audiocore.WaveFile(wave_file)
        #audio.play(wave, loop=loop)
    except:
        return

def power(sound, duration, reverse):
    """
    Animate NeoPixels with accompanying sound effect for power on / off.
    @param sound:    sound name (similar format to play_wav() above)
    @param duration: estimated duration of sound, in seconds (>0.0)
    @param reverse:  if True, do power-off effect (reverses animation)
    """
    if reverse:
        prev = NUM_PIXELS
    else:
        prev = 0
    gc.collect()                   # Tidy up RAM now so animation's smoother
    start_time = time.monotonic()  # Save audio start time
    play_wav(sound)
    while True:
        elapsed = time.monotonic() - start_time  # Time spent playing sound
        if elapsed > duration:                   # Past sound duration?
            break                                # Stop animating
        fraction = elapsed / duration            # Animation time, 0.0 to 1.0
        if reverse:
            fraction = 1.0 - fraction            # 1.0 to 0.0 if reverse
        fraction = math.pow(fraction, 0.5)       # Apply nonlinear curve
        threshold = int(NUM_PIXELS * fraction + 0.5)
        num = threshold - prev # Number of pixels to light on this pass
        if num != 0:
            if reverse:
                strip[threshold:prev] = [0] * -num
            else:
                strip[prev:threshold] = [COLOR_IDLE] * num
            strip.show()
            # NeoPixel writes throw off time.monotonic() ever so slightly
            # because interrupts are disabled during the transfer.
            # We can compensate somewhat by adjusting the start time
            # back by 30 microseconds per pixel.
            start_time -= NUM_PIXELS * 0.00003
            prev = threshold

    if reverse:
        strip.fill(0)                            # At end, ensure strip is off
    else:
        strip.fill(COLOR_IDLE)                   # or all pixels set on
    strip.show()
    #while audio.playing:                         # Wait until audio done
        #pass
    #while pg.mixer.get_busy():
        #pass
    
def mix(color_1, color_2, weight_2):
    """
    Blend between two colors with a given ratio.
    @param color_1:  first color, as an (r,g,b) tuple
    @param color_2:  second color, as an (r,g,b) tuple
    @param weight_2: Blend weight (ratio) of second color, 0.0 to 1.0
    @return: (r,g,b) tuple, blended color
    """
    if weight_2 < 0.0:
        weight_2 = 0.0
    elif weight_2 > 1.0:
        weight_2 = 1.0
    weight_1 = 1.0 - weight_2
    return (int(color_1[0] * weight_1 + color_2[0] * weight_2),
            int(color_1[1] * weight_1 + color_2[1] * weight_2),
            int(color_1[2] * weight_1 + color_2[2] * weight_2))

# Main program loop, repeats indefinitely
while True:

    #red_led.value = True

    if not switch.value:                    # button pressed?
        if mode == 0:                       # If currently off...
            enable.value = True
            power('onthunder', 1.7, False)         # Power up!
            play_wav('waveidle', loop=True)     # Play background hum sound
            mode = 1                        # ON (idle) mode now
        else:                               # else is currently on...
            power('off', 1.15, True)        # Power down
            mode = 0                        # OFF mode now
            pg.mixer.stop()                 # make sure idle hum is off
            enable.value = False
        while not switch.value:             # Wait for button release
            time.sleep(0.2)                 # to avoid repeated triggering

    elif mode >= 1:                         # If not OFF mode...
        x, y, z = accel.acceleration # Read accelerometer
        accel_total = x * x + z * z
        # (Y axis isn't needed for this, assuming Hallowing is mounted
        # sideways to stick.  Also, square root isn't needed, since we're
        # just comparing thresholds...use squared values instead, save math.)
        if accel_total > HIT_THRESHOLD:   # Large acceleration = HIT
            TRIGGER_TIME = time.monotonic() # Save initial time of hit
            play_wav('wavecrash')                 # Start playing 'hit' sound
            #COLOR_ACTIVE = COLOR_HIT        # Set color to fade from
            comet.animate()
            mode = 3                        # HIT mode
        elif mode == 1 and accel_total > SWING_THRESHOLD: # Mild = SWING
            TRIGGER_TIME = time.monotonic() # Save initial time of swing
            play_wav('swing')               # Start playing 'swing' sound
            COLOR_ACTIVE = COLOR_SWING      # Set color to fade from
            mode = 1                        # SWING mode, Adafruit originally set this to 2
        elif mode > 1:                      # If in SWING or HIT mode...
            if pg.mixer.get_busy():               # And sound currently playing... (for Adafruit version was 'if audio.playing:')
                blend = time.monotonic() - TRIGGER_TIME # Time since triggered
                if mode == 2:               # If SWING,
                    blend = abs(0.5 - blend) * 2.0 # ramp up, down
                strip.fill(mix(COLOR_ACTIVE, COLOR_IDLE, blend))
                strip.show()
            else:                           # No sound now, but still MODE > 1
                play_wav('waveidle', loop=True) # Resume background hum
                strip.fill(COLOR_IDLE)      # Set to idle color
                strip.show()
                mode = 1                    # IDLE mode now
