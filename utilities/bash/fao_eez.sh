#!/bin/bash

TABLES=$(bq ls --max_results 10000 pipeline_740__classify  | grep TABLE | pyin 'line.strip().split()[0]')

for T in ${TABLES}; do
   echo bq query --replace=TRUE --destination_table=scratch_david.FAO_Regions2b_${T} --allow_large_results '"SELECT REGEXP_REPLACE(REGEXP_EXTRACT(regions,r'"'(EEZ:[[:alpha:]]*)'"') , '"'EEZ:'"', '"''"') as EEZ, * FROM  [scratch_david.FAO_Regions2_'$T']"'

done  | parallel -j 16
