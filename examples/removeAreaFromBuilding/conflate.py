#!/usr/bin/python

# Jason Remillard - This file is in the public domain.

import psycopg2
import sys
import xml.etree.cElementTree as ElementTree

con = psycopg2.connect(database='gis') 
cur = con.cursor()

cur.execute("select id,version,akeys(tags),avals(tags),nodes from ways where tags @> 'area=>yes'::hstore and tags ? 'building'")

output_root = ElementTree.Element('osmChange', {'version':'0.3' })
output_tree = ElementTree.ElementTree(output_root)
output_op = ElementTree.SubElement(output_root, 'modify')

count = 0
while True: 
  row = cur.fetchone()

  wayid = row[0]
  version = row[1]

  output_way = ElementTree.SubElement(output_op, 'way', { 'id':str(wayid), 'version':str(version) })

  ids = row[4]
  
  for v in ids:
    ElementTree.SubElement(output_way, 'nd', { 'ref':str(v) })

  tags = row[2]
  values = row[3]

  for index,tag in enumerate(tags):
    if ( tag == "source" and values[index] == "MassGIS Buildings (http://www.mass.gov/mgis/lidarbuildingfp2d.htm)" ) :
      values[index] = "MassGIS Data - Building Footprints (2-D, from 2002 LiDAR data)"
       
    if ( tag == "area" and values[index] == "yes" ) :
      # eat it
      False
    else:
      ElementTree.SubElement(output_way, 'tag', { 'k':tag,'v':values[index] })

  count += 1
  # just first 10 for now
  if ( count > 10 ) : 
    break
  
cur.close()
con.close()

output_tree.write("output.osc", "utf-8")






