# coding: utf-8
import csvstore
import list2tree
import os
import simplejson
import sys
import argparse


parser = argparse.ArgumentParser(description="json tree generator", conflict_handler='resolve')
parser.add_argument('infile',nargs="*",default="unitatssac-scraped-20130525.csv")
args = vars(parser.parse_args())



here=os.path.split(__file__)[0]
datadir=os.path.join(here,"../data")


jobs= [ { 'find'  : 'Presidència',
          'files' : [ os.path.join(datadir,"presidencia.json"),
					  os.path.join(here,"../opengov.cat/generalitat/0.3/tree.json"),
					  os.path.join(here,"../opengov.cat/generalitat/0.3/presidencia.json") ]
		},
		{ 'find'  : 'Agricultura',
          'files' : [ os.path.join(datadir,"agricultura.json"),
					  os.path.join(here,"../opengov.cat/generalitat/0.3/agricultura.json") ]
		},
		{ 'find'  : 'Salut',
          'files' : [ os.path.join(datadir,"salut.json"),
					  os.path.join(here,"../opengov.cat/generalitat/0.3/salut.json") ]
		},
		{ 'find'  : 'Empresa',
          'files' : [ os.path.join(datadir,"empresa.json"),
					  os.path.join(here,"../opengov.cat/generalitat/0.3/empresa.json") ]
		},
		{ 'find'  : 'Benestar',
          'files' : [ os.path.join(datadir,"benestar.json"),
					  os.path.join(here,"../opengov.cat/generalitat/0.3/benestar.json") ]
		},
		{ 'find'  : 'Territori',
          'files' : [ os.path.join(datadir,"territori.json"),
					  os.path.join(here,"../opengov.cat/generalitat/0.3/territori.json") ]
		}


	  ]

for fn in args["infile"] :
	entitats=csvstore.csvstore(os.path.join(datadir,fn))
	rootnode=list2tree.list2tree(filter(lambda a: a["nom"], entitats.data),children="_children")
	for job in jobs:
		part=filter(lambda a: a["name"].find(job["find"])>-1,rootnode["_children"])[0]
		for n in job["files"] :
			print "written %s to %s" % (job["find"],n)
			simplejson.dump(part,open(n,"w"));

