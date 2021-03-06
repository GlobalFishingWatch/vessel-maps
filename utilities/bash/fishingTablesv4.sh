#!/bin/bash

TABLES=$(bq ls --max_results 10000 pipeline_classify_logistic_661b  | grep TABLE | pyin 'line.strip().split()[0]')

# NEXTDAY= date -j -v +1d -f "%Y%m%d" ${T} +%Y-%m-%d
# LASTDAY= date -j -v -1d -f "%Y%m%d" ${T} +%Y-%m-%d

for T in ${TABLES}; do
   # if [ ${T:0:4} -eq 2016 ] ;      
   # then 
   echo  bq query --replace=TRUE --destination_table=pipeline_classify_logistic_715_fishing.${T} --allow_large_results '"SELECT * FROM (SELECT IF(prev_lat is null or prev_lon is null, 0, ACOS(COS(RADIANS(90-lat)) *COS(RADIANS(90-prev_lat)) +SIN(RADIANS(90-lat)) *SIN(RADIANS(90-prev_lat)) * COS(RADIANS(lon-prev_lon)))*6371000) prev_gapmeters,  IF(next_lat is null or next_lon is null, 0,ACOS(COS(RADIANS(90-lat)) *COS(RADIANS(90-next_lat)) +SIN(RADIANS(90-lat)) *SIN(RADIANS(90-next_lat)) * COS(RADIANS(lon-next_lon)))*6371000) next_gapmeters,  IF(last_timestamp IS NOT NULL, ((timestamp-last_timestamp)/2)/3600000000, 12) + IF(next_timestamp IS NOT NULL, ((next_timestamp - timestamp)/2)/3600000000, 12) hours, *  FROM (    SELECT      LAG(timestamp, 1) OVER (PARTITION BY seg_id ORDER BY timestamp) last_timestamp,      LEAD(timestamp,1) OVER (PARTITION BY seg_id ORDER BY timestamp) next_timestamp,      LAG(lat, 1) OVER (PARTITION BY seg_id ORDER BY timestamp) prev_lat,      LEAD(lat,1) OVER (PARTITION BY seg_id ORDER BY timestamp) next_lat,      LAG(lon, 1) OVER (PARTITION BY seg_id ORDER BY timestamp) prev_lon,      LEAD(lon,1) OVER (PARTITION BY seg_id ORDER BY timestamp) next_lon,      *,      INTEGER(FLOOR(lat/5)*5) lat_bin_five,      INTEGER(FLOOR(lon/5)*5) lon_bin_five,      (FLOOR(lat*2))/2 lat_bin_half,      (FLOOR(lon*2))/2 lon_bin_half,      HOUR(timestamp) hour,      INTEGER(FLOOR(MINUTE(timestamp)/2)*2) minute_bin    FROM      (select * from TABLE_DATE_RANGE([pipeline_classify_logistic_715.], TIMESTAMP('"'$(date -j -v -1d -f "%Y%m%d" ${T} +%Y-%m-%d)'"'), TIMESTAMP('"'$(date -j -v +1d -f "%Y%m%d" ${T} +%Y-%m-%d)'"')))    WHERE      lat IS NOT NULL      AND lon IS NOT NULL      AND mmsi IN (      SELECT        mmsi      FROM        [scratch_david_mmsi_lists.known_likely_fishing_mmsis_"'${T:0:4}'"])))where date(timestamp) = '"'${T:0:4}-${T:4:2}-${T:6:2}'"'"'
   #; fi
done | parallel -j 16
