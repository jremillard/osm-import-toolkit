Open Street Map Importing and Mechanical Edit Toolkit
==================

Please read and follow the OSM import guidelines here, here, and here, 
no seriously, go read them.

- http://wiki.openstreetmap.org/wiki/Import/Guidelines
- http://wiki.openstreetmap.org/wiki/Mechanical_Edit_Policy
- http://wiki.openstreetmap.org/wiki/Automated_Edits_code_of_conduct

There is a lot of software spread here and there for doing mechanical 
edits and import of Open Street Map data. The goal of this repository 
is to collect best scripts written by myself and others for doing 
imports and mechanical edits and to provide technical documentation 
on the actual process.

Table of Contents
----------------------
[The Process](#process)
[Why Automation Is So Important](#automation)
[Breaking It Down](#steps)
[Obtaining/Fetching Data](#fetch)
[Loading Data into PostGIS](#loading)
[OSM Preparation](#prep)
[Conflating](#conflate)
[Uploading](#upload)
[Environment](#env)

<a name="process"/>
The Process
-----------------

There are many different ways of doing imports and mechanical edits. 
The import documentation on the OSM wiki is necessarily prescriptive to cover 
the wide variety of possible imports. It also needs to cover the 
wide variety of community norms across OSM. The same import might 
be accepted with open arms in one region and be totally unacceptable 
in another region. In practice, some regions of OSM will not accept any 
kinds imports or mechanical edits. Also, you need to be aware that some
members of OSM oppose all imports. Therefor, it is a difficult task to 
document "one" import policy across all of OSM. 

This documentation is descriptive, like a recipe, that if followed 
should provide good results. It is just one path of many to success. 

Import and mechanical edits are hard. They are not hard, like you need
to be a genius to do it. They are hard because they require unusual 
mix of knowledge. To do an import, I believe you need ...

 - Mastery of the OSM data model. You must know how points, ways, and 
relations relate to each other and how they are used in practice to 
model the world. You should be able to read and understand a .osm file
opened in a text editor. Get yourself comfortable mapping roads, houses, address, routes, 
lakes with islands, point of interests, sidewalks, trees, traffic lights,
benches, trails, turn restrictions, doors, stairs, fences, gates, etc. Try mapping in 
all of the editors, JOSM, potlatch, id, etc. In practice, you need to 
do a big pile of normal mapping first. I suggest at least 150 change sets over 6 months. 

 - Ability to do basic programming/scripting. Small imports 
can be done quite well with JOSM and QGIS, but when the data gets larger, an 
entirely different set of tools ends up being required. Larger imports
become a programming/data processing protect. If programming is not your 
thing, just team up with somebody. If your data is very small, then you 
probably don't need this toolkit.

 - Patience and attention to detail. 

<a name="automation"/>
Why Automation Is So Important
--------------------------

You have hopefully noticed that community feedback is central 
to the OSM importing process. In practice this means a bunch of 
people asking you to make changes to your output files! If your 
work flow is automated, changes can be incorporated quickly, 
with consistency and repeatability. If it takes 3 hours, 
and 1000 mouse clicks to produce your output files, it will 
be very difficult to openly accept community input. 

OSM itself is always changing. If your process is automated, fresh 
OSM data can be imported just before the actual upload, minimizing
the chances of things getting out of sync.

This is not intuitive. It is easy to think of the import as only 
being done once, so it seems like it might not be worth the time
to automate it. However, it is really done 25 times as practice. 
Even the final uploading step should be practiced on the 
development server.

The tools in this repository are python scripts, so that you can 
fully automate your process. The example scripts are designed to
not accept any command line arguments or do any kind of user
prompting. This insures that the import process is repeatable. 

<a name="steps"/>
Breaking It Down
------------------------

All imports and mechanical edits, can be broken down to the following steps.

 - Obtaining/fetching external data - Getting your hands on the third party 
data source. For a edit bot, this step is skipped. 

 - Obtaining/fetching OSM data - Most imports and mechanical edits need 
to consider the data that is already in the OSM database. OSM data must
be downloaded.

 - Loading data into PostGIS - The data needs to be transformed into a 
format that makes it convenient to do the conflation. Normally, this means 
loading it into a PostGIS database and getting everything reprojected 
into the same coordinate system.

 - Conflating - This is the step that merges the existing OSM data, 
with the external data, and outputs the changes to be made to OSM. 

 - Conversion for uploading - The OSM servers have a limit on the 
upload size, the output files will need to be subdivided before uploading.
If your output data is not in .osc file, then it will need 
to be converted before uploading.

 - Uploading - Doing the actual upload to the OSM servers. 

<a name="fetch"/>
Obtaining/Fetching Data
----------------------------

Downloading the source and OSM data should be automated. The OSM data will 
change over the coarse of the import project and will require re downloading 
many times. 

The source data might be updated in the middle of the import. If possible its 
downloading should be automated. This is not always possible. The data may be 
delivered to you on CD, email, or the data provider might have a user 
friendly, web 2.0, facebook enabled web site that makes it impossible 
to download the data in bulk via a simple url. Do your best here.

The OSM data extract downloading can always be automated. The recommended source 
for regional OSM extracts is http://download.geofabrik.de/. 

The wget utility can be used to download OSM extracts and external data. 
If the data is in a zip file, the standard python environment provides code 
to unzip source files.

In the examples directories please look at the fetchexternaldata.py, 
and fetchosmdata.py files for example code.

<a name="loading"/>
Loading Data into PostGIS
------------------------------------

There are many possible way of loading .osm files into a PostGIS
database. The two main tools are osmosis and the osm2pgsql. 

osm2pgsql - It can only be used for purely additive imports. 
 - It will setup the schema itself.
 - It will work without having postGIS setup for network access.
 - It is fast.
 - The schema is very easy to use.
 - Defaults to the 900913 coordinate system.
 - Lossy, only common tags are imported.
 - Can't use osm2pgsql to change existing OSM data. No edit bots and no 
complicated conflation logic is possible. It does not have enough 
information to directly write out a change file. Only additive 
imports can use osm2pgsql.

Getting osm2pgsql requires the following steps.
 1. Make a postGIS user that is a super user with the same name as the Linux user account.
 2. Make a database owned by the new postGIS user called "gis". 
 3. Install PostGIS postgis.sql and spatial_ref_sys to gis database.

osmosis - Can be used for any kind of importing/bod activity.
 - It supports many kind of schema that need to be setup before hand. 
 - The best schema's for imports snapshotdb require an Postgresql extension. 
 - It is slow to actually import the data. 
 - It can only talk to PostGIS via a network connection. Even when 
running locally, a network loop back connection must be enabled. 
 - The schema is harder to use. Relations and ways are not mashed together. 
 - It is not lossy, sophisticated conflation logic is possible. 
 - Edit bots are possible
 - Uses the 4326 coordinate system.

Getting osmosis ready to import an extract is more complicated. At 
a high level the following steps are required. 

 1. Make a postGIS user that is a super user with the same name as linux user account.
 2. Make a database owned by the new postGIS user called "gis". 
 3. Install PostGIS postgis.sql and spatial_ref_sys to gis database.
 4. Install hstore extension to gis database.
 5. Enabled network access in PostGIS
 6. Setup schema for pgsnapshot to gis database.
 7. Setup linestring support for pgsnapshot to gis database. 

After the OSM extract has been imported, next the external 
data must be imported so that you can use the PostGIS SQL operations 
between the OSM data and external data. They need in the same 
coordinate system. The osm2pgsql tool imports the OSM data as 900913, the 
osmosis uses 4326. Before you import the external data it must be 
reprojected to either 4326 or 900913.

There are many formats that the external data might be provided in. But, if 
your external data is a .shp (shape) file, then the shp2pgsql tool can be used. 

In the examples directories please look at the postgisloaddata.py for 
example code.

http://wiki.openstreetmap.org/wiki/Database_schema#Database_Schemas. 

<a name="prep"/>
OSM Preparation
------------------

Sometimes it is easier to fix errors in the existing OSM data, rather
than having very complicated conflation logic. These scripts run QA 
checks for some common OSM errors that could otherwise complicate 
conflation processing. 

They all require a osm2pgsql PostGIS database, 
ogr2ogr, and ogr2osm.

 - prep/findaerowwaywithnobuildings.py - Find all aeroway=terminal areas 
that don't also have building=* tag. Building import conflation/merging 
logic that is only using building=* tag, will fail on airport terminals 
that are just tagged with aeroway=terminal. Use this script to fix the
terminals before the import.

 - prep/findschoolswithnobuildings.py - Find all amenity=school areas 
without a building=* tag. Not necessarily an error, but could indicate 
that a school building was tagged with amenity=school without the 
building tag. Building import conflation/merging logic that is only 
using for building=* tag will fail on schools buildings that are just 
tagged with amenity=school. Use this script is used to inspect, and 
fix any incorrectly tagged schools before the import.

 - prep/findoverlappingbuildings.py - Find all overlapping buildings. 
After an import containing buildings, run this script to insure that 
data was not uploaded twice. It is suggested to run it before a 
building/address import to baseline the OSM data in the area. 

 - prep/findlandusereservoir.py - Find all of the ways that use 
landuse=reservoir without a natural=water tag. The 
http://wiki.openstreetmap.org/wiki/Reservoir says that using 
the landuse tag this way is deprecated, unless it is an underground 
reservoir. An image layer will need to checked for actual water.

<a name="conflate"/>
Conflating
---------------------

This is the meat of the import/mechanical edit task. It is hard to talk about 
this generically. Each kind of data, building, addresses, roads, hydrology, 
point of interest, etc have specific issues that need to be handled. The 
/docs directory of the repository has a document for each type import.

 - QA the output files as much as you can stand. Even an intensive community 
review of your sample output files will probably only find half of the problems. 
You need to find the other half yourself. 

 - Most conflation scripts will encounter ambiguous situations. It is better to be 
incomplete, or imprecise than wrong. If something can't be merged correctly 
just leave it out. Incomplete is not wrong. Put it into a separate file that 
to be merged by hand if you feel it is important to import all of the data.

 - Figuring out how to conflate will require that you have a good handle on 
the quality of the external data first. Often different OSM data schema 
imply different levels of uncertainties. For example, 
putting an address on doorway node implies a high level 
of accuracy, whereas, linear address interpolation way much less so. Your 
output data should have the correct OSM schema that reflects the 
actual uncertainty of your source data. Know your external data!

 - The conflation output should try to look like the data was mapped by hand.
In practice, this means shying away from importing data that does not have an 
established tagging system. If the data was important, you can be pretty 
sure that a tag (or two) would exist for it by now. If somebody needs it, 
they can always go to the same source files you used for your import and 
match them to the OSM data. Making the output data look like normal mapping
will improve your chances of getting the import accepted by the community.

 - The import conflation logic should be "stateless". You should 
be able to re-run the conflation work flow after you have finished the final upload 
and get an empty output file. It also means, you should should be 
able to stop half way through your upload, wait 2 months, reprocess everything from scratch 
and have the script correctly pick up the remaining work. Sometimes
conflicts with other mappers might not be detected until the actual upload. If the 
processing is stateless, you simply ignore the failed upload, and reprocess 
the data again at a later date.

In the examples directories please look at the conflate.py for 
example code. The docs directory has documentations specific to 
different kinds of imports.

<a name="upload"/>
Uploading 
-----------------

change set
change set size

development server
revert JOSM plugin 
conflicts
random failures
slow speed

 - upload/osm2osc.py - Many of the utilities that convert external data to 
OSM write out an .osm file. However, only .osc files can be uploaded. 
This simple utility converts an .osm to .osc. This is basically 
unmodified from the version in OSM SVN.

 - upload/osmsplit.py - Breaks an .osc file into several smaller .osc files. 
The OSM API has a 50,000 element limit for a single change set. In practice, 
the change sets should be kept much smaller, around 10,000 elements. Therefor, 
before uploading large .osc files, they need to be broken up. The smaller 
.osc files generated by this script are self contained without cross 
dependencies. The lack of dependencies means files can be uploaded in any 
order and errors in the uploads can be easily handled.

 - upload/osmupload.py - Uploads a set of .osc files into a server that 
supports the OSM API. This is a heavily modified version of the upload.py 
script that is hosted on the OSM SVN server. It keeps a log of the uploads, 
supports testing uploads to the development server, does not use "chunks", 
so that each .osc file upload is atomic, allows comment and source tags 
on the change set to be pulled from files, will not double upload a file, 
and will try hard to always close out a change set if an error occurs. 
The log holds the change set ids, so it is possible to review an already 
completed upload.

<a name="env"/>
Environment
-----------------

This toolkit requires many other tools. Many are included standard 
in Debian Linux and are trivial to install. If Windows is your 
primary operating system, it is recommended to install Debian Linux 
into a virtual machine, like Oracle's busybox http://www.busybox.net/,
 and run the tools inside of the virtual machine. 

 - PostGIS - http://postgis.org/ - PostGIS is an extension to 
PostgreSQL that adds support for common GIS operations via SQL. 
When the import or mechanical edit needs to make decisions based 
on existing OSM data the processing is done in SQL rather than 
processing the .osm/.xml file directly. If possible, use the default 
database name of gis.

 - osm2pgsql - Very simple way of importing OSM extract to a PostGIS 
database. 

 - osmosis - Used to import OSM extracts, make custom extracts, and filter
OSM files by tag.

 - ogr2ogr - http://www.gdal.org/ - Is part of the gdal project. 
It it used to re-project source data and to extract data back out 
from a PostGIS database. Currently gdal does not support the 
.osm file well. This toolkit will use ogr2osm with .shp (shape) 
files, then use ogr2osm to convert from a .shp file to .osm file.

 - ogr2osm - https://github.com/pnorman/ogr2osm - This utility 
converts .shp to .osm files. It is currently not packaged as 
part of Debian. It will need to be installed manually. You 
have the option of installing it anywhere and adding to your 
path, or installing it in ./ogr2osm. Where ./ is the root of 
this repository. The tools will first check if it is ./ogr2osm, 
then try the path. To "install" it into ./org2osm run the 
following git command.

    git clone https://github.com/pnorman/ogr2osm.git


