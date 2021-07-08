import mysql.connector
import hashlib
import os
import fnmatch
from helper import litowin
import json

try:
    with open('dbconfig.json') as f:
        data = json.loads(f.read())
except:
    print("Err")