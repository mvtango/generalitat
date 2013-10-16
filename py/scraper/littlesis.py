# coding: utf-8

from scraper.browser import Browser
from lxml import etree
import os,sys
import shelve 
from lxml.builder import E
import logging
import string 

logging.basicConfig(level=logging.DEBUG,file=sys.stderr)
logger=logging.getLogger(os.path.split(__file__)[1])

_here=os.path.split(__file__)[0]
cache=os.path.join(_here,"data/littlesisids.db")
idcache=shelve.DbfilenameShelf(cache)


class LittleSisBrowser(Browser) :
	
	_key="223643a835ec11609db34615df8687076f981056"
	
	def __init__(self, *args,**kwargs) :
		super(LittleSisBrowser,self).__init__(*args,**kwargs)
		self.headers.update({ 'Accept-Encoding' : "gzip" })
	
	
	def get(self,addr,*args,**kwargs) :
		j="?"
		if addr.find("?") > 0 :
			j="&"
		addr="%s%s_key=%s" % (addr,j,LittleSisBrowser._key)
		return super(LittleSisBrowser,self).get(addr,*args,**kwargs)
		
		
	def tree(self,*args,**kwargs) :
		c=self.get(*args,**kwargs)
		return etree.fromstring(c.content, etree.XMLParser(remove_blank_text=True))


def writeXML(tree,fname) :
	f=open(fname,"w")
	f.write(etree.tostring(tree,pretty_print=True))
	f.close()
		

relationship={ 'Position' : '1',
             'Education' : '2',
             'Membership' : '3',
			 'Family' : '4',
			 'Donation' : '5',
			 'Transaction' : '6',
			 'Lobbying' : '8',
			 'Social' : '9',
			 'Professional' : '10'
}


def id_to_url(ids) :
	if not ids in idcache :
		b=LittleSisBrowser()
		e=b.tree("http://api.littlesis.org/entity/%s.xml" % ids)
		logger.debug("%s -> %s" % (ids,e.xpath("//uri/text()")[0]))
		idcache[ids]=unicode(e.xpath("//uri/text()")[0])
	return idcache[ids]


url="http://api.littlesis.org/entity/%(entity)s/related/degree2.xml?cat1_ids=%(c)s&cat2_ids=%(c)s&num=100&page=%(p)i"


def dump_second_degree(personid,category,output_dir) :
	page=1
	b=LittleSisBrowser()
	try :
		category_key=relationship[category]
	except KeyError,e :
		raise KeyError("'%s' not in list of categories %s" % (e,repr(relationship.keys())))
	person_string="%s_%s" % (string.lower(os.path.split(id_to_url(personid))[1]),personid)
	output_filename="%s/%s_network_%s_%%06d.xml" % (person_string,person_string,string.lower(category))
	while True :
		of=os.path.join(output_dir,output_filename % page)
		od=os.path.split(of)[0]
		if not os.path.exists(od) :
			os.makedirs(od)
		iu=url % { "p" : page, "c" : category_key, "entity" : personid }
		t=b.tree(iu)
		count=int(t.xpath("//Meta/ResultCount/Degree2Entities/text()")[0])
		if (count>0) :
			for ent in t.xpath("//Degree2Entities/Entity") :
				idt=ent.xpath(".//degree1_ids/text()")[0]
				for tti in idt.split(",") :
					u=id_to_url(tti)
					el=E.degree1_url(u)
					ent.append(el)
			writeXML(t,of)
			logger.debug("%s %s Page %s : %s entities written" % (person_string,category,page,count))
			page=page+1
		if (count<100) :
			break


