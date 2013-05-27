#!/usr/bin/python

# Jason Remillard - This file is in the public domain.
# script to download current MA OSM data.

import os
import sys

outputFile = "srcdata/massachusetts-latest.osm.bz2"
srcURL = "http://download.geofabrik.de/north-america/us/massachusetts-latest.osm.bz2"

# make sure our output dirs are setup, and any existing file is clean.
if ( os.path.isdir("srcdata") == False) :
  os.mkdir("srcdata")
if ( os.path.isfile(outputFile)) :
  os.remove(outputFile)

# download MA OSM file extract.
if ( os.system("wget -O " + outputFile + " " + srcURL ) ) :
  print("Error: Can't download MA OSM extract from " + srcURL)
  sys.exit(1)




