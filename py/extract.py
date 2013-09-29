from lxml import etree
import simplejson
import csvstore
import sys
import pprint
import re
from processor import GenericProcessor
from generalitat import depende_de
import logging

logging.basicConfig(file=sys.stdout,level=logging.DEBUG)

logger=logging.getLogger(__name__)



process=GenericProcessor()


files={ "in" : len(sys.argv)>1 and sys.argv[1] or "../data/xml/unitatssac.xml",
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


depende={}
s=csvstore.csvstore("scraped.csv")
for r in s.data :
	depende[r["id"]]=r["iddep-scraped"]


def dependencia(a) :
	if a in depende :
		return depende[a]
	return depende_de(a)



def extract(filename) : 
	from_xml={}
	seen={}
	parser=etree.XMLParser()
	tree=etree.parse(open(filename),parser)
	data=[]
	for row in tree.xpath(parse["row"]) :
		rd={}
		for (k,x) in parse["columns"].items() :
			a=row.xpath(x)
			if a:
				rd[k]="".join([stringstring(ss) for ss in a])
		#logger.info("processed %(id)s %(nom)s" % rd)	
		from_xml[rd["id"]]=True
		rd["iddep-scraped"]=depende_de(rd["id"])
		seen[rd["iddep-scraped"]]=True
		data.append(process.process(rd))
	for ids in seen.keys() :
		if ids and ids not in from_xml :
			d=ids.split("-",2)
			if len(d)>1 :
				data.append({'id' : ids, 'nom': ids.split("-",2)[2], 'iddep' : depende_de(ids), 'iddep-scraped' : depende_de(ids), 'resp' : '' })
			else :
				print "not in xml, not in deps: %s"  % ids
	return data

if __name__=="__main__"  :
	data=extract(files["in"])
	pprint.pprint(data)


# pprint.pprint(map(lambda a:  { "a" : a.get("reaction","-"), "b" : a.get("color",""), "c" : a.get("amendment","") },data));
		
		
