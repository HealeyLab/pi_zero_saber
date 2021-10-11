# -*- coding: utf-8 -*-
"""
Created on Sun Oct  3 14:24:56 2021

@author: Healey
"""


"""set up ADXL345"""

3v3 pin to Rpi GPIO1
GND pin to Rpi GPIO6
SDA pin to Rpi GPIO3
SCL pin to Rpi GPIO5


cd ~
sudo pip3 install --upgrade adafruit-python-shell
wget https://raw.githubusercontent.com/adafruit/Raspberry-Pi-Installer-Scripts/master/raspi-blinka.py
sudo python3 raspi-blinka.py

sudo pip3 install adafruit-circuitpython-adxl34x

"""test ADXL345"""

import time
import board
import adafruit_adxl34x

i2c = board.I2C()  # uses board.SCL and board.SDA

# For ADXL345
accelerometer = adafruit_adxl34x.ADXL345(i2c)

"""print accel readings"""
while True:
    print("%f %f %f" % accelerometer.acceleration)
    time.sleep(0.2)
    
    

"""to just test button"""

import board
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BOARD)

buttonPin = 36
GPIO.setup(buttonPin, GPIO.IN, pull_up_down=GPIO.PUD_UP) #using an internal pull-up resistor in the Pi


while True:
    buttonState = GPIO.input(buttonPin)
    
    if buttonState == False:
        
        print("pressed!")
    else:
        print("listening...")
        

"""make sure bonnet is passing sound"""

speaker-test -c2
    


"""run button with bonnet hat"""

"""one button lead pinned to GND, the other pinned to GPIO26(pin 37)"""

import time
import board
from board import *
from digitalio import DigitalInOut, Direction, Pull

button = DigitalInOut(board.D26)
button.direction = Direction.INPUT
button.pull = Pull.UP

while True:
  if not button.value:
    print("Button pressed")
  time.sleep(0.01)
    
  
"""set up dotstar black 30 led strip"""

import board
import adafruit_dotstar as dotstar
dots = dotstar.DotStar(board.D22, board.D27, 30, auto_write = True, brightness=0.2)

dots.fill((0, 255, 0))

"""for the bonnet"""
dots = dotstar.DotStar(board.D6, board.D5, 3, brightness=0.2)
dots[0] = (255, 0, 0)


"""button press activates accell and lights"""

import board
import time
import adafruit_dotstar as dotstar
import adafruit_adxl34x

from board import *
from digitalio import DigitalInOut, Direction, Pull

button = DigitalInOut(board.D26)
button.direction = Direction.INPUT
button.pull = Pull.UP

dots = dotstar.DotStar(board.D6, board.D5, 30, brightness=0.2)

i2c = board.I2C()  # uses board.SCL and board.SDA

# For ADXL345
accelerometer = adafruit_adxl34x.ADXL345(i2c)

while True:
  if not button.value:
    dots.fill((0, 255, 0))
    print("Button pressed") 
    print("%f %f %f" % accelerometer.acceleration)
    time.sleep(4)
  time.sleep(.1)
  