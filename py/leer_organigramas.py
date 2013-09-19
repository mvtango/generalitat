# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <codecell>

from scrapelib import TreeScraper
import lxml,dumptruck,sqlite3
store=dumptruck.DumpTruck("../data/organigrama.db")
from collections import defaultdict
import os

for t in ('entitats','canvis') :
    store.create_table({'id' : '0' },t,create_only=True)

def leer_organigrama(d, date=None) :
	unchanged=0
	changed=0
	entitats=[]
	canvis=[]
	if os.path.exists(d) :
		t=TreeScraper(d,base=lxml.etree.XMLParser)
		d=date
	else :
		t=TreeScraper("../data/xml/%s-unitatssac.xml" % d ,base=lxml.etree.XMLParser)
	for e in t.extract("//item",
							 id='./id/text()',
							 resp='./resp/text()', 
							 iddep='./iddep/text()',
							 nom='./nom/text()',
							 centres=('./centres/c', 
									  { 'pob' : './pob/text()', 
										'cp' : './cp/text()', 
										'com' : './com/text()'}) ):
		try :
			has=store.execute('select * from entitats where id=? order by stamp desc limit 1',(e['id'],))
		except sqlite3.OperationalError :
			has=[]
		if len(has)!=0 :
			has=has[0]
		else :
			has=defaultdict(lambda : None)
		e["stamp"]=d
		cr={} 
		for k in ('nom','resp','iddep','centres','id') :
			if has[k]!=e[k] :
				 cr[k]={'old' : has[k], 'new' : e[k] }
		if cr :
			cr.update(dict(nid=e['id'], 
						   stamp=d,
						   oldstamp=has['stamp'] ))
			canvis.append(cr)
			entitats.append(e)
			changed+=1
	store.insert(entitats,"entitats")
	store.insert(canvis,"canvis")
	return (unchanged,changed)


if __name__=='__main__' :
	files="""/home/ftd/projekte/generalitat/data/xml/2013-04-26-unitatssac.xml
/home/ftd/projekte/generalitat/data/xml/2013-05-26-unitatssac.xml
/home/ftd/projekte/generalitat/data/xml/2013-05-28-unitatssac.xml
/home/ftd/projekte/generalitat/data/xml/2013-05-29-unitatssac.xml
/home/ftd/projekte/generalitat/data/xml/2013-05-30-unitatssac.xml
/home/ftd/projekte/generalitat/data/xml/2013-05-31-unitatssac.xml
/home/ftd/projekte/generalitat/data/xml/2013-06-01-unitatssac.xml
/home/ftd/projekte/generalitat/data/xml/2013-06-02-unitatssac.xml
/home/ftd/projekte/generalitat/data/xml/2013-06-03-unitatssac.xml
/home/ftd/projekte/generalitat/data/xml/2013-06-04-unitatssac.xml
/home/ftd/projekte/generalitat/data/xml/2013-06-05-unitatssac.xml
/home/ftd/projekte/generalitat/data/xml/2013-06-06-unitatssac.xml
/home/ftd/projekte/generalitat/data/xml/2013-06-07-unitatssac.xml
/home/ftd/projekte/generalitat/data/xml/2013-06-08-unitatssac.xml
/home/ftd/projekte/generalitat/data/xml/2013-06-09-unitatssac.xml
/home/ftd/projekte/generalitat/data/xml/2013-06-10-unitatssac.xml
/home/ftd/projekte/generalitat/data/xml/2013-06-11-unitatssac.xml
/home/ftd/projekte/generalitat/data/xml/2013-06-12-unitatssac.xml
/home/ftd/projekte/generalitat/data/xml/2013-06-13-unitatssac.xml
/home/ftd/projekte/generalitat/data/xml/2013-06-14-unitatssac.xml
/home/ftd/projekte/generalitat/data/xml/2013-06-15-unitatssac.xml
/home/ftd/projekte/generalitat/data/xml/2013-06-16-unitatssac.xml
/home/ftd/projekte/generalitat/data/xml/2013-06-17-unitatssac.xml
/home/ftd/projekte/generalitat/data/xml/2013-06-18-unitatssac.xml
/home/ftd/projekte/generalitat/data/xml/2013-06-19-unitatssac.xml
/home/ftd/projekte/generalitat/data/xml/2013-06-20-unitatssac.xml
/home/ftd/projekte/generalitat/data/xml/2013-06-21-unitatssac.xml
/home/ftd/projekte/generalitat/data/xml/2013-06-22-unitatssac.xml
/home/ftd/projekte/generalitat/data/xml/2013-06-23-unitatssac.xml
/home/ftd/projekte/generalitat/data/xml/2013-06-24-unitatssac.xml
/home/ftd/projekte/generalitat/data/xml/2013-06-25-unitatssac.xml
/home/ftd/projekte/generalitat/data/xml/2013-06-26-unitatssac.xml
/home/ftd/projekte/generalitat/data/xml/2013-06-27-unitatssac.xml
/home/ftd/projekte/generalitat/data/xml/2013-06-28-unitatssac.xml
/home/ftd/projekte/generalitat/data/xml/2013-06-29-unitatssac.xml
/home/ftd/projekte/generalitat/data/xml/2013-06-30-unitatssac.xml
/home/ftd/projekte/generalitat/data/xml/2013-07-01-unitatssac.xml"""
	import re
	for f in files.split("\n") :
		date=re.search(r"xml/(?P<date>\d\d\d\d-\d\d-\d\d)",f).groupdict().get("date","")
		(old,changed)=leer_organigrama(f,date=date)
		print "%s: %s (%s changed)" % (date,old,changed)

