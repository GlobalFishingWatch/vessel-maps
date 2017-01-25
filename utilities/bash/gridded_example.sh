#!/bin/bash

TABLES=$(bq ls --max_results 10000 pipeline_740__classify  | grep TABLE | pyin 'line.strip().split()[0]')

for T in ${TABLES}; do
   echo bq query --replace=TRUE --destination_table=scratch_global_fishing_raster.quarterdegree_${T} --allow_large_results '"SELECT FLOOR(a.lat*4) lat_bin, FLOOR(a.lon*4) lon_bin, date(a.timestamp) date, case when b.label = '"'Trawlers'"' then '"'Trawlers'"' when b.label = '"'Purse_seines'"' then '"'Purse Seines'"' when b.label = '"'Drifting_longlines'"' then '"'Drifting longlines'"' else '"'Other or Unidentified Fishing Gear'"' end label, b.iso3 iso3, b.country_name country_name, SUM(IF(a.measure_new_score > .5, a.hours,0)) fishing_hours FROM ( SELECT mmsi, timestamp, lat, lon, hours, measure_new_score FROM [world-fishing-827:scratch_david.FAO_Regions2b_'$T']) a LEFT JOIN ( SELECT mmsi, IF(training_label IS NOT NULL, training_label, nn_max_label) label, iso3, country_name FROM [scratch_david_mmsi_lists.'${T:0:4}'_fishing_vessel_info]) b ON a.mmsi = b.mmsi GROUP BY lat_bin, lon_bin, label, country_name, iso3, date having fishing_hours > 0"'
done  | parallel -j 8
