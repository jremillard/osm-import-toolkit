#!/usr/bin/python

import urllib
import os
import zipfile
import glob

# Got this script from somebody on the osm talk-us list and hacked it up. My changes
# to the script are public domain.
#
# copies all building shape files from massgis, unzips them, and puts them into srcdata/massgis.

if ( os.path.isdir("srcdata") == False) :
  os.mkdir("srcdata")

if ( os.path.isdir("srcdata/massgis") == False) :
  os.mkdir("srcdata/massgis")

os.system("rm srcdata/massgis/*")

base = "http://wsgw.mass.gov/data/gispub/shape/structures/structures_poly_"

def download():
    for i in range(1,352):
        i=str(i)
        n = i+".zip"
	localname = "srcdata/massgis/buildings_" + n
        b=base+n
        urllib.urlretrieve(b,localname)
        print "working " + i
        st=os.stat(localname)
        if st.st_size>0:
            z=zipfile.ZipFile(localname,"r")
            zl=z.namelist()
            z.extractall("srcdata/massgis")
            z.close()
        os.remove(localname)
if __name__ == "__main__":
    download()
