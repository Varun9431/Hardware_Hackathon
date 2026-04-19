#!/bin/bash

rpicam-vid -t 0 -n \
--width 640 \
--height 480 \
--framerate 10 \
--inline \
--listen \
--flush \
-o tcp://0.0.0.0:8888


