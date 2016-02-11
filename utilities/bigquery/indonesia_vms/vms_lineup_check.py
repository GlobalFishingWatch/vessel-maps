import argparse

import googleapiclient
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from oauth2client.client import GoogleCredentials
from datetime import datetime
import json
import csv

sourcedir = ''
filename = 'tempresults.csv'

m_vessels = []
v_vessles = []

with open(sourcedir + filename,'rU') as f:
    reader = csv.DictReader(f, delimiter=',')
    for row in reader:
        v_vessles.append(row['vms_shipname'])
        m_vessels.append(row['orbcom_mmsi'])



# Grab the application's default credentials from the environment.
credentials = GoogleCredentials.get_application_default()
# Construct the service object for interacting with the BigQuery API.
bigquery_service = build('bigquery', 'v2', credentials=credentials)





for mmsi, vms_name in zip(m_vessels, v_vessles):

	try:
	    query_request = bigquery_service.jobs()
	    query_data = {
	        'query': (
	            '''
				SELECT
				  FLOOR(AVG(dist)) ave_distance,
				  FLOOR(NTH(16, QUANTILES(dist, 21)))
				FROM (
				  SELECT
				    (ACOS(COS(RADIANS(90-a.latitude)) *COS(RADIANS(90-b.lat)) +SIN(RADIANS(90-a.latitude)) *SIN(RADIANS(90-b.lat)) *COS(RADIANS(a.longitude-b.lon)))*6371000 +  ABS(TIMESTAMP_TO_SEC(a.timestamp) - TIMESTAMP_TO_SEC(b.timestamp))*5)  dist //10 knots is 5 m/s, so we're converting time differences to spatial differences
				  FROM ( SELECT * FROM 
				      [scratch_david.GFW_bucketed_VMS_Nov1_Jan13] WHERE shipname = "'''+vms_name +'''")
				     a
				  JOIN EACH (
				    SELECT
				    *
				    FROM
				      [scratch_david.GFW_bucketed_orbcomm_Nov1_Jan13] WHERE mmsi = '''+mmsi+'''
				    ) b
				  ON
				    a.bucket_time = b.bucket_time )
   

	            ;''')
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
		    	# print row
		        print mmsi, "\t", vms_name, "\t", round(float(row['f'][0]['v']))
		        # lon = round(float(row['f'][1]['v']),5)
		        # sog = round(float(row['f'][3]['v']),1)
		        # t = int(float(row['f'][2]['v']))
		        # timestamp = datetime.utcfromtimestamp(t)
		        # sogs.append(sog)
		        # lats.append(lat)
		        # lons.append(lon)
		        # timestamps.append(timestamp)
		        #print('\t'.join(field['v'] for field in row['f']))

	except HttpError as err:
	    print('Error: {}'.format(err.content))
	    raise err




