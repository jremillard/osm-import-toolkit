#!/usr/bin/python

# Jason Remillard - This file is in the public domain.

import os
import sys

outputFile = "osmdata/massachusetts-latest.osm.bz2"

# load osm file into postGIS
if ( os.system("osm2pgsql " + outputFile ) ) :
  print("Error loading " + outputFile + " into postGIS gis database.")
  sys.exit(1)

if ( os.path.isdir("temp") == False) :
  os.mkdir("temp")

projection = "900913"

# the geometry
os.system("rm temp/*")

r = os.system("ogr2ogr -t_srs EPSG:" + projection + " -overwrite temp/wetland_poly.shp externaldata/WETLANDSDEP_POLY.shp"); 
if ( r ) : exit(r);

r = os.system("shp2pgsql -D -I -s EPSG:" + projection + " -d temp/wetland_poly.shp massgis_wetlands | psql -q gis");
if ( r ) : exit(r);

r = os.system("psql gis -c \"select UpdateGeometrySRID('massgis_wetlands','the_geom'," + projection +")\"")
if ( r ) : exit(r);


# the names (itegrated list - il)
os.system("rm temp/*")
r = os.system("ogr2ogr -t_srs EPSG:" + projection + " -overwrite temp/IL_2010_POLY.shp externaldata/IL_2010_POLY.shp"); 
if ( r ) : exit(r);

r = os.system("shp2pgsql -D -I -s EPSG:" + projection + " -d temp/IL_2010_POLY.shp massgis_il | psql -q gis");
if ( r ) : exit(r);

r = os.system("psql gis -c \"select UpdateGeometrySRID('massgis_il','the_geom'," + projection +")\"")
if ( r ) : exit(r);


print("Success!!")






