MassGIS 2013 Building Import
=======================
These scripts are ported over from MassGIS 2013 import http://wiki.openstreetmap.org/wiki/MassGIS_Buildings_Import to use the import toolkit. 

 - go.py - Top level script that runs all the lower level scripts in one command.

 - fetch_and_load.osm.py - downloads MA OSM extract, and loads into postGIS.
 - fetch_structures.py - download MassGIS structure shape files, unzips and stores srcdata/structures.
 - createmissingbuildings.py - writes out an OSM file per down of buildings that are present in the MassGIS data and missing from OSM.



