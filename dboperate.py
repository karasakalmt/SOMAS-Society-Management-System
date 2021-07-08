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

def configDB():
    db_cursor('SHOW TABLES;')
    tables = db_cursor.fetchall()
    all_tables=[]
    for table in tables:
        all_tables+=table[0]
    # keep on from here
    with open('/etc/somasdb.sql', 'r') as f:
            with db_cursor() as cursor:
                cursor.execute(f.read(), multi=True)
            somasdb.commit()

def isExistsDB(id, attribute, table):
    db_cursor.execute(f'''SELECT {attribute} FROM {table} WHERE {table}.{attribute} = '{id}';''')
    value = db_cursor.fetchall()
    try:
        if value[0][0]==id:
            return True
    except:
        return False

def isExistsComposite(id1,id2,attribute1,attribute2,table):#checks if composite key tuple exists
    db_cursor.execute(f'''SELECT {attribute1}, {attribute2} FROM {table} WHERE {attribute1} = '{id1}' AND {attribute2} = '{id2}';''')
    value = db_cursor.fetchall()
    try:
        if value[0][0]==id1 and value[0][1]==id2:
            return True
    except:
        return False

def passwordCheck(email, table, password):
    password = hashlib.md5(password.encode('utf-8')).hexdigest()
    db_cursor.execute(f'''SELECT password FROM {table} WHERE email='{email}';''')
    value = db_cursor.fetchall()
    try:
        if value[0][0] == password:
            return True
    except:
        return False

def attendeeParse(alist):
    attendanceList = []
    u_type = ""
    if alist != []:
        for attendee in alist:
            if attendee[1] == None:
                u_type = "Academic"
            else:
                u_type = attendee[1]
            if len(attendee)==4:
                attendanceList.append({
                'name': attendee[0],
                'no': u_type,
                'email': attendee[2],
                'e_name': attendee[3]
                })
            else:
                attendanceList.append({
                    'name': attendee[0],
                    'no': u_type,
                    'email': attendee[2]
                })
    return attendanceList

def getSocietyInfo(app, slug):
    db_cursor.execute(f'''SELECT * FROM Society WHERE slug='{slug}';''')
    info = db_cursor.fetchall()[0]
    pattern = f"{slug}.*"
    result = ""
    for root, dirs, files in os.walk(os.path.join(app, 'static', 'logos')):
        for name in files:
            if fnmatch.fnmatch(name, pattern):
                result = os.path.join(root, name)
    refactored_result = litowin(result)
    info = {
        'email' : info[0],
        'name' : info[1],
        'logo' : refactored_result,
        'budget' : info[4],
        'description' : info[5],
        'admin-mail' : info[6],
        'advisor-mail' : info[7],
        'slug' : slug
    }
    return info

def getSocAdmAdv(slug):
    db_cursor.execute(f'''SELECT admin_mail, advisor_mail FROM Society WHERE slug='{slug}';''')
    info = db_cursor.fetchall()[0]
    info = {
        'admin-mail' : info[0],
        'advisor-mail' : info[1]
    }
    return info

def societyAuth(email, slug):
    db_cursor.execute(f'''SELECT email FROM Society WHERE slug='{slug}';''')
    info = db_cursor.fetchall()[0]
    if (email == info[0]):
        return True
    return False

def getImage(app, pattern, file):
    pattern = f"{pattern}.*"
    result = ""
    for root, dirs, files in os.walk(os.path.join(app, 'static', file)):
        for name in files:
            if fnmatch.fnmatch(name, pattern):
                result = os.path.join(root, name)
    return result

def parseEvents(events, app):
    event_list = []
    for event in events:
        result = getImage(app, f"{event[6]}-{event[4]}", 'posters')
        db_cursor.execute(f'''SELECT guest FROM Event_Guest WHERE soc_email='{event[5]}' AND e_name='{event[0]}';''')
        guests = db_cursor.fetchall()
        guest_list = []
        if guests:
            for guest in guests:
                guest_list.append(guest[0])
        refactored_result = litowin(result)
        info = {
            'event_name' : event[0],
            'date' : event[1],
            'soc_name' : event[2], 
            'description' : event[3],
            'event_slug' : event[4],
            'soc_email' : event[5],
            'soc_slug' : event[6],
            'poster' : refactored_result,
            'guests' : guest_list
        }
        event_list.append(info)
    return event_list

def getEvents(user, level, app):
    event_list = []
    if(level == 0):
        db_cursor.execute(f'''SELECT event_name, e_date, name, e.description, e.slug, soc_email, s.slug FROM Event e LEFT JOIN Society s on s.email=e.soc_email WHERE e.status = {level} AND adv_email="{user}" ORDER BY e.e_date DESC;''')
        events = db_cursor.fetchall()
        if events != []:
            event_list.extend(parseEvents(events, app))
            
    else:
        db_cursor.execute(f'''SELECT event_name, e_date, name, e.description, e.slug, soc_email, s.slug FROM Event e LEFT JOIN Society s on s.email=e.soc_email WHERE e.status = {level} ORDER BY e_date DESC;''')
        events = db_cursor.fetchall()
        if events != []:
            event_list.extend(parseEvents(events, app))

    return event_list

