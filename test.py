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
from subprocess import run
from datetime import datetime

HOME = os.path.join(os.getenv("HOME"), "Music/op1go")
VENDOR_TE = 0x2367
PRODUCT_OP1 = 0x0002
OP1_BASE_DIRS = set(['tape', 'album', 'synth', 'drum'])
BACKUPS_DIR = os.path.join(HOME, "backups")
BACKUP_DIR_FORMAT = "%Y-%m-%d (%H%M%S)"

def get_visible_folders(d):
    return list(filter(lambda x: os.path.isdir(os.path.join(d, x)), get_visible_children(d)))

def get_visible_children(d):
    return list(filter(lambda x: x[0] != '.', os.listdir(d)))

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

def get_mount_from_line(line):
    match = re.match(r"^\s*(?P<device>/dev/\w+) on (?P<mount>[^\0]+) (type .*)?\(.*\)\s*$", line)
    if match:
        return (match.group("device"), match.group("mount"))
    return None

def is_poopy_mount(mount):
    BAD_PREFIX = ['/dev', '/sys', '/net', '/proc', '/run', '/boot']
    if mount in ["/", "/home"]: return True
    for prefix in BAD_PREFIX:
        if mount.startswith(prefix): return True
    return False

def get_potential_mounts():
    result = run(["mount"], stdout=subprocess.PIPE, universal_newlines=True)
    if result.returncode != 0:
        print("mount command appeared to fail")
        return None

    if result.stdout is None:
        print("uh oh")

    lines = result.stdout.split("\n")
    mounts = [get_mount_from_line(x) for x in lines]
    filtered = [x for x in mounts if x is not None and not is_poopy_mount(x[1])]

    return filtered

def find_op1_mount():
    dirs = []
    mounts = get_potential_mounts()
    if mounts is None:
        dirs = [os.path.join("/Volumes", x) for x in get_visible_folders("/Volumes")]
    else:
        dirs = [x[1] for x in mounts]

    for dir in dirs:
        dir = re.findall('([^\s]+)|$', dir)[0]
        subdirs = get_visible_folders(dir)
        if set(subdirs) & OP1_BASE_DIRS == OP1_BASE_DIRS:
            return dir

    return None

def wait_for_op1_mount(timeout=5):
    i=0
    try:
        while i < timeout:
            time.sleep(1)
            mount = find_op1_mount()
            if mount is not None:
                return mount
            i += 1
        print("timed out waiting for mount.")
        return None
    except KeyboardInterrupt:
        sys.exit(0)

def mountOP1():
    ensure_connection()
    mount = find_op1_mount()
    if mount is None:
        print("Waiting for OP-1 disk to mount...")
        mount = wait_for_op1_mount()
        if mount is None:
            exit("Failed to find mount point of OP-1.")
    return mount

def copytree(src, dst, symlinks=False, ignore=None):
    for item in os.listdir(src):
        s = os.path.join(src, item)
        d = os.path.join(dst, item)
        if os.path.isdir(s):
            shutil.copytree(s, d, symlinks, ignore)
        else:
            shutil.copy2(s, d)
            
def backup_files(mount, BACKUPS_DIR): 
  dstroot = os.path.join(BACKUPS_DIR, datetime.now().strftime(BACKUP_DIR_FORMAT))
  forcedir(dstroot)
  for node in get_visible_children(mount):
      src = os.path.join(mount, node)
      dst = os.path.join(dstroot, node)
      forcedir(dst)
      print("from: %s" % src)
      print("to: %s" % dst)
      copytree(src, dst)

def forcedir(path):
  if not os.path.isdir(path):
    os.makedirs(path)


# create backup directory
forcedir(BACKUPS_DIR)

mount = mountOP1()
print("OP-1 found at %s" % mount)

backup_files(mount, BACKUPS_DIR)
