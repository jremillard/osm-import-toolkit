#!/usr/bin/python

# Jason Remillard - This file is in the public domain.

import psycopg2
import sys
import xml.etree.cElementTree as ElementTree
import os

if ( os.path.isdir('stage') == False) :
  os.mkdir('stage')

os.system("rm stage/*.osc")

con = psycopg2.connect(database='gis') 
cur = con.cursor()

cur.execute(
 "select "
 "  id, "
 "  version, " 
 "  akeys(tags), "
 "  avals(tags), "
 "  nodes, "
 "  massgis_il.waterbody "
 "from ways "
 "left join massgis_il on " 
 "  tags -> 'massgis:PALIS_ID' = massgis_il.watercode " 
 "where "
 "  tags @> 'natural=>water'::hstore")

output_root = ElementTree.Element('osmChange', {'version':'0.6' })
output_tree = ElementTree.ElementTree(output_root)
output_op = ElementTree.SubElement(output_root, 'modify')

count = 0
fileCount = 1;
row = cur.fetchone()

while row is not None: 

  wayid = row[0]
  version = row[1]

  tags = row[2]
  values = row[3]
  ids = row[4]
  name = row[5]

  editWay = False
  hasName = False

  for index,tag in enumerate(tags):    
    if ( tag.find("massgis:") == 0) :
      editWay = True
    if ( tag == "name") :
      hasName = True

  if ( editWay and hasName == False and name != None) :

    output_way = ElementTree.SubElement(output_op, 'way', { 'id':str(wayid), 'version':str(version) })

    for v in ids:
      ElementTree.SubElement(output_way, 'nd', { 'ref':str(v) })

    for index,tag in enumerate(tags):    
      if ( tag == "area" and values[index] == "yes" ) :
        # eat it
        False
      elif ( tag == "source" and values[index] == "DEP Wetlands (1:12,000) - April 2007 (http://www.mass.gov/mgis/wetdep.htm)") :
        # eat it
        False
      elif ( tag.find("massgis:") == 0) : 
        # eat it
        False
      else:
        ElementTree.SubElement(output_way, 'tag', 
          { 'k':tag.decode('utf-8'),'v':values[index].decode('utf-8') })
    
    if ( hasName == False and name != None) :
      ElementTree.SubElement(output_way, 'tag', 
        { 'k':'name','v':name.decode('utf-8') })

    count += 1

    # 2000 elements per file
    if ( count > 2000 ) : 
      filename = "stage/water-nomassgis-%04i.osc" % (fileCount)
      output_tree.write(filename, "utf-8")
      fileCount += 1;
      count = 0

      output_root = ElementTree.Element('osmChange', {'version':'0.3' })
      output_tree = ElementTree.ElementTree(output_root)
      output_op = ElementTree.SubElement(output_root, 'modify')

  row = cur.fetchone()

cur.close()
con.close()

filename = "stage/water-nomassgis-%04i.osc" % (fileCount)
output_tree.write(filename, "utf-8")




