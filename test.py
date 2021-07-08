import mysql.connector
import hashlib
import os
import fnmatch
from helper import litowin
import json

with open('dbconfig.json') as f:
    data = json.loads(f.read())
    
somasdb = mysql.connector.connect(
    host=data['host'],
    user=data['user'],
    passwd=data['password'],
    auth_plugin='mysql_native_password',
    database=data['db']
)
db_cursor = somasdb.cursor()

db_cursor.execute("SHOW TABLES")
tables = db_cursor.fetchall()
for table in tables:
    print(table[0]+', ', end= '')