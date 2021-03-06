# coding: utf-8

from flask import Flask,request,Response,render_template,g,jsonify,url_for,redirect
from config import Config
from dbhelper import dbhelper
import re,datetime
import editdist,os,logging

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


def _in_out_both(ent) :
	if ent["resp"]=="null" and ent["oldresp"]!="null" :
		return "responsable-out"
	if ent["resp"]!="null" and ent["oldresp"]=="null" :
		return "responsable-in"
	return "responsable"


classify = { "canvisresp" : _in_out_both,
			 "canvisnom"  : lambda a : "nombre",
			 "borrados"  : lambda a : "borradas",
			 "nuevos"  : lambda a : "nuevas",
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
	for (t,v) in classify.items() :
		for r in res[t] :
			r["class"]=v(r)	
	return res
	
@app.route('/d/<dep>/<start>/<end>') 
@app.route('/d/<dep>/<start>')
@app.route('/d/<start>')
@app.route('/')
def diario(start=None,dep=None,end=None) :
	if dep is None and start is not None and re.match("^\d$",start) :
		dep=start
		start=None
	if start is None :
		start=(datetime.datetime.now()-datetime.timedelta(days=6)).strftime("%Y-%m-%d")
	if end is None :
		end=(datetime.datetime.strptime(start,"%Y-%m-%d")+datetime.timedelta(days=6)).strftime("%Y-%m-%d")
	else :
		if end=='avui' :
			end=datetime.datetime.now().strftime("%Y-%m-%d")
	if dep is not None and dep != '0' :
		qs=" and iddep='%s' " % dep
	else :
		qs=""
	diff=(datetime.datetime.strptime(end,"%Y-%m-%d")-datetime.datetime.strptime(start,"%Y-%m-%d")).days
	resultados=query_all("select * from %%s where stamp>=? and stamp<=? %s order by  iddep asc, stamp asc, id asc" % (qs,),(start,end))
	startdate=datetime.datetime.strptime(start,"%Y-%m-%d")
	nav=[ { 'link' : url_for('diario',dep=dep,start=away(startdate,-diff)), 'title' : "des de %s" % away(startdate,-diff),  'text' : '&laquo;' },
		  { 'link' : url_for('diario',dep=dep,start=away(startdate,diff)), 'title' : "des de %s" % away(startdate,diff),'text' : '&raquo;' },
	    ]
	rformat=request.args.get("format",False)
	if rformat=="json" :
		return jsonify(resultados=resultados,start=start,dep=dep,end=end)
	else :
		return render_template("diario.html", resultados=resultados, start=start, end=end, dep=dep,
	                                      total=reduce(lambda a,b: a+len(b), resultados.values(),0),
	                                      nav=nav,
					      request=request
	                                      )

@app.route('/e/<idd>')
def entidad(idd=None) :
	resultados=query_all("select * from %s where id=?",(idd,))
	total=reduce(lambda a,b: a+len(b), resultados.values(),0)
	entidad=query_db("select * from entitats where id=? order by stamp desc", (idd,),one=True)
	return render_template("entidad.html", resultados=resultados, total=total, entidad=entidad)
	
@app.route('/p/<nom>')
def persona(nom=None) :
	resultados=query_db("select * from entitats where resp=? order by stamp desc",(nom,))
	return render_template("persona.html", resultados=resultados)

	
	
	

@app.route('/c/<cid>')
def canvi(cid=None) :
	canvi=query_db("select *,rowid as cid from canvis where rowid=?",(cid,),one=True)
	old=query_db("select * from entitats where rowid=?",(canvi["oldid"],),one=True)
	new=query_db("select * from entitats where rowid=?",(canvi["newid"],),one=True)
	return render_template("canvi.html", canvi=canvi, old=old, new=new)
	


	
	
@app.route('/multi/') 
def multiple() :
	resultados=query_db("""
	select distinct id,resp,nom,iddep,stamp from entitats where resp in (select resp from (select distinct resp,count(distinct id) as cn from entitats where resp!="null" and resp not like "Conseller%" group by resp having cn>1 order by cn asc)) order by resp,stamp
	""")
	return render_template("multiple.html",resultados=resultados)


@app.route('/api/canvis/<dep>/<start>/<end>') 
def api(start=None,dep=None,end=None,typ=None) :
	if dep is None or start is None or end is None:
		return jsonify({ "status" : "error", "message" : "See %s for details." % url_for("rtfm") })
	if dep != 'all' :
		dep=re.search("(\d+)",dep)
		if dep :
			qs=" and iddep='%s' " % dep.groups()[0]
		else :
			qs=""
	else :
		qs=""
	resultados=query_all("select * from %%s where stamp>=? and stamp<=? %s order by  iddep asc, stamp asc, id asc" % (qs,),(start,end))
	return jsonify({ "status" : "ok", "resultados" : resultados})

@app.route('/api/')
def rtfm() :
	return redirect("/es/2014/04/como-colaborar-en-el-sismografo-jpd14/#api", code=302)


if not app.debug:
    import loghelper
    loghelper.mail_on_exception(app.logger,subject="%s exception" % __name__ )
    loghelper.rotating_logfile(app.logger,filename=os.path.join(app.config['HOME'],"log/app.log"), level=logging.DEBUG)
  
if __name__ == '__main__':
	app.run(debug=True,host="0.0.0.0")
