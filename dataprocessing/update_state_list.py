#!/usr/bin/env python

import json
import sys

from boto.exception import S3ResponseError
from boto.s3.connection import S3Connection
from boto.s3.key import Key
from pymongo import Connection

import config
import utils

STATE = sys.argv[1]
try: CLEAR = sys.argv[2]
except: CLEAR = None

connection = Connection()
db = connection[config.CENSUS_DB]
collection = db[config.GEOGRAPHIES_COLLECTION]

row_count = 0
deployed = 0

c = S3Connection()
bucket = c.get_bucket(config.S3_BUCKET)

k = Key(bucket)
k.key = 'states.jsonp'

try:
    data = k.get_contents_as_string()

    # No existing file 
    if not data:
        raise S3ResponseError()
    
    # Strip off jsonp wrapper
    contents = utils.gunzip_data(data)
    data = contents[7:-1]

    states = json.loads(data)
except S3ResponseError:
    states = []

if CLEAR == 'CLEAR':
    states = [STATE]
else:
    if STATE not in states:
        states.append(STATE)

jsonp = 'states(%s)' % json.dumps(states)
compressed = utils.gzip_data(jsonp)

k.set_contents_from_string(compressed, headers={ 'Content-encoding': 'gzip', 'Content-Type': 'application/json' }, policy='public-read')

