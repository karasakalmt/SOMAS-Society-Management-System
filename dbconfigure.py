import mysql.connector
import json

def dbJSON_create(host, user, password, db):
    jsonData = {
        "host": host,
        "user": user,
        "password": password,
        "db": db
    }
    with open('dbconfig.json', 'w') as outfile:
        json.dump(jsonData, outfile, indent=4)

def configDB():
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
    db_cursor.execute('SHOW TABLES;')
    tables = db_cursor.fetchall()
    all_tables=[]
    for table in tables:
        all_tables+=table
    print(all_tables)
    if(all_tables==['Administrator', 'Advised', 'Advisor', 'Attendee', 'Event', 'Event_Guest', 'Payment', 'Society', 'SocietyMembers', 'Student', 'User']):
        return False
    with open('etc/somasdb.sql', 'r') as f:
        db_cursor.execute(f.read(), multi=True)
    return True

if __name__ == '__main__':
    host = input("Host: ")
    user = input("User: ")
    password = input("Password: ")
    db = input("Database: ")
    dbJSON_create(host, user, password, db)
    flag = configDB()
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
    if(flag):
        print("Database configured successfully")
    else:
        print("Database already configured")

    admin = input("Create an admin account [y/n]: ")
    if(admin == 'y'):
        admin_name = input("Admin name: ")
        admin_email = input("Admin Email: ")
        admin_pass = input("Admin Password: ")
        db_cursor.execute(f'''INSERT INTO Administrator VALUES ('{admin_email}',"{admin_name}",MD5("{admin_pass}"));''')
    else:
        pass
