#! /usr/bin/python

import os
import sys
import re
import time
import usb.core
import usb.util
import hashlib
import subprocess
import shutil
import ctypes
from datetime import datetime

VENDOR_TE = 0x2367
PRODUCT_OP1 = 0x0002
USBID_OP1 = "*Teenage_OP-1*"
OP1_BASE_DIRS = set(['tape', 'album', 'synth', 'drum'])
MOUNT_DIR = "/media/op1"
BACKUP_DIR_FORMAT = "%Y-%m-%d (%H%M%S)"
HOME = os.path.join(os.getenv("HOME"), "op1go-backups")
BACKUPS_DIR = os.path.join(HOME, "backups")

# OP-1 connection
def ensure_connection():
  if not is_connected():
    print("Connect your OP-1 and put it in DISK mode (Shift+COM -> 3)...")
    wait_for_connection()

def is_connected():
  return usb.core.find(idVendor=VENDOR_TE, idProduct=PRODUCT_OP1) is not None

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
  if ret != 0:
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
    src = os.path.join(mount, node)
    dst = os.path.join(dstroot, node)
    forcedir(dst)
    print("from: %s" % src)
    print("to: %s" % dst)
    #copytree(src, dst)

####################################################################################
# create mount point and local backup folders
forcedir(BACKUPS_DIR)
forcedir(MOUNT_DIR)

# wait until OP-1 is connected
print("")
ensure_connection()

# mount OP-1
mountpath = getmountpath()
print("Mountpath: %s" % mountpath)
mountdevice(mountpath, MOUNT_DIR, 'ext4', 'rw')

# copy files to local storage
backup_files(MOUNT_DIR, BACKUPS_DIR)

# unmount OP-1
unmountdevice(MOUNT_DIR)


