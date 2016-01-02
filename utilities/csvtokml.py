#!/usr/bin/env python

import logging
from optparse import OptionParser
import re
from string import Template
import csv
from dateutil.parser import parse as parse_date
from datetime import datetime, timedelta, date
import sys
import bisect
   
   
MIN_INTERVAL = 60   # minimum interval between placemarks in seconds


time_gap_styles = [
    {
        'range': (0, (3600 * 12)),
        'style': 'trackStyle1'
    },
    {
        'range': ((3600 * 12), (3600 * 48)),
        'style': 'trackStyle2'
    },
    {
        'range': ((3600 * 48), sys.maxint),
        'style': 'trackStyle3'
    },
]



document_kml_template = Template(
"""<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2" xmlns:gx="http://www.google.com/kml/ext/2.2" xmlns:kml="http://www.opengis.net/kml/2.2" xmlns:atom="http://www.w3.org/2005/Atom">
<Document>
	<name>$name</name>
	<StyleMap id="vesselStyleMap">
		<Pair>
			<key>normal</key>
			<styleUrl>#normVesselStyle</styleUrl>
		</Pair>
		<Pair>
			<key>highlight</key>
			<styleUrl>#hlightVesselStyle</styleUrl>
		</Pair>
	</StyleMap>
	<Style id="hlightVesselStyle">
		<IconStyle>
            <scale>1.2</scale>  
    		<color>ff006666</color>
			<Icon>
				<href>http://alerts.skytruth.org/markers/vessel_direction.png</href>
			</Icon>
            <hotSpot x="16" y="3" xunits="pixels" yunits="pixels"/>
		</IconStyle>
        <LabelStyle><color>ff999999</color><scale>0.8</scale></LabelStyle>
	</Style>
	<Style id="normVesselStyle">
		<IconStyle>
		  <color>ff009999</color>
		  <Icon><href>http://alerts.skytruth.org/markers/vessel_direction.png</href></Icon>
          <hotSpot x="16" y="3" xunits="pixels" yunits="pixels"/>
		</IconStyle>
        <LabelStyle><scale>0</scale></LabelStyle>
	</Style>
	<StyleMap id="trackStyle1">
		<Pair>
			<key>normal</key>
			<styleUrl>#normTrackStyle1</styleUrl>
		</Pair>
		<Pair>
			<key>highlight</key>
			<styleUrl>#hlightTrackStyle1</styleUrl>
		</Pair>
	</StyleMap>
	<Style id="hlightTrackStyle1">
		<LineStyle>
			<color>ff999999</color>
			<width>2</width>
		</LineStyle>
	</Style>
	<Style id="normTrackStyle1">
		<LineStyle>
			<color>ff999999</color>
			<width>1.2</width>
		</LineStyle>
	</Style>	
	<StyleMap id="trackStyle2">
		<Pair>
			<key>normal</key>
			<styleUrl>#normTrackStyle2</styleUrl>
		</Pair>
		<Pair>
			<key>highlight</key>
			<styleUrl>#hlightTrackStyle2</styleUrl>
		</Pair>
	</StyleMap>
	<Style id="hlightTrackStyle2">
		<LineStyle>
			<color>ff00ffff</color>
			<width>6</width>
		</LineStyle>
	</Style>
	<Style id="normTrackStyle2">
		<LineStyle>
			<color>ff00ffff</color>
			<width>4</width>
		</LineStyle>
	</Style>	
	<StyleMap id="trackStyle3">
		<Pair>
			<key>normal</key>
			<styleUrl>#normTrackStyle3</styleUrl>
		</Pair>
		<Pair>
			<key>highlight</key>
			<styleUrl>#hlightTrackStyle3</styleUrl>
		</Pair>
	</StyleMap>
	<Style id="hlightTrackStyle3">
		<LineStyle>
			<color>ff0000ff</color>
			<width>6</width>
		</LineStyle>
	</Style>
	<Style id="normTrackStyle3">
		<LineStyle>
			<color>ff0000ff</color>
			<width>4</width>
		</LineStyle>
	</Style>		
    $vessels_kml
</Document>
</kml>
"""	)


vessel_kml_template = Template(
"""<Folder>
    <name>$name</name>
<Folder>
    <name>Vessel Tracks</name>
$track_kml
</Folder>

<Folder>
    <name>AIS Points</name>
$placemarks_kml
</Folder>

</Folder>
"""	 )


