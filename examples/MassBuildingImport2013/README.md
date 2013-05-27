MassGIS 2013 Building Import
=======================
These scripts are ported over from MassGIS 2013 import http://wiki.openstreetmap.org/wiki/MassGIS_Buildings_Import to use the import toolkit. 

 - go.py - Top level script that runs all the lower level scripts in one command.

 - fetch_and_load.osm.py - Downloads MA OSM extract and loads it into PostGIS.
 - fetch_structures.py - Downloads and unzips the 351 MassGIS structure shape files from MassGIS website.
 - createmissingbuildings.py - Writes out an OSM file per down of buildings that are present in the MassGIS data and missing from OSM.

The scripts create the following subdirectories

 - srcdata - Stores the Mass OSM extract file.
 - srcdata/massgis - Stores the 351 shape files downloaded from MassGIS website.
 - staging - Stores the output .osm files. Two .osm files per town. One file has the strutures that are missing from OSM. The second file has the OSM buildings that overlap with the MassGIS structures. The directory also contains the conversion of the missing from OSM .osm file to .osc.
 - upload - .osc files that are ready for uploading. A .osc file that has an upload log will not be overwritten by the creatmissingbuildings.py script.

