#!/usr/bin/env python


'''
RENAME to config.py
'''

# WEBSERVER
HOST = '127.0.0.1'
PORT = 8001
DEBUG = True


# Flask
STATIC_FOLDER = 'static'


# Database
DBUSER = '**************'
DBPASS = '**************'
DBHOST = 'localhost'
DBNAME = 'babar3'

_DBQUEUE = 'mysql://%s:%s@%s/%s' % ( DBUSER, DBPASS, DBHOST, DBNAME)
