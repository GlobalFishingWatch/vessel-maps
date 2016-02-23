import numpy as np
import csv 
import math

import rasterio as rio
import affine


vessel_days = np.load("../../data/density/density2015.npy")

profile = {
    'crs': 'EPSG:4326',
    'nodata': -9999,
    'dtype': rio.float64,
    'height': 1800,
    'width': 3600,
    'count': 1,
    'driver':"GTiff",
    'transform': affine.Affine(0.1, 0, -180, 
              0, -0.1, 90)}

out_tif = "../../data/density/density_2015.tiff"

with rio.open(out_tif, 'w', **profile) as dst:
    dst.write(np.flipud(vessel_days), indexes=1)





