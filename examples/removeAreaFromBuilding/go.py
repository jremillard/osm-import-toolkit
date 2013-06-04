#!/usr/bin/python

# Jason Remillard - This file is in the public domain.
# Script to run the entire export data processing workflow.

import os
import sys

if ( os.system("./fetchosmdata.py.py") ) :
  sys.exit(1)

if ( os.system("./fetchexternaldata.py") ) :
  sys.exit(1)

if ( os.system("./postgisloaddata.py") ) :
  sys.exit(1)

#if ( os.system("./conflate.py")) :
#  os.exit(1)

#if ( os.system("./stage.py")) :
#  os.exit(1)





