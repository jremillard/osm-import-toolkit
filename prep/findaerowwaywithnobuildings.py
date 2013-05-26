#!usr/bin/python

# Jason Remillard - This file is in the public domain.

import sys, os, zipfile

# get aeroway=terminals without building tags.
sql = "select way from planet_osm_polygon as way1 where way1.aeroway = 'terminal' and not exists (select * from planet_osm_polygon as way2 where way2.building != '' and ST_Intersects(way1.way,way2.way))"

os.system("ogr2ogr -sql \"" + sql + "\" -overwrite -f 'ESRI Shapefile' temp/badaeroway.shp PG:dbname=gis " )
os.system("python ogr2osm/ogr2osm.py -f -o output/badaeroway.osm temp/badaeroway.shp")




  
