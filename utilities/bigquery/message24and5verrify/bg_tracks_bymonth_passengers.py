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



vessels = [211472760,367581780,244690549,657937000,518100069,413692720,244670420,538005877,211513530,413441050,338167000,413401850,247167800,525001098,211533560,525005045,211495320,244020933,247177100,366902330,265588910,525016105,413418090,211643790,440110292,203999394,412756410,227273890,273414400,235054656,525019187,533160005,265665510,265575820,257518000,276786000,211227270,235052123,227705102,271041367,211510510,271010301,240764000,503486500,243070617,775996539,367162680,244670234,422034200,211457700,477995475,219000899,431301736,251390110,367074170,211291170,244710393,244630119,525021133,211231780,413788196,203999351,413832002,230052810,227592820,271010436,244169000,273567890,366962380,211508570,237628000,265586620,229990000,244670757,273911300,525023144,247159100,309997000,367143000,413327410,265547270,209896000,525001094,271010308,257277400,271010791,224133620,440147650,367009760,367978000,211533570,338761000,717100160,440145000,525015867,247208100,413694660,247237800,243042432,431300346,367327330,264162293,884259400,440111460,265604530,431000306,237622300,251837870,211297990,224200000,224184950,366984110,255804680,470690000,309964000,269057423,574606338,338891000,548545300,309416000,205513690,366985340,258695000,247240500,800010205,244700919,367400420,235104000,271040358,367438210,244710412,525009307,211437180,367642980,470513000,620008000,257239400,230655000,258149000,247079100,303075000,239776700,235086964,257368400,211512590,413431440,232003391,529838000,259681000,431005296,271041279,230108610,224402000,277339000,240521000,316001237,316019244,211512380,44710802,367602540,219017917,211542050,525006235,725010300,372694000,413324190,219006009,227574020,273368080,355342000,367544620,413469150,265572330,412761550,211512870,412204440,227292280,431000652,413988608,413450570,211535070,211520020,235076756,413762675,540008300,525018356,413787622,249099000,219000859,232343000,230197000,345070074,269057308,375145000,244710812,247290300,367330820,211462760,574012741]

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
					   [scratch_david_vesselsPyBossa.200_passengers]
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

