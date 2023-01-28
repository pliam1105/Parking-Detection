#!/bin/bash
export TERM=xterm-256color
cd /home/parking/tensorflow_files/PARKING
. ../virtualenv/bin/activate
watch "python3 detector_box.py parking_image.png regions.p"