track_template = Template (
"""	<Placemark>
	<name>$name</name>
	<styleUrl>#$style</styleUrl>
	<LineString>
		<tessellate>1</tessellate>
		<coordinates>
		    $coords
		</coordinates>
	</LineString>
	<TimeSpan><begin>$time_begin</begin><end>$time_end</end></TimeSpan>
 	
</Placemark>""")

placemark_folder_template = Template(
"""<Folder>
    <name>$name</name>
$placemarks_kml
</Folder>
"""	 )


placemark_template = Template(
"""<Placemark>
    <name>$datetime</name>
    <description>
<table width="300">
    <tr><th align="right">Vessel Name</th><td>$name</td></tr>
    <tr><th align="right">Vessel Type</th><td>$type</td></tr>
    <tr><th align="right">MMSI</th><td>$mmsi</td></tr>
    <tr><th align="right">Length</th><td>$length meters</td></tr>
    <tr><th align="right">Datetime</th><td>$datetime</td></tr>
    <tr><th align="right">True Heading</th><td>$true_heading</td></tr>
    <tr><th align="right">Speed Over Ground</th><td>$sog</td></tr>
    <tr><th align="right">Course Over Ground</th><td>$cog</td></tr>
    <tr><th align="right">Latitude</th><td>$latitude</td></tr>
    <tr><th align="right">Longitude</th><td>$longitude</td></tr>
    <tr><th align="right">Vessel Info</th><td><a href="$marinetraffic_url">marinetraffic.com</a> <a href="$itu_url">ITU</a></td></tr>
</table>    
    </description>    
	<styleUrl>#vesselStyleMap</styleUrl>
    <TimeStamp><when>$timestamp</when></TimeStamp>
    <Point>
        <coordinates>$longitude,$latitude,0</coordinates>
    </Point>
    <Style><IconStyle><heading>$cog</heading><color>$icon_color</color></IconStyle></Style>
</Placemark>""")



class Vessel ():
    def __init__(self, params):
        self.mmsi = params['mmsi']  # This can't be null
        self.name = params.get('name')
        self.vessel_type = params.get('type'),
        self.length = params.get('length'),
        self.url = params.get('url')
        self.marinetraffic_url = params.get('marinetraffic_url')
        self.itu_url = params.get('itu_url')
        self.ais = []
        self.timestamps = []
            
    def add_ais (self, ais):
        idx = 0
        dt = ais['datetime']
        if self.ais:
            # ignore anything that is less than MIN_INTERVAL seconds away from a record we already have in the list
            idx = bisect.bisect (self.timestamps,dt)      
            if idx > 0 and abs((dt - self.timestamps[idx-1]).total_seconds()) < MIN_INTERVAL:
                return
            if idx < len(self.timestamps) and abs((dt - self.timestamps[idx]).total_seconds()) < MIN_INTERVAL:
                return
        self.timestamps.insert (idx, dt)
        self.ais.insert (idx, ais)
        
    

        

def convert (infile_name, outfile_name):
    vessels = read_csv (infile_name)
    
    print "Found %s vessels" % len(vessels)
    
    params = {'name': outfile_name}
    params['vessels_kml'] = '\n'.join([get_vessel_kml(vessel, mmsi) for mmsi,vessel in vessels.items()])
    document_kml = document_kml_template.substitute (params)
    with open (outfile_name, 'wb') as kml_file:
        kml_file.write (document_kml)    
    
def get_vessel_kml (vessel, mmsi):
    params = {'name': vessel.name}
#    params['placemarks_kml'] = '\n'.join([get_placemark_kml(ais) for ais  in vessel.ais])
    params['placemarks_kml'] = get_placemark_folders_kml(vessel)
    params['track_kml'] = get_track_kml (vessel)
    return vessel_kml_template.substitute (params)
    
def get_placemark_folders_kml (vessel):
    ais_days = {}
    for ais in vessel.ais:
        d = ais['datetime'].date()
        if not ais_days.get(d):
            ais_days[d] = []
        ais_days[d].append (ais)
    return '\n'.join([get_placemark_folder_kml(dt.strftime('%Y-%m-%d'), ais_days[dt]) for dt in sorted(ais_days.keys())])
                
