#!/usr/bin/python

# Jason Remillard - This file is in the public domain.

import os
import sys
import csv
import psycopg2

gnisFile = "externaldata/NationalFile.txt"

if (os.system("psql gis -f gnisschema.sql")):
  print("Error loading gnisschema.sql into into postGIS gis database.")
  sys.exit(1)

con = psycopg2.connect(database='gis') 
cur = con.cursor()

with open(gnisFile, 'rt') as f:
  reader = csv.reader(f,delimiter='|')
  for row in reader:
    if ( len(row) > 10 and (row[2] == 'Lake' or row[2] == 'Reservoir')) :
      cur.execute("insert into gnis (featureid, name, featureclass, geom) values(" + 
        row[0] + "," + 
        "'" + row[1].replace("'","''") + "'," + 
        "'" + row[2].replace("'","''") + "'," +
        "ST_PointFromText('POINT(" + row[9] + ' ' + row[10] + ")', 4326))");

cur.close()

con.commit()
con.close()

outputFile = "osmdata/massachusetts-latest.osm.bz2"

if ( os.path.isdir("temp") == False) :
  os.mkdir("temp")

os.system("rm temp/*")

# if you are not using debian, these files are probably not at this path.
if (os.system("psql gis -f /usr/share/doc/osmosis/examples/pgsnapshot_schema_0.6.sql")):
  print("Error loading pgsnapshot_schema_0.6.sql into into postGIS gis database.")
  sys.exit(1)

if (os.system("psql gis -f /usr/share/doc/osmosis/examples/pgsnapshot_schema_0.6_linestring.sql")):
  print("Error loading pgsnapshot_schema_0.6_linestring.sql into postGIS gis database.")
  sys.exit(1)

# load osm file into postGIS
if ( os.system("bzcat " + outputFile + " | osmosis --read-xml - --wp user=\"mapping\" database=\"gis\""  ) ) :
  print("Error loading " + outputFile + " into postGIS gis database.")
  sys.exit(1)

print("Success!!")






