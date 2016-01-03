#!/usr/bin/env python
#--------------------------------------------------------------------------
# tile_grid.py
#
# generates a regular grid of box shaped polygons in an OGR compatible file
# format  in web mercator (EPSG:3857) projection or geographic coordinates
# (EPSG:4326)
#
# tile_grid.py is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# tile_grid.py is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with tile_grid.py.  If not, see <http://www.gnu.org/licenses/>.
#
#--------------------------------------------------------------------------

try:
    from osgeo import ogr
except ImportError:
    import ogr

try:
    import osgeo.osr as osr
except ImportError:
    import osr

from math import *

import os, sys

def Usage():
    print 'Usage: tile_grid.py [options] <tile_count> <outfile>'
    print
    print 'Options:'
    print '  -f <format>:              output file format'
    print '  -dsco <creation_options>: dataset creation options'
    print '  -nln <layer>:             output layer name (default:grid)'
    print '  -srs <srs>:               grid srs (4326|3857)'
    print '  -o <overlap>:             amount of overlap in srs units'
    print
    sys.exit(1)

print 'tile_grid.py - generate a regular polygon grid with OGR'
print '-----------------------------------------------------------------------------'
print 'Copyright (C) 2015 Christoph Hormann'
print 'This program comes with ABSOLUTELY NO WARRANTY;'
print 'This is free software, and you are welcome to redistribute'
print 'it under certain conditions; see COPYING for details.'
print

outfile = None
maskfile = None
ftype = 'ESRI Shapefile'
dsco = None
nln = "grid"
srid = "4326"
count_x = None
count_y = None
overlap = -1

ext_3857 = [-20037508.342789244, -20037508.342789244, 20037508.342789244, 20037508.342789244]
ext_4326 = [-180.0, -90.0, 180.0, 90.0]

if sys.argv is None:
    Usage()
    
# Parse command line arguments.
i = 1
while i < len(sys.argv):
    arg = sys.argv[i]

    if arg == '-f':
        i = i + 1
        ftype = sys.argv[i]

    elif arg == '-dsco':
        i = i + 1
        dsco = sys.argv[i]

    elif arg == '-nln':
        i = i + 1
        nln = sys.argv[i]

    elif arg == '-srs':
        i = i + 1
        srid = sys.argv[i]

    elif arg == '-overlap':
        i = i + 1
        overlap = float(sys.argv[i])

    elif count_x is None:
        count_x = int(arg)

    elif outfile is None:
        outfile = arg

    else:
        Usage()

    i = i + 1

if  outfile is None:
    Usage()

driver = ogr.GetDriverByName(ftype)

if os.path.exists(outfile):
    driver.DeleteDataSource(outfile)
if dsco is None:
    outDS = driver.CreateDataSource(outfile)
else:
    outDS = driver.CreateDataSource(outfile, [dsco])

if outDS is None:
   print 'Could not create file %s' % outfile
   sys.exit(1)

srs = osr.SpatialReference()

if srid == '3857':
    print 'EPSG:3857 coordinate system'
    srs.ImportFromEPSG(3857)
    ext = ext_3857
    count_y = count_x
    if overlap < 0:
        overlap = 100.0
else:
    print 'EPSG:4326 coordinate system'
    srs.ImportFromEPSG(4326)
    ext = ext_4326
    count_y = count_x/2
    if overlap < 0:
		    overlap = 0.001


outLayer = outDS.CreateLayer(nln, srs, ogr.wkbPolygon)
featureDefn = outLayer.GetLayerDefn()
    
outLayer.StartTransaction()

cnt = 0
   
print 'generating grid...'

for yc in range(count_y):
    for xc in range(count_x):
        ymin = ext[1] + (ext[3] - ext[1])*yc/count_y  - 0.5*overlap
        ymax = ext[1] + (ext[3] - ext[1])*(yc+1)/count_y + 0.5*overlap

        if srid == '3857':
            xmin = ext[0] + (ext[2] - ext[0])*xc/count_x - 0.5*overlap
            xmax = ext[0] + (ext[2] - ext[0])*(xc+1)/count_x + 0.5*overlap
        else:
            overlap_comp = overlap/cos(radians(0.5*(ymin+ymax)))
            xmin = ext[0] + (ext[2] - ext[0])*xc/count_x - 0.5*overlap_comp
            xmax = ext[0] + (ext[2] - ext[0])*(xc+1)/count_x + 0.5*overlap_comp
            if (ymin < ext[1]):
                ymin = ext[1]
            if (xmin < ext[0]):
                xmin = ext[0]
            if (ymax > ext[3]):
                ymax = ext[3]
            if (xmax > ext[2]):
                xmax = ext[2]

        outFeature = ogr.Feature(featureDefn)
        outFeature.SetGeometry(ogr.CreateGeometryFromWkt('POLYGON((%0.7f %0.7f, %0.7f %0.7f, %0.7f %0.7f, %0.7f %0.7f, %0.7f %0.7f))' % (xmin, ymin, xmin, ymax, xmax, ymax, xmax, ymin, xmin, ymin)))
        outLayer.CreateFeature(outFeature)
        outFeature.Destroy()
        cnt += 1

outLayer.CommitTransaction()

print 'polygons generated: ', cnt
         
outDS.Destroy()
