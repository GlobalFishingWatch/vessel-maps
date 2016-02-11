import csv
import numpy as np

sourcedir = ''
filename = 'fishing_effort_v1.csv'
cellsize = .25

values = []
lats = []
lons = []

with open(sourcedir + filename,'rU') as f:
    reader = csv.DictReader(f, delimiter=',')
    for row in reader:
    	values.append(row)
    	lats.append(float(row['bucket_lat']))
    	lons.append(float(row['bucket_lon']))

print max(lats), min(lats), max(lons), min(lons)
print type(max(lats))#, min(lats), max(lons), min(lons)

ncols = (max(lons)-min(lons))/cellsize + 1
nrows = (max(lats)-min(lats))/cellsize + 1
xllcorner = min(lons)
yllcorner = min(lats)
grid = np.zeros((nrows,ncols))

for v in values:
	r = int(float(v['bucket_lat'])*4-yllcorner*4)
	c = int(float(v['bucket_lon'])*4-xllcorner*4)
	grid[r,c] = int(v['count'])

f = open("fishing_grid.asc", "w")

f.write("ncols "+str(ncols)+"\n")
f.write("nrows "+str(nrows)+"\n")
f.write("xllcorner "+str(xllcorner)+"\n")
f.write("yllcorner "+str(yllcorner)+"\n")
f.write("cellsize "+str(cellsize)+"\n")
f.write("no_data_value -9999\n")
for r in np.flipud(grid):
	s = ""
	for c in r:
		s+=str(int(c))+" "
	s = s[:-1]+"\n"
	f.write(s)
f.close()


