# coding: utf-8

from scrapelib import TreeScraper,TextParser,TextEditor


exdate=TextParser('^.*\((?P<update>[^\)]+)\).*$')
exspace=TextEditor([(r'[\xa0\n\t ]+',' '),])

def depto(idd) :
	d=TreeScraper("http://www10.gencat.cat/sac/AppJava/organisme_fitxa.jsp?codi=%s" % idd)
	r=d.extract("div#contingut",titulo=".//h3/text()",mapa=".//a[@class='mapa']/@href",
          resp=".//div[@class='esquerra' and contains(.//text(),'Responsable')]/../div[@class='columna2']/text()",
          carreg=u".//div[@class='esquerra' and contains(.//text(),'Càrrec')]/../div[@class='columna2']/text()",
          address=u".//div[@class='esquerra' and contains(.//text(),'Adreça')]/../div[@class='columna2']/text()",
          tel=u".//div[@class='esquerra' and contains(.//text(),'Telèfon')]/../div[@class='columna2']/text()",
          fax=u".//div[@class='esquerra' and contains(.//text(),'Fax')]/../div[@class='columna2']/text()",
          pob=u".//div[@class='esquerra' and contains(.//text(),'Població')]/../div[@class='columna2']/text()",
          email=u".//div[@class='esquerra' and contains(.//text(),'Contacte')]/../div[@class='columna2']/a/text()",
          desc=u".//div[@class='esquerra' and contains(.//text(),'Funcions')]/../div[@class='columna2']/text()",
          normativa=u".//div[@class='esquerra' and contains(.//text(),'Normativa')]/../div[@class='columna2']/ul/li/a",
          update=u".//div[contains(@class,'fecha') and contains(./text(),'actualització')]/text()"
          )
	if len(r)==1 :
		rr={}
		r[0]["normativa"]=[exspace(unicode(a)) for a in r[0]["normativa"]]
		for (k,v) in r[0].items() :
			if type(v) != type([]) :
				rr[k]=exspace(unicode(v))
			elif v==[] :
				rr[k]=''
			elif type(v)==type(u"") :
				rr[k]=exspace(v)
			else :
				rr[k]=v
		rr.update({ 'id' : idd})
		rr.update(exdate(rr['update']))
		return rr		
	else :
		raise OperationalError, r


def scrape_list(ids) :
	res=[]
	for tid in ids :
		res.append(depto(tid))
	return database.upsert(res,"departaments")


if __name__=='__main__' :
	import dumptruck, random,sys
	database=dumptruck.DumpTruck("../data/generalitat.sqlite")
	ids=[a["id"] for a in database.execute("select id from dependencies where id not like 'id-%' and id not in (select id from departaments)") ]
	if not ids :
		print "None missing"
		sys.exit()
	cont=True
	res=[]
	already={}
	tries=1
	import pprint
	while cont :
		try :
			did=random.choice(ids)
			if did in already :
				tries+=1
				if tries>2*len(ids) :
					break
				continue
			already[did]=True
			ar=database.execute("select count(*) as c from departaments where id=?", (did,))
			if ar[0]["c"]==0 :
				res.append(depto(did))
				print "%s : %s" % (did,repr(res[-1]["titulo"]))
		except KeyboardInterrupt :
			cont=False

	print "%s results" % (len(res),)	
	print "stored: %s" % database.upsert(res,"departaments")


			
		
