# Copyright (c) 2017 Adafruit Industries
# Author: Tony DiCola & James DeVito
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
import time
import subprocess

import Adafruit_SSD1306

from PIL import Image, ImageDraw, ImageFont

# Raspberry Pi pin configuration:
RST = None  # on the PiOLED this pin isnt used
# Note the following are only used with SPI:
DC = 23
SPI_PORT = 0
SPI_DEVICE = 0

# 128x32 display with hardware I2C:
disp = Adafruit_SSD1306.SSD1306_128_32(rst=RST)

# Initialize library.
disp.begin()
disp.set_contrast(200)

# Clear display.
disp.clear()
disp.display()

# Create blank image for drawing.
# Make sure to create image with mode '1' for 1-bit color.
width = disp.width
height = disp.height
image = Image.new('1', (width, height))

# Get drawing object to draw on image.
draw = ImageDraw.Draw(image)

# Draw a black filled box to clear the image.
draw.rectangle((0, 0, width, height), outline=0, fill=0)

# Load default font.
font = ImageFont.load_default()

cmd = (
    "vcgencmd measure_temp | cut -c 6-9 | awk '{printf \"CPU: %d\\x27C \", $1}' && "
    "top -n 1 -b | grep \"Cpu(s)\" | awk '{printf \"%.1f%%\\n\", $2 + $4}' && "
    "free -m | awk 'NR==2{printf \"Mem: %s/%sMB %.2f%%\\n\", $3,$2,$3*100/$2}' && "
    "df -h | awk '$NF==\"/\"{printf \"Disk: %d/%dGB %s\", $3,$2,$5}'")

text_fill = 200
rect_fill = 0

i = 0
while True:

    # Default colors for 2 hours. Then invert for 10 minutes to prevent uneven screen burn
    if i >= 72000:
        if i >= 78000:
            text_fill = 200
            rect_fill = 0
            i = 0
        else:
            text_fill = 0
            rect_fill = 200

    draw.rectangle((0, 0, width, height), outline=rect_fill, fill=rect_fill)

    info = subprocess.check_output(cmd, shell=True).decode("ascii").split('\n')

    top = 0
    for line in info:
        draw.text((0, top), line, fill=text_fill)
        top += 8

    # Display image.
    disp.image(image)
    disp.display()
    time.sleep(0.1)
    i += 1
