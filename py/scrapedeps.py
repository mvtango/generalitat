from csvstore import csvstore	
from generalitat import depende_de
store=csvstore("../data/unitatssac-scraped.csv")

for item in store.data :
	item["dep_scraped_new"]=depende_de(item["id"])
	print "%s -> %s " % (item["id"],item["dep_scraped_new"])
	

