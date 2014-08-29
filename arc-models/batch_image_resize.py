# batch image processing to 5001x5001
import sys, os
from  PIL import Image
fname = "C:/Users/Eric Cawi/Documents/SAR"
pngs = "/test_cases"
directory = fname + pngs
width = 5001
height = 5001
# Iterate through every image in the directory and resize them
for file in os.listdir(directory):
  print "Resizing image " + file
  # Open the image
  img = Image.open(directory + "/" + file)
  # Resize it
  img = img.resize((width, height), Image.BILINEAR)
  # Save it back to disk
  img.save(fname+"/test_cases2/" + file)
