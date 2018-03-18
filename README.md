# OP1GO

Backup your OP-1 on the go with this code and a Raspberry Pi Zero.

## How to get started

* Setup your Pi and SD card (see below)
* `sudo apt-get update`
* `sudo apt-get install python3-pip git`
* `git clone https://github.com/tacoe/op1go`
* `pip3 install pyusb`

## Setup Pi/SD card

AKA the 2018 way to setup a Raspberry Pi, from a Mac, for SSH-ing over USB (no keyboard/display needed)

* Get a micro-SD card. You'll need about 3Gb for the system, the rest is available for OP-1 backups.
* Burn Raspbian Stretch Lite (Etcher is an easy and foolproof way) on it.
* Re-insert the card so the 'boot' partition gets mounted
* In a terminal:
  * `cd /Volumes/boot`
  * `sudo touch ssh`
  * `sudo nano config.txt` -- to the bottom of the file, add `dtoverlay=dwc2` and save
  * `sudo nano cmdline.txt` -- after `rootwait`, add `modules-load=dwc2,g_ether`, save
* Eject the card
* Start the Raspberry Pi while connected to your Mac's USB
* Connect to it using `ssh pi@raspberrypi.local` and the default password (`raspberry`).
