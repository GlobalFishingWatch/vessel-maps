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




vessels = [123450800,512003888,367338620,775000000,735059223,205548000,224016620,356394000,359001000,432927000]

# list from 2/24, file CLAV_fishing_ambiguous_20160224.csv
vessels = [416702000,271072475,577077000,416171700,224224000,441032000,577105000,370599000,229705000,432106000,271072208,227370000,577132000,636092595,416308000,577077000,577132000,576277000,370599000,224303000,356567000,227146300,529578000,416001900,416001900,227458000,577077000,627093246,357788000,432861000,431731000,431301346,357788000,227146300,576274000,370599000,227503000,431619000,529578000,431619000,431465000,441032000,416602000,441720000,431254000,576507000,229705000,431717000,432954000,273356760,576277000,576397000,224307000,224276000,576274000,370599000,431002000,416308000,431469000,576276000,576397000,229705000,271072850,576274000,577132000,577169000,576397000,529346000,577077000,576397000,416730000,432370000,431028000,576274000,416833000,432564000,577105000,576274000,431796000,224307000,416171700,432564000,432558000,432288000,431263000,431263000,432106000,627093246,636092595,224082260,416602000,416602000,416730000,431919000,224072890,247110180,431614000,431796000,273356760,432861000,413270220,432558000,247110080,432399000,577132000,413270220,263575000,227370000,576270000,577105000,374008000,577105000,273351170,224082260,224020170,357788000,529578000,224100530,431000423,432399000,576276000,529346000,432760000,273351170,431710000,431225000,577077000,374008000,431263000,374008000,416833000,577169000,431469000,273351170,529346000,432395000,372295000,413270220,224224000,431465000,431263000,576270000,227503000,271072208,416702000,432322000,431225000,440182000,432395000,636092595,224020170,627093246,431717000,432321000,224276000,627093246,576507000,431272000,441032000,247110180,432370000,224020170,224100530,576507000,627093246,576270000,273356760,441032000,247110080,431731000,440182000,431710000,229705000,224082260,627093246,431272000,432760000,577169000,370599000,431465000,273356760,577169000,273351170,576277000,441032000,576397000,256000325,576270000,224100530,576276000,529578000,441720000,577132000,529346000,356567000,273356760,441720000,432288000,238602140,577169000,576277000,577105000,576276000,431254000,576277000,431028000,440182000,432322000,357788000,431919000,432321000,577132000,529578000,224303000,256000325,576276000,431614000,441720000,416833000,576507000,416730000,440182000]

for mmsi in vessels:

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
					  [tilesets.pipeline_2015_08_24_08_19_01]
					WHERE
					  mmsi ='''+str(mmsi)+'''
					  AND latitude>-90
					  AND latitude<90
					  AND longitude !=0
					  AND latitude IS NOT null
					  AND longitude IS NOT NULL
					  AND timestamp IS NOT NULL
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
				js = {}
				js['lats']=m_lats
				js['lons']=m_lons
				js['sogs']=m_sogs
				js['timestamps']=m_timestamps
				# js['type'] = "LineString"
				# js['coordinates'] = [[round(lon,5),round(lat,5)] for lat,lon in zip(lats,lons)] #stupid to have higher than 5 digets
				t = json.dumps(js)
				f = open("../data/vessels/"+str(mmsi)+"_"+str(y)+"_"+str(m)+".json",'w')
				f.write(t)
				f.close()
			else:
				print "no values for "+str(mmsi)

