import sqlite3
from flask import g
import simplejson
import datetime
import os,sys
import sha
import logging
import datetime
import copy, time
import loghelper

def dbhelper(app) :

	def make_dicts(cur, row):
		a=dict((cur.description[idx][0], value)
			for idx, value in enumerate(row))
		return a

	def ping(db) :
		try :
			f=db.execute("select 1").fetchall()
			return True
		except sqlite3.ProgrammingError :
			return False

	def get_db():
		db = getattr(g, '_database', None)
		if db is None or not ping(db):
			db = g._database = sqlite3.connect(app.config["DATABASE_PATH"],isolation_level="DEFERRED",timeout=2)
		db.row_factory = make_dicts
		return db
		
	def query_db(query, args=(), one=False):
		cur = get_db().execute(query, args)
		rv = cur.fetchall()
		cur.close()
		result=(rv[0] if rv else None) if one else rv
		return result


	def _close_connection(exception):
		db = getattr(g, '_database', None)
		if db is not None:
			db.close()
			setattr(g,'_database',None)
	
	@app.teardown_appcontext
	def close_connection(exception):
		_close_connection(exception)
		
	return query_db
    
