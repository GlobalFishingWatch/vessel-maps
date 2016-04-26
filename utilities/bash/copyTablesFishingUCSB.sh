#!/bin/bash

TABLES=$(bq ls --max_results 10000 pipeline_classify_fishing  | grep TABLE | pyin 'line.strip().split()[0]')

for T in ${TABLES}; do
    echo bq -q cp -f pipeline_classify_fishing.${T} ucsb-gfw:pipeline_classify_fishing.${T}
done | parallel -j 16 
