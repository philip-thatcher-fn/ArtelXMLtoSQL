import mysql.connector

db = mysql.connector.connect(
  host="localhost",
  user="python_user",
  passwd="*f39SEXJlUG1"
)

# print(db)

cursor = db.cursor()

# cursor.execute('CREATE DATABASE ARTEL_DATA')

cursor.execute('SHOW DATABASES')

for x in cursor:
    print(x)