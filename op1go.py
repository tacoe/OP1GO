#! /usr/bin/python

import os
import sys
import re
import time
import usb.core
import usb.util
import shutil
from datetime import datetime

VENDOR = 0x2367
PRODUCT = 0x0002
USBID_OP1 = "*Teenage_OP-1*"
MOUNT_DIR = "/media/op1"
BACKUP_DIR_FORMAT = "%Y-%m-%d (%H%M%S)"
HOME = "/op1go"
BACKUPS_DIR = os.path.join(HOME, "backups")

# OP-1 connection
def ensure_connection():
  if not is_connected():
    print("Connect your OP-1 and put it in DISK mode (Shift+COM -> 3)...")
    wait_for_connection()

def is_connected():
  return usb.core.find(idVendor=VENDOR, idProduct=PRODUCT) is not None

def wait_for_connection():
  try:
    while True:
      time.sleep(1)
      if is_connected():
        break
  except KeyboardInterrupt:
    sys.exit(0)

# mounting
def mountdevice(source, target, fs, options=''):
  ret = os.system('mount {} {}'.format(source, target))
  if ret not in (0, 8192):
    raise RuntimeError("Error mounting {} on {}: {}".format(source, target, ret))

def unmountdevice(target):
  ret = os.system('umount {}'.format(target))
  if ret != 0:
    raise RuntimeError("Error unmounting {}: {}".format(target, ret))

def getmountpath():
  o = os.popen('readlink -f /dev/disk/by-id/' + USBID_OP1).read()
  if USBID_OP1 in o:
    raise RuntimeError("Error getting OP-1 mount path: {}".format(o))
  else:
    return o.rstrip()

# copying
def forcedir(path):
  if not os.path.isdir(path):
    os.makedirs(path)

def get_visible_folders(d):
  return list(filter(lambda x: os.path.isdir(os.path.join(d, x)), get_visible_children(d)))

def get_visible_children(d):
  return list(filter(lambda x: x[0] != '.', os.listdir(d)))

def copytree(src, dst, symlinks=False, ignore=None):
  for item in os.listdir(src):
    s = os.path.join(src, item)
    d = os.path.join(dst, item)
    if os.path.isdir(s):
      shutil.copytree(s, d, symlinks, ignore)
    else:
      shutil.copy2(s, d)

def backup_files(source, destination): 
  dstroot = os.path.join(destination, datetime.now().strftime(BACKUP_DIR_FORMAT))
  forcedir(dstroot)
  for node in get_visible_children(source):
    src = os.path.join(source, node)
    dst = os.path.join(dstroot, node)
    print(" . from: {} to {}".format(src, dst))
    forcedir(dst)
    copytree(src, dst)
    blink(1)

# misc
def blink(count):
  os.system("echo none | sudo tee /sys/class/leds/led0/trigger >/dev/null 2>&1")
  for i in range(0,count):
    os.system("echo 0 | sudo tee /sys/class/leds/led0/brightness >/dev/null 2>&1")
    time.sleep(0.15)
    os.system("echo 1 | sudo tee /sys/class/leds/led0/brightness >/dev/null 2>&1")
    time.sleep(0.05)

def blinklong():
  os.system("echo none | sudo tee /sys/class/leds/led0/trigger >/dev/null 2>&1")
  os.system("echo 0 | sudo tee /sys/class/leds/led0/brightness >/dev/null 2>&1")
  time.sleep(1)
  os.system("echo 1 | sudo tee /sys/class/leds/led0/brightness >/dev/null 2>&1")

def blinkyay():
  os.system("echo none | sudo tee /sys/class/leds/led0/trigger >/dev/null 2>&1")
  for i in range(0,1000000):
    os.system("echo 0 | sudo tee /sys/class/leds/led0/brightness >/dev/null 2>&1")
    time.sleep(0.01)
    os.system("echo 1 | sudo tee /sys/class/leds/led0/brightness >/dev/null 2>&1")
    time.sleep(0.01)


## Main ##

# create mount point and local backup folders
blinklong()
forcedir(BACKUPS_DIR)
forcedir(MOUNT_DIR)

# wait until OP-1 is connected
print(" > Starting - waiting for OP-1 to connect")
ensure_connection()
time.sleep(5)

# mount OP-1
mountpath = getmountpath()
print(" > OP-1 device path: %s" % mountpath)
mountdevice(mountpath, MOUNT_DIR, 'ext4', 'rw')
print(" > Device mounted at %s" % MOUNT_DIR)

# copy files to local storage
blink(5)
print(" > Copying files...")
backup_files(MOUNT_DIR, BACKUPS_DIR)

# unmount OP-1
print(" > Unmounting OP-1")
unmountdevice(MOUNT_DIR)
print(" > Done.")
blinkyay()


