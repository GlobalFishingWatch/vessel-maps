#!/bin/bash

TABLES=$(bq ls --max_results 10000 pipeline_740__classify  | grep TABLE | pyin 'line.strip().split()[0]')

for T in ${TABLES}; do
    echo bq -q cp -f scratch_david.FAO_Regions2b_${T} ucsb-gfw:fao_v2.${T}
done | parallel -j 16 

for T in ${TABLES}; do
    echo bq -q cp -f scratch_david.FAO_Regions2b_${T} gfw-partners:fao_v2.${T}
done | parallel -j 16 

for T in ${TABLES}; do
    echo bq -q cp -f scratch_david.FAO_Regions2b_${T} frz-watch-program:fao_v2.${T}
done | parallel -j 16 

