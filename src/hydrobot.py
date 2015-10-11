#!/usr/bin/python
import time
import RPi.GPIO as GPIO


## Settings
pins = [3,5,7,8,10,12,11,13]


## Setup
GPIO.setmode(GPIO.BOARD)
for pin in pins:
  GPIO.setup(pin, GPIO.OUT)


## Functions
def high(pin):
  print('Setting pin %s to high'%(str(pin)))
  GPIO.output(pin,GPIO.LOW)
def low(pin):
  print('Setting pin %s to low'%(str(pin)))
  GPIO.output(pin,GPIO.HIGH)


## Main
for pin in pins:
  low(pin)
while True:
  for pin in pins:
    high(pin)
    time.sleep(1)
    low(pin)
    time.sleep(1)
  time.sleep(5)


## Finish
GPIO.cleanup()
