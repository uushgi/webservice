from flask import *
from db import *
import requests
from sqlite3 import connect

app = Flask(__name__)
app.secret_key = '324235515436'

CLIENT_ID = '4004acc77b2b4dbba0c4fa8208583ac6'
CLIENT_SECRET = '2abc3be40fec4ccbba24572a9235260e'


@app.route('/get-booked-slots', methods=['GET'])
def get_booked_slots():
    venue = request.args.get('venue')
    date = request.args.get('date')
    booked_slots = get_booked_slots_db(venue, date)
    return jsonify({'booked_slots': booked_slots})



@app.route('/', methods=["POST", "GET"])
def index():
    auth_status = session.get('authenticated', False)
    user_data = session.get('user_data', None)
    auth_success = request.args.get('auth_success', False)
    error_message = session.pop('error_message', None)

    # данные для джинджи
    venues = [
        {'id': 'Дюшес', 'name': 'Дюшес', 'likes': 42, 'image': 'venue1.png'},
        {'id': 'Sticker', 'name': 'Sticker', 'likes': 38, 'image': 'venue2.png'},
        {'id': 'Euphoria', 'name': 'Euphoria', 'likes': 35, 'image': 'venue3.png'},
        {'id': 'InSpo', 'name': 'InSpo', 'likes': 29, 'image': 'venue4.png'}
    ]

    news = [
        {'date': '6.6.2025', 'title': 'Lorem ipsum',
         'text': 'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt'},
        {'date': '5.6.2025', 'title': 'Lorem ipsum',
         'text': 'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt'},
        {'date': '4.6.2025', 'title': 'Lorem ipsum',
         'text': 'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt'}
    ]

    if request.method == 'POST' and 'calendar_book' in request.form:
        if not auth_status:
            session['error_message'] = 'Пожалуйста, войдите в систему'
            return redirect(url_for('index'))

        venue = request.form.get('venue')
        date = request.form.get('date')
        times = request.form.getlist('times[]')

        if not all([venue, date, times]) or len(times) == 0:
            session['error_message'] = 'Пожалуйста, выберите дату и время'
            return redirect(url_for('index'))

        user_email = user_data['email']
        connection = connect('db/dushess.db')
        cursor = connection.cursor()

        times_sorted = sorted(times)
        time_start = times_sorted[0]
        time_end = times_sorted[-1]

        cursor.execute('SELECT time_start, time_end FROM Booking WHERE venue_id = ? AND datetime = ?', (venue, date))
        rows = cursor.fetchall()
        for b_start, b_end in rows:
            if not (b_end < time_start or b_start > time_end):
                connection.close()
                return redirect(url_for('index'))

        cursor.execute('''
            INSERT INTO Booking (venue_id, user_id, datetime, time_start, time_end, datetime_of_booking)
            VALUES (?, ?, ?, ?, ?, datetime("now"))
        ''', (venue, user_email, date, time_start, time_end))
        connection.commit()
        connection.close()
        print(f"бронь: {user_email} | {venue} | {date} | {time_start}-{time_end}")
        session['booking_success'] = True
        return redirect(url_for('index'))

    return render_template('index.html',
                           auth_status=auth_status,
                           user_data=user_data,
                           auth_success=auth_success,
                           booking_success=session.pop('booking_success', False),
                           error_message=error_message,
                           CLIENT_ID=CLIENT_ID,
                           venues=venues,
                           news=news)

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/dushes")
def dushes():
    return render_template("dushes.html")

@app.route("/sticker")
def sticker():
    return render_template("sticker.html")

@app.route("/euphoria")
def euphoria():
    return render_template("euphoria.html")

@app.route("/inspo")
def inspo():
    return render_template("inspo.html")

@app.route("/profile")
def profile():
    email = 'max loh'
    Get_user_bookings(email)
    return render_template("profile.html")

@app.route("/catalogue")
def catalogue():
    return render_template("catalogue.html")

@app.route("/contacts")
def contacts():
    return render_template("contacts.html")

@app.route("/adminpanel")
def adminpanel():
    return render_template("adminpanel.html")

@app.route('/yandex-auth')
def yandex_auth():
    code = request.args.get('code')

    if not code:
        return redirect('/')

    try:
        token_url = 'https://oauth.yandex.ru/token'
        data = {
            'grant_type': 'authorization_code',
            'code': code,
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET
        }

        response = requests.post(token_url, data=data)
        response.raise_for_status()

        access_token = response.json().get('access_token')
        if not access_token:
            return redirect('/')

        user_url = 'https://login.yandex.ru/info'
        headers = {'Authorization': f'OAuth {access_token}'}
        user_response = requests.get(user_url, headers=headers)
        user_response.raise_for_status()

        user_data = user_response.json()
        print("\n--- Данные пользователя ---")
        print(f"ID: {user_data.get('id')}")
        print(f"Email: {user_data.get('default_email')}")

        email = user_data.get('default_email')
        if not email:
            return redirect('/')

        connection = connect('db/dushess.db')
        cursor = connection.cursor()
        cursor.execute('SELECT id FROM Users WHERE login = ?', (email,))
        exists = cursor.fetchone()
        if not exists:
            cursor.execute('INSERT INTO Users (login) VALUES (?)', (email,))
            connection.commit()
        connection.close()

        session['authenticated'] = True
        session['user_data'] = {
            'email': email
        }

        return redirect(url_for('index', auth_success=True))

    except Exception as e:
        print(f"Ошибка: {str(e)}")
        return redirect('/')


@app.route('/logout')
def logout():
    session.pop('authenticated', None)
    session.pop('user_data', None)
    return redirect(url_for('index'))

@app.context_processor
def inject_globals():
    return {
        'CLIENT_ID': CLIENT_ID,
        'auth_status': session.get('authenticated', False),
        'user_data': session.get('user_data', None),
        'auth_success': session.get('auth_success', False)
    }

def Get_user_bookings(user_id):
    connection = connect('db/dushess.db')
    cursor = connection.cursor()

    cursor.execute('SELECT id, venue_id, datetime, time_start, time_end, datetime_of_booking FROM Booking WHERE user_id = ?', (user_id,))
    result = cursor.fetchall()
    connection.close()
    return result

if __name__ == '__main__':
    app.run(debug=True)