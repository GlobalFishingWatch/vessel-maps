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



vessels = [259665000,367495980,245121000,244700518,316013161,413816268,251606110,368756000,574100159,412070090,775810000,273443580,225386000,419001009,211500040,419000644,412475890,230028680,205330790,412008333,601120519,244147000,245443000,413271150,311019800,413363350,253311000,235065925,422248000,273352310,244830652,574012796,249139000,263139000,279202325,219007363,253046000,413375130,312139000,227148000,244710850,413461110,636014663,564986000,272514000,258244000,244780536,412376070,244740925,412376010,412018480,574100103,659252000,357681000,412375790,257254500,412303160,257750600,244750450,243070818,419152000,419792000,413350620,367117140,431004385,232003506,244770799,574100133,377272000,412270580,413437560,227682070,601140359,100904029,413484230,412373820,205280590,412704240,203999358,413021180,273452350,211588410,413363330,412321270,413699190,253188000,413482930,412070420,671348000,273194000,205555000,211669090,800150305,211541710,412472970,341903000,576326000,211588490,244710911,412057020,440008790,413444670,428290000,574100228,232000790,244730483,367317850,266313000,366939140,225005960,367366670,244700254,211638060,273411366,243072102,244690016,637057960,574012795,412435440,244730286,412426020,200003794,413442240,574100164,205051000,244010568,211626060,367498360,413695810,244780207,276781000,367500770,538002801,244780696,205146000,235084947,436000326,413358690,228344700,212890000,253104000,725000255,251524000,277002000,338158987,219573000,413406460,574100236,413303290,338104037,243042515,211294420,244740092,272705000,503541000,413040010,341607000,244780537,265831000,211670280,205062000,574100188,273358970,419132000,245820000,244690101,211536210,244272000,211660790,413362640,413551260,419000503,205114000,574100229,211470570,258357000,210921000,257548800,244790087,227105230,303117000,419000296,219001514,316022888,413356450,574101377,219001647,367468880,244750048,249127000,211631370,211606120,257005970,367635840,253093000,244790391,413450130,412473920,211626540,243042401]

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
					   [scratch_david_vesselsPyBossa.200_dredging_or_underwater_ops]
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

