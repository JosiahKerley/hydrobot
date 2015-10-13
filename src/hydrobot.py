#!/usr/bin/python
import sys
import time
import yaml
import json
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
  root_pattern = 'output::'+settings['node']['id']+'::'
  r = redis.StrictRedis(host=settings['hub']['host'],port=settings['hub']['port'])
  r.set('node::'+settings['node']['id'],dump(settings['node']))
  pins = []
  for i in settings['node']['pins']:
    pins.append(int(i.keys()[0]))
  for i in pins:
    print root_pattern+str(i)
    if r.get(root_pattern+str(i)) == None:
      r.set(root_pattern+str(i),'low')
  while True:
    current_outputs = r.keys(root_pattern+'*')
    for key in current_outputs:
      print(key)
      state = r.get(key)
      pin = str(key.replace(root_pattern,''))
      if state == 'low':
        try: low(pin)
        except: print('Error setting %s'%(str(pin)))
      elif state == 'high':
        try: high(pin)
        except: print('Error setting %s'%(str(pin)))
    time.sleep(settings['node']['poll'])



##-> Main <-##
if '--daemon' in sys.argv:
  if 'node' in settings['role']:

    ## Setup
    try: GPIO.cleanup()
    except: pass
    GPIO.setmode(GPIO.BOARD)
    pins = []
    for i in settings['node']['pins']:
      v = int(i.keys()[0])
      print(v)
      pins.append(v)
    for pin in pins:
      GPIO.setup(pin, GPIO.OUT)

    ## Functions
    def high(pin):
      print('Setting pin %s to high'%(str(pin)))
      GPIO.output(int(pin),GPIO.LOW)
    def low(pin):
      print('Setting pin %s to low'%(str(pin)))
      GPIO.output(int(pin),GPIO.HIGH)

    ## Start
    for pin in pins:
      low(pin)
    thread = threading.Thread(target=node)
    thread.start()

  if 'hub' in settings['role']:
    r = redis.StrictRedis(host=settings['hub']['host'],port=settings['hub']['port'])
    from flask import Flask
    app = Flask(__name__)



    ## Getters
    def get_nodes():
      """ Returns dict of nodes registered """
      nodes = {}
      for n in r.keys('node::*'):
        node = n.replace('node::','')
        data = {}
        data = dict(data.items() + (load(r.get(n))).items())
        nodes[node] = data
      return(nodes)


    def get_outputs():
      """ Returns dict of outputs """
      outputs = {}                                                                                                                                                              
      node_outputs = {}
      for o in r.keys('output::*'):                                                                                                                                             
        print o
        output = o.replace('output::','').split('::')
        data = {}
        data['state'] = r.get(o)
        try: node_outputs[output[0]][output[1]] = data
        except:
          node_outputs[output[0]] = {}
          node_outputs[output[0]][output[1]] = data
      nodes = get_nodes()
      name_outputs = {}
      for n in nodes:
        pins = nodes[n]['pins']                                                                                                                                                 
        for p in pins:
          pin = str(p.keys()[0])                                                                                                                                                
          state = node_outputs[n][pin]
          named = p[p.keys()[0]]
          named = dict(named.items() + ({"pin":pin}).items())                                                                                                                   
          named = dict(named.items() + ({"node":n}).items())
          named = dict(named.items() + (state).items())
          name_outputs[p[p.keys()[0]]['name']] = named                                                                                                                          
      outputs = name_outputs
      return(outputs)


    ## Routes
    @app.route('/')
    def route_root():
      """ Root route """
      data = {}
      data['nodes']   = get_nodes()  
      data['outputs'] = get_outputs()                                                                                                                                           
      return(json.dumps(data,indent=2))


    @app.route('/outputs')
    def route_outputs():
      """ Output route """
      data = get_outputs()
      return(json.dumps(data,indent=2))

    app.run(settings['hub']['api']['host'],port=settings['hub']['api']['port'],debug=True)


