from sqlite3 import *


connection = connect('db/dushess.db')
cursor = connection.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS Users (
id INTEGER PRIMARY KEY,
login TEXT NOT NULL);
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS Admins (
    id INTEGER PRIMARY KEY,
    login TEXT NOT NULL,
    password TEXT NOT NULL
);
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS BanUsers (
    id INTEGER PRIMARY KEY,
    login TEXT NOT NULL
);
''')
def Add_to_db(nameDB, firstArguement, secondArguement, thirdArgument):
    if nameDB == 'Users':
        cursor.execute('INSERT INTO Users (id, login) VALUES (?, ?)', (firstArguement, secondArguement))


connection.commit()
connection.close()
