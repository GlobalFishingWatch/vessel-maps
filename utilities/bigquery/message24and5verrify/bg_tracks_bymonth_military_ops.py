import argparse

import googleapiclient
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from oauth2client.client import GoogleCredentials
from datetime import datetime
import json

#ranges of the years
year_range = [2015]
quarter_range =[i for i in range(0,4)] #three months, four quarters

# Grab the application's default credentials from the environment.
credentials = GoogleCredentials.get_application_default()
# Construct the service object for interacting with the BigQuery API.
bigquery_service = build('bigquery', 'v2', credentials=credentials)



vessels = [657111008,211210680,613006000,367370000,366999975,775909000,220428000,431999598,770576002,431999553,276700000,265500630,366999613,368881000,367211000,770576005,211210420,261233000,211211840,369970277,710400000,725000395,367877000,664302000,419090600,538070880,211210920,303859000,259045000,503115000,367949000,338988000,419059900,211903000,657887000,431999697,725001380,367279000,431999532,367923000,263020000,366966000,657717000,367852000,316009747,657715000,265618260,369998000,232697000,369970257,234597000,770576001,230997240,235005245,366999513,244911000,419000247,211211240,265591590,671470000,710482000,263015000,245311000,261279000,234084000,369461000,261263000,233063000,316009418,220432000,369930000,316013411,405000122,210000,245288000,316200000,366999508,211211170,366999770,366999658,219000417,266034000,43822180,235067855,228766000,220429000,235067941,211212720,369970763,261213000,211210670,664301100,245965000,567247000,224139770,470333000,33294408,211927000,367838000,316192000,725000329,366999973,259019000,227800900,211211310,211211190,316160000,205212000,211211160,265501220,657706000,261257000,369323000,211211320,265602480,525014074,367866000,275411000,512155000,265591580,211211960,263122000,53265489,369953000,367265000,211210480,367951000,261283000,211212400,316136000,224495000,211931000,261250000,220189000,265618270,657847000,419220264,367283000,257169900,261298000,366958000,261228000,261217000,232311959,245329000,368771000,627400600,316143000,657111030,533168000,316129000,226923000,367912000,263047002,265403000,367948000,250088000,211211200,211213640,219000416,366997110,657111061,224555000,219263000,366999983,369970517,257001000,235059372,338982000,366999977,367299000,235008226,368905000,512156000,230005150,657705000,710423000,657111053,245321000,211210910,232461600,431999556,461000404,564999000,657111051,234586000,233844000,431999595,211211820,276742000,366999600,316196000,227800800,316013412,366999524,265618280,211913000,368709000,261246000,366954000]

for mmsi in vessels:
	# t = '1420156800'
	# t= int(float(t))
	# t = datetime.utcfromtimestamp(t)

	# print t
	# print str(t)
	# t = datetime(2015,1,1)
	# print t.total_seconds()


	try:
	    query_request = bigquery_service.jobs()
	    query_data = {
	        'query': (
	            '''SELECT
					  latitude,
					  longitude,
					  timestamp,
					  sog
					FROM
					   [scratch_david_vesselsPyBossa.200_military_ops]
					WHERE
					  mmsi ='''+str(mmsi)+'''
					  AND latitude>-90
					  AND latitude<90
					  AND longitude !=0
					  AND latitude IS NOT null
					  AND longitude IS NOT NULL
					  AND timestamp IS NOT NULL
					  AND sog is NOT NULL
					ORDER BY
					  timestamp ;''')
	    }

	    query_response = query_request.query(
	        projectId='world-fishing-827',
	        body=query_data).execute()

	    sogs =[]
	    timestamps = []
	    lats = []
	    lons = []
	    
	    print('Query Results:')
	    if 'rows' in query_response:
		    for row in query_response['rows']:
		    	#print row['f'][0]['v']
		        lat = round(float(row['f'][0]['v']),5)
		        lon = round(float(row['f'][1]['v']),5)
		        sog = round(float(row['f'][3]['v']),1)
		        t = int(float(row['f'][2]['v']))
		        timestamp = datetime.utcfromtimestamp(t)
		        sogs.append(sog)
		        lats.append(lat)
		        lons.append(lon)
		        timestamps.append(timestamp)
		        #print('\t'.join(field['v'] for field in row['f']))

	except HttpError as err:
	    print('Error: {}'.format(err.content))
	    raise err

	for y in year_range:
		for m in quarter_range:
			m_lats = []
			m_lons = []
			m_sogs = []
			m_timestamps = []
			for i in range(len(lats)):
				if int(timestamps[i].month/4) == m and timestamps[i].year == y:
					m_lats.append(lats[i])
					m_lons.append(lons[i])
					m_timestamps.append(str(timestamps[i]))
					m_sogs.append(sogs[i])


			if len(m_lats)>100: #has to have at least 100 positions in the quarter
			    # zeros = 0.
			    # for i in range(len(m_sogs)):
			    # 	if m_sogs[i]==<.1:
			    # 		zeros+=1
			    # if zeros / len(m_sogs) <.3:


				js = {}
				js['lats']=m_lats
				js['lons']=m_lons
				js['sogs']=m_sogs
				js['timestamps']=m_timestamps
				# js['type'] = "LineString"
				# js['coordinates'] = [[round(lon,5),round(lat,5)] for lat,lon in zip(lats,lons)] #stupid to have higher than 5 digets
				t = json.dumps(js)
				f = open("../../data/vessels/"+str(mmsi)+"_"+str(y)+"_q"+str(m+1)+".json",'w')
				f.write(t)
				f.close()
			else:
				print "no values for "+str(mmsi) + " on "+str(y)+ "-"+str(m)

