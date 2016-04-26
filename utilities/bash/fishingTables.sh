#!/bin/bash

TABLES=$(bq ls --max_results 10000 pipeline_classify  | grep TABLE | pyin 'line.strip().split()[0]')

for T in ${TABLES}; do    
  echo bq query --destination_table=pipeline_classify_fishing.${T} --allow_large_results '"SELECT * from [pipeline_classify.'${T}]' where mmsi in (SELECT mmsi FROM [scratch_bjorn.2015_combined_fishing])"'
done | parallel -j 16 
