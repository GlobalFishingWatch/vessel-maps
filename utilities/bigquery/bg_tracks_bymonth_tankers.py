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


#random 100 towing vessels
vessels = [371603000,431000792,413829796,431003767,376173000,247227900,357162000,538006025,229483000,413450770,636016724,413900854,311028200,567004440,273377120,422143000,211512750,636016183,441701000,636016291,636011630,267130501,431401961,239278000,244285000,412553970,210745000,525004105,671597000,235764000,244660420,413451450,432807000,311036700,374878000,538003864,241275000,258310000,319963000,241050000,538005374,413360770,419018000,440115330,413472260,355973000,259781000,431400367,477257200,273332710,354843000,564520000,413960467,431000175,735057772,558588000,538002667,725019210,525007037,351458000,240920000,414731000,413771367,572488210,240547000,431004325,374136000,228320900,311026700,412380360,354453000,372903000,533130000,310542000,431200655,636014739,256231000,316222000,273378220,370467000,413202240,525005085,311000438,564365000,431004247,413557000,431402034,256377000,373129000,431100146,373608000,563936000,241394000,477653800,413378940,538003856,503482000,566904000,372457000,636013117,538003031,122111121,548313000,412434630,215392000,215155000,431400102,356773000,477851400,441687000,413554120,565526000,441365000,309671000,367501540,431100878,241007000,412375320,431000162,354671000,565814000,235079501,246295000,548060200,440106200,351932000,316214000,636014527,374109000,310478000,636092135,240973000,240510000,413765879,244750137,563716000,273444330,319205000,310539000,636014203,431101028,413474710,273166100,636015705,269057510,440232000,431002799,239274000,352755000,150203145,413375720,636091632,353229000,261000560,538006045,431300215,567001730,226028000,240644000,273373240,357751000,503795000,440367000,413378810,241112000,413470440,273354340,240147000,244670267,273345530,477144300,355212000,636013273,257772000,431401882,636012909,220518000,431401849,441878000,413375470,431005055,357598000,538001711,566980000,538090474,229845000,538002500,525019372,413378230,372796000,212118000,413377780,413814905,355057000,533194000,244700196,563482000,354073000,230956000,273350240]

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
					   [scratch_david_vesselsPyBossa.200_tankers]
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

