import argparse

import googleapiclient
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from oauth2client.client import GoogleCredentials
from datetime import datetime
import json

#ranges of the years
year_range = [2013,2014]
month_range =[i for i in range(1,13)]

# Grab the application's default credentials from the environment.
credentials = GoogleCredentials.get_application_default()
# Construct the service object for interacting with the BigQuery API.
bigquery_service = build('bigquery', 'v2', credentials=credentials)




vessels = [12348,36764000,212121212,224523000,224651000,224680000,224782000,259211000,303137000,338712000,350107000,365878412,366827000,366927000,367324020,367347000,367359220,368489000,371502000,412320033,412320034,412331031,412331032,412354058,412370007,412371178,412371179,412371191,412371192,412420197,412420238,412420254,412420255,412420433,412420435,412420436,412420798,412420804,412420892,412420922,412420933,412422352,412422693,412422696,412422702,412422704,412440011,412440044,412440234,412440236,412440237,412440238,412678390,412695550,412695560,412695580,412695620,412695640,412985000,413011000,413691220,413692650,413693270,416002859,416002962,416003556,416003600,416004339,416004369,416004409,416004411,416004421,416004838,416010900,416072600,416119800,416211600,416306430,416631000,431101320,431182000,431254000,431329000,431379000,431500040,431602130,431704490,431725000,431798000,432353000,432365000,432453000,432454000,432475000,432856000,440045000,440053000,440055000,440089000,440195000,440233000,440246000,440280000,440287000,440295000,440298000,440382000,440444000,440450000,440462000,440479000,440492000,440503000,440504000,440517000,440522000,440542000,440549000,440574000,440575000,440590000,440595000,440617000,440620000,440623000,440624000,440628000,440636000,440641000,440644000,440645000,440646000,440647000,440648000,440654000,440656000,440704000,440705000,440706000,440707000,440731000,440733000,440751000,440765000,440770000,440772000,440773000,440778000,440780000,440781000,440782000,440787000,440788000,440792000,440796000,440801000,440807000,440821000,440823000,440826000,440847000,440858000,440871000,440886000,440894000,440895000,440900000,440920000,440926000,440929000,440931000,440933000,440934000,440936000,440944000,440946000,440950000,440952000,440954000,440958000,440968000,440986000,440987000,440987654,440990000,440992000,441014000,441015000,441018000,441038000,441043000,441047000,441066000,441072000,441084000,441090000,441098000,441166000,441201562,441220316,441220317,441241000,441251000,441374000,441483000,441493000,441536000,441584000,441644000,441645000,441650000,441660000,441680000,441811000,441812000,441825000,441853000,444080710,512000089,512012000,512085000,515777000,520241000,529414000,529417000,529440000,529469000,529676000,529686000,529729000,563030260,576375000,577077000,735057565,735057638,735058003,735059088,760000380,760119000]

vessels = [440659000,440786000,431603220,440927000,735059089,440802000]

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
					  lat,
					  lon,
					  timestamp,
					  speed
					FROM
					  [scratch_david_vesselsPyBossa.sharkpaper_fishingvesseltracks]
					WHERE
					  mmsi ='''+str(mmsi)+'''
					  AND lat>-90
					  AND lat<90
					  AND lon !=0
					  AND lat IS NOT null
					  AND lon IS NOT NULL
					  AND timestamp IS NOT NULL
					  AND speed is NOT NULL
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


			if len(m_lats)>5: #has to have at least 100 positions in the month
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
				f = open("../../../data/vessels/sharkpaper/"+str(mmsi)+"_"+str(y)+"_"+str(m)+".json",'w')
				f.write(t)
				f.close()
			else:
				print "too many values for "+str(mmsi) + " on "+str(y)+ "-"+str(m)