def get_placemark_folder_kml (name, records):
    params = {'name': name}
    params['placemarks_kml'] = '\n'.join([get_placemark_kml(ais) for ais  in records])
    return placemark_folder_template.substitute (params)

def get_placemark_kml (record):
    params = record
    params['timestamp'] = record['datetime'].strftime ('%Y-%m-%dT%H:%M:%SZ') 
    try:
        c = min(float(record['sog']), 15) * 17
    except:
        c = 0    
        
    params['icon_color'] = 'ff00%02x%02x' % (c, 255-c)
    return  placemark_template.safe_substitute (params)


def get_time_gap_style (dt, last_dt):
    td = (dt - last_dt).total_seconds()
    for s in time_gap_styles:
        if td >= s['range'][0] and td < s['range'][1]:
            return s

def get_track_segment_kml (records, style):
    params = {'name': 'Vessel Track'}
    params['coords'] = ' '.join(['%(longitude)s,%(latitude)s,0'%r for r in records])
    params['time_begin'] = records[0]['datetime'].strftime ('%Y-%m-%dT%H:%M:%SZ')
    params['time_end'] = records[-1]['datetime'].strftime ('%Y-%m-%dT%H:%M:%SZ')
    params['style'] = style['style']
    return track_template.substitute(params)
    
def get_track_kml (vessel):
    kml = []
    records = []
    last_dt = vessel.timestamps[0]
    last_style = get_time_gap_style (last_dt, last_dt)
        
    for ais in vessel.ais:
        dt = ais['datetime']
        style = get_time_gap_style (dt, last_dt)
        if style != last_style and records:
            kml.append (get_track_segment_kml(records, last_style))
            records = [records[-1]]
        records.append (ais)
        last_style = style
        last_dt = dt
    
    if records:
        kml.append (get_track_segment_kml(records, last_style))
    
    return '\n'.join (kml)
    
# load csv file into a dict keyed by MMSI, and then by timestamp
def read_csv (infile_name):    
    vessels = {}
    
    with open(infile_name, 'rb') as csvfile:  
#        dialect = csv.Sniffer().sniff(csvfile.read(1024), delimiters=',') 
#        csvfile.seek(0)   
#        reader = csv.DictReader(csvfile, dialect=dialect)
        reader = csv.DictReader(csvfile)
        last_dt = datetime (2000,1,1)
        for row in reader:
            row = {k.lower():v  for k,v in row.iteritems()}
            dt = row.get('datetime')
            if dt is None:
                dt = row.get('timestamp')
            mmsi = row.get('mmsi')
            if not row.get('name'):
                row['name'] = mmsi
            row['marinetraffic_url'] = 'http://www.marinetraffic.com/ais/shipdetails.aspx?MMSI=%s'% mmsi
            row['itu_url'] = 'http://www.itu.int/cgi-bin/htsh/mars/ship_search.sh?sh_mmsi=%s' % mmsi
            if mmsi and dt:
                if not vessels.get(mmsi):
                    vessels[mmsi] = Vessel (row)
                try:
                    dt = parse_date(dt, fuzzy=1)
                except ValueError:
                    dt = datetime.fromtimestamp(int(dt))
                    
                row['datetime'] = dt
                
                vessels[mmsi].add_ais(row)
                    
    return vessels
        
     



def main ():
    desc = ""
    
    usage = """%prog [options] INFILE OUTFILE

  INFILE 
    filename containing AIS Data in CSV format
  OUTFILE
    output filename to get kml output
    
"""
    parser = OptionParser(description=desc, usage=usage)

    parser.set_defaults(loglevel=logging.INFO)
    parser.add_option("-q", "--quiet",
                          action="store_const", dest="loglevel", const=logging.ERROR, 
                          help="Only output error messages")
    parser.add_option("-v", "--verbose",
                          action="store_const", dest="loglevel", const=logging.DEBUG, 
                          help="Output debugging information")

    (options, args) = parser.parse_args()
    
    if len(args) < 2:
        parser.error("Not enough arguments.")
    elif len(args) > 2:
        parser.error("Too many arguments.")
        

    logging.basicConfig(format='%(levelname)s: %(message)s', level=options.loglevel)

    infile_name = args[0]
    outfile_name = args[1]
    
    print '%s => %s' % (infile_name, outfile_name)
    
    convert (infile_name, outfile_name)
    

if __name__ == "__main__":
    main ()
