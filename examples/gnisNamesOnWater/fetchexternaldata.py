#!/usr/bin/python

# Jason Remillard - This file is in the public domain.

# Script to download full GNIS database, and unzip it.

import os
import sys
import urllib
import zipfile

outputDir = "externaldata"

# filename changes all of the time, pass ISO date in.
gnisDate = "20130811"
if ( len(sys.argv) > 1 ) :
  gnisDate = sys.argv[1]

outputFile = outputDir + "/NationalFile.zip"
srcURL = "http://geonames.usgs.gov/docs/stategaz/NationalFile_" + gnisDate + ".zip"

# make sure our output dirs are setup, and any existing file is clean.
if ( os.path.isdir(outputDir) == False) :
  os.mkdir(outputDir)
if ( os.path.isfile(outputFile)) :
  os.remove(outputFile)

# download MA OSM file extract.
if ( os.system("wget -O " + outputFile + " " + srcURL ) ) :
  print("Error: Can't download NationalFile extract from " + srcURL)
  sys.exit(1)

# unzip
z=zipfile.ZipFile(outputFile,"r")
zl=z.namelist()
z.extractall(outputDir)
z.close()
os.remove(outputFile)
os.rename( "externaldata/NationalFile_" + gnisDate + ".txt","externaldata/NationalFile.txt")






