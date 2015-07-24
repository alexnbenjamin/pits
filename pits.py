# -*- coding: utf-8 -*-

'''
Behold! Python Image-to-Speech (affectionally known as pits)

The following code outputs synthesized speech based on text present in a picture. The algorithm is
designed to detect signs and documents within photographs, isolate and correctively perspective warp
the document region, optimize for readability, then perform optical character recognition and text-
to-speech. It works best on pictures whose text is outlined in a rectangle, and can handle all sorts
of crazy photograph angles and lighting conditions!

The workflow is as follows:
    1.  Read and resize the input image.
    2.  Generate an edge-detected image and search for rectangles.
    3.  Identify the document region as the largest clear rectangle.
    4.  Analyze the region and warp to achieve an as-normal perspective view of the document.
    5.  Perform adaptive thresholding to generate crisp, binary images for OCR.
    6.  Run the thresholded, normalized documents through OCR to extract text as a string.
    7.  Output synthesized speech of extracted string using pyttsx.

The usage via command line is:
    python pits.py <your_image_name>

I'd love to see this technology used in products ranging from automobile safety improvements, quality
of life assistance for the visually impaired, helping children learn to read, and quickly generating
audiobooks/audio files from documents.

ANB
'''

import numpy as np
import cv2
import Image
import pytesseract
import pyttsx
import re
import sys

# Section 1: Edge detection/feature detection to determine document area

# Step 1.1: Load the image, resize, edge-detect, and find the 10 largest contours

img = cv2.imread(sys.argv[1])
small = cv2.resize(img, (0, 0), fx=0.9, fy=0.9) # 0.5 scale is a good blanket for typical phone pics
edges = cv2.Canny(small, 50, 100)
cv2.imwrite('edges.jpg', edges) # this saves the edge-detected image; can be safely commented
(contours, hierarchy) = cv2.findContours(edges.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
sorted_contours = sorted(contours, key = cv2.contourArea, reverse = True)[:10]

# Step 1.2: The largest contour with 4 corners is taken as the document region

for c in sorted_contours:
    polygon = cv2.approxPolyDP(c, 0.02 * cv2.arcLength(c, True), True)
    if len(polygon) == 4:
        doc_contour = polygon
        break

# This draws a box around the document region and saves the resulting image; can be safely commented
cv2.drawContours(small, [doc_contour], -1, (0, 255, 0), 2)
cv2.imwrite("highlighted.jpg", small)

# Section 2: Analyze and perform corrective perspective warp on document region

# Step 2.1: Determine top/bottom/left/right corners

max_sum = 0
min_sum = 10000
min_x = 10000
locs = [9, 9, 9, 9]

# This process is a little barbaric if we consider some of the tools numpy makes available, but because
# the computation is minimal (and thus the final application is performant) I leave it as is for clarity

for i in range(doc_contour.shape[0]):
    this_sum = doc_contour[i][0][0] + doc_contour[i][0][1]
    if this_sum > max_sum:
        max_sum = this_sum
        br = doc_contour[i]
        locs[2] = i
    if this_sum < min_sum:
        min_sum = this_sum
        tl = doc_contour[i]
        locs[0] = i
for i in range(doc_contour.shape[0]):
    if i not in locs:
        if doc_contour[i][0][0] < min_x:
            min_x = doc_contour[i][0][0]
            bl = doc_contour[i]
            locs[3] = i
for i in range(doc_contour.shape[0]):
    if i not in locs:
        tr = doc_contour[i]
        locs[1] = i

corners = np.zeros((4,2), dtype=np.float32)
corners[0] = tl
corners[1] = tr
corners[2] = br
corners[3] = bl

# Step 2.2: Determine final document size

width_bot = np.linalg.norm(br-bl)
width_top = np.linalg.norm(tr-tl)
width = int(max(width_bot, width_top))

height_left = np.linalg.norm(tl-bl)
height_right = np.linalg.norm(tr-br)
height = int(max(height_left, height_right))

out = np.array([[0, 0], [width-1, 0], [width-1, height-1], [0, height-1]], dtype=np.float32)

# Step 2.3: Perform warp

tmx = cv2.getPerspectiveTransform(corners, out)
warped = cv2.warpPerspective(small, tmx, (width, height))
cv2.imwrite('warped.jpg', warped) # saves the normal-perspective color image; can be safely commented

# Step 3: Optimize readability (contrast, sharpness, etc.) for OCR

warped = cv2.cvtColor(warped, cv2.COLOR_BGR2GRAY)
warped = cv2.adaptiveThreshold(warped, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 19, 10)
cv2.imwrite('prepped.jpg', warped) # saves the thresholded (for OCR) image; can be safely commented

# Step 4: OCR and TTS

# Step 4.1: Retrieve string via OCR, substitute non-ASCII and commonly mistaken characters

the_words = (pytesseract.image_to_string(Image.open('prepped.jpg')))
the_words = the_words.replace('\\', 'l')
the_words = the_words.replace('—', '-')
the_words = the_words.replace("0", "O")
the_words = the_words.replace("ﬂ", "O")
the_words = the_words.replace('ﬁ', 'fi')
regex = re.compile('[^a-zA-Z \n .!,;\':-]')
the_words = regex.sub('', the_words)

# Step 4.2: Synthesize speech from the_words via pyttsx!

engine = pyttsx.init()
engine.setProperty('rate', 170) # rate of speech can be adjusted based on preference
engine.say(the_words)
engine.runAndWait()