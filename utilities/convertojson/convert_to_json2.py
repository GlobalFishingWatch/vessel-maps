import csv
import json



vessels = [123450800,512003888,367338620,775000000,735059223,205548000,224016620,356394000,359001000,432927000]

sourcedir = "../../data/vessels/"

for v in vessels:
	lats = []
	lons = []
	sogs = []
	timestamps = []
	filename = str(v)+".csv"

	with open(sourcedir + filename,'rU') as f:
	    reader = csv.DictReader(f, delimiter=',')
	    for row in reader:
	    	try:
	    		lat = round(float(row['latitude']),5)
	    		lon = round(float(row['longitude']),5)
	    		sog = round(float(row['sog']),1)
	    		timestamp = row['timestamp']
	    		if lat!= 0 and lat != 90 and lon!=0:
		    		sogs.append(sog)
		    		lats.append(lat)
		    		lons.append(lon)
		    		timestamps.append(timestamp)
	    	except:
	    		print row['lat'], row['lon']

	js = {}
	js['lats']=lats
	js['lons']=lons
	js['sogs']=sogs
	js['timestamps']=timestamps
	# js['type'] = "LineString"
	# js['coordinates'] = [[round(lon,5),round(lat,5)] for lat,lon in zip(lats,lons)] #stupid to have higher than 5 digets
	t = json.dumps(js)
	f = open("../../data/vessels/"+str(v)+".json",'w')
	f.write(t)
	f.close()

