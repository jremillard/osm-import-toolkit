#!/usr/bin/python

# Jason Remillard - This file is in the public domain.

# Script to download major hydro data from MassGIS. Unfortunately 1/10000 hydro 
# data is contained in a windows .exe. The contents of the .exe should be downloaded
# 
# http://www.mass.gov/anf/research-and-tech/it-serv-and-support/application-serv/office-of-geographic-information-massgis/datalayers/depwetlands112000.html
#
# and placed into srcdata

import os
import sys
import urllib
import zipfile

if ( os.path.isdir("temp") == False) :
  os.mkdir("temp")
os.system("rm temp/*")

outputFile = "srcdata/majorhydro.zip"
srcURL = "http://wsgw.mass.gov/data/gispub/shape/state/majorhydro.zip"

# make sure our output dirs are setup, and any existing file is clean.
if ( os.path.isdir("srcdata") == False) :
  os.mkdir("srcdata")
if ( os.path.isfile(outputFile)) :
  os.remove(outputFile)

# download MA OSM file extract.
if ( os.system("wget -O " + outputFile + " " + srcURL ) ) :
  print("Error: Can't download majorhydro.zip extract from " + srcURL)
  sys.exit(1)

# unzip
z=zipfile.ZipFile(outputFile,"r")
zl=z.namelist()
z.extractall("srcdata")
z.close()
os.remove(outputFile)

# reproject to 900913, which is what we use inside of postGIS
r = os.system("ogr2ogr -t_srs EPSG:900913 -overwrite temp/majpond_poly.shp srcdata/MAJPOND_POLY.shp"); 
if ( r ) : exit(r);

r = os.system("ogr2ogr -t_srs EPSG:900913 -overwrite temp/wetland_poly.shp srcdata/WETLANDSDEP_POLY.shp"); 
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





