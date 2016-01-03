
poly_grid polygon splitting script
==================================

This repository contains a bash script that splits and optionally inverts 
polygons in a spatialite database in a regular grid pattern with overlaps.

It is written for use for generating coastline polygon files on
[openstreetmapdata.com](http://openstreetmapdata.com/).


Dependencies
------------

requires the following to operate:

* [GDAL/OGR](http://www.gdal.org/index.html)
* [spatialite](http://www.gaia-gis.it/gaia-sins/)
* polysplit from https://github.com/geoloqi/polysplit.git (unless used with 'n'-option)
* tile_grid.py (should be included with this script)

Legal stuff
-----------

This program is licensed under the GNU GPL version 3.

Copyright 2015 Christoph Hormann
