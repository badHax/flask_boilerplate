"""
source http://roryokeeffe.com/production-logging-in-flask-python/
you want to import 'log' from this package as your production logger
"""
import logging
from logentries import LogentriesHandler
import datetime.datetime as datetime
import time
from flask import request
from fask.ext.login import current_user

from app_name import app
 
# - Filter/Formatter
class ContextualFilter(logging.Filter):
    def filter(self, log_record):
        """ Provide some extra variables to give our logs some
            better info
        """
        log_record.utcnow = (datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S,%f %Z'))
        log_record.url = request.path
        log_record.method = request.method
        
        # Try to get the IP address of the user through reverse proxy
        log_record.ip = request.environ.get('HTTP_X_REAL_IP',request.remote_addr)
        if current_user.is_anonymous():
            log_record.user_id = 'guest'
        else:
            log_record.user_id = current_user.get_id()
             
        return True
 
# Use said info
log_format = ("%(utcnow)s\tl=%(levelname)s\tu=%(user_id)s\tip=%(ip)s"
"\tm=%(method)s\turl=%(url)s\tmsg=%(message)s")
formatter = logging.Formatter(log_format)
        
# - Handlers
# -- Stream handler
streamHandler = logging.StreamHandler()
streamHandler.setLevel(logging.INFO)
streamHandler.setFormatter(formatter)
 
# -- LogEntries handler
leHandler = LogentriesHandler(app.config['LOGENTRIES_TOKEN'])
leHandler.setLevel(logging.INFO)
leHandler.setFormatter(formatter)
 
# - Logger
log = app.logger
log.setLevel(logging.DEBUG)
log.addFilter(ContextualFilter())
log.addHandler(streamHandler)
log.addHandler(leHandler)