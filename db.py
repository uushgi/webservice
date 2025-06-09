from sqlite3 import *
from datetime import *

connection = connect('db/dushess.db')
cursor = connection.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS Users (
id INTEGER PRIMARY KEY AUTOINCREMENT,
login TEXT UNIQUE NOT NULL);
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS Admins (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    login TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
);
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS BanUsers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    login TEXT UNIQUE NOT NULL
);
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS DushesTime (
    day TEXT NOT NULL,
    time_10_00 INTEGER,
    time_10_30 INTEGER,
    time_11_00 INTEGER,
    time_11_30 INTEGER,
    time_12_00 INTEGER,
    time_12_30 INTEGER,
    time_13_00 INTEGER,
    time_13_30 INTEGER,
    time_14_00 INTEGER,
    time_14_30 INTEGER,
    time_15_00 INTEGER,
    time_15_30 INTEGER,
    time_16_00 INTEGER,
    time_16_30 INTEGER,
    time_17_00 INTEGER,
    time_17_30 INTEGER,
    time_18_00 INTEGER,
    time_18_30 INTEGER,
    time_19_00 INTEGER,
    time_19_30 INTEGER,
    time_20_00 INTEGER,
    time_20_30 INTEGER,
    time_21_00 INTEGER,
    time_21_30 INTEGER,
    time_22_00 INTEGER
);
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS EuphoriaTime (
    day TEXT NOT NULL,
    time_10_00 INTEGER,
    time_10_30 INTEGER,
    time_11_00 INTEGER,
    time_11_30 INTEGER,
    time_12_00 INTEGER,
    time_12_30 INTEGER,
    time_13_00 INTEGER,
    time_13_30 INTEGER,
    time_14_00 INTEGER,
    time_14_30 INTEGER,
    time_15_00 INTEGER,
    time_15_30 INTEGER,
    time_16_00 INTEGER,
    time_16_30 INTEGER,
    time_17_00 INTEGER,
    time_17_30 INTEGER,
    time_18_00 INTEGER,
    time_18_30 INTEGER,
    time_19_00 INTEGER,
    time_19_30 INTEGER,
    time_20_00 INTEGER,
    time_20_30 INTEGER,
    time_21_00 INTEGER,
    time_21_30 INTEGER,
    time_22_00 INTEGER
);
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS InSpoTime (
    day TEXT NOT NULL,
    time_10_00 INTEGER,
    time_10_30 INTEGER,
    time_11_00 INTEGER,
    time_11_30 INTEGER,
    time_12_00 INTEGER,
    time_12_30 INTEGER,
    time_13_00 INTEGER,
    time_13_30 INTEGER,
    time_14_00 INTEGER,
    time_14_30 INTEGER,
    time_15_00 INTEGER,
    time_15_30 INTEGER,
    time_16_00 INTEGER,
    time_16_30 INTEGER,
    time_17_00 INTEGER,
    time_17_30 INTEGER,
    time_18_00 INTEGER,
    time_18_30 INTEGER,
    time_19_00 INTEGER,
    time_19_30 INTEGER,
    time_20_00 INTEGER,
    time_20_30 INTEGER,
    time_21_00 INTEGER,
    time_21_30 INTEGER,
    time_22_00 INTEGER
);
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS StickerTime (
    day TEXT NOT NULL,
    time_10_00 INTEGER,
    time_10_30 INTEGER,
    time_11_00 INTEGER,
    time_11_30 INTEGER,
    time_12_00 INTEGER,
    time_12_30 INTEGER,
    time_13_00 INTEGER,
    time_13_30 INTEGER,
    time_14_00 INTEGER,
    time_14_30 INTEGER,
    time_15_00 INTEGER,
    time_15_30 INTEGER,
    time_16_00 INTEGER,
    time_16_30 INTEGER,
    time_17_00 INTEGER,
    time_17_30 INTEGER,
    time_18_00 INTEGER,
    time_18_30 INTEGER,
    time_19_00 INTEGER,
    time_19_30 INTEGER,
    time_20_00 INTEGER,
    time_20_30 INTEGER,
    time_21_00 INTEGER,
    time_21_30 INTEGER,
    time_22_00 INTEGER
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
    return cursor.fetchone()

    connection.commit()
    connection.close()

def Take_out_column_db(tableName, columnType):
    connection = connect('db/dushess.db')
    cursor = connection.cursor()

    cursor.execute(f'SELECT {columnType} FROM {tableName}')
    return cursor.fetchall()

    connection.commit()
    connection.close()


def Create_TimeBook_db(tableName):
    try:
        if Take_out_column_db(tableName, 'day')[0]:
            None
    except:
        current_date = datetime.strptime('2025-01-01', '%Y-%m-%d')

        for i in range(365):
            formatted_date = current_date.strftime('%Y-%m-%d')
            Add_element_db(tableName, 'day', day=formatted_date)
            current_date += timedelta(days=1)


def Get_user_bookings(tableName, user_login):
    connection = connect('db/dushess.db')
    cursor = connection.cursor()

    # Получаем все дни, где у пользователя есть бронирования
    cursor.execute(f'''
    SELECT day, 
           time_10_00, time_10_30, time_11_00, time_11_30,
           time_12_00, time_12_30, time_13_00, time_13_30,
           time_14_00, time_14_30, time_15_00, time_15_30,
           time_16_00, time_16_30, time_17_00, time_17_30,
           time_18_00, time_18_30, time_19_00, time_19_30,
           time_20_00, time_20_30, time_21_00, time_21_30,
           time_22_00
    FROM {tableName}
    WHERE time_10_00 = ? OR time_10_30 = ? OR time_11_00 = ? OR time_11_30 = ? OR
          time_12_00 = ? OR time_12_30 = ? OR time_13_00 = ? OR time_13_30 = ? OR
          time_14_00 = ? OR time_14_30 = ? OR time_15_00 = ? OR time_15_30 = ? OR
          time_16_00 = ? OR time_16_30 = ? OR time_17_00 = ? OR time_17_30 = ? OR
          time_18_00 = ? OR time_18_30 = ? OR time_19_00 = ? OR time_19_30 = ? OR
          time_20_00 = ? OR time_20_30 = ? OR time_21_00 = ? OR time_21_30 = ? OR
          time_22_00 = ?
    ''', (user_login,) * 25)

    bookings = []
    for row in cursor.fetchall():
        day = row[0]
        for i in range(1, 25):
            if row[i] == user_login:
                time_slot = f"time_{10 + (i - 1) // 2}:{(i - 1) % 2 * 30:02d}"
                bookings.append({'day': day, 'time': time_slot, 'room': tableName})

    connection.close()
    return bookings