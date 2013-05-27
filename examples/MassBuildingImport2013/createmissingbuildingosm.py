#!usr/bin/python

# Jason Remillard - This file is in the public domain.

import sys, os, zipfile

def exportTown(townnumber,townname) :

  os.system("rm temp/*")

  # reproject to 900913, which is what we use inside of postGIS
  r = os.system("ogr2ogr -t_srs EPSG:900913 -overwrite temp/structures_poly_" + townname + ".shp ../srcdata/massgis_structures/structures_poly_" + str(townnumber) + ".shp"); 
  if ( r ) : exit(r);

  # import to postGIS
  r = os.system("shp2pgsql -D -I -s EPSG:900913 -d temp/structures_poly_" + townname + ".shp massgis_structures | psql -q gis");
  if ( r ) : exit(r);

  # set the projection, shp2pgsl does not do this, don't know why...
  r = os.system("psql gis -c \"select UpdateGeometrySRID('massgis_structures','the_geom',900913)\"")
  if ( r ) : exit(r);

  r = os.system("rm temp/*")
  if ( r ) : exit(r);

  outBase = "output/" + townname + "_";

  # get structures missing from OSM
  sql = ("select ST_SimplifyPreserveTopology(the_geom,0.20),'yes' as building "
         "from massgis_structures " 
         "where "
         "  massgis_structures.town_id = " + str(townnumber) + " and "
         "  not exists "
         "  (select * from planet_osm_polygon as osm "
         "   where "
         "     osm.building != '' and "
         "     ST_Intersects(osm.way,massgis_structures.the_geom))")

  r = os.system("ogr2ogr -sql \"" + sql + "\" -overwrite -f 'ESRI Shapefile' temp/structures_missing_from_osm_" + townname + ".shp PG:dbname=gis " )
  if ( r ) : exit(r);

  r = os.system("python ogr2osm/ogr2osm.py -f -o " + outBase + "buildings_missing_from_osm.osm temp/structures_missing_from_osm_" + townname + ".shp")
  if ( r ) : exit(r);


  # get all structures
  #sql = "select ST_SimplifyPreserveTopology(the_geom,0.20),'yes' as building from massgis_structures"

  #os.system("ogr2ogr -sql \"" + sql + "\" -overwrite -f 'ESRI Shapefile' temp/massgis_structures_" + townname + ".shp PG:dbname=gis " )
  #os.system("python ogr2osm/ogr2osm.py -f -o " + outBase + "all_massgis_buildings.osm temp/massgis_structures_" + townname + ".shp")

  # get structures overlapping with OSM
  sql = ("select ST_SimplifyPreserveTopology(the_geom,0.20),'yes' as building "
         "from massgis_structures " 
         "where "
         "  massgis_structures.town_id = " + str(townnumber) + " and "
         "  exists "
         "  (select * from planet_osm_polygon as osm "
         "   where "
         "     osm.building != '' and "
         "     ST_Intersects(osm.way,massgis_structures.the_geom))")

  r = os.system("ogr2ogr -sql \"" + sql + "\" -overwrite -f 'ESRI Shapefile' temp/structures_overlap_with_osm_" + townname + ".shp PG:dbname=gis " )
  if ( r ) : exit(r);

  r = os.system("python ogr2osm/ogr2osm.py -f -o " + outBase + "buildings_overlap_with_osm.osm temp/structures_overlap_with_osm_" + townname + ".shp")
  if ( r ) : exit(r);

  # get structures missing from MassGIS
  # can't easily limit search to town.
  #sql = "select way,'yes' as building from planet_osm_polygon as osm where osm.building != '' and not exists (''select * from massgis_structures as m  where ST_Intersects('osm.way,m.the_geom))"

  #os.system("ogr2ogr -sql \"" + sql + "\" -overwrite -f 'ESRI Shapefile' temp/structures_missing_from_massgis_" + str('townnumber) + ".shp PG:dbname=gis " )
  #os.system("python ogr2osm/ogr2osm.py -f -o output/structures_missing_from_massgis_" + str('townnumber) + ".osm temp/structures_missing_from_massgis_" + str('townnumber) + ".shp")

  #z=zipfile.ZipFile(outBase + "osm_massgis_structures_merge.zip","w")
  #z.write(outBase + "buildings_missing_from_osm.osm");
  #z.write(outBase + "buildings_overlap_with_osm.osm");
  #z.close()

