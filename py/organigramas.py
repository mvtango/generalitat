# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <codecell>

from scrapelib import TreeScraper
import lxml,dumptruck,sqlite3,datetime
store=dumptruck.DumpTruck("../data/organigrama.db")
from collections import defaultdict
import os,re



init_db=[
"""CREATE TABLE if not exists `canvis` (
            `stamp` text
          , `newid` integer, `type` text, `oldid` integer, `id` text);""",
"""CREATE TABLE if not exists `entitats` (
            `stamp` text
          , `id` text, `nom` text, `centres` json text, `resp` text, `iddep` text);""",
"""CREATE INDEX if not exists canvis_newid ON `canvis` (`newid`);""",
"""CREATE INDEX if not exists canvis_oldid ON `canvis` (`oldid`);""",
"""CREATE INDEX if not exists canvis_type ON `canvis` (`type`);""",
"""CREATE INDEX if not exists entitats_id ON `entitats` (`id`);""",
"""CREATE UNIQUE INDEX if not exists entitats_id_stamp ON `entitats` (`id`,`stamp`);""",
"""CREATE INDEX if not exists entitats_stamp ON `entitats` (`stamp`);""",
"""CREATE VIEW if not exists canvisdep as select a.nom as nom, a.id as id, a.stamp as stamp, a.resp as resp,b.stamp as oldstamp, b.iddep as oldiddep,a.iddep as iddep, a.centres as centres from entitats as a, entitats as b, canvis where canvis.type="change" and canvis.newid=a.rowid and canvis.oldid=b.rowid and a.iddep != b.iddep;""",
"""CREATE VIEW if not exists canvisnom as select a.nom as nom, a.id as id, a.stamp as stamp, a.resp as resp,b.stamp as oldstamp, b.nom as oldnom,a.iddep as iddep, a.centres as centres from entitats as a, entitats as b, canvis where canvis.type="change" and canvis.newid=a.rowid and canvis.oldid=b.rowid and a.nom != b.nom;""",
"""CREATE VIEW if not exists canvisresp as select a.nom as nom, a.id as id, a.stamp as stamp, a.resp as resp,b.stamp as oldstamp, b.resp as oldresp,a.iddep as iddep, a.centres as centres from entitats as a, entitats as b, canvis where canvis.type="change" and canvis.newid=a.rowid and canvis.oldid=b.rowid and a.resp != b.resp;""",
"""CREATE VIEW if not exists nuevos as select a.nom as nom, a.id as id, a.stamp as stamp, a.resp as resp, a.iddep as iddep, a.centres as centres from entitats as a, canvis where canvis.type="new" and canvis.newid=a.rowid and canvis.stamp>(select min(stamp) from canvis);""",
"""CREATE VIEW if not exists borrados as select a.nom as nom, a.id as id, a.stamp as stamp, a.resp as resp, a.iddep as iddep, a.centres as centres from entitats as a, canvis where canvis.type="delete" and canvis.oldid=a.rowid and canvis.stamp>(select min(stamp) from canvis);""",
]

for s in init_db :
	try :
		store.execute(s)
	except sqlite3.OperationalError,e :
		print "%s: %s" % (s,e)
		
		
		
def leer_organigrama(d,date) :
	if os.path.exists(d) :
		t=TreeScraper(open(d),base=lxml.etree.XMLParser)
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
                                            e.update({ 'stamp' : d })
                                            yield e
        
        
def upsert_entidad(o) :
    has=store.execute("select *,rowid from entitats where id=? order by stamp desc limit 1",(o['id'],))
    if len(has)==0 :
        res={ 'entitats' : o, 'canvis' : { 'type' : 'new', 'oldid' : None, 'stamp' : o['stamp'], 'id' : o['id'] } }
        return res
    else :
        no=has[0]
        same=True
        for k in o.keys() :
            if k in ('stamp',) :
                continue
            if no[k]!=o[k] :
                same=False
                break
        if not same :
            res={ 'entitats' : o , 'canvis' : {'type' : 'change', 'oldid' : no["rowid"], 'stamp' : o['stamp'], 'id' : o['id'] } }
            return res
        else :
            return {}
        
        
def update_db(d) :
    stats=defaultdict(lambda : 0)
    jobs=[]
    newest=dict([(a["id"],{ 'present' : False, 'rowid' : a['rowid'], 'id' : a['id']} ) for a in store.execute("select id,rowid from entitats where stamp=(select max(stamp) from entitats)")])
    date=re.search(r"/(?P<date>2[01]\d\d-[01]\d-[0123]\d)",d).groupdict()["date"]
    for o in leer_organigrama(d,date) :
        r=upsert_entidad(o)
        if r :
            jobs.append(r)
            stats[r["canvis"]["type"]]+=1
        if o["id"] in newest :
            newest[o["id"]]["present"]=True        
    try :
    	ids=store.insert([a['entitats'] for a in jobs],'entitats')
    except sqlite3.IntegrityError,e :
	stats["error"] = "already stored : %s" % date
    else :
    	canvis=[]
    	for z in zip([a["canvis"] for a in jobs],ids) :
        	z[0].update({'newid': z[1]})
        	canvis.append(z[0])
    	store.insert(canvis,'canvis')
    	deleted=filter(lambda a: a["present"]==False, newest.values())
    	if len(deleted) :
        	stats["deleted"]=len(deleted)
        	cs=[]
        	for dele in deleted :
            		cs.append({ 'type' : 'delete', 'oldid' : dele['rowid'], 'newid' : None, 'stamp' : date, 'id' : dele['id'] })
        	store.insert(cs,'canvis')
    	else :
        	stats["deleted"]=0
	stats["error"]=''
    return stats



if __name__=='__main__'  :
	import sys,pprint
	files=sys.argv[1:]
	files.sort()
	for f in files :
		r=update_db(f)
		print "%s: " % f,
		print "%(error)s %(new)s new %(change)s changed %(delete)s deleted" % r
		
