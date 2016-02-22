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
out_folder = "../../data/pipa/"


mmsi_1a = []
mmsi_1b = []
mmsi_2 = []
mmsi_s2 = []

with open('mmsi_list.csv','rU') as f:
    reader = csv.DictReader(f, delimiter=',')
    for row in reader:
        mmsi = row['MMSI']
        if row['Fig 1A Jul-Dec 2014']:
            mmsi_1a.append(mmsi)
        if row['Fig 1B Jan-Jun 2015']:
            mmsi_1b.append(mmsi)
        if row['Fig 2 High Seas PS']:
            mmsi_2.append(mmsi)
        if row['Fig S2 Jan-Jun 2014']:
            mmsi_s2.append(mmsi)



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

    try:
        if len(lats) == 0:
            print "no values for ", mmsi
            return

        #print max(lats), min(lats), max(lons), min(lons)
        global ncols
        ncols = (max(lons)-min(lons))/cellsize + 1
        global nrows 
        nrows = (max(lats)-min(lats))/cellsize + 1
        global xllcorner
        xllcorner = min(lons)
        global yllcorner
        yllcorner = min(lats)
        grid = np.zeros((nrows,ncols))

        #print ncols, nrows, xllcorner, yllcorner

        for v in values:
            r = int(float(v['bucket_lat'])/cellsize-yllcorner/cellsize)
            c = int(float(v['bucket_lon'])/cellsize-xllcorner/cellsize)
            grid[r,c] = int(v['count'])

        write_asc(out_file_name,grid)
        return grid
    except:
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
#         FLOOR(FIRST(lat)*4)/4 AS bucket_lat,
#         FLOOR(FIRST(lon)* 4)/4 AS bucket_lon
#       FROM
#         [PIPA_Policy_Paper.PIPA_FFA_2014]
#       WHERE mmsi = '''+mmsi +'''
#       and local_day >= timestamp("2014-07-01 00:00:00")
#       and local_day < timestamp("2015-01-01 00:00:00")
#       GROUP BY
#         mmsi,
#         local_day)
#     GROUP BY
#       bucket_lat,
#       bucket_lon''') }

#     fc_score = query_bigquery(query, out_folder+"1a/"+mmsi+".asc", cellsize)


print "mmsi_1b"

for mmsi in mmsi_1b:
    print mmsi
    query = {  'query': ('''SELECT
      bucket_lon,
      bucket_lat,
      COUNT(*) count
    FROM (
      SELECT
        FLOOR(FIRST(lat)*4)/4 AS bucket_lat,
        FLOOR(FIRST(lon)* 4)/4 AS bucket_lon
      FROM
        [PIPA_Policy_Paper.PIPA_FFA_2015]
      WHERE mmsi = '''+mmsi +'''
      and local_day >= timestamp("2015-01-01 00:00:00")
      and local_day < timestamp("2015-07-01 00:00:00")
      GROUP BY
        mmsi,
        local_day)
    GROUP BY
      bucket_lat,
      bucket_lon''') }

    fc_score = query_bigquery(query, out_folder+"1b/"+mmsi+".asc", cellsize)



# print "going to mmsi_2"
# cellsize = 1

# for mmsi in mmsi_2:
#     print mmsi, 
#     query = {  'query': ('''SELECT
#   bucket_lon,
#   bucket_lat,
#   COUNT(*)
# FROM (
#   SELECT
#     FLOOR(first(lat)) AS bucket_lat,
#     FLOOR(first (lon)) AS bucket_lon
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

#     fc_score = query_bigquery(query, out_folder+"2/"+mmsi+".asc", cellsize)




# print "mmsi_S2"
# cellsize = .25

# for mmsi in mmsi_s2:
#     print mmsi , 
#     query = {  'query': ('''SELECT
#       bucket_lon,
#       bucket_lat,
#       COUNT(*) count
#     FROM (
#       SELECT
#         FLOOR(FIRST(lat)*4)/4 AS bucket_lat,
#         FLOOR(FIRST(lon)* 4)/4 AS bucket_lon
#       FROM
#         [PIPA_Policy_Paper.PIPA_FFA_2014]
#       WHERE mmsi = '''+mmsi +'''
#       and local_day >= timestamp("2014-01-01 00:00:00")
#       and local_day < timestamp("2014-07-01 00:00:00")
#       GROUP BY
#         mmsi,
#         local_day)
#     GROUP BY
#       bucket_lat,
#       bucket_lon''') }

#     fc_score = query_bigquery(query, out_folder+"s2/"+mmsi+".asc", cellsize)



