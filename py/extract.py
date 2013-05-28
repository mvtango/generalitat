from lxml import etree
import simplejson
import pprint
import re
from processor import GenericProcessor
process=GenericProcessor()


files={ "in" : "../data/xml/unitatssac.xml",
        "out" : "../data/unitatssac.json" }


parse={"row" : "//item",
       "columns" : {
				"id" : ".//id/text()",
				"nom" : ".//nom/text()",
				"resp" : ".//resp/text()",
				"iddep" : ".//iddep/text()",
				"dep" : ".//iddep/text()",
				"centres" : ".//centres"
      }
}


def stringstring(a) :
	try :
		return etree.tostring(a)
	except TypeError :
		return a


parser=etree.HTMLParser()
tree=etree.parse(open(files["in"]),parser)

data=[]
for row in tree.xpath(parse["row"]) :
	rd={}
	for (k,x) in parse["columns"].items() :
		a=row.xpath(x)
		if a:
			rd[k]="".join([stringstring(ss) for ss in a])
	
	data.append(process.process(rd))
	

# pprint.pprint(map(lambda a:  { "a" : a.get("reaction","-"), "b" : a.get("color",""), "c" : a.get("amendment","") },data));
pprint.pprint(data)
		
		
