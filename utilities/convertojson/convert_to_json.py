import csv
import json




vessels = [123450800,205548000,224016620,356394000,359001000,432927000,512003888,735059223,775000000]


sourcedir = "../../data/vessels/"

for v in vessels:
	lats = []
	lons = []
	filename = str(v)+".csv"

	with open(sourcedir + filename,'rU') as f:
	    reader = csv.DictReader(f, delimiter=',')
	    for row in reader:
	    	try:
	    		lat = float(row['latitude'])
	    		lon = float(row['longitude'])
	    		lats.append(lat)
	    		lons.append(lon)
	    	except:
	    		print row['lat'], row['lon']

	js = {}
	js['type'] = "LineString"
	js['coordinates'] = [[round(lon,5),round(lat,5)] for lat,lon in zip(lats,lons)] #stupid to have higher than 5 digets
	t = json.dumps(js)
	f = open("../../data/vessels/"+str(v)+".json",'w')
	f.write(t)
	f.close()

