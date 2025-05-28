from sqlite3 import *

connection = connect('db/dushess.db')
cursor = connection.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS Users (
id INTEGER PRIMARY KEY AUTOINCREMENT,
login TEXT NOT NULL);
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS Admins (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    login TEXT NOT NULL,
    password TEXT NOT NULL
);
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS BanUsers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    login TEXT NOT NULL
);
''')
connection.close()
def Add_to_db(*args):
    connection = connect('db/dushess.db')
    cursor = connection.cursor()
    cursor.execute("SELECT COUNT(*) FROM Users")
    if args[0] == 'Users':
        cursor.execute('INSERT INTO Users (login) VALUES (?)', (args[1],))
    elif args[0] == 'Admins':
        cursor.execute('INSERT INTO Admins (login, password) VALUES (?, ?)', (args[1], args[2]))
    elif args[0] == 'BanUsers':
        cursor.execute('INSERT INTO BanUsers (login) VALUES (?)', (args[1],))
    connection.commit()
    connection.close()