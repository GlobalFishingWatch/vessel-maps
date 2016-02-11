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



vessels = [256000244,265712710,235008854,230047550,367583060,249389000,244670926,244110083,601161700,235038638,416243600,367399010,367476540,413096260,366916090,207832390,247042920,235075616,235085287,503708300,538070922,316026271,211655910,306753000,235082136,235097329,235109224,338140617,367582950,448159576,211296460,258155530,235107858,412525000,265582490,419001202,367488870,238968740,205881910,503461500,503797400,272105100,445275000,269214000,367114920,367421820,219007466,316020657,269105760,518728000,211473160,249555000,503788100,366735860,366832850,235053629,366841360,225915770,238650340,211669490,512003517,503010070,301000022,710004520,227040690,205443710,235091248,338184628,257814470,367562570,232398000,235053112,257564820,271020124,265664330,577228000,367647830,227284980,257043500,224108660,412092085,338140775,373521000,338141077,265613280,235081631,503518700,229167000,235026342,211294080,367640250,265677470,503021980,538070904,775992030,235105528,367457480,235099883,987357573,248569000,211390280,244596000,367677550,360965432,224440220,224253760,412329635,538070298,236111467,265544600,366990760,235091719,224340630,563028440,235064936,228326700,265542140,211622090,725001240,538070307,278782000,367573650,275727530,338082289,338185302,229804000,118855500,265744740,503006390,503470400,503452400,503633400,367636240,225982107,338179712,244790600,244710608,265632230,338151147,367461360,244690309,227795830,367664240,235057366,227116170,503699300,257753390,412092090,265605010,366886050,367449030,367371980,235107307,250001803,316025138,257066640,366628610,247050190,227650980,235089127,367431880,238025240,205797010,235072117,211306370,271043069,235013663,248000373,257741290,227683560,367525340,265621840,503755200,367090940,316010949,227132610,247322670,338093392,232007590,518378000,211219240,413788349,244770240,266271000,238592240,211355670,367412440,367442310,367418520,338173478,224279440,367440940,276004580,211695070,316024522,376268000,234702000,265688730,373076000,238302000]

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
					   [scratch_david_vesselsPyBossa.200_sailing]
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

