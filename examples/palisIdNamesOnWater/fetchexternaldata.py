#!/usr/bin/python

# Jason Remillard - This file is in the public domain.

# This script will download the PALIS_ID/palis-saris-lookups file with the
# names in it.

import os
import sys
import urllib
import zipfile

outputDir = "externaldata"

# make sure our output dirs are setup, and any existing file is clean.
if ( os.path.isdir(outputDir) == False) :
  os.mkdir(outputDir)

# The "MassGIS Data - MassDEP 2010 Integrated List of Waters (305(b)/303(d))" download.
outputFile = outputDir + "/wbs2010_shp.zip"
srcURL = "http://wsgw.mass.gov/data/gispub/shape/state/wbs2010_shp.zip"

if ( os.path.isfile(outputFile)) :
  os.remove(outputFile)

# download MassGIS water and unzip.
if ( os.system("wget -O " + outputFile + " " + srcURL ) ) :
  print("Error: Can't download " + srcURL)
  sys.exit(1)

# unzip
z=zipfile.ZipFile(outputFile,"r")
zl=z.namelist()
z.extractall(outputDir)
z.close()
os.remove(outputFile)




