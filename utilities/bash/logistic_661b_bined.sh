#!/bin/bash

TABLES=$(bq ls --max_results 10000 pipeline_classify_logistic_661b  | grep TABLE | pyin 'line.strip().split()[0]')

for T in ${TABLES}; do       
   echo  bq query --destination_table=pipeline_classify_logistic_661b_bined.${T} --allow_large_results '"SELECT  integer(floor(lat/5)*5) lat_bin_five,  integer(floor(lon/5)*5) lon_bin_five,    (floor(lat*2))/2 lat_bin_half,  (floor(lon*2))/2 lon_bin_half,  hour(timestamp) hour,  integer(floor(minute(timestamp)/2)*2) minute_bin,  LAG(timestamp, 1) OVER (PARTITION BY seg_id ORDER BY timestamp) last_timestamp,  LEAD(timestamp,1) OVER (PARTITION BY seg_id ORDER BY timestamp) next_timestamp,  *FROM  [pipeline_classify_logistic_661b.'${T}']"' 
done | parallel -j 16