def convertMassGISTownNumbersToName( number) :

  d = dict( [ ('1','ABINGTON'),
  ('2','ACTON'),
  ('3','ACUSHNET'),
  ('4','ADAMS'),
  ('5','AGAWAM'),
  ('6','ALFORD'),
  ('7','AMESBURY'),
  ('8','AMHERST'),
  ('9','ANDOVER'),
  ('10','ARLINGTON'),
  ('11','ASHBURNHAM'),
  ('12','ASHBY'),
  ('13','ASHFIELD'),
  ('14','ASHLAND'),
  ('15','ATHOL'),
  ('16','ATTLEBORO'),
  ('17','AUBURN'),
  ('18','AVON'),
  ('19','AYER'),
  ('20','BARNSTABLE'),
  ('21','BARRE'),
  ('22','BECKET'),
  ('23','BEDFORD'),
  ('24','BELCHERTOWN'),
  ('25','BELLINGHAM'),
  ('26','BELMONT'),
  ('27','BERKLEY'),
  ('28','BERLIN'),
  ('29','BERNARDSTON'),
  ('30','BEVERLY'),
  ('31','BILLERICA'),
  ('32','BLACKSTONE'),
  ('33','BLANDFORD'),
  ('34','BOLTON'),
  ('35','BOSTON'),
  ('36','BOURNE'),
  ('37','BOXBOROUGH'),
  ('38','BOXFORD'),
  ('39','BOYLSTON'),
  ('40','BRAINTREE'),
  ('41','BREWSTER'),
  ('42','BRIDGEWATER'),
  ('43','BRIMFIELD'),
  ('44','BROCKTON'),
  ('45','BROOKFIELD'),
  ('46','BROOKLINE'),
  ('47','BUCKLAND'),
  ('48','BURLINGTON'),
  ('49','CAMBRIDGE'),
  ('50','CANTON'),
  ('51','CARLISLE'),
  ('52','CARVER'),
  ('53','CHARLEMONT'),
  ('54','CHARLTON'),
  ('55','CHATHAM'),
  ('56','CHELMSFORD'),
  ('57','CHELSEA'),
  ('58','CHESHIRE'),
  ('59','CHESTER'),
  ('60','CHESTERFIELD'),
  ('61','CHICOPEE'),
  ('62','CHILMARK'),
  ('63','CLARKSBURG'),
  ('64','CLINTON'),
  ('65','COHASSET'),
  ('66','COLRAIN'),
  ('67','CONCORD'),
  ('68','CONWAY'),
  ('69','CUMMINGTON'),
  ('70','DALTON'),
  ('71','DANVERS'),
  ('72','DARTMOUTH'),
  ('73','DEDHAM'),
  ('74','DEERFIELD'),
  ('75','DENNIS'),
  ('76','DIGHTON'),
  ('77','DOUGLAS'),
  ('78','DOVER'),
  ('79','DRACUT'),
  ('80','DUDLEY'),
  ('81','DUNSTABLE'),
  ('82','DUXBURY'),
  ('83','EAST_BRIDGEWATER'),
  ('84','EAST_BROOKFIELD'),
  ('85','EAST_LONGMEADOW'),
  ('86','EASTHAM'),
  ('87','EASTHAMPTON'),
  ('88','EASTON'),
  ('89','EDGARTOWN'),
  ('90','EGREMONT'),
  ('91','ERVING'),
  ('92','ESSEX'),
  ('93','EVERETT'),
  ('94','FAIRHAVEN'),
  ('95','FALL_RIVER'),
  ('96','FALMOUTH'),
  ('97','FITCHBURG'),
  ('98','FLORIDA'),
  ('99','FOXBOROUGH'),
  ('100','FRAMINGHAM'),
  ('101','FRANKLIN'),
  ('102','FREETOWN'),
  ('103','GARDNER'),
  ('104','GAY_HEAD'),
  ('105','GEORGETOWN'),
  ('106','GILL'),
  ('107','GLOUCESTER'),
  ('108','GOSHEN'),
  ('109','GOSNOLD'),
  ('110','GRAFTON'),
  ('111','GRANBY'),
  ('112','GRANVILLE'),
  ('113','GREAT_BARRINGTON'),
  ('114','GREENFIELD'),
  ('115','GROTON'),
  ('116','GROVELAND'),
  ('117','HADLEY'),
  ('118','HALIFAX'),
  ('119','HAMILTON'),
  ('120','HAMPDEN'),
  ('121','HANCOCK'),
  ('122','HANOVER'),
  ('123','HANSON'),
  ('124','HARDWICK'),
  ('125','HARVARD'),
  ('126','HARWICH'),
  ('127','HATFIELD'),
  ('128','HAVERHILL'),
  ('129','HAWLEY'),
  ('130','HEATH'),
  ('131','HINGHAM'),
  ('132','HINSDALE'),
  ('133','HOLBROOK'),
  ('134','HOLDEN'),
  ('135','HOLLAND'),
  ('136','HOLLISTON'),
  ('137','HOLYOKE'),
  ('138','HOPEDALE'),
  ('139','HOPKINTON'),
  ('140','HUBBARDSTON'),
  ('141','HUDSON'),
  ('142','HULL'),
  ('143','HUNTINGTON'),
  ('144','IPSWICH'),
  ('145','KINGSTON'),
  ('146','LAKEVILLE'),
  ('147','LANCASTER'),
  ('148','LANESBOROUGH'),
  ('149','LAWRENCE'),
  ('150','LEE'),
  ('151','LEICESTER'),
  ('152','LENOX'),
  ('153','LEOMINSTER'),
  ('154','LEVERETT'),
  ('155','LEXINGTON'),
  ('156','LEYDEN'),
  ('157','LINCOLN'),
  ('158','LITTLETON'),
  ('159','LONGMEADOW'),
  ('160','LOWELL'),
  ('161','LUDLOW'),
  ('162','LUNENBURG'),
  ('163','LYNN'),
  ('164','LYNNFIELD'),
  ('165','MALDEN'),
  ('166','MANCHESTER'),
  ('167','MANSFIELD'),
  ('168','MARBLEHEAD'),
  ('169','MARION'),
  ('170','MARLBOROUGH'),
  ('171','MARSHFIELD'),
  ('172','MASHPEE'),
  ('173','MATTAPOISETT'),
  ('174','MAYNARD'),
  ('175','MEDFIELD'),
  ('176','MEDFORD'),
  ('177','MEDWAY'),
  ('178','MELROSE'),
  ('179','MENDON'),
  ('180','MERRIMAC'),
  ('181','METHUEN'),
  ('182','MIDDLEBOROUGH'),
  ('183','MIDDLEFIELD'),
  ('184','MIDDLETON'),
  ('185','MILFORD'),
  ('186','MILLBURY'),
  ('187','MILLIS'),
  ('188','MILLVILLE'),
  ('189','MILTON'),
  ('190','MONROE'),
  ('191','MONSON'),
  ('192','MONTAGUE'),
  ('193','MONTEREY'),
  ('194','MONTGOMERY'),
  ('195','MOUNT_WASHINGTON'),
  ('196','NAHANT'),
  ('197','NANTUCKET'),
  ('198','NATICK'),
  ('199','NEEDHAM'),
  ('200','NEW_ASHFORD'),
  ('201','NEW_BEDFORD'),
  ('202','NEW_BRAINTREE'),
  ('203','NEW_MARLBOROUGH'),
  ('204','NEW_SALEM'),
  ('205','NEWBURY'),
  ('206','NEWBURYPORT'),
  ('207','NEWTON'),
  ('208','NORFOLK'),
  ('209','NORTH_ADAMS'),
  ('210','NORTH_ANDOVER'),
  ('211','NORTH_ATTLEBOROUGH'),
  ('212','NORTH_BROOKFIELD'),
  ('213','NORTH_READING'),
  ('214','NORTHAMPTON'),
  ('215','NORTHBOROUGH'),
  ('216','NORTHBRIDGE'),
  ('217','NORTHFIELD'),
  ('218','NORTON'),
  ('219','NORWELL'),
  ('220','NORWOOD'),
  ('221','OAK_BLUFFS'),
  ('222','OAKHAM'),
  ('223','ORANGE'),
  ('224','ORLEANS'),
  ('225','OTIS'),
  ('226','OXFORD'),
  ('227','PALMER'),
  ('228','PAXTON'),
  ('229','PEABODY'),
  ('230','PELHAM'),
  ('231','PEMBROKE'),
  ('232','PEPPERELL'),
  ('233','PERU'),
  ('234','PETERSHAM'),
  ('235','PHILLIPSTON'),
  ('236','PITTSFIELD'),
  ('237','PLAINFIELD'),
  ('238','PLAINVILLE'),
  ('239','PLYMOUTH'),
  ('240','PLYMPTON'),
  ('241','PRINCETON'),
  ('242','PROVINCETOWN'),
  ('243','QUINCY'),
  ('244','RANDOLPH'),
  ('245','RAYNHAM'),
  ('246','READING'),
  ('247','REHOBOTH'),
  ('248','REVERE'),
  ('249','RICHMOND'),
  ('250','ROCHESTER'),
  ('251','ROCKLAND'),
  ('252','ROCKPORT'),
  ('253','ROWE'),
  ('254','ROWLEY'),
  ('255','ROYALSTON'),
  ('256','RUSSELL'),
  ('257','RUTLAND'),
  ('258','SALEM'),
  ('259','SALISBURY'),
  ('260','SANDISFIELD'),
  ('261','SANDWICH'),
  ('262','SAUGU'),
  ('263','SAVOY'),
  ('264','SCITUATE'),
  ('265','SEEKONK'),
  ('266','SHARON'),
  ('267','SHEFFIELD'),
  ('268','SHELBURNE'),
  ('269','SHERBORN'),
  ('270','SHIRLEY'),
  ('271','SHREWSBURY'),
  ('272','SHUTESBURY'),
  ('273','SOMERSET'),
  ('274','SOMERVILLE'),
  ('275','SOUTH_HADL'),
  ('276','SOUTHAMPTON'),
  ('277','SOUTHBOROUGH'),
  ('278','SOUTHBRIDGE'),
  ('279','SOUTHWICK'),
  ('280','SPENCER'),
  ('281','SPRINGFIELD'),
  ('282','STERLING'),
  ('283','STOCKBRIDGE'),
  ('284','STONEHAM'),
  ('285','STOUGHTON'),
  ('286','STOW'),
  ('287','STURBRIDGE'),
  ('288','SUDBURY'),
  ('289','SUNDERLAND'),
  ('290','SUTTON'),
  ('291','SWAMPSCOTT'),
  ('292','SWANSEA'),
  ('293','TAUNTON'),
  ('294','TEMPLETON'),
  ('295','TEWKSBURY'),
  ('296','TISBURY'),
  ('297','TOLLAND'),
  ('298','TOPSFIELD'),
  ('299','TOWNSEND'),
  ('300','TRURO'),
  ('301','TYNGSBOROUGH'),
  ('302','TYRINGHAM'),
  ('303','UPTON'),
  ('304','UXBRIDGE'),
  ('305','WAKEFIELD'),
  ('306','WALES'),
  ('307','WALPOLE'),
  ('308','WALTHAM'),
  ('309','WARE'),
  ('310','WAREHAM'),
  ('311','WARREN'),
  ('312','WARWICK'),
  ('313','WASHINGTON'),
  ('314','WATERTOWN'),
  ('315','WAYLAND'),
  ('316','WEBSTER'),
  ('317','WELLESLEY'),
  ('318','WELLFLEET'),
  ('319','WENDELL'),
  ('320','WENHAM'),
  ('321','WEST_BOYLSTON'),
  ('322','WEST_BRIDGEWATER'),
  ('323','WEST_BROOKFIELD'),
  ('324','WEST_NEWBURY'),
  ('325','WEST_SPRINGFIELD'),
  ('326','WEST_STOCKBRIDGE'),
  ('327','WEST_TISBURY'),
  ('328','WESTBOROUGH'),
  ('329','WESTFIELD'),
  ('330','WESTFORD'),
  ('331','WESTHAMPTON'),
  ('332','WESTMINSTER'),
  ('333','WESTON'),
  ('334','WESTPORT'),
  ('335','WESTWOOD'),
  ('336','WEYMOUTH'),
  ('337','WHATELY'),
  ('338','WHITMAN'),
  ('339','WILBRAHAM'),
  ('340','WILLIAMSBURG'),
  ('341','WILLIAMSTOWN'),
  ('342','WILMINGTON'),
  ('343','WINCHENDON'),
  ('344','WINCHESTER'),
  ('345','WINDSOR'),
  ('346','WINTHROP'),
  ('347','WOBURN'),
  ('348','WORCESTER'),
  ('349','WORTHINGTON'),
  ('350','WRENTHAM'),
  ('351','YARMOUTH')])
  
  return d[str(number)]

townnumbers = sys.argv[1:]
if (len(townnumbers) == 0): 
  townnumbers = range(1,352)

for townnumber in townnumbers:
  exportTown( townnumber,convertMassGISTownNumbersToName(townnumber))







  
