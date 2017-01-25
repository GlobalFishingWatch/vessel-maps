
import subprocess

proc = subprocess.Popen(["bq ls --max_results 10000 scratch_david"], stdout=subprocess.PIPE, shell=True)
(out, err) = proc.communicate()
toprocess = out
tp = toprocess.split("\n")
tp = [t.replace(" ","").replace("TABLE","") for t in tp]


def copyFAO(destinationTable):

	big_c = "("
	for t in tp:
		if "FAO_Regions_" in t and len(t) == len('FAO_Regions_20120101'):
			d = t[-8:]
			big_c += "echo 'bq -q cp -f scratch_david.FAO_Regions_{0} {1}:fao.{0}';".format(d,destinationTable)
			# big_c += "echo 'bq -q cp -f scratch_david.FAO_Regions_{0} g:fao.{0}';".format(d)
			# big_c += "echo 'bq -q cp -f scratch_david.FAO_Regions_{0} frz-watch-program:fao.{0}';".format(d)

	big_c = big_c[:-1]+") | parallel -j 16"
	p = subprocess.Popen(big_c, shell=True)
	print p.communicate()


copyFAO('ucsb-gfw')
copyFAO('gfw-partners')
copyFAO('frz-watch-program')