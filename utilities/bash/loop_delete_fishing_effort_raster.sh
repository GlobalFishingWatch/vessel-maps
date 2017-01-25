#!/bin/bash

TABLES=$(bq ls --max_results 10000 pipeline_classify_logistic_661b  | grep TABLE | pyin 'line.strip().split()[0]')

for T in ${TABLES}; do
    echo bq rm -f scratch_global_fishing_raster.fishing_effort_${T}
done | parallel -j 16 
