import csv
import json



vessels = ['temp_525019038','temp_CPBRATASENA']
vessels = ['525019035','DIPASENADUA']
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
	    		lat = round(float(row['lat']),5)
	    		lon = round(float(row['lon']),5)
	    		#
	    		timestamp = row['timestamp']
	    		if lat!= 0 and lat != 90 and lon!=0:
		    		timestamps.append(timestamp)
		    		lats.append(lat)
		    		lons.append(lon)
	    	except:

				try:
					lat = round(float(row['latitude']),5)
					lon = round(float(row['longitude']),5)
					#timestamp = round(float(row['timestamp']),1)
					timestamp = row['timestamp']
					if lat!= 0 and lat != 90 and lon!=0:
						timestamps.append(timestamp)
						lats.append(lat)
						lons.append(lon)
				except:
					print row, "fail"
					exit()
			    # except:
			    # 	print row, 'fail'
	js = {}
	js['lats']=lats
	js['lons']=lons
	#js['sogs']=sogs
	js['timestamps'] = timestamps
	# js['type'] = "LineString"
	# js['coordinates'] = [[round(lon,5),round(lat,5)] for lat,lon in zip(lats,lons)] #stupid to have higher than 5 digets
	t = json.dumps(js)
	f = open("../../data/vessels/"+str(v)+".json",'w')
	f.write(t)
	f.close()

