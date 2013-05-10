import csvstore
import generalitat
import simplejson

generalitat.cache=simplejson.load(open("generalitat.cache.json"))
entitats=csvstore.csvstore("unitatssac-scraped.csv")
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
	entitats.store("unitatssac-2013050-break-scraped-xml.csv")
	simplejson.dump(generalitat.cache,open("generalitat.cache-out.json","w"))
	print "stored"
