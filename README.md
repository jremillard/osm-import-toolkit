Open Street Map Importing and Mechanical Edit Toolkit
==================

Please read and follow the OSM import guidelines here below.

- http://wiki.openstreetmap.org/wiki/Import/Guidelines
- http://wiki.openstreetmap.org/wiki/Mechanical_Edit_Policy
- http://wiki.openstreetmap.org/wiki/Automated_Edits_code_of_conduct

There is a lot of software around for doing mechanical 
edits and imports of Open Street Map data. The goal of this repository 
is to collect the best scripts written for doing 
imports and mechanical edits and to provide technical documentation 
on the actual process.

Table of Contents
----------------------
 + [The Process](#process)
 + [Why Automation Is So Important](#automation)
 + [Community](#comm)
 + [Technical - Breaking It Down](#tsteps)
 + [Obtaining/Fetching Data](#fetch)
 + [Loading Data into PostGIS](#loading)
 + [OSM Preparation](#prep)
 + [Conflating](#conflate)
 + [Ongoing Imports](#ongoing)
 + [Building Imports](#buildings)
 + [Change Set Management](#changeset)
 + [Environment](#env)

<a name="process"/>
The Process
-----------------

There are many different ways of doing imports and mechanical edits. 
The import documentation on the OSM wiki is necessarily prescriptive to cover 
the wide variety of possible imports. The OSM wiki also needs to cover the 
wide variety of community norms across OSM. The same import that might 
be accepted with open arms in one region and, then be totally unacceptable 
in another region. In practice, some regions of OSM will not accept any 
kinds of imports or mechanical edits. Also, you need to be aware that some
members of OSM oppose all imports. Therefor, it is a difficult task to 
document "one" import policy across all of OSM. 

This documentation is descriptive, like a recipe, that if followed 
should provide good results. It is just one path, of many, to success 
and does not represent any kind of official OSM policy. 

Import and mechanical edits are hard. They are not hard, like you need
to be a genius to do it, but they are hard because they require an unusual 
mix of knowledge. To do an import, I believe you need ...

 - Mastery of the OSM data model. You must know how points, ways, and 
relations relate to each other and how they are used in practice to 
model the world. You should be able to read and understand an .osm file
opened in a text editor. Get yourself comfortable mapping roads, houses, address, routes, 
lakes with islands, point of interests, sidewalks, trees, traffic lights,
benches, trails, turn restrictions, doors, stairs, fences, gates, etc. Try mapping in 
all of the editors: JOSM, potlatch, ID, etc. In practice, you need to 
do a big pile of normal mapping first. I would suggest at least 150 change sets over 6 months. 

 - Ability to do basic programming/scripting. Small imports 
can be done quite well with JOSM and QGIS, but when the data gets larger, an 
entirely different set of tools ends up being required. Larger imports
become a programming/data processing protect. If programming is not your 
thing, I recommend teaming up with somebody. If your data is very small, then you 
probably don't need this toolkit.

 - Patience and attention to detail. 

<a name="comm"/>
Community
--------------------------

Random hints.

 - If you are not sure about the data license, post a link to the data to the [import mailing list][http://lists.openstreetmap.org/listinfo/imports] and ask for help.

 - Use the [wiki template][http://wiki.openstreetmap.org/wiki/Import/Plan_Outline] to setup your import wiki page. 
 
 - Use the [Who's around me][http://resultmaps.neis-one.org/oooc] to find mappers that might be effected by your import.

 - Use the [Mailing Lists][http://wiki.openstreetmap.org/wiki/Mailing_lists]. 

<a name="automation"/>
Why Automation Is So Important
--------------------------

You have hopefully noticed that community feedback is central 
to the OSM importing process. In practice this means a bunch of 
people asking you to make changes to your output files! If your 
work flow is automated, changes can be incorporated quickly, 
with consistency, and repeatability. If it takes 3 hours, 
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

<a name="tsteps"/>
Technical - Breaking It Down
------------------------

All imports and mechanical edits, can be broken down to the following steps.

 - Obtaining/fetching external data - Get your hands on some third party 
data source. For an edit bot, this step is skipped. 

 - Obtaining/fetching OSM data - Most imports and mechanical edits need 
to consider the data that is already in the OSM database. OSM data must
be downloaded.

 - Loading data into PostGIS - The data needs to be transformed into a 
format that makes it convenient to do the conflation (merging) with 
existing OSM data. Normally, this means loading it into a PostGIS database 
and getting everything reprojected into the same coordinate system.

 - Conflating - This is the step that merges the existing OSM data, 
with the external data, and outputs the changes to be made to OSM. 

 - Conversion for uploading - The OSM servers have a limit on the 
upload size. The output files will need to be subdivided before uploading.
If your output data is not in an .osc file, then it will need 
to be converted before uploading.

 - Uploading - Doing the actual upload to the OSM servers. 

<a name="fetch"/>
Obtaining/Fetching Data
----------------------------

Downloading the source and OSM data should be automated. The OSM data will 
change over the coarse of the import project and will require re downloading 
many times. 

The source data might even even be updated in the middle of the import. If possible, its 
downloading should be automated. However, this is not always possible. The data may be 
delivered to you on CD, email, or the data provider might have a user 
friendly, web 2.0, facebook enabled web site that makes it impossible 
to download the data in bulk via a simple url. Just do your best here.

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

There are many possible ways of loading .osm files into a PostGIS
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

osmosis - Can be used for any kind of importing/bot activity.
 - It supports many kind of schema that need to be setup before hand. 
 - The best schema's for imports, snapshotdb, require an Postgresql extension. 
 - It is slow to actually import the data. 
 - It can only talk to PostGIS via a network connection. Even when 
running locally, a network loopback connection must be enabled. 
 - The schema is harder to use. Relations and ways are not mashed together. 
 - It is not lossy, sophisticated conflation logic is possible. 
 - Edit bots are possible.
 - Uses the 4326 coordinate system.

Getting osmosis ready to import an extract is more complicated. At 
a high level the following steps are required. 

 1. Make a postGIS user that is a super user with the same name as linux user account.
 2. Make a database owned by the new postGIS user called "gis". 
 3. Install PostGIS postgis.sql and spatial_ref_sys to gis database.
 4. Install hstore extension to gis database.
 5. Enabled network access in PostGIS.
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

Sometimes it is easier to fix errors and idiosyncrasies in the existing 
OSM data, rather than having very complicated conflation logic. 
These scripts run QA checks for some common OSM errors that could 
otherwise complicate the conflation processing. 

They all require an osm2pgsql PostGIS database, 
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
using building=* tag will fail on school buildings that are just 
tagged with amenity=school. Use this script to inspect, and 
fix any incorrectly tagged schools before the import.

 - prep/findoverlappingbuildings.py - Find all overlapping buildings. 
After an import containing buildings, run this script to insure that 
data was not uploaded twice. It is suggested to run this before a 
building/address import to baseline the OSM data in the area. 

 - prep/findlandusereservoir.py - Find all of the ways that use 
landuse=reservoir without a natural=water tag. The 
http://wiki.openstreetmap.org/wiki/Reservoir An image 
layer will need to checked for actual water.

<a name="conflate"/>
Conflating
---------------------

This is the meat of the import/mechanical edit task. It is hard to talk about 
this generically. Each kind of data, buildings, addresses, roads, hydrology, 
point of interest, etc have specific issues that need to be handled. 

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
putting an address on a doorway node implies a high level 
of accuracy, whereas, address interpolation way much less so. Your 
output data should have the correct OSM schema that reflects the 
actual uncertainty of your source data. Know your external data!

 - The conflation output should try to look like the data was mapped by hand.
In practice, this means shying away from importing data that does not have an 
established tagging system. If the data was important to OSM, you can be pretty 
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

<a name="ongoing" />
Ongoing Imports
---------------------

Ongoing imports of things like bus stops, gas stations, and all kinds 
of other POI's are basically an advanced version of the conflation problem. 
The goal is to keep OSM synchronized with an external source data 
and at the same time be robust and considerate of normal OSM mapping activity. 

All of the following will happen to the POI nodes you are trying to maintain.

- POI node is deleted.
- POI node is put into a relation. 
- POI node is deleted and all the maintained tags are merged into another node, perhaps
a building node.
- POI node is deleted, and all the maintained tags are merged into a way, perhaps a
building way, or parking way.
- POI node is deleted, and all the tags are merged into a relation.
- New tags are added to your POI node.
- POI node is moved a 1 meter
- POI node is moved a 10 meters.
- POI node is moved a 1000 meters.
- POI node is moved a 10000 meters.
- POI tags you are maintaining are changed in conflict with your source
data.

The following high level guidelines should be considered:

The most important rule, is that the posture of the code 
should be deferential to normal mappers. Aggressive and/or 
rude behavior from import code (aka bots), will not be 
tolerated by the community. 

Strive to preserve edits made by others. That includes changes to the 
position, adding tags, merging, etc.

Preserve the existing OSM node/way ID when edits are made. 
Don't delete then add the entity, or higher level relations and 
ways will be broken. Deleting and adding also makes it very 
difficult to understand change set history of a specific entity.

The code should pay attention to who last touched the data.
The code can be aggressive if nobody else has touched the data except 
itself. However, if non-bot user id is on the data, the code should be 
conservative with conflation issues.

The code should skip anything that looks weird and get a human
involved. There are some scenarios that will need to get resolved by
sending an message to another mapper and discussing the changes.
Sometimes, you will just need to fix the map manually because it was
broken by accident. Supporting human intervention should be 
directly supported by the code. Be sure to code and test against 
partial updates.

At this point you might be saying, no worries, all of these issues are 
what primary keys were invented for! Take a persistent ID from the source 
data and put it into OSM via a custom tag. However using these ids might 
make things more complicated because they are also not immune to normal 
edits. With the ID's you now need to code against the following 
additional situations in combination of the issues already listed.

- The ref:yourimportname is copied to several new POI's you are not maintaining.
- The ref:yourimportname is changed to a new random value.
- The ref:yourimportname tag is deleted, POI node otherwise stays the same.
- POI node is deleted and some tags (not your ref) are merged into another node.
- POI node is deleted and some tags (not your ref) are merged into another way.

You can't 100% trust your ref:yourimportname, it will be copied, deleted, and
generally messed with. Don't think of it like a db primary key, it is
more like a hint, and not the primary identity of the entity. 

The most robust code will need to treat the location and the maintained 
tags as the authoritative identity of the POI entity. Some people who 
have experience with updating OSM data via an external ID have decided 
that ignoring any ID's results in the most robust solution. 

Developing code for ongoing updates is complicated, the dev API test 
server should be heavily utilized to debug and test the code. 

This project is for doing on-going imports. 

https://github.com/insideout10/open-street-map-importer

Please, let me know if other code exists.

<a name="buildings">
Building Imports
-------------------------

Merging/Conflating

The merging of building data into OSM is pretty straight forward in theory.
Basically, don't import the building if it overlaps with a building already
in OSM.
 
The SQL to do this looks like this (this also de-nodes to 0.2 meters).

    select 
      ST_SimplifyPreserveTopology(the_geom,0.20),'yes' as building
    from 
      massgis_structures
    where 
      not exists 
      (select * 
       from 
         planet_osm_polygon as osm 
       where 
         osm.building != '' and ST_Intersects(osm.way,massgis_structures.the_geom))


The ST_Intersects call is not foolproof. There are at least three 
classes of buildings that sometimes are mapped without buildings 
tags: schools (amenity=school), parking garages (amenity=parking), 
and airport terminals (aeroway=terminal). Without the building tag, 
the SQL overlap check fails. The OSM data needs to be prepared by 
hand before the actual import is run to insure the conflation 
script works 100% of the time.

The schools, parking lots, and airport terminals can also be found
and inspected by using the JOSM mirror plugin via an overpass
query, or a XAPI query, or the following SQL.

    select way 
      from planet_osm_polygon as way1
     where 
       way1.amenity = ''school'' and 
       not exists 
       (select * 
         from 
           planet_osm_polygon as way2 
         where 
           way2.building != '' and ST_Intersects(way1.way,way2.way))"


The most technically difficult aspect of a building import is dealing
with buildings that are touching each other or are very close together. 
Some data sources will merge the buildings together into one footprint/shape.
This is the easy case, and if directly imported will be acceptable in
OSM. However, if the buildings are represented by different shape 
primitives, then things get more complicated. Consider the case of two 
buildings that are touching each other, but are different sizes. In the 
source data, the two buildings are probably represented by two different 
shapes. However, in OSM, those buildings needs to be merged together so that
the ways share nodes. 

This import has PostGIS code that correctly deals with the overlapping buildings.

http://wiki.openstreetmap.org/wiki/Baltimore_Buildings_Import


<a name="changeset"/>
Change Set Management
-----------------

There is a 50K entity limit on individual change sets. Every node, way
and relation counts as an entity. JOSM is a fantastic tool, however please
don't use it for uploading change sets that are larger than 50,000 elements. Why?

- JOSM cuts the OSM files exactly at the limit of change set size, it 
makes the change set un-revertible with the JOSM revert plugin. 

- JOSM sorts the upload so that all nodes are uploaded first, then ways, 
then relations. If the upload fails before you finish, you can have 50,000
untagged nodes uploaded, with no ways, leaving a big mess. 

Another issue to be aware of is that it is tricky to break up a large data set by 
hand in JOSM. Its copy and paste mechanism is very literal, unless you are very
careful, your new data layer will be missing dependent relations or its dependent 
nodes

If you have more than 50,000 entities to upload, don't use JOSM to upload them
directly and don't attempt to split up the data using JOSM. Use the script 
in this repository, or write it directly into your conflation script.

The question is sometimes asked, if 50,000 elements are too many, how many 
elements should a change set have? If you have 10,000 elements change sets
be prepared for about 5% the uploads to fail. If you are at 2,000 elements, 
very few of the uploads will fail, much less than 1%. 

However, more important than the failure percentage, is insuring 
that a failure does not leave the data in OSM broken. The only way to 
insure that, is to make the data inside a change sets <b>stand alone</b>. If the
import has more than one change set, they should be able to be 
uploaded in any order. If you are doing an import that has heavily 
connected data, like roads or rivers, then it would be better to have 
larger change sets, rather than breaking up a connected data set. 

Need to talk about the following....

 - change set tags
 - development server
 - revert JOSM plugin 
 - conflicts


The following scripts are included in the repository. 

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


