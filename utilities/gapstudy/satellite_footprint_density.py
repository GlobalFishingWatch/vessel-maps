from datetime import datetime, timedelta
import json
import numpy as np
import math 
from math import radians, cos, sin, asin, sqrt

# day_zero = datetime(2012,4,1)
# d = row['f'][0]['v'].split("-")
# d = datetime(int(d[0]),int(d[1]),int(d[2]))
# d_index = (d-day_zero).days

#grid = np.zeros(shape=(1370,36,72))

# print (datetime(2015,12,31) - day_zero).days

# exit()

# Grab the application's default credentials from the environment.

#density = np.load('vessel_density.npy')[0]


density_from_satelite = np.zeros(shape = (36,72))

satellite_radius = 1500

def haversine(lon1, lat1, lon2, lat2):
    """
    Calculate the great circle distance between two points 
    on the earth (specified in decimal degrees)
    """
    # convert decimal degrees to radians 
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

    # haversine formula 
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a)) 
    r = 6371 # Radius of earth in kilometers. Use 3956 for miles
    return c * r

def distance_between_boxes(lat_box_0,lon_box_0,lat_box_1,lon_box_1):
    lat1 = lat_box_0*5-90+2.5
    lat2 = lat_box_1*5-90+2.5
    lon1 = lon_box_0*5-180+2.5
    lon2 = lon_box_1*5-180+2.5
    return haversine(lon1, lat1, lon2, lat2)


lat_box_not = 30
lon_box_not = 0

grid_for_average = [ [[] for i in range(72)] for k in range(36)]
# grid_for_average[lat_box][lon_box] -- a list of the other values we should average across


for lat_box in range(36):
    for lon_box in range(72):        
        for i in range (36):
            for k in range (72):
                if distance_between_boxes(i,k,lat_box,lon_box) < satellite_radius:
                    #print i*5-90+2.5, k*5-180+2.5, distance_between_boxes(i,k,lat_box_not,lon_box_not)
                    grid_for_average[lat_box][lon_box].append([i,k])
                # print i,k,lat_box_0,lon_box_0


print grid_for_average[0][0]
print grid_for_average[18][36]

# earth_circumference = 40075 #in km
# box_width_degrees = 5
# satellite_diameter = 3000.
# box_height = earth_circumference / 360 * box_width_degrees

# #how wide 5 degrees is by latitude
# box_width = np.zeros(shape=36)
# for i in range(36):
#     lat = i*5-90+2.5
#     lat = lat*math.pi/180
#     box_width[i] = earth_circumference/360.*math.cos(lat)*box_width_degrees
#     boxes_across = satellite_diameter / box_width[i]
#     print i*5-90+2.5, box_width[i], boxes_across






