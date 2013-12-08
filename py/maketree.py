# coding: utf-8
import csvstore
import list2tree
import os
import simplejson
import sys
import argparse
from extract import extract
import datetime

parser = argparse.ArgumentParser(description="json tree generator", conflict_handler='resolve')
parser.add_argument('infile',nargs="*",default="unitatssac-scraped-20130525.csv")
args = vars(parser.parse_args())



here=os.path.split(__file__)[0]
datadir=os.path.join(here,"../data")


jobs= [ { 'find'  : u'Departament de la Presidència',
          'files' : [ #  os.path.join(datadir,"presidencia.json"),
#					  os.path.join(here,"../opengov.cat/generalitat/0.3/tree.json"),
					  os.path.join(here,"../data/web/presidencia.json"),
#					  os.path.join(here,"../opengov.cat/generalitat/0.3/presidencia.json")
 ]
		},
		{ 'find'  : u'Agricultura',
          'files' : [ #os.path.join(datadir,"agricultura.json"),
					  os.path.join(here,"../data/web/agricultura.json"),
#					  os.path.join(here,"../opengov.cat/generalitat/0.3/agricultura.json")
 ]
		},
		{ 'find'  : u'Salut',
          'files' : [ #os.path.join(datadir,"salut.json"),
					  os.path.join(here,"../data/web/salut.json"),
#					  os.path.join(here,"../opengov.cat/generalitat/0.3/salut.json") 
]
		},
		{ 'find'  : u'Empresa',
          'files' : [ #os.path.join(datadir,"empresa.json"),
					  os.path.join(here,"../data/web/empresa.json"),
#					  os.path.join(here,"../opengov.cat/generalitat/0.3/empresa.json") 
		]
		},
		{ 'find'  : u'Benestar',
          'files' : [ #os.path.join(datadir,"benestar.json"),
					  os.path.join(here,"../data/web/benestar.json"),
#					  os.path.join(here,"../opengov.cat/generalitat/0.3/benestar.json") 
]
		},
		{ 'find'  : u'Territori',
          'files' : [ #os.path.join(datadir,"territori.json"),
					  os.path.join(here,"../data/web/territori.json"),
#					  os.path.join(here,"../opengov.cat/generalitat/0.3/territori.json") 
]
		},
		{ 'find'  : u'Ensenyament',
          'files' : [ #os.path.join(datadir,"ensenyament.json"),
					  os.path.join(here,"../data/web/ensenyament.json"),
#					  os.path.join(here,"../opengov.cat/generalitat/0.3/ensenyament.json") 
		]
		},
		{ 'find'  : 'Generalitat',
          'files' : [ #os.path.join(datadir,"generalitat.json"),
					  os.path.join(here,"../data/web/generaliat.json"),
#					  os.path.join(here,"../opengov.cat/generalitat/0.3/generalitat.json") 
]
		},
		{ 'find'  : 'CatSalut',
          'files' : [ 
					  os.path.join(here,"../data/web/catsalut.json"),
		 	]
		},
	    { 'find'  : 'ICS',
          'files' : [ 
					  os.path.join(here,"../data/web/ics.json"),
		 	]
		}




	  ]

childattr="_children"

for fn in args["infile"] :
	entitats=extract(fn)
	rootnode=list2tree.list2tree(entitats,children=childattr)
	rootnode["name"]="Generalitat"
	nameindex=[rootnode]
	now=datetime.datetime.now().strftime("%d/%m/%Y")
	for i in xrange(0,4) :
		newn=[]
		for n in nameindex :
			for c in n.get(childattr,[]) :
				newn.append(c)
		nameindex.extend(newn)
	print "names: %s" % repr([a["name"] for a in nameindex])
	
	for job in jobs:
		parts=filter(lambda a: a["name"].find(job["find"])>-1,nameindex)
		if len(parts)>0 :
			part=parts[0]
			part["data"]["updated"]=now
		else :
			print "Not found: %s" % repr(job["find"])
			continue
		for n in job["files"] :
			print "written %s to %s" % (repr(job["find"]),n)
			simplejson.dump(part,open(n,"w"));

