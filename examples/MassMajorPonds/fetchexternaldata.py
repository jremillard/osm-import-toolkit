#!/usr/bin/python

# Jason Remillard - This file is in the public domain.

# Script to download major hydro data from MassGIS. Unfortunately 1/10000 hydro 
# data is contained in a windows .exe. The contents of the .exe should be downloaded
# 
# http://www.mass.gov/anf/research-and-tech/it-serv-and-support/application-serv/office-of-geographic-information-massgis/datalayers/depwetlands112000.html
#
# and placed into externaldata, this script will download the palis-saris-lookups file with the
# names in it.

import os
import sys
import urllib
import zipfile

outputDir = "externaldata"

outputFile = outputDir + "/wbs2010_shp.zip"
srcURL = "http://wsgw.mass.gov/data/gispub/shape/state/wbs2010_shp.zip"

# make sure our output dirs are setup, and any existing file is clean.
if ( os.path.isdir(outputDir) == False) :
  os.mkdir(outputDir)
if ( os.path.isfile(outputFile)) :
  os.remove(outputFile)

# download MA OSM file extract.
if ( os.system("wget -O " + outputFile + " " + srcURL ) ) :
  print("Error: Can't download palis-saris-lookups.zip extract from " + srcURL)
  sys.exit(1)

# unzip
z=zipfile.ZipFile(outputFile,"r")
zl=z.namelist()
z.extractall(outputDir)
z.close()
os.remove(outputFile)




