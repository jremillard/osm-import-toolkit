#!/usr/bin/python

# Jason Remillard - This file is in the public domain.
# Script to run the entire export data processing workflow.

import os
import sys

if ( os.system("./fetch_and_load_osm.py") ) :
  sys.exit(1)

if ( os.system("./fetch_structures.py") ) :
  sys.exit(1)

#if ( os.system("./createmissingbuildingosm.py")) :
#  os.exit(1)






