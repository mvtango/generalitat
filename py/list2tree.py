import simplejson

def log(*args) :
	pass # print args

def dict2node(item) :
		return({ "name" : item["nom"], "id" : item["id"], "data" : item })


def list2tree(lista,children="children") :
	rootnode={ "name": "Entitats", "id" : "0gen", "data" : {} }
	rootnode[children]=[]
	index={}
	depindex={}
	for item in lista :
		ds=item["iddep-scraped"]
		index[item["id"]]=dict2node(item)
		if not ds in depindex :
			depindex[ds]=[index[item["id"]]]
			# print "New depindex %s" % ds
		else :
			depindex[ds].append(index[item["id"]])
	for item in filter(lambda a:  a["iddep"]==a["id"],lista) :
		rootnode[children].append(index[item["id"]])
	found=True
	rno=0
	while found :
		found=False
		added=[]
		rno=rno+1
		for n in index.values() :
			if n["id"] in depindex and not children in n:
				n[children]=depindex[n["id"]]
				added.append(n)
				found=True
				log("#%s: %s deps for %s: %s" % (rno,len(n[children]),n["name"],",".join(map(lambda a:a["name"],n[children]))))
	return(rootnode) # map(lambda a:a[1],filter(lambda a: a[0] not in index , depindex.items())))
	
	
def writetree(o,n) :
    f=open(n,"w")
    f.write("window.data=")
    simplejson.dump(o,f)
    f.close()
