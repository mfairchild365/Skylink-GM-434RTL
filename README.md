# Skylink-GM-434RTL Notifier

## Summery of project
This was a weekend project. I already had a Skylink-GM-434RTL installed in my house. For clarification, yes it is a garage door alarm, and yes the only reason why I have it is because I forget to close my garage door ALL THE TIME. The device came with a receiver which will loudly beep until the garage door is closed. Very helpful.

I was curious how the device worked, and I had an amazon gift card to spend along with a spare raspberry Pi 2. Why not hack the device and have it send me a text whenever my garage door opens and closes? Seems simple enough right?

## My supplies:
This is all that I used to get this thing working:

- Skylink-GM-434RT - http://www.amazon.com/Skylink-GM-434RTL-Wireless-Household-Protection/dp/B004969FB6
- raspberry pi 2
- A software defined radio (RTL-SDR): http://www.amazon.com/gp/product/B009U7WZCA


## WHAT HAVE I DONE!?
Going into this, I had absolutely no idea what I was getting into or how any of this stuff worked. This stuff was magic to me. I knew the alarm communicated with the receiver wirelessly, but how!? Well, a quick google search put me in the right direction: radio waves! So, I researched how to get a raspberry pi to detect radio singles and discovered the world of the RTL-SDR, or software defined radios. Basically, you plug a little device into your usb port, run some software, and you can eavesdrop on the radio, TV, your neighbors, a crazy amount of devices, etc. Don't tell the NSA. However, most of this is just noise and super hard to decode.

### Finding the frequency

So, after I got a RTL-SDR, my first task was to find the frequency at which it operated. To accomplish this, plugged the SDR into my windows PC, downloaded [SDR#](http://airspy.com/download/) and went to town.

It turns out that my little SDR has a crazy frequency range, and manually finding it would take years. So, I scanned for it using a plugin. That was pretty cool, but I still didn't have any luck. Probably because the the alarm sent a burst of radio waves for a split second and the scanner was not watching the right frequency at the right time. If the scanner watched every possible frequency at all times, I might have found it.

So, what now. MORE RESEARCH! I googled and googled until my eyes were blue. As a last resort, I hopped on amazon and searched reviews in hopes of finding something. TADA! Someone posed a review along the lines of "Hey, I need to improve the range of this thing", and the seller replied "it works at 433mhz!".

So, it turns out that most devices work at the 433mhz range. I just didn't know that.

Using the sdr# program, I was able to confirm that the little device was operating at 433.880.000hz. It would send small bursts of radio waves whenever it opened and closed. The bursts looked nearly identical, but it turns out that they not even close.

### Reading the frequency
Okay, now I needed to know how to do this pragmatically. I am a programmer by trade, so I had a general idea of how to go about this. Search for things that already do it!

I came up with a few existing projects:

- Freq Show: this is a small program designed for the pi, which uses python libraries show charts and data about radio singles. https://learn.adafruit.com/freq-show-raspberry-pi-rtl-sdr-scanner/installation
	- This was also helpful because it showed me how to get the drivers installed for the RTL-SDR device
- rtl_433, which is a C program specifically designed to analyze device data on the 433mhz range.

python is easier than C, so I went the python route first. Analyzing the Freq Show code, I was able to come up with a script that will notify me when my garage door opens or closes. However, it CAN NOT tell me if it was opened or closed, just that one of the two happened. This is because I was simply looking for pulses from the alarm, and nothing else. You can find that script here: https://github.com/mfairchild365/Skylink-GM-434RTL/blob/master/door.py

Okay, but my receiver knows when it is open vs closed. How do I get that data? Long story short, the alarm sends DATA over the radio to the receiver. Okay, but what data and how do I read it?

rtl_433 to the rescue! At first, I was only able to see gibberish when using rtl_433 to analyze the pulses. There was nothing that would reliably differentiate the open vs closed states.

So, I played with the sample rate. When I tested with 5000 Hz, I got what I needed. rtl_433 was able to decode the singles and I got some binary data! The key difference was the presence of `01100001` for the open single and `10000001` for the closed single. Now THAT is something that I can use.

Problem: I couldn't find a python library to get this data for me, and I didn't want to spend 50 years trying to build one myself.

Solution: wrap rtl_443. With python, I was able to launch a subprocess of rtl_443 and watch the output for the values that I needed to key off of! See https://github.com/mfairchild365/Skylink-GM-434RTL/blob/master/door-notifier.py

With that in place, I was able to have it trigger an email, which would then be routed to a text message to my phone.

I rock.

(well, we will see how well it actually works in production)

## How to get the thing up and running

### For both projects you need this:

Install system packages:

```
sudo apt-get update
sudo apt-get install cmake build-essential python-pip libusb-1.0-0-dev python-numpy git
```

Install the drivers for RTL-SDR

```
cd ~
git clone git://git.osmocom.org/rtl-sdr.git
cd rtl-sdr
mkdir build
cd build
cmake ../ -DINSTALL_UDEV_RULES=ON -DDETACH_KERNEL_DRIVER=ON
make
sudo make install
sudo ldconfig
```

### for door.py you need this:

Install the RTL-SDR Python wrapper:

```
sudo pip install pyrtlsdr
```

### for the better door-notifier.py you need this

Install the configure wrapper for python
```
sudo pip install config
```

You also need to install rtl_433. To do so, follow the instructions found here: https://github.com/merbanan/rtl_433

Then copy `door-notifier.sample.cfg` to `door-notifier.cfg` and edit accordingly.

To run: `python door-notifier.py`

You might be able to run it on a cron, such as `@reboot /path/to/python door-notifier.py > outputfile.txt`

## Notes

So, my cron idea didn't work. It appears that something is funky on the first few runs. Possible calibration is off?

The first time I run `rtl_433 2>&1 -s005000 -A -f 433880000` after booting, I just get gibberish

However, once I run `rtl_433 2>&1 -s250000 -A -f 433880000` and `rtl_433 2>&1 -s005000 -A -f 433880000` a few times, the 5000 sample rate starts to work correctly. Then I can run `python /home/pi/door/door-notifier.py > /home/pi/door/out.txt &`, exit the server and it works as expected.
