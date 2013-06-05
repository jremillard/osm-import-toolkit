'''
A translation function for ogr2osm pond import, basiclly remove empty name tags, can't
seem to figure out how to do that from the ogr2shp script.
'''

def filterTags(attrs):
    if not attrs:
        return
    tags = {}

    # Names
    if 'name' in attrs and attrs['name'] != '' :
        tags['name'] = attrs['name']
    tags['natural'] = attrs['natural']
    tags['water'] = attrs['water']

    return tags



