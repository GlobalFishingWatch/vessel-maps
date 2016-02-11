import argparse
import googleapiclient
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from oauth2client.client import GoogleCredentials
from datetime import datetime, timedelta
import json
import numpy as np 

day_zero = datetime(2012,4,1)

d = "2012-04-01".split("-")

day_now = datetime(int(d[0]),int(d[1]),int(d[2]))

print day_zero, day_now
print (day_now - day_zero).days

exit()

grid = np.zeroes(shape=(1367,36,72))


# Grab the application's default credentials from the environment.
credentials = GoogleCredentials.get_application_default()
# Construct the service object for interacting with the BigQuery API.
bigquery_service = build('bigquery', 'v2', credentials=credentials)


lat_bin = 35
lon_bin = -130
times = []
vessels = []


if 1:
    query_request = bigquery_service.jobs()
    query_data = {
        'query': (
            '''
SELECT date, vessels FROM [scratch_david_gapanalysis.vessel_density_by_day_2012_2015] 
where lat_bin = ''' + str(lat_bin)+''' and lon_bin = ''' + str(lon_bin) + ''' order by date''')
    }

    query_response = query_request.query(
        projectId='world-fishing-827',
        body=query_data).execute()

  
    
    print('Query Results:')
    if 'rows' in query_response:
        for row in query_response['rows']:
            #print row['f'][0]['v']
            times.append(row['f'][0]['v'])
            vessels.append(int(row['f'][1]['v']))

            #print('\t'.join(field['v'] for field in row['f']))

else:# HttpError as err:
    pass
    #print('Error: {}'.format(err.content))
    #raise err

print len(times)
exit()

for d, v in zip(times,vessels):
    print d+"\t"+str(v)
