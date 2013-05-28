#!/usr/bin/python

# Jason Remillard - This file is in the public domain.

import os
import sys

outputFile = "osmdata/massachusetts-latest.osm.bz2"

if ( os.path.isdir("temp") == False) :
  os.mkdir("temp")

os.system("rm temp/*")

# load osm file into postGIS
if ( os.system("osm2pgsql " + outputFile ) ) :
  print("Error loading " + outputFile + " into postGIS gis database.")
  sys.exit(1)

# reproject to 900913, which is what we use inside of postGIS
r = os.system("ogr2ogr -t_srs EPSG:900913 -overwrite temp/majpond_poly.shp externaldata/MAJPOND_POLY.shp"); 
if ( r ) : exit(r);

r = os.system("ogr2ogr -t_srs EPSG:900913 -overwrite temp/wetland_poly.shp externaldata/WETLANDSDEP_POLY.shp"); 
if ( r ) : exit(r);


# import to postGIS
r = os.system("shp2pgsql -D -I -s EPSG:900913 -d temp/majpond_poly.shp massgis_majorponds | psql -q gis");
if ( r ) : exit(r);

r = os.system("shp2pgsql -D -I -s EPSG:900913 -d temp/wetland_poly.shp massgis_wetlands | psql -q gis");
if ( r ) : exit(r);

# set the projection, shp2pgsl does not do this, don't know why...
r = os.system("psql gis -c \"select UpdateGeometrySRID('massgis_majorponds','the_geom',900913)\"")
if ( r ) : exit(r);

r = os.system("psql gis -c \"select UpdateGeometrySRID('massgis_wetlands','the_geom',900913)\"")
if ( r ) : exit(r);

print("Success!!")






