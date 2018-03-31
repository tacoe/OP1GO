# OP1GO

Ultraportable backups for Teenage Engineering's OP-1.

![OP1GO on a Pi Zero](https://i.imgur.com/txgngQ7.jpg)

## Setup

* This setup assumes MacOS. We'll configure the Raspberry Pi for a headless, networking-less setup. You can simply SSH into your raspberry pi transparently over the USB cable (the OS takes care of mapping `raspberrypi.local` for you).
* Get a Raspberry Pi Zero, a micro-USB to female USB A breakout (for the OP-1 cable), a power adapter, a micro USB cable, a micro-SD card, and an adapter to plug the micro-SD card into your macbook. You'll need about 3Gb for the system, the rest is available for OP-1 backups. You don't even need to solder on any headers, making it extra minimal!
* Download Raspbian Stretch Lite from the Raspberry Pi website and burn it on SD (Download Etcher from etcher.io for an easy and foolproof way). When done, re-insert the card so the 'boot' partition gets mounted.
* In a terminal we'll edit the boot volume. (Before the very first boot on a Pi, we can make changes to how the OS gets expanded on first boot. Handy!)
  * `cd /Volumes/boot`
  * `sudo touch ssh` to enable ssh
  * `sudo nano config.txt` -- to the bottom of the file, add `dtoverlay=dwc2`, add `dtparam=act_led_trigger=none` and save. This takes care of the USB networking and turning off the ACT led so we can use for our own purposes.
  * `sudo nano cmdline.txt` -- after `rootwait`, add `modules-load=dwc2,g_ether`, save. This too is for the USB networking.
* Eject the card
* Start the Raspberry Pi while connected to your Mac's USB and give it a bit of time to get through first boot.
* Connect to it using `ssh pi@raspberrypi.local` and the default password (`raspberry`). Might want to change the password at this step (use `passwd`).
* `sudo apt-get update`
* `sudo apt-get install python3-pip git netatalk`
* `git clone https://github.com/tacoe/op1go`
* `cd op1go`
* `sudo pip3 install pyusb` (the `sudo` is needed because the script itself needs root access)
* `sudo nano /etc/rc.local`, then add a new line `sudo python3 /home/pi/op1go/op1go.py &` (towards the end, before the `exit` statement) and save
* `sudo nano /etc/netatalk/AppleVolumes.default`, then add a new line `/op1go` at the end of the file and save
* Unplug the Pi from your Mac -- it's now ready for use.

## Usage

*WARNING: This is not tested extensively. Don't count on this tool for anything serious.*

While on vacation, and it's time to back up that OP-1 (when the tape is full, or both album sides used, when got some brilliant presets, whatever), plug your Pi Zero in a wallcharger (micro-USB port marked 'PWR'), and connect the OP-1 to it (micro-USB port marked 'USB'). Wait for the green LED on the Pi to turn off for a while. Now set the OP-1 into disk mode (shift-COM, then 3). After a while the Pi's LED will blink and it will start copying. It'll blink a few times as it goes. When it's done (this will take a few minutes), the Pi will start blinking rapidly and evenly. This means it's done. You can now disconnect everything. Next time, just rinse and repeat. OP1GO will make a new backup folder every time.

*If after a long time (>10 minutes) your Pi still isn't blinking rapidly, do NOT assume the backup was successful.*

When you return home, open Finder, hit cmd-K and enter `afp://raspberrypi.local`, login with `raspberry` and `pi` (or whatever you changed the password to), select the `op1go` share. Now you'll see your backups and you can copy them to your Mac.

## Misc

Uses code from James McGinty's neat opie.

The software is provided “as is”, without warranty of any kind, express or implied, including but not limited to the warranties of merchantability, fitness for a particular purpose and noninfringement. In no event shall the authors or copyright holders be liable for any claim, damages or other liability, whether in an action of contract, tort or otherwise, arising from, out of or in connection with the software or the use or other dealings in the software.