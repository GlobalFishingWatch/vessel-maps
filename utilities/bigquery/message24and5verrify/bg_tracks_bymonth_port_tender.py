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



vessels = [271010755,413791176,271010402,271001184,271043421,413457190,412328520,271010494,235103029,272023100,503028810,413809683,428150815,211624330,271044102,503507600,272118500,271041571,412330610,265521460,272071900,271043820,227011090,219012397,351009373,338106016,413771176,272086800,263671870,235022613,440114370,211471230,271017011,503494900,413303610,236111242,369970007,263671860,271043514,440700470,645304000,413220118,272118800,412369699,235087045,412438230,351008921,367376310,263621000,272102700,413821278,265513140,503010510,367616090,421357560,271040321,272010719,366855940,235079911,271010590,273354570,423187100,503725200,272058800,271042094,503531900,224357880,636012580,219015153,413474440,413327170,271010841,224003210,413554790,503769100,860031906,273348160,503543100,265737440,413467340,503680000,503715500,219010987,503498800,271040440,412361650,272058600,512004963,265623120,271010910,273320940,273375130,271044149,305588000,219010979,265688500,230941690,224366360,211662170,413357470,246336000,412428016,90909,271010630,537021425,412379780,272112900,246548009,275283000,272058700,440133510,232004751,257761500,367352680,273353570,440134280,787777888,272005900,272121400,271001170,367067090,412419660,271010403,413453260,272091400,440133490,351008920,224026720,8396,440140010,503024740,533000204,503530900,235081368,440148030,236111668,367540350,503616300,503710300,219005313,257558800,351008991,440133460,273362060,235105849,225976920,412374020,235057852,660001310,271010715,235093883,227168170,235090387,235071183,271040415,512003419,412302038,211225620,414041077,271001198,440133520,271040408,525019421,265685680,291710118,227027000,277486000,431000803,412756650,271010493,367098330,273315360,271043401,412488989,503734600,265687230,235001425,413806244,213752000,246242000,503574700,366648910,351008934,271010400,366982260,245418000,413447776,235110174,563032530,367474960,440133540,412302777,244780981,413817656,235059964,272115100,272614000,225980521,273449780,271040650]

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
					   [scratch_david_vesselsPyBossa.200_port_tender]
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

