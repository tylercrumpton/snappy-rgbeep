from binascii import hexlify
from snapconnect import snap

from win32ctypes import win32api
import pymouse
import pykeyboard
from rx import Observable

import win32com.client

from time import sleep

pymouse.win32api = win32api
pykeyboard.win32api = win32api
from pymouse import PyMouse
from pykeyboard import PyKeyboard

key_dict = {}
current_key = 'a'

m = PyMouse()
k = PyKeyboard()

def get_rpc_observable(name):
  def event_observer(observer):
    def rpc_callback(*args):
      observer.on_next({
        'event': name,
        'snapaddr': our_instance.rpc_source_addr(),
        'args': args
      })
    our_instance.add_rpc_func(name, rpc_callback)
  return Observable.create(event_observer)

shell = win32com.client.Dispatch("WScript.Shell")

def print_value(snap_addr):
    global current_key
    if snap_addr not in key_dict:
        key_dict[snap_addr] = current_key
        current_key = chr(ord(current_key) + 1)
    k.press_key(key_dict[snap_addr])
    sleep(0.050)
    k.release_key(key_dict[snap_addr])
    #shell.SendKeys("a")
    print("Address: {0}, Key: {1}".format(snap_addr, key_dict[snap_addr]))

SERIAL_TYPE = snap.SERIAL_TYPE_SNAPSTICK200
SERIAL_PORT = 0

# Create a SNAP instance
our_instance = snap.Snap(funcs={})
our_instance.open_serial(SERIAL_TYPE, SERIAL_PORT)

def on_error(e):
    print e

get_rpc_observable("report_press") \
  .group_by(lambda event: event["snapaddr"]) \
  .flat_map(lambda device_taps: \
    device_taps \
      .map(lambda event: hexlify(event["snapaddr"])) \
      #.throttle_first(40) \
  ) \
  .subscribe(print_value, on_error)

our_instance.loop()


