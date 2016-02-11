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



vessels = [219826000,316001616,503151500,316004943,265732940,316007682,366999622,316005374,369494425,371278000,316017000,338158711,366999707,413109000,205037800,701000022,235007795,265570780,369493624,440559000,36663,211205600,636012442,219167000,431093000,251363110,224070190,36603,219000193,272684000,211290190,369493460,227170920,323000057,422313000,275159000,258258500,265576690,219000174,265571660,224030380,227005130,316115000,111224512,220003000,246156000,235094359,272683000,271010037,622115018,432740000,251285110,224157670,211205650,366999609,431282000,357536000,235030386,432527000,257218500,271043387,235091414,231595000,211362530,263104000,503144600,271010032,246281000,265506380,369493007,257382500,219007457,263058004,265636740,367260000,616962000,258073000,230988240,232004399,316001375,503041600,235106574,367285000,503592100,265580750,265705100,316004106,366999616,263070000,257918900,548061100,111219507,36628,431420000,265506310,367292000,436000153,338926409,235101098,265568080,211141920,235110657,227009310,235097314,224069950,316005375,232002574,412054790,244790292,224493000,232002480,725019687,316005758,277078000,369494177,369990102,316010216,308246000,265581960,265634990,235086904,265546950,225391000,265546970,259460000,265630560,431800063,440087000,251604000,227007020,316006673,235101096,367602350,431100060,265745680,211290170,232010878,205379990,265714480,265587440,265526850,232002183,111224509,271010038,271010031,219014951,316002528,235077918,234368000,235007808,211362540,412621000,473111186,224003390,235003642,367291000,224860000,211290210,235091304,227010490,219186000,246514000,230059760,412021170,244248000,375138000,316013639,219002791,345036018,224556340,219010518,211428100,238116240,111219506,219018258,235005115,224944850,412380480,232003052,235007809,265628490,36665,36630,413054540,265660450,211401930,367290000,503654900,235082759,247021900,235092233,219009417,219001959,235108934,265585880,369493428,230061400,265687880,219011205,257227000]

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
					   [scratch_david_vesselsPyBossa.200_search_and_rescue]
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

