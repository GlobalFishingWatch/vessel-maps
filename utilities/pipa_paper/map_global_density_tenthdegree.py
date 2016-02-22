import numpy as np
import matplotlib.pyplot as plt
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
import matplotlib
from matplotlib import colors,colorbar
import csv 
import math




def get_area(lat):
    lat_degree = 69 #miles
    # Convert latitude and longitude to 
    # spherical coordinates in radians.
    degrees_to_radians = math.pi/180.0        
    # phi = 90 - latitude
    phi = (lat+.05)*degrees_to_radians #plus 0.5 to get the middle
    lon_degree = math.cos(phi)*69 #miles
    return  lat_degree*lon_degree* 2.58999 #miles to square km


sourcedir = "../../data/density/"
filename = "densitytenth2015_4cutoff.csv"
filename = "00000.csv"
filename = "003.csv"
filename = "densitytenth2015.csv"


vessel_days = np.zeros(shape=(1800,3600))


test_array = np.zeros(shape=(3600))
test_array2 = np.zeros(shape=(3600))


=
with open(sourcedir + filename,'rU') as f:
    reader = csv.DictReader(f, delimiter=',')
    for row in reader:
        lat = float(row['lat_bin'])+90
        lon = float(row['lon_bin'])+180
        if lat<180 and lat>-1 and lon>-1 and lon<360:
            lat_index = lat*10
            lon_index = lon*10
            days = float(row['number'])

            area = get_area(lat-90) # area of 1 by 1 degree at a given lat

            vessel_days[lat_index][lon_index] = days / (365* area*.1*.1) *100000 #vessels per day per 10^5 square km






print vessel_days.max()


tm = 1000. #this is just to scale the the following... this makes the colormap



colors = [["#FFFFFF",0,0],
          ['#894081', 5,5],
          ['#338ACA',10,10],
          ['#47AEC4',25,25],
          ['#49A578',50,50],
          ['#82B130',100,100],
          ['#F8C728',250,250],
          ['#EFA639',500,500],
          ['#E58230',1000,1000]]
          
                 
          
          
cdict = { 'red':tuple(   (color[2]/tm, int(color[0][1:3],16)/256.0, int(color[0][1:3],16)/256.0) for color in colors ),
          'green':tuple( (color[2]/tm, int(color[0][3:5],16)/256.0, int(color[0][3:5],16)/256.0) for color in colors ),
          'blue':tuple(  (color[2]/tm, int(color[0][5:7],16)/256.0, int(color[0][5:7],16)/256.0) for color in colors )}


tm = 1000.

# colors = colors[1:]
# for i in range(len(colors)):
#     colors[i] = [colors[i][0], colors[i][1]-1, colors[i][2]-1]


cdict2 = { 'red':tuple(   (color[2]/tm, int(color[0][1:3],16)/256.0, int(color[0][1:3],16)/256.0) for color in colors ),
          'green':tuple( (color[2]/tm, int(color[0][3:5],16)/256.0, int(color[0][3:5],16)/256.0) for color in colors ),
          'blue':tuple(  (color[2]/tm, int(color[0][5:7],16)/256.0, int(color[0][5:7],16)/256.0) for color in colors )}#,
          #'alpha': ((0,0,0),(.00001,1,1),(1,1,1)) }



'''#I left the following in just to show the format of the colormap -- it is a series of tuples
cdict = {'red': ((0.0, 0.0, 0.0),
                  (0.5, 1.0, 0.7),
                  (1.0, 1.0, 1.0)),
          'green': ((0.0, 0.0, 0.0),
                    (0.5, 1.0, 0.0),
                    (1.0, 1.0, 1.0)),
          'blue': ((0.0, 0.0, 0.0),
                   (0.5, 1.0, 0.0),
                   (1.0, 0.5, 1.0))}
'''
my_cmap = matplotlib.colors.LinearSegmentedColormap('my_colormap',cdict,256)
my_cmap.set_bad(alpha = 0.0)
    
my_cmap2 = matplotlib.colors.LinearSegmentedColormap('my_colormap',cdict2,256)
my_cmap2.set_bad(alpha = 0.0)  

firstlat = 90
lastlat = -90
firstlon = -180
lastlon = 180
scale = .1

numlats = int((firstlat-lastlat)/scale+.5)
numlons = int((lastlon-firstlon)/scale+.5)
    
#     data_array = np.zeros((numlats, numlons)) #data_array is in format data_array[lat index][lon index]

lat_boxes = np.linspace(lastlat,firstlat,num=numlats,endpoint=False)
lon_boxes = np.linspace(firstlon,lastlon,num=numlons,endpoint=False)


fig = plt.figure()


m = Basemap(llcrnrlat=lastlat, urcrnrlat=firstlat,
          llcrnrlon=firstlon, urcrnrlon=lastlon, lat_ts=0, projection='mill',resolution="h")


m.drawmapboundary()
#     m.drawcoastlines(linewidth=.2)
m.fillcontinents('#555555')#, lake_color, ax, zorder, alpha)


x = np.linspace(-180, 180, 360*10 )
y = np.linspace(lastlat, firstlat, (firstlat-lastlat)*10)
x, y = np.meshgrid(x, y)
converted_x, converted_y = m(x, y)
from matplotlib import colors,colorbar

norm = colors.LogNorm(vmin=1, vmax=1000)

m3 = 10

m.pcolormesh(converted_x, converted_y, vessel_days, norm=norm, vmin=1, vmax=m3**3)
#plt.pcolormesh(x, y, z, cmap='RdBu', vmin=z_min, vmax=z_max)

t = "Density of Vessels per Day, 2015"
plt.title(t)
# topodat = m.transform_scalar(gap_buckets,lon_boxes,lat_boxes,nx,ny)
# 
# im = m.imshow(topodat,interpolation='none',vmin=-1,vmax=10,cmap=my_cmap,zorder = 0,alpha=1)#,norm=LogNorm(vmin=0.00000001, vmax=.00064))#cm.s3pcpn)#,)


# cbar = fig.colorbar(im)#, ticks=[-1, 0, 1])
# theticks = [i*100 for i in range(10)]
# cbar = fig.colorbar(im, cmap =my_cmap2, orientation='horizontal')

ax = fig.add_axes([0.15, 0.1, 0.4, 0.02]) #x coordinate , 
#ax.patch.set_alpha(0.0)
#ax.axis('off')
# my_cmap=choose_cmap('reds')
norm = colors.Normalize(vmin=0, vmax=1000)
norm = colors.LogNorm(vmin=1, vmax=1000)
lvls = np.logspace(0,3,7)

cb = colorbar.ColorbarBase(ax,norm = norm,
#                                     ticks=theticks,
                                   orientation='horizontal', ticks=lvls)


cb.ax.set_xticklabels(["<1" ,int(m3**.5), m3, int(m3**1.5), m3*m3,int(m3**2.5), str(int(m3**3))+"+"], fontsize=10)
cb.set_label('Vessels per day per 10^5 km^2',labelpad=-40, y=0.45)

# plt.text(1.1, .15, 'Pixels with fewer than 20 boats per\nday in 2014 are shown in gray', fontsize = 10)
# plt.axis('off')

# plt.show()
plt.savefig("vessel_density_2015_first_b_t.png",bbox_inches='tight',dpi=450,transparent=True,pad_inches=0)


