#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sun Dec  2 14:52:44 2018

@author: greg
"""

import cv2
import numpy as np
import time
import streamlink

# use live streamer to figure out the stream info
streams = streamlink.streams("http://twitch.tv/Strafesh0t")
stream = streams['best']
# open our out file.
fname = "test.mpg"
vid_file = open(fname, "wb")
# dump from the stream into an mpg file -- get a buffer going
fd = stream.open()
for i in range(0, 2*2048):
    if i % 256 == 0:
        print("Buffering...")
    new_bytes = fd.read(1024)
    vid_file.write(new_bytes)
# open the video file from the begining
print("Done buffering.")
cam = cv2.VideoCapture(fname)
while True:
    ret, img = cam.read()
    try:
        if ret:
            gray_image = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            blur = cv2.GaussianBlur(gray_image, (9, 9), 0)
            canny = cv2.Canny(blur, 60, 140)

            cv2.imshow('live_img', canny)
            # cv2.resizeWindow('live_img', 600, 600)

    except:
        print("DERP")
        continue
    if (0xFF & cv2.waitKey(5) == 27) or img.size == 0:
        break
    time.sleep(0.05)
    # dump some more data to the stream so we don't run out.
    new_bytes = fd.read(1024*16)
    vid_file.write(new_bytes)
vid_file.close()
fd.close()
