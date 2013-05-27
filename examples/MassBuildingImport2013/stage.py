#LISCENSE
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

#INTRODUCTION
# This program serves as an interface with the bulk
# uploader program. It allows one to specify a directory
# containing multiple osm files and have them all uploaded at
# once. Please use this program carefully and reach a
# a community consensus before massive imports.
# ~ingalls

#REQUIREMENTS
# Python2
# Python3

import os
import shutil
import sys
import optparse

rootLoc = os.getcwd()
version = "0.2"
fileLoc = ""
comment = ""
num = 0
	
#print "Enter Source Directory (Press enter for current)"
#fileLoc = raw_input(":")
sourceFiles = "src/"
outputFiles = "upload/"

#print "Enter Changeset Comment"
#comment = raw_input(":")
comment = 'Imported MassGIS Building Structures - %%filename%% - 4th data set';
source = 'Building Structures (2-D, from 2011-2012 Ortho Imagery) - Office of Geographic Information (MassGIS), Commonwealth of Massachusetts, Information Technology Division';

if not os.path.exists(rootLoc + "/" + outputFiles):
    os.makedirs(rootLoc + "/" + outputFiles)

for osmfile in os.listdir(sourceFiles): 
    if osmfile.endswith(".osm"):
        fullOsmFile = sourceFiles + osmfile
        smallOutputStatusFile = outputFiles + osmfile[:-4] + "-status.txt"
        largeOutputStatusFile = outputFiles + osmfile[:-4] + "-part0000-status.txt"

        if ( not os.path.exists(smallOutputStatusFile) and not os.path.exists(largeOutputStatusFile) ) :

            print("converting to osc: " + fullOsmFile)
            r = os.system("python3.1 osm2osc.py " + fullOsmFile)
            if ( r ) :
               sys.exit(1)

            fullOSCFile = fullOsmFile[:-4] + ".osc"

            # clean out older OSC files, may have changed maxElements up or down.
            if ( os.path.exists( outputFiles + osmfile[:-4] + ".osc" ) ) :
                os.remove( outputFiles + osmfile[:-4] + ".osc")
                os.remove( outputFiles + osmfile[:-4] + ".comment")
                os.remove( outputFiles + osmfile[:-4] + ".source")

            fileCount = 0
            while ( os.path.exists( outputFiles + osmfile[:-4] + "-part%04d.osc" % (fileCount,) )) :
                os.remove( outputFiles + osmfile[:-4] + "-part%04d.osc" % (fileCount,) ) 
                os.remove( outputFiles + osmfile[:-4] + "-part%04d.comment" % (fileCount,) ) 
                os.remove( outputFiles + osmfile[:-4] + "-part%04d.source" % (fileCount,) ) 
                fileCount += 1

            print("splitting osc: " + fullOSCFile)
            r = os.system("python osmsplit.py --outputDir " + outputFiles + " --maxElements 10000 " + fullOSCFile)
            if ( r ) : 
                sys.exit(1)
            os.remove( fullOSCFile)
        else :
            print("already uploaded skipping: " + fullOsmFile)

# write out comment and source files.
for oscfile in os.listdir(outputFiles): 
    if oscfile.endswith(".osc"):
        commentFilename = outputFiles + oscfile[:-4] + ".comment"
        if ( not os.path.exists(commentFilename)  ) :
            commentFile = open( commentFilename,"w")
            commentFile.write(comment.replace('%%filename%%',oscfile))
            commentFile.close()

            sourceFilename = outputFiles + oscfile[:-4] + ".source"
            sourceFile = open( sourceFilename,"w")
            sourceFile.write(source)
            sourceFile.close()

	


	



