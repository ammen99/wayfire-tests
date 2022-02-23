#!/bin/env python3

import lycon
import numpy as np
import sys

if len(sys.argv) != 3:
    print("Usage: wfimgcompare.py <Image 1> <Image 2>")
    sys.exit(-1)

img1 = lycon.load(sys.argv[1])
img2 = lycon.load(sys.argv[2])

if img1.shape != img2.shape:
    sys.exit(1)

total_sqdiff = np.linalg.norm(img1 - img2)

PC_DIFFERENCE=0.001

w, h, _ = img1.shape
if total_sqdiff > w * h * PC_DIFFERENCE:
    sys.exit(2)
