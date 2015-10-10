#!/usr/bin/python
import time
import RPi.GPIO as GPIO


## Settings
pins = [3,5,7,8,10,12,11,13]


## Setup
GPIO.setmode(GPIO.BOARD)
GPIO.setup(11, GPIO.OUT)


## Functions
def high(pin):  
  GPIO.output(pin,GPIO.HIGH)  
def low(pin):
  GPIO.output(pin,GPIO.LOW)  


## Main
while True:
  for pin in pins:
    high(pin)
    time.sleep(1)
    low(pin)
    time.sleep(1)
  time.sleep(5)


## Finish
GPIO.cleanup()
