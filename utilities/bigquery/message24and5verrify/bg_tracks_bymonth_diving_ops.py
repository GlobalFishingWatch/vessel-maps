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



vessels = [235086588,338140283,503638500,257717800,273349730,338412000,312914000,366918400,253323000,470761000,366614000,219305000,272079800,308674000,251456110,503725300,235033134,660005670,413046110,312069000,272138400,372294000,367567190,413001955,257999810,257046500,272118700,230940470,257732900,368059000,309129000,261379000,338366000,622121520,512000771,503000590,367545860,372162000,245989000,367359630,338078958,257243800,236519000,207829760,265586780,423162100,345070202,515609000,271001129,345050038,235038015,413378280,470865000,306089000,377615000,271019027,235031085,211342230,367663920,205599000,235083664,230030370,367086190,230940710,419224000,257109500,470988000,413053540,366918450,413900556,419395000,235074917,308971000,367001230,232159000,338145223,366843720,368242000,265666150,273350970,271040540,636008162,257126600,710020310,367346050,308382000,8497979,257150900,503224900,230044550,367077630,503538900,257220040,235090985,273353250,367347250,503553900,235070155,374095000,367072840,367548000,235019572,470775000,325390000,311073300,235004366,419227000,419621000,710009840,367241000,470262000,503050300,232002927,344021498,413900941,257791290,338140284,412375150,367434140,367474360,219004293,227274510,312869000,235022608,235068128,235023771,367303260,503446300,306929000,470678000,247321900,503050100,265669620,244780813,232585000,272876400,366878830,367377490,345070253,257796500,338140285,775996002,419000235,265590560,503004920,235051508,232287000,775996601,710005590,345070220,408398000,277502000,367081260,212983020,775996607,235062421,636010844,408577000,227717090,345070085,538002193,367455470,518480000,366867730,314243000,412375350,375771000,265703830,273358910]

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
					   [scratch_david_vesselsPyBossa.200_diving_ops]
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

