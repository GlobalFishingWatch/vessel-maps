import argparse
import googleapiclient
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from oauth2client.client import GoogleCredentials
from datetime import datetime, timedelta
import json
import numpy as np 

day_zero = datetime(2012,4,1)
grid = np.zeros(shape=(1370,36,72))

# print (datetime(2015,12,31) - day_zero).days

# exit()

# Grab the application's default credentials from the environment.
credentials = GoogleCredentials.get_application_default()
# Construct the service object for interacting with the BigQuery API.
bigquery_service = build('bigquery', 'v2', credentials=credentials)


try:
    query_request = bigquery_service.jobs()
    query_data = {
        'query': (
            '''
SELECT date, lat_bin, lon_bin, vessels 
FROM [scratch_david_gapanalysis.vessel_density_by_day_2012_2015]''')
    }

    query_response = query_request.query(
        projectId='world-fishing-827',
        body=query_data).execute()
    
    print('Query Results:')
    if 'rows' in query_response:
        for row in query_response['rows']:
            d = row['f'][0]['v'].split("-")
            d = datetime(int(d[0]),int(d[1]),int(d[2]))
            d_index = (d-day_zero).days
            lat_bin = float(row['f'][1]['v'])/5
            lon_bin = float(row['f'][2]['v'])/5
            #times.append(row['f'][0]['v'])
            v = int(row['f'][3]['v'])
            grid[d_index][lat_bin][lon_bin] =  v

            #print('\t'.join(field['v'] for field in row['f']))

except HttpError as err:
    print('Error: {}'.format(err.content))
    raise err


np.save('vessel_density.npy', grid)
