import csvstore
import list2tree

entitats=csvstore.csvstore("unitatssac-scraped.csv")

rootnode=list2tree.list2tree(filter(lambda a: a["nom"], entitats.data))

pres=filter(lambda a: a["name"].find("Presidència")>-1,rootnode["children"])[0]

list2tree.writetree(pres,"presidencia.json");
