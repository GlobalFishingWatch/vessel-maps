import numpy as np
import matplotlib.mlab as mlab
import matplotlib.pyplot as plt
import json
import csv
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
from datetime import datetime, timedelta
import fiona
from matplotlib.patches import Polygon


# mmsis = [412206471,412206475,412206481,412206495,412206498,412206501,412206503,412206508,412206511,412206513,412206516,412206517,412206519,412206522,412206526,412206527,412206531,412206538,412206545,412206556,412206557,412206561,412206565,412206573,412206575,412206576]
def draw_screen_poly( outside_ring, m, color, linewidth, opacity):
    lons = []
    lats = []
    for point in outside_ring:
        lats.append(point[1])
        l = point[0]
        lons.append(l)
    
    # if lons[0]<230:
    #     x, y = m( lons, lats )
    #     xy = zip(x,y)
    #     poly = Polygon( xy, facecolor=color,fill=False, alpha=1,lw=1.5, edgecolor="#222222" ,zorder=10)
    #     plt.gca().add_patch(poly)


def col(t):
    d = t.day
    v = hex(int(d/31.*255))[2:]
    if len(v)<2:
        v = "0"+v
    return "#00"+v+v

sourcedir = ''

    
lats = []
lons = []
times =[]

lats2 = []
lons2 = []
times2 = []

# mmsi = '440705000'

filename = '/Users/David/Desktop/Jobs/GlobalFishingWatch/github/vessel-maps/data/seismic_vessels/seismic5.csv'
with open(sourcedir + filename,'rU') as f:
    reader = csv.DictReader(f, delimiter=',')
    for row in reader:
        try:#row['mmsi'] == mmsi: 
#             t = int(row['timestamp'])
#             t = datetime(t)
#             times.append(t)
            if float(row['sog'])>3 and float(row['sog'])<6:
                lon = float(row['lon'])
                # if lon < 0:
                #     lon = (360+lon) 
                lats.append(float(row['lat']))
                lons.append(lon)
                # times.append(t)
        except:
            pass




fig = plt.figure()

plt.figure(figsize=(20, 20)) 

ax = fig.add_subplot(111)                    
ax.spines["top"].set_visible(False)  
ax.spines["bottom"].set_visible(False)  
ax.spines["right"].set_visible(False)  
ax.spines["left"].set_visible(False)    
ax.axis('off')  
         
# alllats = lats+lats2
# alllons = lons+lons2
               
# min_lat = min(alllats)-5
# min_lon = min(alllons)-5 
# max_lat = max(alllats)+5
# max_lon = max(alllons)+5

min_lat = -80
min_lon = -180
max_lat = 80
max_lon = 180




# min_lat = max(-800, min(min(lats),min(lats2)))
# min_lon = min(min(lons),min(lons2))-5
# max_lat = min(60, max(max(lats),max(lats2))) #this prevents us from choosing a bad lat
# max_lon = max(max(lons),max(lons2))+5



m =\
Basemap(llcrnrlon=min_lon,llcrnrlat=min_lat,urcrnrlon=max_lon,urcrnrlat=max_lat,projection='mill', resolution ='l')
# m = Basemap(projection='kav7',lon_0=0,resolution=None)
m.drawcoastlines(color="#cccccc")
# m.fillcontinents(color='coral',lake_color='aqua')

# m.drawmapboundary()
# m.drawcoastlines()
           

            
m.fillcontinents("#cccccc")

# #date to show on the chart
# t_start = datetime.strptime(gap_start,"%Y-%m-%d %H:%M:%S UTC")
# t_show = t_start.strftime("%Y-%m-%d")
   

  
# x2,y2= m(lons2,lats2)
# color =  "#7879FA"    
# size = .5
# m.plot(x2,y2,marker = 'o',color=color,markersize=size,markeredgecolor = 'none',alpha = 1,linestyle='None',zorder=2)#carbon
       
x,y= m(lons,lats)
color =  "#FA0C1D"  
size = .5
m.plot(x,y,marker = 'o',color=color,markersize=size,markeredgecolor = 'none',alpha = .1,linestyle='None',zorder=1)#carbon

#theShapes = fiona.open('/Users/David/Desktop/Jobs/GlobalFishingWatch/geospatial_code/MPA-EEZ/patched-eez/patched-eez.shp')
# theShapes = fiona.open('PIPA_Boundary_Kiribati_EEZ/PIPA_boundary.shp')
# for p in theShapes:
#     geo = p['geometry']
#     if geo['type'] == 'Polygon':
#         outside_ring = geo['coordinates'][0]
#         draw_screen_poly(outside_ring, m, "#ffffff", .5, 1)      

#     elif geo['type']=='MultiPolygon':
#         for r in geo['coordinates']:
#             outside_ring = r[0]
#             draw_screen_poly(outside_ring, m,"#ffffff" , .5, 1 ) 

plt.title('Seismic Vessel Tracks When Traveling\n Between 3 and 6 Knots, 2012-2015',fontsize=30)

# plt.show()           
plt.savefig("Seismic_Tracks.png", bbox_inches="tight", edgecolor='none')

#plt.savefig('Vessel_track_'+str(mmsi)+'_'+t_start.strftime("%Y-%m-%d")+'.png',bbox_inches="tight", edgecolor='none')
                      

            

                


