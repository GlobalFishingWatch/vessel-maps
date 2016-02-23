import argparse
import googleapiclient
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from oauth2client.client import GoogleCredentials
from datetime import datetime
import json
import numpy as np
import csv

sourcedir = ''
cellsize = .25
out_folder = "../../data/pipa_v2/"


mmsi_1a = []
mmsi_1b = []
mmsi_s8 = []
mmsi_s2 = []

with open('mmsi_list_v2.csv','rU') as f:
    reader = csv.DictReader(f, delimiter=',')
    for row in reader:
        mmsi = row['mmsi']
        if row['Fig 1A']:
            mmsi_1a.append(mmsi)
        if row['Fig 1B']:
            mmsi_1b.append(mmsi)
        if row['Fig S8']:
            mmsi_s8.append(mmsi)
        if row['Fig S2']:
            mmsi_s2.append(mmsi)



def query_bigquery(query_data, out_file_name, cellsize):

    try:
        query_request = bigquery_service.jobs()
        
        query_response = query_request.query(
            projectId='gfw-partners',
            body=query_data).execute()

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

    if 1:
        if len(lats) == 0:
            print "no values for ", mmsi
            return


        global xllcorner
        global yllcorner
        global ncols
        global nrows 

        if cellsize == .25:
            ncols = (178-167)*4
            nrows = -(- 8 - 0.5)*4
            yllcorner = -8
            xllcorner = -178
            c_inverse = 4

        if cellsize == 1:
            ncols = (30+(180-73))
            nrows = (15+15)
            yllcorner = -15
            xllcorner = -210
            c_inverse = 1

        grid = np.zeros((nrows,ncols))

        #print ncols, nrows, xllcorner, yllcorner

        for v in values:
            lon = int(v['bucket_lon'])
            if lon > 0:
                lon = lon - 360
            r = int(v['bucket_lat'])-yllcorner*c_inverse
            c = lon - xllcorner/cellsize
            print r, v['bucket_lat'], c, lon
            grid[r][c] = int(v['count'])

        np.flipud(grid).dump(open(out_file_name.replace(".asc",".npy"), 'wb'))

    else:
        print "fail!" , mmsi




# Grab the application's default credentials from the environment.
credentials = GoogleCredentials.get_application_default()
# Construct the service object for interacting with the BigQuery API.
bigquery_service = build('bigquery', 'v2', credentials=credentials)

# for mmsi in mmsi_1a:
#     print mmsi
#     query = {  'query': ('''SELECT
#       bucket_lon,
#       bucket_lat,
#       COUNT(*) count
#     FROM (
#       SELECT
#         integer(FLOOR(FIRST(lat)*4)) AS bucket_lat,
#         integer(FLOOR(FIRST(lon)* 4)) AS bucket_lon
#       FROM
#         [PIPA_Policy_Paper.PIPA_fig_1A]
#       WHERE mmsi = '''+mmsi +'''
#       and local_day >= timestamp("2014-07-01 00:00:00")
#       and local_day < timestamp("2015-01-01 00:00:00")
#       and lat<.5
#       GROUP BY
#         mmsi,
#         local_day)
#     GROUP BY
#       bucket_lat,
#       bucket_lon''') }

#     query_bigquery(query, out_folder+"1a/"+mmsi+".asc", cellsize)


# print "mmsi_1b"

# for mmsi in mmsi_1b:
#     print mmsi
#     query = {  'query': ('''SELECT
#       bucket_lon,
#       bucket_lat,
#       COUNT(*) count
#     FROM (
#       SELECT
#         integer(FLOOR(FIRST(lat)*4)) AS bucket_lat,
#         integer(FLOOR(FIRST(lon)*4)) AS bucket_lon
#       FROM
#         [PIPA_Policy_Paper.PIPA_fig_1B]
#       WHERE mmsi = '''+mmsi +'''
#       and local_day >= timestamp("2015-01-01 00:00:00")
#       and local_day < timestamp("2015-07-01 00:00:00")
#       and lat<.5
#       GROUP BY
#         mmsi,
#         local_day)
#     GROUP BY
#       bucket_lat,
#       bucket_lon''') }

#     query_bigquery(query, out_folder+"1b/"+mmsi+".asc", cellsize)



# print "going to mmsi_2"
# cellsize = 1

# for mmsi in mmsi_s8:
#     print mmsi, 
#     query = {  'query': ('''SELECT
#   bucket_lon,
#   bucket_lat,
#   COUNT(*)
# FROM (
#   SELECT
#     integer(FLOOR(first(lat))) AS bucket_lat,
#     integer(FLOOR(first (lon))) AS bucket_lon
#   FROM
#     [PIPA_Policy_Paper.Tropical_Pacific_Purse_Seine_2014_Aug_29_2015]
#   WHERE
#     eez IS NULL 
#     and mmsi = '''+mmsi+'''
#     group by mmsi, local_day)
# GROUP BY
#   bucket_lat,
#   bucket_lon
#       ''') }

#     query_bigquery(query, out_folder+"s8/"+mmsi+".asc", cellsize)




print "mmsi_S2"
cellsize = .25

for mmsi in mmsi_s2:
    print mmsi , 
    query = {  'query': ('''SELECT
      bucket_lon,
      bucket_lat,
      COUNT(*) count
    FROM (
      SELECT
        integer(FLOOR(FIRST(lat)*4)) AS bucket_lat,
        integer(FLOOR(FIRST(lon)*4)) AS bucket_lon
      FROM
        [PIPA_Policy_Paper.PIPA_fig_S2]
      WHERE mmsi = '''+mmsi +'''
      and local_day >= timestamp("2014-01-01 00:00:00")
      and local_day < timestamp("2014-07-01 00:00:00")
      and lat<.5
      GROUP BY
        mmsi,
        local_day)
    GROUP BY
      bucket_lat,
      bucket_lon''') }

    query_bigquery(query, out_folder+"s2/"+mmsi+".asc", cellsize)



