import csvstore
import generalitat
import simplejson
import os

here=os.path.split(__file__)[0]

datadir=os.path.join(here,"../data")

files={ "in" : "unitatssac-scraped-20130525-out.csv",
        "out" : "unitatssac-scraped-20130525-salud.csv"
       }
       
# generalitat.cache=simplejson.load(open(os.path.join(datadir,"generalitat.cache.json")))
entitats=csvstore.csvstore(os.path.join(datadir,files["in"]))
analyze=False

try  :
	for e in entitats.data : 
		if not analyze :
			if e["id"] != "7290" :
				continue
			analyze=True
		if e["iddep"]=="2803" :
				p=e["iddep-scraped"]
				try :
					e["iddep-scraped"] = generalitat.depende_de(e["id"]) 
				except KeyboardInterrupt :
					print "break"
					raise
				except Exception,e:
					print "Exception: %s" % e 
				else :
					if (p==e["iddep-scraped"]) :
						print "Same!",
					else :
						print "Different - ",
					print "%s -> %s" % (e["id"],e["iddep-scraped"])
finally :
	entitats.store(os.path.join(datadir,files["out"]))
	print "stored"
