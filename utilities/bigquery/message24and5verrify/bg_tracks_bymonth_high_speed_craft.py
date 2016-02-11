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



vessels = [577138000,538005477,503000084,257208500,413484890,235051007,249898000,413695620,235102965,251059110,412461340,219018009,250001313,257507700,525016659,413443550,377094000,235098037,412477670,376496000,247042400,565927000,412467870,412460920,235075161,412209290,419000779,657122200,477937400,276696000,470727000,247297400,413406570,503487200,259594000,367167520,224008000,362063000,235089035,345070298,422315000,470955000,258999000,235031854,238116540,440602480,902764116,366738610,235076772,235053184,235090838,235067956,259560000,412325123,412375570,440125730,377489000,412211589,258108000,413766863,413989708,224101000,244830667,235089685,367026670,235103214,243070115,219460000,413366040,209375000,209122000,235083707,470304000,235104009,235069011,244830872,533015700,368331000,477197300,412462040,244830668,416476000,258202500,503010620,377005000,235000799,657110800,419000428,235091254,235074636,257336400,438037000,238613740,413695450,235092014,367104050,235107648,470329000,367020870,353393000,412460910,470116000,412414580,235102932,247492000,338036000,316014594,412324333,356,235036365,470149000,211209290,258306500,271042657,219002731,338126447,244710979,212394000,219463000,235092017,235103032,239658000,1020012020,413377610,368410000,345010039,235092981,911497944,725001785,238648410,422022000,228322800,259427000,533015500,366953970,228325800,413468090,338052430,272643000,412358610,725066537,375069000,311074000,235068462,258064000,525018273,512000741,235085534,219418000,413471870,235108448,423013100,271002469,235102689,345070190,219018788,235105282,219017203,235081002,235072516,235089895,244730569,235080246,601212400,235094873,210941000,224197000,540011300,338163000,413464420,235003348,319362000,576305000,434123500,760029709,413460550,440120320,47795119,366813470,235092103,235007473,211214980,228305900,209074000,512000742,237836700,201100138,413857925,235080196,235096619,376237000,412880120,525016501,235108597,370523000,235064699,366693520,431001105,235103385]

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
					   [scratch_david_vesselsPyBossa.200_high_speed_craft]
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

