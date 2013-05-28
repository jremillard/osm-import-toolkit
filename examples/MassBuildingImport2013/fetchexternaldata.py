#!/usr/bin/python

import urllib
import os
import zipfile
import glob

# Got this script from somebody on the osm talk-us list and hacked it up. My changes
# to the script are public domain.
#
# copies all building shape files from massgis, unzips them, and puts them into externaldata.

outputDir = "externaldata"

if ( os.path.isdir(outputDir) == False) :
  os.mkdir(outputDir)

os.system("rm " + outputDir + "/*")

base = "http://wsgw.mass.gov/data/gispub/shape/structures/structures_poly_"

def download():
    for i in range(1,352):
        i=str(i)
        n = i+".zip"
	localname = outputDir + "/buildings_" + n
        b=base+n
        urllib.urlretrieve(b,localname)
        print "downloaded town " + i
        st=os.stat(localname)
        if st.st_size>0:
            try :
                z=zipfile.ZipFile(localname,"r")
            except:
                urllib.urlretrieve(b,localname)
                z=zipfile.ZipFile(localname,"r")

            zl=z.namelist()
            z.extractall(outputDir)
            z.close()
        os.remove(localname)
if __name__ == "__main__":
    download()
