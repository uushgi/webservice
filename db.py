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

cursor.execute('''
CREATE TABLE IF NOT EXISTS VenueLikes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    venue_id INTEGER NOT NULL,
    UNIQUE(user_id, venue_id),
    FOREIGN KEY (user_id) REFERENCES Users (id),
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

def get_user_bookings_split(user_id):
    connection = connect('db/dushess.db')
    cursor = connection.cursor()
    cursor.execute('''
        SELECT Booking.id, Venue.name, Booking.datetime, Booking.time_start, Booking.time_end, Booking.datetime_of_booking
        FROM Booking
        JOIN Venue ON Booking.venue_id = Venue.id
        WHERE Booking.user_id = ?
    ''', (user_id,))
    bookings = cursor.fetchall()
    connection.close()

    now = datetime.now()
    active = []
    history = []
    for b in bookings:
        b_date = b[2]
        b_end = b[4]
        dt = datetime.strptime(b_date + ' ' + b_end, '%Y-%m-%d %H:%M')
        if dt >= now:
            active.append(b)
        else:
            history.append(b)
    return active, history

def get_booked_slots_db(venue_id, date):
    connection = connect('db/dushess.db')
    cursor = connection.cursor()
    cursor.execute('SELECT time_start, time_end FROM Booking WHERE venue_id = ? AND datetime = ?', (venue_id, date))
    rows = cursor.fetchall()
    connection.close()

    booked_slots = set()
    for time_start, time_end in rows:
        h1, m1 = map(int, time_start.split(':'))
        h2, m2 = map(int, time_end.split(':'))
        t1 = h1 * 60 + m1
        t2 = h2 * 60 + m2

        t = t1
        while t <= t2:
            booked_slots.add(f'{t//60:02d}:{t%60:02d}')
            t += 30
    return sorted(booked_slots)

def get_venues_with_likes(user_email=None):
    connection = connect('db/dushess.db')
    cursor = connection.cursor()
    cursor.execute('''
        SELECT Venue.id, Venue.name, Venue.likes, Photo.path
        FROM Venue
        LEFT JOIN Photo ON Venue.id = Photo.venue_id
    ''')
    venues = cursor.fetchall()
    user_likes = set()
    if user_email:
        cursor.execute('SELECT id FROM Users WHERE login = ?', (user_email,))
        user = cursor.fetchone()
        if user:
            user_id = user[0]
            cursor.execute('SELECT venue_id FROM VenueLikes WHERE user_id = ?', (user_id,))
            user_likes = set(row[0] for row in cursor.fetchall())
    result = []
    for v in venues:
        result.append({
            'id': v[0],
            'name': v[1],
            'likes': v[2],
            'image': v[3] or '',
            'liked': v[0] in user_likes
        })
    connection.close()
    return result
