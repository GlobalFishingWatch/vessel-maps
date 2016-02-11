import csv

sourcedir = '/Users/David/Desktop/Jobs/GlobalFishingWatch/ResearchArticles/SharkDougBarbara/'
filename = 'clav_lp.csv'

v = {}
mmsis = []

with open(sourcedir + filename,'rU') as f:
    reader = csv.DictReader(f, delimiter=',')
    for row in reader:
        mmsi = row['mmsi']
        v[mmsi]= {'vesseltype':row['shiptype'], 'list_source': 'CLAV'}
        mmsis.append(mmsi)
        if  '432271000' in mmsi:
        	print "what?"


filename = 'ffa_lp.csv'

with open(sourcedir + filename,'rU') as f:
    reader = csv.DictReader(f, delimiter=',')
    for row in reader:
        mmsi = row['mmsi']
        if mmsi not in mmsis:
            v[mmsi]= {'vesseltype':row['vesseltype'], 'list_source': 'FFA'}
            mmsis.append(mmsi)
        else:
            v[mmsi]['list_source'] = "FFA and CLAV"
            mmsis.append(mmsi)

for k in v:
    print k+"\t"+v[k]['vesseltype']+"\t"+v[k]['list_source']
