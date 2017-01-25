#!/bin/bash

TABLES=$(bq ls --max_results 10000 pipeline_classify_logistic_661b | grep TABLE | pyin 'line.strip().split()[0]')


for T in ${TABLES}; do
    echo bq -q cp -f  pipeline_classify_logistic_715.${T} frz-watch-program:pipeline_classify.${T}
    echo bq -q cp -f  pipeline_classify_logistic_715_fishing.${T} frz-watch-program:pipeline_classify_fishing.${T}
done | parallel -j 16 

for T in ${TABLES}; do
    echo bq -q cp -f pipeline_classify_logistic_715.${T} gfw-partners:pipeline_classify.${T}
    echo bq -q cp -f pipeline_classify_logistic_715_fishing.${T} gfw-partners:pipeline_classify_fishing.${T}
done | parallel -j 16 

for T in ${TABLES}; do
    echo bq -q cp -f  pipeline_classify_logistic_715.${T} ucsb-gfw:pipeline_classify.${T}
    echo bq -q cp -f  pipeline_classify_logistic_715_fishing.${T} ucsb-gfw:pipeline_classify_fishing.${T}
done | parallel -j 16 

