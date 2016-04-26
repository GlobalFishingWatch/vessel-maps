#!/bin/bash

TABLES=$(bq ls --max_results 10000 pipeline_classify  | grep TABLE | pyin 'line.strip().split()[0]')

for T in ${TABLES}; do
    echo bq -q cp -f pipeline_classify.${T} frz-watch-program:pipeline_classify.${T}
done | parallel -j 16 
