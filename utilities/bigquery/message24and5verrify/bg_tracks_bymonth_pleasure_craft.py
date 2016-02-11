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



vessels = [367367320,271041023,367304550,367391870,338165885,257661800,367645050,503470200,271041985,377534000,205417510,229891000,567507000,215243000,244810194,538070509,316025203,367303760,367477510,9103567,271017016,303535000,422764000,366788910,319295000,538070427,271040993,219013226,563014690,319052400,257840870,338147656,319964000,503007460,271041721,207824860,338094686,271044267,265620030,422007600,237963600,271042123,235087458,224052990,369516000,265751580,538070658,235104118,338168353,338066905,244780978,338129773,271040972,538070339,375119000,353001344,238779140,367414180,219020400,319026600,367409580,219001853,416004839,319634000,367619960,251253440,503023320,225958860,319061900,503697300,338202134,271041207,265655500,235061569,244770432,230021100,211703500,258121590,244740678,319005500,258039720,538070513,412439041,271041488,338148853,265578210,367525270,338051951,235088747,413904129,339306000,265675920,538080079,273382420,211487190,319041000,271042940,319735000,235093686,338146125,338095845,319618000,367631830,224620680,257566700,319055900,235100119,271041104,244670950,258094990,445402000,258040920,247115500,538080008,319059100,503514000,319078900,319993000,367316540,265710270,226096000,271041299,247254490,319031900,319112000,244660837,248419000,316020913,257575190,271041645,244270334,367603590,235059000,353001458,235112247,338181063,244730315,377039000,271010660,205194324,367434620,367635390,525024075,212983041,271040200,227106070,319520000,319775000,366041153,367400370,271043847,251192640,248000331,319079300,319908000,212983017,367533740,369578000,211684850,257728190,563021710,236111998,258129650,338092675,258178560,273337860,9103568,563034390,211411480,244770397,271040511,413202091,258094980,367420190,367422280,207825520,413788347,235074591,538070760,211353020,563025850,338135832,306970007,247046060,258138570,319034600,9103758,367586160,9104168,367541760,338146617,258996970,271043597,338163729,232716000,503648400,271041157,235068081,303454000,367415090]

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
					   [scratch_david_vesselsPyBossa.200_pleasure_craft]
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

