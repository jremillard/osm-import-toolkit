#!/usr/bin/python

# Jason Remillard - This file is in the public domain.

import os
import sys
import tempfile
import optparse
import subprocess

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
 
parser = optparse.OptionParser(
   description='Creates an .osm file containing overlapping buildings > 1 sq meter. '
               'The dependencies are ogr2ogr, a postGIS database loaded with OSM '
               'data using with osm2pgsql, and ogr2osm. ogr2osm must be in the '
               'current directory, on path, or in ./ogr2osm directory. ',
   usage='findoverlappingbuildings.py [options] [outputfile.osm]')

parser.add_option('','--dbname',help='PostGIS database name, defaults to gis.',dest='database',default='gis')

(param,filenames) = parser.parse_args()

outputFile = 'overlappingbuildings.osm'
if ( len ( filenames) > 0 ) :
  outputFile = filenames[0]

# see if ogr2ogr is installed on path.
if ( commandCheck(["ogr2ogr","--version"]) == False ) : 
  print("error: ogr2ogr is not installed or not on the path.")
  sys.exit(1)

# try to find ogr2osm.py, not packaged yet by anybody.
ogr2osmCmd = ""
if ( commandCheck(["../ogr2osm/ogr2osm.py","-h"])) : 
  ogr2osmCmd = "../ogr2osm/ogr2osm.py"
elif ( commandCheck(["python","../ogr2osm/ogr2osm.py","-h"])) : 
  ogr2osmCmd = "python ../ogr2osm/ogr2osm.py"
elif ( commandCheck(["ogr2osm","-h"])) : 
  ogr2osmCmd = "ogr2osm"
else :
  print("error: ogr2osm is not installed or is not on the path. See README.md for instructions.")
  sys.exit(1)

if ( os.path.isfile(outputFile)) :
  os.remove(outputFile)

sql = ("select way "
       "from planet_osm_polygon as way1 "
       "where "
       " way1.building <> '' and "
       " exists "
       "  (select * "
       "   from planet_osm_polygon as way2 "
       "   where "
       "   way1.osm_id <> way2.osm_id and "
       "   way2.building <> '' and "
       "   ST_Intersects(way1.way,way2.way) and "
       "   ST_IsValid( way1.way) and "
       "   ST_IsValid( way2.way) and "
       "   ST_Area(ST_Intersection(way1.way, way2.way)) > 1 )")

tempShapeFile = tempfile.mktemp();

if ( os.system("ogr2ogr -sql \"" + sql + "\" -overwrite -f 'ESRI Shapefile' " + tempShapeFile + ".shp PG:dbname=\"" + param.database + "\" ") ) :
  print("error: ogr2ogr command failed.")
  sys.exit(1)

if ( os.system(ogr2osmCmd + " -f -o " + outputFile + " " + tempShapeFile + ".shp") ) :
  print("error: ogr2osm command failed.")
  os.remove(tempShapeFile + ".shp")
  os.remove(tempShapeFile + ".dbf")
  os.remove(tempShapeFile + ".shx")
  sys.exit(1)

os.remove(tempShapeFile + ".shp")
os.remove(tempShapeFile + ".dbf")
os.remove(tempShapeFile + ".shx")

print("Writing output file " + outputFile)

sys.exit(0)



