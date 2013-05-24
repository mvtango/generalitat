import csvstore
import generalitat
import simplejson
import os

here=os.path.split(__file__)[0]

datadir=os.path.join(here,"../data")

# generalitat.cache=simplejson.load(open(os.path.join(datadir,"generalitat.cache.json")))
entitats=csvstore.csvstore(os.path.join(datadir,"unitatssac-scraped.csv"))
try  :
	for e in entitats.data : 
		try :
			e["iddep-scraped-new"] = generalitat.depende_de(e["id"]) 
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
