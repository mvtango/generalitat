import re
import requests
from lxml import etree
from multiprocessing import Lock

organigrama_url="http://www10.gencat.cat/sac/AppJava/organigrama_query.jsp?nivell=16&pares=true&codi=%s&jq=200001"
cache={}

cachelock=Lock()

class ListConsumer :

    def __init__(self) :
        self.stack=[]
        self.superior={}
    
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
            if n:
				hrefid=n.groups()[0]
				self.stack[-1]["hrefid"]=hrefid
				if len(self.stack)>2 :
					if (("id" in self.stack[-2]) or ("hrefid" in self.stack[-2])):
						if hrefid in self.superior :
							raise ValueError, "%s already has an assigned superior: %s (new value: %s)" % (self.stack[-2],self.superior[self.stack[-2]],hrefid)
						if "id" in self.stack[-2] :
							self.superior[hrefid]=self.stack[-2]["id"]
						else :
							self.superior[hrefid]=self.stack[-2]["hrefid"]
						self.log("%s es superior a %s" % (self.superior[hrefid],hrefid))
					else :
						if "textid" in self.stack[-2] :
							self.superior[hrefid]=self.stack[-2]["textid"]
            
    def end(self,tag) :
        if tag=="ul" :
            self.log("list end")
            self.stack=self.stack[:-1]
    
    
    def data(self,data) :
		if len(self.stack)>0 :
			cur=self.stack[-1]
			cur["text"]=data
			cur["textid"]="id-%s" % abs(hash(data))	
			self.log("%(text)s" % cur)
    
    
    def comment(self,comment) :
        pass
    
    def close(self) :
        pass
    
    def log(self,*args) :
        pass # print args
        
        
def dependencias(txt) :
    lc=ListConsumer()
    parser=etree.HTMLParser(recover=True, target=lc)
    etree.fromstring(txt,parser)
    return lc.superior
    
   
def depende_de(codi) :
	if not codi in cache :
		dep=dependencias(requests.get(organigrama_url % codi).content)
		cachelock.acquire()
		cache.update(dep)
		cachelock.release()
		if not codi in cache :
			cache[codi]=None
	return cache[codi]

		
