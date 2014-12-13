myo-ros
=======

Simple Myo ROS Module

This script provides EMG, IMU and Thalmic Gesture data from the Myo Band to ROS.
This script is based on the myo-raw project - especially on the myo\_raw.py 
file. (see https://github.com/dzhu/myo-raw/ which is available under the MIT 
LICENSE)

Changes:
========
Following changes where made:
  - ros code added
  - removed code for myo firmware < 1.0
  - removed pygame stuff to keep it compact


Installation:
=============
Requires that you initialized your Myo once using the Myo Connect tool.

For the bluetooth dongle add following to: /etc/udev/rules.d/90-bluegiga\_le.rules 
# ATTR{product}=="BLED112"
ATTRS{idVendor}=="2458", ATTRS{idProduct}=="0001", ENV{ID\_MM\_DEVICE\_IGNORE}="1", SYMLINK="bluegiga/bled112"



Usage:
======
start a roscore and 
$ python myo\_ros.py

wait till connected and perform the initialization gesture



provides:
  - publishes data in topics: /myo/data/...
  - subscribes to: /myo/vibrate


ToDo:
=====

Try to 

