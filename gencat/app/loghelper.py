import logging
from logging import Formatter


def mail_on_exception(logger,subject="Exception ",level=logging.ERROR) :
    from logging.handlers import SMTPHandler
    mail_handler = SMTPHandler('mx.onosendai.de',
                               'martin@bitbucket.onosendai.de',
                               'martin.virtel@gmail.com', subject )
    mail_handler.setLevel(level)
    logger.addHandler(mail_handler)

    mail_handler.setFormatter(Formatter('''
Message type:       %(levelname)s
Location:           %(pathname)s:%(lineno)d
Module:             %(module)s
Function:           %(funcName)s
Time:               %(asctime)s

Message:

%(message)s
'''))

def rotating_logfile(logger,filename,level=logging.DEBUG) :
    from logging.handlers import RotatingFileHandler
    file_handler=RotatingFileHandler(filename,maxBytes=5*1024*1024,backupCount=5)
    file_handler.setLevel(level)
    logger.addHandler(file_handler)
    file_handler.setFormatter(Formatter(
'%(asctime)s %(levelname)s: %(message)s '
'[in %(pathname)s:%(lineno)d]'
))

