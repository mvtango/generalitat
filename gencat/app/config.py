import os,re
import socket
from dumptruck import DumpTruck

_me=socket.gethostname()
_here=os.path.split(__file__)[0]


class Config(object):
    DEBUG = False
    TESTING = False
    DATABASE_PATH = os.path.join(_here,"../../data/organigrama.db")
    STORE=DumpTruck(dbname=DATABASE_PATH,auto_commit=False)
    HOME=_here
    DEPTS=dict([(a['id'],re.sub(r"Departament d('|e )(la )?","",a['nom'])) for a in STORE.execute("select nom,id from entitats where id in (select distinct iddep from entitats)")])


class ProductionConfig(Config):
    DATABASE_URI = 'mysql://user@localhost/foo'

class DevelopmentConfig(Config):
	DEBUG = True
	TESTING = True 

if _me in ('martin-UX21A' , ) :
	Config=DevelopmentConfig
	
