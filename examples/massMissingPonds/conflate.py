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
os.system("rm temp/*")

stageDir = "stage"

if ( os.path.isdir(stageDir) == False) :
  os.mkdir(stageDir)

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

# For each water poly, export it if it does not overlap with a water feature or a 
# waterway feature in OSM. Try to get the name from massgis_il, but leave it empty
# if not present, and make a guess at the water type from name and area.
sql = ("select " +
       "  distinct ST_SimplifyPreserveTopology(massgis_wetlands.the_geom,1), " +
       "  'water' as natural, " +
       "   case " + 
       "     when poly_code = 1 then 'reservoir' " +
       "     else '' " + 
       "   end as water,  " +
       "   massgis_il.waterbody as name " +
       "from massgis_wetlands " + 
       "left join massgis_il on " +
       "  cast( massgis_wetlands.palis_id as text) = massgis_il.watercode " +
       "where " + 
       "  wetcode = 9 and areaacres > 1 and (poly_code = 1 or poly_code = 6) and " +
       "  not exists (select * from planet_osm_polygon as osm " +
         "   where " +
         "     (osm.natural = 'water' or " +
         "      osm.waterway != '' or " +
         "      osm.landuse = 'reservoir') and " +
         "     ST_IsValid( osm.way ) and " +
         "     ST_Intersects(osm.way,massgis_wetlands.the_geom)) and"
       "  not exists ( select * from planet_osm_line as osm " + 
         "   where " +
         "     osm.waterway != '' and " +
         "     ST_IsValid( osm.way ) and " +
         "     ST_Intersects(osm.way,massgis_wetlands.the_geom))")

r = os.system("ogr2ogr -sql \"" + sql + "\"" + 
              " -overwrite -f 'ESRI Shapefile' temp/ponds_missing_from_osm.shp PG:dbname=gis " )
if ( r ) : exit(r)

# ogrtranslation.py just kills the empty name tags.
r = os.system(ogr2osmCmd + " -f -t ./ogrtranslation.py -o " + stageDir + "/ponds_missing_from_osm.osm temp/ponds_missing_from_osm.shp")
if ( r ) : exit(r)








