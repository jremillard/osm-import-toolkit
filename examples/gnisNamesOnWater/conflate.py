#!/usr/bin/python

# Jason Remillard - This file is in the public domain.

import psycopg2
import sys
import xml.etree.cElementTree as ElementTree
import os


con = psycopg2.connect(database='gis') 
cur = con.cursor()

cur.execute(
  "CREATE TEMP TABLE water (id bigint, palisid text, name text); "
  "SELECT AddGeometryColumn( '', 'water', 'geom', 4326, 'POLYGON', 2); "
  "CREATE INDEX idx_water_geom ON water USING gist (geom); "
  );

cur.execute(
  "INSERT into water( id, name, palisid, geom) "
  "  select "
  "    id, " 
  "    tags::hstore -> 'name', "
  "    tags::hstore -> 'massgis:PALIS_ID', "
  "    ST_BuildArea(ways.linestring) "
  "  from ways "
  "  where "
  "    tags @> 'natural=>water'::hstore and "
  "    ST_IsValid( ST_BuildArea(ways.linestring) ) and "
  "    ST_BuildArea(ways.linestring) is not null;"
  );

cur.execute(
  "select " 
  "  water.name, "
  "  massgis_il.waterbody, "
  "  gnis.name as gnis_name "
  "from water "
  "left join gnis on " 
  "  ST_Intersects(water.geom,gnis.geom) " 
  "left join massgis_il on " 
  "  water.palisid = massgis_il.watercode "
  );

row = cur.fetchone()

missingName = 0
newName = 0
existingName = 0
differentName = 0

while row is not None: 

  line = ''
  if ( row[0] != None ) :
    line += row[0]
  line += ","
  if ( row[1] != None ) :
    line += row[1]
  line += ","
  if ( row[2] != None ) :
    line += row[2]

  if ( row[0] != None or row[1] != None or row[2] != None ) :
    if( row[0] != None ) :
      existingName += 1
    else:
      newName += 1
      
    #print(line)

    if (row[0] != None and row[1] != None and row[0] != row[1] ) :
      print line
      differentName += 1
      
    if (row[1] != None and row[2] != None and row[1] != row[2] ) :
      print line
      differentName += 1

    if (row[0] != None and row[2] != None and row[0] != row[2] ) :
      print line
      differentName += 1

  else:
    missingName += 1

  row = cur.fetchone()

print("no name count %d" % (missingName))
print("new name count %d" % (newName))
print("different count %d" % (differentName))
print("same name count %d" % (existingName-differentName))


