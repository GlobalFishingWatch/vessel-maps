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



vessels = [337800000,369255000,413820313,413975079,413975297,413813806,413778395,368030000,2242132,338471000,211512210,412360230,338670000,367626030,412360680,413418240,589327333,412070510,228887500,251207110,440122070,244660944,274382106,440141440,413901647,211668930,413990401,244650678,512003831,62000,413357130,303515000,366920940,366238710,368319000,367575310,367434260,413432500,257371500,731457156,367643990,563511000,123454322,366891140,366791090,413450410,244660859,258222000,413906446,211474520,413970721,211476020,419000489,366910920,720501355,367372420,244180386,413778878,413950139,413803178,413768000,368552000,416793000,413970372,440134620,244110172,367532840,412413010,244660619,413802800,211517780,776732074,525015295,413436080,412360010,367895000,211524100,525006134,770576296,413778503,367330620,413780594,203999433,238399040,564334566,211463350,413829144,366739920,412320690,413805206,440105520,367173260,413900894,413971142,413790932,338792000,367300160,413777142,3203,368358000,257077440,211495040,264163261,413357110,338663000,413940258,755060000,27920241,366456000,257238500,366099000,503670900,209910000,369232000,413771132,338032000,413802258,227789220,367368950,413059876,366996310,755001283,369193000,413970388,412466710,413774019,735057546,413775674,338628000,413125521,413778107,211481170,440125930,413986478,413771029,338280000,574767000,755004073,226008970,470119000,413902300,413815823,413777455,413782617,279202157,413987085,413983708,413780899,369638000,900125889,367593750,413984478,538002329,413775558,413698320,366935000,367486000,2512003,257691500,369336000,244074473,412378710,211514600,413769349,413779233,367111000,338407000,701006612,211488280,413957700,227789260,413806061,367057260,226002910,232126000,369257000,413804863,413950623,366282000,367615000,413814997,367579840,412420911,368456000,366284000,200004228,367330630,413096010,303177000,413320180,657121600,413953900,366978490,413974994,413773165,413958726,367561270,367638080,365655122]

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
					   [scratch_david_vesselsPyBossa.200_wing_in_ground]
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

