#!/usr/bin/python

# Jason Remillard - This file is in the public domain.

import os
import sys

outputFile = "srcdata/massachusetts-latest.osm.bz2"

# load osm file into postGIS
if ( os.system("osm2pgsql " + outputFile ) ) :
  print("Error loading " + outputFile + " into postGIS gis database.")
  sys.exit(1)



