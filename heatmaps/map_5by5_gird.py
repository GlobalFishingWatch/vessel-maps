'''
This script reads in a csv file where the data is organized in three rows,
with lat, lon, and a value. The lat and lon need to be multiples of 5 (0,5,10).
It is currently configured to read a file where the column headers are:
"lat" | "lon" | "num_vessel_days"
'''

import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
import matplotlib
from matplotlib import colors,colorbar
import csv 
import math


sourcedir = "../data/"
filename = "all_orbcomm.csv"
outdir = "../images/"
maxvalue = 1000 #the maximum value of the heatmap

#get the area of a one by one degree grid as a function of latitude
#obviously, this approximate, especially at higher latitudes
def get_area(lat):
    lat_degree = 69 #miles
    # Convert latitude and longitude to 
    # spherical coordinates in radians.
    degrees_to_radians = math.pi/180.0        
    # phi = 90 - latitude
    phi = (lat+2.5)*degrees_to_radians #plus 2.5 to get the middle
    lon_degree = math.cos(phi)*69 #miles
    return  lat_degree*lon_degree* 2.58999 #miles to square km


#initialize the grid
the_grid = np.zeros(shape=(36,72))


with open(sourcedir + filename,'rU') as f:
    reader = csv.DictReader(f, delimiter=',')
    for row in reader:
        lat = float(row['lat'])+90
        lon = float(row['lon'])+180
        if lat<180 and lat>-1 and lon>-1 and lon<360: #ignore bad lat and lon values
            lat_index = lat/5
            lon_index = lon/5
            days = float(row['num_vessel_days'])
            the_grid[lat_index][lon_index] = days/454 #number of days in the orbcom data
            #1/1/14 to 3/1/15 -- Ths is  [data_production__source_data__ais__normalized.ORBCOMM]
            #365+31+30+28 = 454 -- so we get the number of vessels per day
            area = get_area(lat_index*5 - 90+2.5)*5*5 #area of 1 degree box times 5 by 5 degrees
            #added 2.5 to get the center of the grid cell
            the_grid[lat_index][lon_index] = the_grid[lat_index][lon_index] / area *100000 #per 10^5 square km
            #used a higher number here so that the scale was more reasonable


#This next little bit is cheating. There were bad values showing up right along the 0th meridian, so I grabbed
#the values to the left of it
for lat_index in range(10):
    for lon_index in range(30,40):
        if lat_index < 9 and (lon_index == 72/2 or lon_index == 72/2+1): #to get rid of some of the bad values
            the_grid[lat_index][lon_index] = the_grid[lat_index][lon_index-3]

d = np.zeros(shape=(36,72))



firstlat = 85
lastlat = -80
firstlon = -180
lastlon = 180
scale = 5.

numlats = int((firstlat-lastlat)/scale+.5)
numlons = int((lastlon-firstlon)/scale+.5)
lat_boxes = np.linspace(lastlat,firstlat,num=numlats,endpoint=False)
lon_boxes = np.linspace(firstlon,lastlon,num=numlons,endpoint=False)

fig = plt.figure()

m = Basemap(llcrnrlat=lastlat, urcrnrlat=firstlat,
          llcrnrlon=firstlon, urcrnrlon=lastlon, lat_ts=0, projection='mill',resolution="l")

m.drawmapboundary()
#     m.drawcoastlines(linewidth=.2)
m.fillcontinents('#555555')#, lake_color, ax, zorder, alpha)

x = np.linspace(-180, 180, 360/5 )
y = np.linspace(lastlat, firstlat, (firstlat-lastlat)/5 +3)
x, y = np.meshgrid(x, y)
converted_x, converted_y = m(x, y)
norm = colors.LogNorm(vmin=1, vmax=1000)

m.pcolormesh(converted_x, converted_y, the_grid, norm=norm, vmin=1, vmax=maxvalue)


#title -- has to go before making the colorbar
t = "Density of Vessels per Day, 2014-2015"
plt.title(t)

#make the colorbar
ax = fig.add_axes([0.15, 0.1, 0.4, 0.02]) #x coordinate , 
norm = colors.Normalize(vmin=0, vmax=1000)
norm = colors.LogNorm(vmin=1, vmax=1000)
lvls = np.logspace(0,3,7)
cb = colorbar.ColorbarBase(ax,norm = norm,
#                                     ticks=theticks,
                                   orientation='horizontal', ticks=lvls)

#logritmic colorbar
cb.ax.set_xticklabels(["<1" ,int(maxvalue**(1./6)+.5), int(maxvalue**(2./6)+.5), int(maxvalue**(3./6)+.5), int(maxvalue**(4./6)+.5), int(maxvalue**(5./6)+.5), str(int(maxvalue))+"+"], fontsize=10)
cb.set_label('Vessels per day per 10^5 km^2',labelpad=-40, y=0.45)

plt.savefig(outdir+"vessel_days_allorcomm_permile.png",bbox_inches='tight',dpi=100,transparent=True,pad_inches=0)


