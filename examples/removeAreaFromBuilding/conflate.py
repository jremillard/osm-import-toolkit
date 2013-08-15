#!/usr/bin/python

# Jason Remillard - This file is in the public domain.

import psycopg2
import sys
import xml.etree.cElementTree as ElementTree
import os

os.system("rm stage/*.osc")

def removeSourceAndAreaTag() :

  con = psycopg2.connect(database='gis') 
  cur = con.cursor()

  cur.execute(
    "select id,version,akeys(tags),avals(tags),nodes "
    "from ways "
    "where "
    "  tags @> 'source=>\"MassGIS Buildings (http://www.mass.gov/mgis/lidarbuildingfp2d.htm)\"'::hstore and "
    "  tags ? 'building'")

  output_root = ElementTree.Element('osmChange', {'version':'0.6' })
  output_tree = ElementTree.ElementTree(output_root)
  output_op = ElementTree.SubElement(output_root, 'modify')

  count = 0
  fileCount = 1;
  row = cur.fetchone()

  while row is not None: 

    wayid = row[0]
    version = row[1]

    output_way = ElementTree.SubElement(output_op, 'way', { 'id':str(wayid), 'version':str(version) })

    ids = row[4]
  
    for v in ids:
      ElementTree.SubElement(output_way, 'nd', { 'ref':str(v) })

    tags = row[2]
    values = row[3]

    for index,tag in enumerate(tags):    
      if ( tag == "area" and values[index] == "yes" ) :
        # eat it
        False
      elif ( tag == "source" ) :
        # eat it
        False
      else:
        ElementTree.SubElement(output_way, 'tag', 
          { 'k':tag.decode('utf-8'),'v':values[index].decode('utf-8') })

    count += 1

    # 2000 elements per file
    if ( count > 2000 ) : 
      filename = "stage/with-bad-source-%04i.osc" % (fileCount)
      output_tree.write(filename, "utf-8")
      fileCount += 1;
      count = 0

      output_root = ElementTree.Element('osmChange', {'version':'0.3' })
      output_tree = ElementTree.ElementTree(output_root)
      output_op = ElementTree.SubElement(output_root, 'modify')

    row = cur.fetchone()

  cur.close()
  con.close()

  filename = "stage/with-bad-source-%04i.osc" % (fileCount)
  output_tree.write(filename, "utf-8")

def removeJustAreaTag() :

  con = psycopg2.connect(database='gis') 
  cur = con.cursor()

  cur.execute(
    "select id,version,akeys(tags),avals(tags),nodes "
    "from ways "
    "where "
    "  not tags @> 'source=>\"MassGIS Buildings (http://www.mass.gov/mgis/lidarbuildingfp2d.htm)\"'::hstore and "
    "  tags ? 'building' and "
    "  tags ? 'area'")

  output_root = ElementTree.Element('osmChange', {'version':'0.3' })
  output_tree = ElementTree.ElementTree(output_root)
  output_op = ElementTree.SubElement(output_root, 'modify')

  row = cur.fetchone()
  while row is not None: 
    
    wayid = row[0]
    version = row[1]

    output_way = ElementTree.SubElement(output_op, 'way', { 'id':str(wayid), 'version':str(version) })

    ids = row[4]
  
    for v in ids:
      ElementTree.SubElement(output_way, 'nd', { 'ref':str(v) })

    tags = row[2]
    values = row[3]
       
    for index,tag in enumerate(tags):    
      if ( tag == "area" and values[index] == "yes" ) :
        # eat it
        False
      else:
        ElementTree.SubElement(output_way, 'tag', 
          { 'k':tag.decode('utf-8'),'v':values[index].decode('utf-8') })
  
    row = cur.fetchone()

  cur.close()
  con.close()

  output_tree.write("stage/extra-area-leave-source.osc", "utf-8")


removeSourceAndAreaTag()
removeJustAreaTag()



