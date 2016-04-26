#!/bin/bash

TABLES=$(bq ls --max_results 10000 pipeline_classify  | grep TABLE | pyin 'line.strip().split()[0]')

for T in ${TABLES}; do    
  echo bq query --destination_table=type5and24messages.${T} --allow_large_results '"SELECT * from [pipeline_classify.'${T}]' where type = 24 or type = 5"'
done | parallel -j 16 
