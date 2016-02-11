import argparse
import googleapiclient
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from oauth2client.client import GoogleCredentials
from datetime import datetime
import json
import numpy as np


sourcedir = ''
cellsize = .25

def write_asc(out_file_name,grid):
    f = open(out_file_name, "w")
    f.write("ncols "+str(ncols)+"\n")
    f.write("nrows "+str(nrows)+"\n")
    f.write("xllcorner "+str(xllcorner)+"\n")
    f.write("yllcorner "+str(yllcorner)+"\n")
    f.write("cellsize "+str(cellsize)+"\n")
    f.write("no_data_value -9999\n")
    for r in np.flipud(grid):
        s = ""
        for c in r:
            s+=str(int(c))+" "
        s = s[:-1]+"\n"
        f.write(s)
    f.close()


def query_bigquery(query_data, out_file_name):

    try:
        query_request = bigquery_service.jobs()
        
        query_response = query_request.query(
            projectId='world-fishing-827',
            body=query_data).execute()


        print('Query Complete:')
        


        values = []
        lats = []
        lons = []
        if 'rows' in query_response:
            for r in query_response['rows']:
                bucket_lon = float(r['f'][0]['v'])
                bucket_lat = float(r['f'][1]['v'])
                count = int(r['f'][2]['v'])
                lats.append(bucket_lat)
                lons.append(bucket_lon)
                values.append({'bucket_lon':bucket_lon, 'bucket_lat':bucket_lat, 'count':count})



    except HttpError as err:
        print('Error: {}'.format(err.content))
        raise err

    print 'boudning box: ',
    print max(lats), min(lats), max(lons), min(lons)
    global ncols
    ncols = (max(lons)-min(lons))/cellsize + 1
    global nrows 
    nrows = (max(lats)-min(lats))/cellsize + 1
    global xllcorner
    xllcorner = min(lons)
    global yllcorner
    yllcorner = min(lats)
    grid = np.zeros((nrows,ncols))

    for v in values:
        r = int(float(v['bucket_lat'])*4-yllcorner*4)
        c = int(float(v['bucket_lon'])*4-xllcorner*4)
        grid[r,c] = int(v['count'])

    write_asc(out_file_name,grid)
    return grid



# Grab the application's default credentials from the environment.
credentials = GoogleCredentials.get_application_default()
# Construct the service object for interacting with the BigQuery API.
bigquery_service = build('bigquery', 'v2', credentials=credentials)



query_score_ffaclav = {  'query': ('''SELECT bucket_lon, bucket_lat, COUNT(*) FROM
                                      (SELECT
                                        FLOOR(FIRST(latitude)*4)/4 AS bucket_lat,
                                        FLOOR(FIRST(longitude)* 4)/4 AS bucket_lon
                                       FROM [scratch_david.sharkpaper_2013_2014_clavffa]
                                       WHERE score>.5
                                       GROUP BY mmsi, local_day)
                                     GROUP BY bucket_lat, bucket_lon''') }

query_speed_ffaclav = {  'query': ('''SELECT bucket_lon, bucket_lat, COUNT(*) FROM
                                      (SELECT
                                        FLOOR(FIRST(latitude)*4)/4 AS bucket_lat,
                                        FLOOR(FIRST(longitude)* 4)/4 AS bucket_lon
                                       FROM [scratch_david.sharkpaper_2013_2014_clavffa]
                                       WHERE speed_filter=1
                                       GROUP BY mmsi, local_day)
                                     GROUP BY bucket_lat, bucket_lon''') }

query_score_no_ffaclav = {  'query': ('''SELECT bucket_lon, bucket_lat, COUNT(*) FROM
                                      (SELECT
                                        FLOOR(FIRST(latitude)*4)/4 AS bucket_lat,
                                        FLOOR(FIRST(longitude)* 4)/4 AS bucket_lon
                                       FROM [scratch_david.sharkpaper_2013_2014_not_clavffa]
                                       WHERE score>.5
                                       GROUP BY mmsi, local_day)
                                     GROUP BY bucket_lat, bucket_lon''') }

query_speed_no_ffaclav = {  'query': ('''SELECT bucket_lon, bucket_lat, COUNT(*) FROM
                                      (SELECT
                                        FLOOR(FIRST(latitude)*4)/4 AS bucket_lat,
                                        FLOOR(FIRST(longitude)* 4)/4 AS bucket_lon
                                       FROM [scratch_david.sharkpaper_2013_2014_not_clavffa]
                                       WHERE speed_filter=1
                                       GROUP BY mmsi, local_day)
                                     GROUP BY bucket_lat, bucket_lon''') }


fc_score = query_bigquery(query_score_ffaclav, "ffaclav_score_2013_2014.asc")
fc_speed = query_bigquery(query_speed_ffaclav, "ffaclav_speed_2013_2014.asc")
nfc_score = query_bigquery(query_score_no_ffaclav, "no_ffaclav_score_2013_2014.asc")
nfc_speed = query_bigquery(query_speed_no_ffaclav, "no_ffaclav_speed_2013_2014.asc")

print "fc score = ", np.sum(fc_score)
print "fc speed = ", np.sum(fc_speed)

print "not in database score = ", np.sum(nfc_score)
print "not in database speed = ", np.sum(nfc_speed)

score_minus_speed = fc_score - fc_speed
write_asc('ffaclav_score_minus_speed.asc',score_minus_speed)


