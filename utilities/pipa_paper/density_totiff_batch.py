
import numpy as np
import csv 
import math
import rasterio as rio
import affine


source_dir = "../../data/pipa_v2/"
infile = "1a/224523000.npy"
out_dir = "../../data/pipa/"


def create_tifs(extra, cellsize):

    from os import listdir
    from os.path import isfile, join
    onlyfiles = [f for f in listdir(source_dir+extra) if isfile(join(source_dir+extra, f))]

    if cellsize == .25:
        ncols = (178-167)*4
        nrows = -(- 8 - 0.5)*4
        yllcorner = -8
        xllcorner = -178
        c_inverse = 4
        y_max = .5

    if cellsize == 1:
        ncols = (30+(-73.7+180))
        nrows = (15--15)
        yllcorner = -210
        xllcorner = -15
        c_inverse = 1
        y_max = 14

    profile = {
        'crs': 'EPSG:4326',
        'nodata': -9999,
        'dtype': rio.float64,
        'height': nrows,
        'width': ncols,
        'count': 1,
        'driver':"GTiff",
        'transform': affine.Affine(cellsize, 0, xllcorner, 
                  0, -cellsize, y_max)}

    for f in onlyfiles:
        if ".npy" in f:
            grid = np.load(source_dir + extra+ f)
            out_tif = out_dir + extra + f.replace('.npy',".tif")
            with rio.open(out_tif, 'w', **profile) as dst:
                dst.write(grid, indexes=1)



create_tifs("1a/", .25)
create_tifs("1b/", .25)
create_tifs("s8/", 1)
create_tifs("s2/", .25)

