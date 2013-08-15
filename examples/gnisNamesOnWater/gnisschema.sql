-- Jason Remillard - This file is in the public domain.

-- create schema for gnis features, we only care about the id, name, type, and lat/lon. 
-- The rest of the data is not imported to save time/space.

DROP TABLE IF EXISTS gnis;
 
CREATE TABLE gnis (
 featureid int,
 name varchar(128),
 featureclass varchar(16)
);

SELECT AddGeometryColumn( '', 'gnis', 'geom', 4326, 'POINT', 2);

CREATE INDEX idx_gnis_geom ON gnis USING gist (geom);
