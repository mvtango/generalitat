# coding: utf-8
import csvstore
import list2tree
import os
import simplejson

here=os.path.split(__file__)[0]

datadir=os.path.join(here,"../data")


entitats=csvstore.csvstore(os.path.join(datadir,"unitatssac-scraped.csv"))

rootnode=list2tree.list2tree(filter(lambda a: a["nom"], entitats.data))

pres=filter(lambda a: a["name"].find("Presidència")>-1,rootnode["children"])[0]

simplejson.dump(pres,open(os.path.join(datadir,"presidencia.json"),"w"));
