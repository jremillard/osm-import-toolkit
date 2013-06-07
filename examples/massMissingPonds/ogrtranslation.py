'''
A translation function for ogr2osm, All it does is remove empty tags, can't
seem to figure out how to do that from the ogr2shp script.
'''

def filterTags(attrs):
  if not attrs:
    return
  tags = {}
 
  for tag in attrs :
    if attrs[tag] != '' : 
      tags[tag] = attrs[tag]
     
  return tags



