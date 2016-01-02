import csv
import datetime

sourcedir = "../data/seismic_vessels/"
filename = "seismic5.csv"


year = 2012

for year in range(2012,2016):
    lats = []
    lons = []
    timestamps = []
    sogs = []
    cogs = []
    mmsi = '209108000'
    with open(sourcedir + filename,'rU') as f:
        reader = csv.DictReader(f, delimiter=',')
        for row in reader:
            y = row['timestamp'][:4]
            if int(y)==year:
                if mmsi != row['mmsi']:
        			with open(sourcedir+"seismic_cvs/"+mmsi+"_"+str(year)+'.csv', 'w') as fp:
        			    a = csv.writer(fp, delimiter=',')
        			    data = [['latitude','longitude','timestamp','mmsi','sog','cog']]
        			    for lat, lon, timestamp, sog, cog in zip (lats,lons,timestamps, sogs, cogs):
        			    	data.append([lat,lon,timestamp,mmsi, sog, cog]) 
        			    a.writerows(data)
        			mmsi = row['mmsi']
        			lats = []
        			lons = []
        			timestamps = []
        			sogs = []
        			cogs = []
                lats.append(row['lat'])
                lons.append(row['lon'])
                timestamps.append(row['timestamp']) 
                sogs.append(row['sog'])        
                cogs.append(row['cog'])



    with open(sourcedir+"seismic_cvs/"+mmsi+"_"+str(year)+'.csv', 'w') as fp:
        y = row['timestamp'][:4]
        if int(y)==year:
            a = csv.writer(fp, delimiter=',')
            data = [['latitude','longitude','timestamp','mmsi','sog','cog']]
            for lat, lon, timestamp, sog, cog in zip (lats,lons,timestamps, sogs, cogs):
            	data.append([lat,lon,timestamp,mmsi, sog, cog]) 
            a.writerows(data)