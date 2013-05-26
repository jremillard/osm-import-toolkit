#!usr/bin/python

# Jason Remillard - This file is in the public domain.

import sys, os, zipfile

# get structures missing from OSM
sql = "select way from planet_osm_polygon as way1 where way1.amenity = 'school' and not exists (select * from planet_osm_polygon as way2 where way2.building != '' and ST_Intersects(way1.way,way2.way))"

os.system("ogr2ogr -sql \"" + sql + "\" -overwrite -f 'ESRI Shapefile' temp/badschools.shp PG:dbname=gis " )
os.system("python ogr2osm/ogr2osm.py -f -o output/badschools.osm temp/badschools.shp")




  
