import csvstore
import generalitat
import simplejson
import os

here=os.path.split(__file__)[0]

datadir=os.path.join(here,"../data")

generalitat.cache=simplejson.load(open(os.path.join(datadir,"generalitat.cache.json")))
entitats=csvstore.csvstore(os.path.join(datadir,"unitatssac-scraped.csv"))
try  :
	for e in entitats.data : 
		if not e["iddep-scraped"] : 
			try :
				e["iddep-scraped"] = generalitat.depende_de(e["id"]) 
			except KeyError : 
				generalitat.cache[e["id"]]=None 
			except KeyboardInterrupt :
				print "break"
				raise
			except Exception:
				pass
			else :
				print "%s -> %s" % (e["id"],e["iddep-scraped"])
finally :
	entitats.store(os.path.join(datadir,"unitatssac-scraped-result.csv"))
	simplejson.dump(generalitat.cache,open(os.path.join(datadir,"generalitat.cache-result.json"),"w"))
	print "stored"
