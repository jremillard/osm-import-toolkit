#! /usr/bin/python
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

"""
Splits an Open Street Map change files (OSC) into smaller OSC files. Useful 
for making a large OSC file fit into the 50,000 element change set limit
that Open Street Map servers have.

The OSC file format is documented here. http://wiki.openstreetmap.org/wiki/OsmChange
This scripts supports v0.3 and v0.6.
"""

import os
import sys
import traceback
import optparse
import shutil
import math

import xml.etree.cElementTree as ElementTree

def chunkSortByLon( chunk ) :
    lon = 0
    for member in chunk['members'] :
	if ( member['tag'] == 'node' ) :
	   lon = member['element'].attrib.get("lon") 
    return lon

def writeChunk( oscGraph,part_op,chunk,operation,tag) :
    for node in chunk['members'] : 
        if ( node['tag'] == tag and
             node['operation'] == operation) :
            part_op.append(node['element'])

def assignChunk( oscGraph, key, chunkNumber ) :
    if ( oscGraph[key]['chunkAssignment'] >= 0 ) : 
        return 0

    oscGraph[key]['chunkAssignment'] = chunkNumber
    assignCount = 1

    for parent in oscGraph[key]['parents'] :
        assignCount += assignChunk( oscGraph,parent,chunkNumber)

    for child in oscGraph[key]['children'] :
        assignCount += assignChunk( oscGraph,child,chunkNumber)
    return assignCount

def splitOSC( filename, outputDir, maxElements) :
    print "   " + filename + " ",
    tree = ElementTree.parse(filename)
    root = tree.getroot()

    oscGraph = {}
    if root.tag != "osmChange" or (root.attrib.get("version") != "0.3" and
            root.attrib.get("version") != "0.6"):
        print >>sys.stderr, u"File %s is not a v0.3 or v0.6 osmChange file!" % (filename,)
        sys.exit(1)
       
    # setup nodes in connectivity graph
    for operation in root:        
        for element in operation:
            key = element.tag + element.attrib.get("id")
            # chunkAssignment < 0 not assigned yet.
            if ( operation.tag == 'create' ) : 
                oscGraph[key] = { 
			'tag' : element.tag, 
			'operation': operation.tag,
			'children' : [] , 
			'parents' : [], 
			'chunkAssignment' : -1, 
			'element' : element  
		}
            else :
                print >>sys.stderr, u"File %s: Only creating elements supported for now. Sorry no %s." % (filename,operation.tag)
                sys.exit(1)
                
    # make connections between nodes
    for operation in root:        
        for element in operation:
            key = element.tag + element.attrib.get("id")

            if ( element.tag == 'way' ) : 
                for child in element:
                    if ( child.tag == 'nd') :
                        childKey = 'node' + child.attrib.get("ref")
                        oscGraph[key]['children'].append( childKey)
                        oscGraph[childKey]['parents'].append(key)
            elif ( element.tag == 'relation' ) :
                 for child in element:
                    if ( child.tag == 'member') :
                        childKey = child.attrib.get("type") + child.attrib.get("ref")
                        oscGraph[key]['children'].append( childKey)
                        oscGraph[childKey]['parents'].append(key)

    # assign chunks to each element, keep track of how many elements are in each
    # chunk so we know how to split them. A chunk is a set of ways, nodes, relations
    # that point to each other. These "chunks" can't be broken across changesets
    # files without creating dependencies between uploads.
    chunks = []
    nextChunk = 0;
    
    for key in oscGraph : 
        if ( oscGraph[key]['chunkAssignment'] < 0 ) :
	    numberOfElementsInChunk = assignChunk( oscGraph,key,nextChunk)
            chunks.append( { 'count': numberOfElementsInChunk, 'members' : [] })
            nextChunk += 1

    # build list of elements in each chunk for faster access when writing files out
    # it is too slow to crawl through the graph for every chuck write
    for key in oscGraph : 
	chunks[oscGraph[key]['chunkAssignment']]['members'].append(oscGraph[key])

    # sort the chucks so the output files are not random located
    chunks = sorted(chunks, key=chunkSortByLon )

    totalElements = 0.0
    for chunk in chunks : 
        totalElements += chunk['count']
        
    files = int(math.ceil( totalElements / maxElements))
    if ( files > 0 ) :
    	averageElementsPerFile = int(math.ceil(totalElements/files))
    else :
	# empty change set file.
    	averageElementsPerFile = 1
	files = 1

    if ( files == 1 ) :
        shutil.copyfile(filename, outputDir + filename.split("/")[-1]) 
    else :
	
	# figure out what chunks go in what files
	chunksInFiles = [ [] ]
	currentFileSize = 0
        for chunk in chunks :
            if ( currentFileSize > 0 and currentFileSize+chunk['count'] > maxElements ) :
	        chunksInFiles.append([])
                currentFileSize = 0
	    
            chunksInFiles[-1].append( chunk)
	    currentFileSize += chunk['count']

	    if ( currentFileSize > maxElements) :
	        print >>sys.stderr, u"File %s: has a set of changes that is larger than the limit." % (filename)


	for fileIndex in range( 0,len(chunksInFiles)) :

            filename_base = filename[:-4].split("/")[-1];
            outputFilename = "%s%s-part%04i.osc" % (outputDir,filename_base, fileIndex)

	    # if input file is v0.3, then the output file will be v0.3
            part_root = ElementTree.Element('osmChange', {'version':root.attrib.get("version")})
            part_tree = ElementTree.ElementTree(part_root)

            part_op = ElementTree.SubElement(part_root, 'create')
	    for chunk in chunksInFiles[fileIndex] :
		writeChunk( oscGraph,part_op,chunk,'create','node')
            	writeChunk( oscGraph,part_op,chunk,'create','way')
            	writeChunk( oscGraph,part_op,chunk,'create','relation')

            part_op = ElementTree.SubElement(part_root, 'modify')
	    for chunk in chunksInFiles[fileIndex] :
		writeChunk( oscGraph,part_op,chunk,'modify','node')
            	writeChunk( oscGraph,part_op,chunk,'modify','way')
            	writeChunk( oscGraph,part_op,chunk,'modify','relation')

            part_op = ElementTree.SubElement(part_root, 'delete')
	    for chunk in chunksInFiles[fileIndex] :
		writeChunk( oscGraph,part_op,chunk,'delete','relation')
            	writeChunk( oscGraph,part_op,chunk,'delete','way')
            	writeChunk( oscGraph,part_op,chunk,'delete','node')

            part_tree.write(outputFilename, "utf-8")

	print ""

try:
    parser = optparse.OptionParser(description='Splits an Open Street Map change set file (OSC) into smaller OSC files.',usage='osmsplit.py [options] uploadfile1.osc')

    parser.add_option(
        '--outputDir',
        help='output directory for split files',
        dest='outputDir',
        default='.')
    parser.add_option(
        '--maxElements',
        help='maximum elements in each output OSC file',
        dest='maxElements',
        type='int',
        default=10000)

    (param,filenames) = parser.parse_args()

    outputDir = param.outputDir
    if ( param.outputDir and outputDir[-1] != '/') :
	outputDir = outputDir + '/'	
	
    for filename in filenames:
        splitOSC( filename, outputDir, param.maxElements)
 
except Exception,err:
    print >>sys.stderr, repr(err)
    traceback.print_exc(file=sys.stderr)
    sys.exit(1)
