# coding:utf-8

import re
import requests
from lxml import etree
from multiprocessing import Lock
import pprint
import simplejson
import logging
import dumptruck
import datetime

logger=logging.getLogger(__name__)

organigrama_url="http://www10.gencat.cat/sac/AppJava/organigrama_query.jsp?nivell=1&pares=true&codi=%s&jq=200001"
database=dumptruck.DumpTruck("../data/generalitat.sqlite")

cachelock=Lock()
cache={} 

class ListConsumer :

    def __init__(self) :
        self.stack=[]
        self.superior={}
	self.waiting_superior=False  # Text-Only nodes
    
    def start(self,tag,attrib) :
        if tag=="ul" :
            self.log("%slist start" % ("#" * len(self.stack),))
            self.stack.append({ });
        if tag=="li" :
            if "id" in attrib: 
                self.stack[-1]["id"]=attrib["id"]
                self.log("list item id %s" % attrib["id"])
        if tag=="a" :
            n=re.search("codi=(\d+)",attrib["href"])
            if not n:
		self.waiting_superior=self.stack[-2].get("id",self.stack[-2].get("hrefid",self.stack[-2]["textid"]))
	    else :
				self.waiting_superior=False
				hrefid=n.groups()[0]
				self.stack[-1]["hrefid"]=hrefid
				if len(self.stack)>1 :
					if (("id" in self.stack[-2]) or ("hrefid" in self.stack[-2]) or ("textid" in self.stack[-2])):
						if hrefid in self.superior :
							raise ValueError, "%s already has an assigned superior: %s (new value: %s)" % (self.stack[-2],self.superior[self.stack[-2]],hrefid)
						if "id" in self.stack[-2] :
							self.superior[hrefid]=self.stack[-2]["id"]
						else :
							if "hrefid" in self.stack[-2] :
								self.superior[hrefid]=self.stack[-2]["hrefid"]
							else :
								if "textid" in self.stack[-2] :
									self.superior[hrefid]=self.stack[-2]["textid"]
						self.log("%s es superior a %s" % (self.superior[hrefid],hrefid))
					else :
						if "textid" in self.stack[-2] :
							self.superior[hrefid]=self.stack[-2]["textid"]
				else :
					self.log("stack is %s" % len(self.stack))
					if len(self.stack)==1 :
						self.superior[self.stack[0]["hrefid"]]=self.stack[0]["hrefid"]
						self.log("%(hrefid)s es el nivel máximo" % self.stack[0])
            
    def end(self,tag) :
        if tag=="ul" :
            self.log("list end")
            self.stack=self.stack[:-1]
    
    
    def data(self,data) :
		if len(self.stack)>0 :
			cur=self.stack[-1]
			cur["text"]=data
			cur["textid"]="id-%s-%s" % (abs(hash(data)),data)	
			self.log("textid assigned: %(text)s" % cur)
			if self.waiting_superior :
				self.superior[cur["textid"]]=self.waiting_superior
				self.waiting_superior=False
				self.log("%s es superior a %s" % (self.superior[cur["textid"]],cur["textid"]))
    
    
    def comment(self,comment) :
        pass
    
    def close(self) :
        pass
    
    def log(self,*args) :
		pass # print args
        

def dep_from_db(idd) :
	r=database.execute("select superior from dependencies where id=?",(idd,))
	if len(r)>0 :
		return r[0]["superior"]
	else :
		return False

def update_deps(ddict) :
	n={ 'changed' : 0, 'new' : 0 }
	now=datetime.datetime.now()
	for (idd,superior) in ddict.items() :
		d=dep_from_db(idd)
		if d is False :
			database.insert({'id' : idd, 'superior' : superior, 'stamp' : now},'dependencies')
			n["new"]+=1
		else :
			if d!=superior :
				database.execute("update dependencies set superior=?,stamp=? where id=?",(superior,now,idd))
				n["changed"]+=1
	return n

        
def dependencias(codi) :
    # print txt
    url=organigrama_url % codi
    logger.debug("fetching %s" % (url,))
    lc=ListConsumer()
    parser=etree.HTMLParser(recover=True, target=lc)
    etree.fromstring(requests.get(url).content,parser)
    lc.log(pprint.pformat(lc.superior))
    return lc.superior
    
  

 
def depende_de(codi) :
	dep=dep_from_db(codi)
	if dep is False :
		url=organigrama_url % codi
		dep=dependencias(codi)
		n=update_deps(dep)
		print("%(new)s nuevas, %(changed)s cambiadas" % n)
		return dep_from_db(codi)
	else :
		return(dep)

		
