# coding: utf-8

from flask import Flask,request,Response,render_template,g,jsonify,url_for,redirect
from config import Config
from dbhelper import dbhelper
import re,datetime
import editdist

if __name__ == '__main__' :

	app = Flask(__name__, static_url_path="/static/gencat")      
	
else :
	
	app = Flask(__name__, static_url_path="/static")      

app.config.from_object(Config)

query_db=dbhelper(app)



def test_distance(a1,a2) :
	def tester(a) :
		return float(editdist.distance(repr(a[a1]),repr(a[a2])))/float(max([len(a[a1]),len(a[a2])]))
	return tester

tests = { "canvisresp" : test_distance("resp","oldresp"),
		  "canvisnom" : test_distance("nom","oldnom")
	     }

def away(n,days) :
	return (n+datetime.timedelta(days=days)).strftime("%Y-%m-%d")
 
 
def query_all(query,param) :
	res={}
	for t in ("nuevos","borrados","canvisnom","canvisresp") :
		res[t]=query_db(query % t,param)
	for (t,v) in tests.items() :
		for r in res[t] :
			r["test"]=v(r)
		res[t]=filter(lambda a: a["test"]>0.1,res[t])
	return res
	
 
@app.route('/d/<dep>/<start>')
@app.route('/d/<start>')
@app.route('/')
def diario(start=None,dep=None) :
	end=None
	if dep is None and start is not None and re.match("^\d$",start) :
		dep=start
		start=None
	if start is None :
		start=(datetime.datetime.now()-datetime.timedelta(days=7)).strftime("%Y-%m-%d")
	if end is None :
		end=(datetime.datetime.strptime(start,"%Y-%m-%d")+datetime.timedelta(days=7)).strftime("%Y-%m-%d")
	if dep is not None :
		qs=" and iddep='%s' " % dep
	else :
		qs=""
	resultados=query_all("select * from %%s where stamp>=? and stamp<=? %s order by  iddep asc, stamp asc, id asc" % (qs,),(start,end))
	startdate=datetime.datetime.strptime(start,"%Y-%m-%d")
	nav=[ { 'link' : url_for('diario',dep=dep,start=away(startdate,-8)), 'text' : 'anterior' },
		  { 'link' : url_for('diario',dep=dep,start=away(startdate,8)), 'text' : 'posterior' },
	    ]
	return render_template("diario.html", resultados=resultados, start=start, end=end, dep=dep,
	                                      total=reduce(lambda a,b: a+len(b), resultados.values(),0),
	                                      nav=nav
	                                      )

@app.route('/e/<idd>')
def entidad(idd=None) :
	resultados=query_all("select * from %s where id=?",(idd,))
	total=reduce(lambda a,b: a+len(b), resultados.values(),0)
	entidad=query_db("select * from entitats where id=? order by stamp desc", (idd,),one=True)
	return render_template("entidad.html", resultados=resultados, total=total, entidad=entidad)
	
	
	




if not app.debug:
    import loghelper
    loghelper.mail_on_exception(app.logger,subject="%s exception" % __name__ )
    loghelper.rotating_logfile(app.logger,filename=os.path.join(app.config['HOME'],"log/app.log"), level=logging.DEBUG)
  
if __name__ == '__main__':
	app.run(debug=True,host="0.0.0.0")
