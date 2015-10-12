#!/usr/bin/python
import time
import yaml
import redis
import threading
import RPi.GPIO as GPIO
from cPickle import loads as load
from cPickle import dumps as dump


## Settings
with open('/etc/hydrobot/settings.yml','r') as f:
  settings = yaml.load(f.read())


## Node Role
def node():
  r = redis.StrictRedis(host=settings['hub']['host'],port=settings['hub']['port'])
  r.set('node::'+settings['node']['id'],dump(settings['node']))
  while True:
    root_pattern = 'output::'+settings['node']['id']+'::'
    current_outputs = r.keys(root_pattern+'*')
    for key in current_outputs:
      state = r.get(key)
      pin = str(key.replace(root_pattern,''))
    time.sleep(settings['node']['poll'])


##-> Main <-##

if 'node' in settings['role']:

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

  ## Start
  #GPIO.cleanup()
  #for pin in pins:
  #  low(pin)
  thread = threading.Thread(target=node)
  thread.start()

