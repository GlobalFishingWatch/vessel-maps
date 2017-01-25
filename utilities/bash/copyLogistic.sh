#!/bin/bash

TABLES=$(bq ls --max_results 10000 pipeline_classify_logistic_661b | grep TABLE | pyin 'line.strip().split()[0]')

for T in ${TABLES}; do
    echo bq -q cp -f pipeline_classify_logistic_661b.${T} frz-watch-program:pipeline_classify_logistic_661b.${T}
done | parallel -j 16 

for T in ${TABLES}; do
    echo bq -q cp -f pipeline_classify_logistic_661b.${T} gfw-partners:pipeline_classify_logistic_661b.${T}
done | parallel -j 16 

for T in ${TABLES}; do
    echo bq -q cp -f pipeline_classify_logistic_661b.${T} ucsb-gfw:pipeline_classify_logistic_661b.${T}
done | parallel -j 16 

