import csv
import os

class csvstore :

	def __init__(self,name) :
		self.name=name
		f=open(name)
		s=csv.Sniffer()
		self.dialect=s.sniff(f.readline())
		if not self.dialect.escapechar :
			self.dialect.escapechar="\\"
		if not self.dialect.quotechar :
			self.dialect.escapechar="\\"
		f.seek(0)
		r=csv.reader(f,dialect=self.dialect)
		self.fields=r.next()
		f.seek(0)
		self.data=[]
		r=csv.DictReader(f,dialect=self.dialect)
		while True :
			try :
				self.data.append(r.next())
			except StopIteration :
				break

		
		
	def store(self,name,**kwargs) :
		nf=[f for f in self.fields]
		for d in self.data :
			for k in d.keys() :
				if not k in nf :
					nf.append(k)
		f=open(name,"w")
		wh=csv.writer(f,dialect=self.dialect)
		wh.writerow(nf)
		w=csv.DictWriter(f,nf,dialect=self.dialect,**kwargs)
		w.writerows(self.data)
		f.close()
			
		
		
