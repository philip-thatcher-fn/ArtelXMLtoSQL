import mysql.connector

# db = mysql.connector.connect(host='localhost',
#                              user='python_user',
#                              passwd='*f39SEXJlUG1'
#                              )


db = mysql.connector.connect(host='localhost',
                             user='python_user',
                             passwd='*f39SEXJlUG1',
                             database='artel_data'
                             )

# print(db)

# cursor.execute('CREATE DATABASE test_data')
# cursor.execute('SHOW DATABASES')

# cursor.execute('CREATE TABLE customers (name VARCHAR(255), address VARCHAR(255))')
# cursor.execute('SHOW TABLES')
#
# for x in cursor:
#     print(x)
#
# cursor.execute('ALTER TABLE customers ADD COLUMN id INT AUTO_INCREMENT PRIMARY KEY')
#
# db.commit()

# sql = 'INSERT INTO customers (name, address) VALUES (%s, %s)'
# val = ('Mary', 'Chicago')
# cursor.execute(sql, val)

# sql = 'INSERT INTO customers (name, address) VALUES (%s, %s)'
# val = [
#   ('Peter', 'Lowstreet 4'),
#   ('Amy', 'Apple st 652'),
#   ('Hannah', 'Mountain 21'),
#   ('Michael', 'Valley 345'),
#   ('Sandy', 'Ocean blvd 2'),
#   ('Betty', 'Green Grass 1'),
#   ('Richard', 'Sky st 331'),
#   ('Susan', 'One way 98'),
#   ('Vicky', 'Yellow Garden 2'),
#   ('Ben', 'Park Lane 38'),
#   ('William', 'Central st 954'),
#   ('Chuck', 'Main Road 989'),
#   ('Viola', 'Sideway 1633')
# ]
#
# cursor.executemany(sql, val)
#
# db.commit()
#
# print(cursor.rowcount, 'Record(s) inserted.')

# cursor.execute('SELECT * FROM customers')

# cursor.execute('SELECT name, address FROM customers')

# cursor.execute("SELECT * FROM customers WHERE address LIKE '%way%'")
#
# result = cursor.fetchall()
#
# for x in result:
#   print(x)

# cursor = db.cursor()
cursor.execute('CREATE TABLE test_well_data (id INT AUTO_INCREMENT PRIMARY KEY, Group1_Row VARCHAR(255), Group1_Col VARCHAR(255), Group1_Vol VARCHAR(255))')