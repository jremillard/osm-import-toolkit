#!usr/bin/python

# Jason Remillard - This file is in the public domain.

import sys, os, zipfile

os.system("rm temp/*")

# get structures missing from OSM
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

print sql

os.system("ogr2ogr -sql \"" + sql + "\" -overwrite -f 'ESRI Shapefile' temp/overlappingbuildings.shp PG:dbname=gis " )
os.system("python ogr2osm/ogr2osm.py -f -o output/overlappingbuildings.osm temp/overlappingbuildings.shp")




  
