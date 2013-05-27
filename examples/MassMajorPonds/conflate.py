#!/usr/bin/python

# Jason Remillard - This file is in the public domain.

import sys, os, zipfile, subprocess

# run a command, return true if it worked, false if it did not work, used 
# to see if something is installed. Insures nothing goes to stdout,stderr
# used to make sure the environment is setup.
def commandCheck( args ) :
  ret = 1
  try: 
    subprocess.check_output(args,stderr=subprocess.STDOUT)
  except:
    ret = 0
  return ret

if ( os.path.isdir("temp") == False) :
  os.mkdir("temp")

r = os.system("rm temp/*")

if ( os.path.isdir("staging") == False) :
  os.mkdir("staging")

# try to find ogr2osm.py, not packaged yet by anybody.
ogr2osmCmd = ""
if ( commandCheck(["../../ogr2osm/ogr2osm.py","-h"])) : 
  ogr2osmCmd = "../../ogr2osm/ogr2osm.py"
elif ( commandCheck(["python","../../ogr2osm/ogr2osm.py","-h"])) : 
  ogr2osmCmd = "python ../../ogr2osm/ogr2osm.py"
elif ( commandCheck(["ogr2osm","-h"])) : 
  ogr2osmCmd = "ogr2osm"
else :
  print("error: ogr2osm is not installed or is not on the path. See README.md for instructions.")
  sys.exit(1)

# select water poly that has maximum overlap with each major pond poly, export name if preset.
sql = ("select " +
       "  the_geom,'water' as natural,'pond' as water, name " +
       "from massgis_majorponds");

r = os.system("ogr2ogr -sql \"" + sql + "\"" + 
              " -overwrite -f 'ESRI Shapefile' temp/ponds_missing_from_osm.shp PG:dbname=gis " )
if ( r ) : exit(r)

r = os.system(ogr2osmCmd + " -f -o staging/ponds_missing_from_osm.osm temp/ponds_missing_from_osm.shp")
if ( r ) : exit(r)




