import mysql.connector
from connect import dbuser, dbpass, dbhost, dbport, dbname
connection = None

def getCursor():
    global connection
    if connection is None:
        connection = mysql.connector.connect(
            user=dbuser,
            password=dbpass,
            host=dbhost,
            port=dbport,
            database=dbname,
            auth_plugin='',
            autocommit=True
        )
    cursor = connection.cursor()
    return cursor

