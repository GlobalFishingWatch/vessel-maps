import argparse

import googleapiclient
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from oauth2client.client import GoogleCredentials
from datetime import datetime
import json

#ranges of the years
year_range = [2014,2015]
month_range =[i for i in range(1,13)]

# Grab the application's default credentials from the environment.
credentials = GoogleCredentials.get_application_default()
# Construct the service object for interacting with the BigQuery API.
bigquery_service = build('bigquery', 'v2', credentials=credentials)




vessels = [412002777,316008961,412423199,412328565,412469022,440000690,412418996,412430414,251194540,200000055,412212518,227101600,412479576,100704340,412061922,412332837,110701275,412432048,247155210,412437435,257488620,412448749,416004801,412284083,412762020,412444188,224055250,412447295,412464376,413000110,412443322,412413220,412462593,800017081,412322577,412352633,412444796,412470461,412419975,412286699,413011032,432845000,412008170,251415440,412412715,412443614,219019804,412425899,412421803,412449545,412416335,900007537,231184000,796917797]
vessels = [701000662,725009500,412360539,257311740,900658520,412416586,412441214,998508330,257705500,800021303,900405802,247051730,100706176,900000328,257001210,412480156,412596013,412450746,412123411,345903913,265502370,251415640,800028837,412428092,200001801,900303106,412411689,999000013,263583000,90143213,416029363,413441090,261008070,235071779,412473587,412433799,224094160,271072382,412322696,412457011,247121880,412433643,228282000,466518320,265616100,247121820,412332286,412459953,412464495,412202682,338145405,824335820,412515898,412419197,235087027,412464331,410025515,412489777,412441905,412445383,412449247,412323921,412417063,412001628,412478686,412450085,412328918,304145000,247143580,900402635,270007565,412435094,265668860,130400923,412329271,272740000,412462038,231045000,100705209,412064497,412431119,412213461,412417065,412416059,412201603,412413956,412286805,251576540,900019534,412421998,412430411,412418804,412510026,800036107,200005718,224020790,412437981,412422289,412698540,412300862,259595000,413214763,440500247,900412851,412469752,412460866,800003792,412427022,431702990,200006419,412330746,416000831,412418459,412206498,412327101,235090864,412479526,900264110,412418411,988585757,228258000,900367122,200007915,412412192,271062117,412446733,412202537,345904243,412568997,800036705,367416270,412413602,412418986,412423422,247063630,412200527,412213273,699889966,413022596,900006043,251080110,210000009,205155000,412328001,900404892,412326262]

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
					  [scratch_david.random_200_fishing_vessels]
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
		for m in month_range:
			m_lats = []
			m_lons = []
			m_sogs = []
			m_timestamps = []
			for i in range(len(lats)):
				if timestamps[i].month == m and timestamps[i].year == y:
					m_lats.append(lats[i])
					m_lons.append(lons[i])
					m_timestamps.append(str(timestamps[i]))
					m_sogs.append(sogs[i])


			if len(m_lats)>100: #has to have at least 100 positions in the month
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
				f = open("../../data/vessels/"+str(mmsi)+"_"+str(y)+"_"+str(m)+".json",'w')
				f.write(t)
				f.close()
			else:
				print "no values for "+str(mmsi) + " on "+str(y)+ "-"+str(m)

