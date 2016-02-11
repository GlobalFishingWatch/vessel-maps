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



vessels = [440500130,265501860,413058020,331000004,413788387,503000012,413050030,266334000,367531720,265422000,412097150,205437190,412057580,259040000,659061000,413213000,563000006,413044950,265820000,316023267,236112094,316021598,275307000,503339200,211627340,275342000,413009227,412057560,211126670,413035020,367666930,412035130,412035081,211179240,211309750,412488843,412000203,211182390,244070618,412015190,412370020,367639120,412040290,367638940,205469000,525001004,265515580,413413306,6459028,369494594,211493040,412032021,235101211,503065000,265509150,412040360,412040330,413035160,503423700,735059055,412015110,247176800,413024150,701527000,413888839,338096624,207110000,246586000,413035490,412045014,412671000,413304080,413035530,235054954,211548430,413044830,275186000,412460056,419956483,245171000,701571000,205387490,412030040,412060070,338112395,413035430,257019000,412380750,412021017,246096000,413110008,237708400,362183000,412420715,413045190,211217670,218346000,413035180,412050210,338945000,413827345,244917000,413888807,211309740,265044000,516260863,440299000,413057010,377645000,412040390,412040010,413480080,265390000,412032022,369990149,503571400,277533000,244740184,413045040,264900159,367531750,412031001,273376340,735057506,265565250,413696040,413096070,601739000,265504730,244670377,211152520,412015090,412123126,413024120,413329840,440891000,244964000,211233510,245659000,413044630,412331230,246562000,211118300,244566000,246223000,316105000,235010460,413035330,211215700,246221000,412040050,413098209,276146000,413433260,316021592,413850802,440460000,440115400,548357891,413452210,900033002,412112300,412046014,701505000,266125000,413775379,412009157,457069000,367503220,265675230,244030470,338282000,246310000,440136000,413523110,730000145,413096180,265515570,412031018,412050040,265566020,244077693,253103792,440114740,412380560,509909950,412040030,503006850,227190370,265675220,412015050,413035520,367639170,367523960,701509000,412035160,276798000,207451100,413330110,265501900]

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
					   [scratch_david_vesselsPyBossa.200_law_enforcement]
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

