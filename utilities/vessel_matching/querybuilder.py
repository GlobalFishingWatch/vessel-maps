
def makequery(t1,t2):
    extra = ''
    if t1 == "imo" or t2 == "imo":
	    extra = 'AND imo !=0 '
    t1_normalized = normalize(t1)
    t2_normalized = normalize(t2)

    query = '''SELECT "'''+t1+'''" Attribute1_Type, STRING('''+t1_normalized+''') Attribute1_Value, 
	     "'''+t2+ '''" Attribute2_Type, STRING('''+t2_normalized+''') Attribute2_Value, 
	     first(timestamp) Start_Date, last(timestamp) End_date, count(*) Count, "Type5_24" Source, month(timestamp) month, year(timestamp) year
	     from [Vessel_identity_messages.type5_24_2012_2015]
	     WHERE '''+t1+''' is not null AND '''+t1+''' IS NOT NULL '''+ extra +'''
	     group by Attribute1_Type, Attribute1_Value, Attribute2_Type, Attribute2_Value, month, year'''
    return query

def normalize(t):
    if t == 'shipename':
    	return "REGEXP_REPLACE(shipname, '[^\\w]', '') "
    return t


messages = ["mmsi","imo","shipname","callsign","shiptype_text"]


print "SELECT Attribute1_Type,Attribute1_Value,Attribute2_Type,Attribute2_Value,Start_Date,End_Date,Count,Source FROM"

for i in range(len(messages)):
	for j in range(i+1, len(messages)):
		print "("+ makequery(messages[i],messages[j]) +"),"


