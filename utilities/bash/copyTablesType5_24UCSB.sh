#!/bin/bash

TABLES=$(bq ls --max_results 10000 type5and24messages  | grep TABLE | pyin 'line.strip().split()[0]')

for T in ${TABLES}; do
    echo bq -q cp -f type5and24messages.${T} ucsb-gfw:type5and24messages.${T}
done | parallel -j 16 
