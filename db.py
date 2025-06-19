from sqlite3 import *
from datetime import *

connection = connect('db/dushess.db')
cursor = connection.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS Users (
id INTEGER PRIMARY KEY AUTOINCREMENT,
login TEXT UNIQUE NOT NULL,
is_active INTEGER DEFAULT 1,
is_can_Book INTEGER DEFAULT 1,
is_admin INTEGER DEFAULT 0
);
''')


cursor.execute('''
CREATE TABLE IF NOT EXISTS Booking (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    venue_id INTEGER,
    user_id INTEGER,
    datetime TEXT NOT NULL,
    time_start TEXT NOT NULL,
    time_end TEXT NOT NULL,
    datetime_of_booking TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES Users (id)
    FOREIGN KEY (venue_id) REFERENCES Venue (id)
);
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS FAQ (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    question TEXT NOT NULL,
    answer TEXT NOT NULL
);
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS News (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    datetime TEXT NOT NULL,
    title TEXT NOT NULL,
    content TEXT NOT NULL
);
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS Venue (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT NOT NULL,
    likes INTEGER DEFAULT 0,
    template_name TEXT NOT NULL
);
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS Photo (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    path TEXT NOT NULL,
    name TEXT,
    venue_id INTEGER,
    FOREIGN KEY (venue_id) REFERENCES Venue (id)
);
''')




def Add_element_db(tableName, *columnNames, **values):
    connection = connect('db/dushess.db')
    cursor = connection.cursor()

    countOfArg = ', '.join(['?'] * (len(values)))
    columnsStr = ', '.join(columnNames)
    print(list(values.values()))

    cursor.execute(f'INSERT INTO {tableName} ({columnsStr}) VALUES ({countOfArg})', list(values.values()))
    connection.commit()
    connection.close()

def Delete_element_db(tableName, deleteID):
    connection = connect('db/dushess.db')
    cursor = connection.cursor()

    cursor.execute(f'DELETE FROM {tableName} WHERE id = ?', (deleteID,))

    connection.commit()
    connection.close()

def Update_element_db(tableName, columnSetType, indexColumn, replaceableElement, indexElement):
    connection = connect('db/dushess.db')
    cursor = connection.cursor()

    cursor.execute(f'UPDATE {tableName} SET {columnSetType} = ? WHERE {indexColumn} = ?', (replaceableElement, indexElement))

    connection.commit()
    connection.close()

def Take_out_element_db(tableName, columnType, indexColumn, indexElement):
    connection = connect('db/dushess.db')
    cursor = connection.cursor()

    cursor.execute(f'SELECT {columnType} FROM {tableName} WHERE {indexColumn} = ?', (indexElement,))

    connection.commit()
    connection.close()
    return cursor.fetchone()


def Take_out_column_db(tableName, columnType):
    connection = connect('db/dushess.db')
    cursor = connection.cursor()

    cursor.execute(f'SELECT {columnType} FROM {tableName}')

    connection.commit()
    connection.close()
    return cursor.fetchall()



def Get_user_bookings(user_id):
    connection = connect('db/dushess.db')
    cursor = connection.cursor()

    cursor.execute(f'SELECT id AND venue_id AND datetime AND time_start AND time_end AND datetime_of_booking FROM Booking WHERE user_id = ?', (user_id,))

    connection.commit()
    connection.close()
    return cursor.fetchall()
