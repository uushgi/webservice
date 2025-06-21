from flask import *
from db import *
import requests
from sqlite3 import connect
from datetime import datetime, timedelta

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


def get_news():
    connection = connect('db/dushess.db')
    cursor = connection.cursor()
    cursor.execute('SELECT datetime, title, content FROM News ORDER BY datetime DESC')
    news = cursor.fetchall()
    connection.close()
    return [{'date': n[0], 'title': n[1], 'text': n[2]} for n in news]

def get_faq():
    connection = connect('db/dushess.db')
    cursor = connection.cursor()
    cursor.execute('SELECT question, answer FROM FAQ ORDER BY id ASC')
    faq = cursor.fetchall()
    connection.close()
    return [{'question': q[0], 'answer': q[1]} for q in faq]

@app.route('/', methods=["POST", "GET"])
def index():
    auth_status = session.get('authenticated', False)
    user_data = session.get('user_data', None)
    auth_success = request.args.get('auth_success', False)
    error_message = session.pop('error_message', None)

    # venues теперь из базы
    venues = get_venues_with_likes(user_data['email'] if user_data else None)

    news = get_news()
    faq = get_faq()

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

        active_bookings, _ = get_user_bookings_split(user_email)
        if len(active_bookings) >= 2:
            session['error_message'] = 'Нельзя иметь больше двух активных бронирований одновременно'
            return redirect(url_for('index'))

        connection = connect('db/dushess.db')
        cursor = connection.cursor()

        times_sorted = sorted(times)
        time_start = times_sorted[0]
        # Прибавляем 30 минут к последнему времени
        last_time = datetime.strptime(times_sorted[-1], '%H:%M')
        time_end = (last_time + timedelta(minutes=30)).strftime('%H:%M')

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
                           news=news,
                           faq=faq)

@app.route("/about")
def about():
    return render_template("about.html")

def get_venue_by_template(template_name):
    connection = connect('db/dushess.db')
    cursor = connection.cursor()
    cursor.execute('''
        SELECT Venue.name, Venue.description, Venue.info, Photo.path
        FROM Venue
        LEFT JOIN Photo ON Venue.id = Photo.venue_id
        WHERE Venue.template_name = ?
    ''', (template_name,))
    row = cursor.fetchone()
    connection.close()
    if row:
        return {'name': row[0], 'description': row[1], 'info': row[2], 'image': row[3]}
    return None

@app.route("/dushes")
def dushes():
    venue = get_venue_by_template('dushes.html')
    return render_template("dushes.html", venue=venue)

@app.route("/sticker")
def sticker():
    venue = get_venue_by_template('sticker.html')
    return render_template("sticker.html", venue=venue)

@app.route("/euphoria")
def euphoria():
    venue = get_venue_by_template('euphoria.html')
    return render_template("euphoria.html", venue=venue)

@app.route("/inspo")
def inspo():
    venue = get_venue_by_template('inspo.html')
    return render_template("inspo.html", venue=venue)

@app.route("/profile", methods=["GET", "POST"])
def profile():
    user_data = session.get('user_data')
    if not user_data:
        return redirect(url_for('index'))
    email = user_data['email']

    from db import get_user_bookings_split, Delete_element_db

    if request.method == 'POST' and 'cancel_booking' in request.form:
        booking_id = request.form.get('booking_id')
        if booking_id:
            Delete_element_db('Booking', booking_id)
            return redirect(url_for('profile'))

    active_bookings, history_bookings = get_user_bookings_split(email)
    return render_template("profile.html", active_bookings=active_bookings, history_bookings=history_bookings)

@app.route("/catalogue")
def catalogue():
    return render_template("catalogue.html")

@app.route("/contacts")
def contacts():
    return render_template("contacts.html")

@app.route("/adminpanel")
def adminpanel():
    return render_template("adminpanel.html")

@app.route('/adminpanel/active-bookings')
def admin_active_bookings():
    return render_template('admin_active_bookings.html')

@app.route('/adminpanel/cancel-booking')
def admin_cancel_booking():
    return render_template('admin_cancel_booking.html')

@app.route('/adminpanel/booking-history')
def admin_booking_history():
    return render_template('admin_booking_history.html')

@app.route('/adminpanel/manual-booking')
def admin_manual_booking():
    return render_template('admin_manual_booking.html')

@app.route('/adminpanel/edit-photo')
def admin_edit_photo():
    return render_template('admin_edit_photo.html')

@app.route('/adminpanel/edit-text')
def admin_edit_text():
    return render_template('admin_edit_text.html')

@app.route('/adminpanel/ban-user')
def admin_ban_user():
    return render_template('admin_ban_user.html')

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

    cursor.execute('''
        SELECT Booking.id, Venue.name, Booking.datetime, Booking.time_start, Booking.time_end, Booking.datetime_of_booking
        FROM Booking
        JOIN Venue ON Booking.venue_id = Venue.id
        WHERE Booking.user_id = ?
    ''', (user_id,))
    result = cursor.fetchall()
    connection.close()
    return result

@app.route('/like-venue', methods=['POST'])
def like_venue():
    if not session.get('authenticated'):
        return jsonify({'success': False, 'error': 'not_authenticated'}), 401
    user_data = session.get('user_data')
    if not user_data:
        return jsonify({'success': False, 'error': 'no_user'}), 401
    user_email = user_data['email']
    venue_id = request.json.get('venue_id')
    if not venue_id:
        return jsonify({'success': False, 'error': 'no_venue_id'}), 400
    connection = connect('db/dushess.db')
    cursor = connection.cursor()
    cursor.execute('SELECT id FROM Users WHERE login = ?', (user_email,))
    user = cursor.fetchone()
    if not user:
        connection.close()
        return jsonify({'success': False, 'error': 'user_not_found'}), 404
    user_id = user[0]
    # проверка
    cursor.execute('SELECT 1 FROM VenueLikes WHERE user_id = ? AND venue_id = ?', (user_id, venue_id))
    already_liked = cursor.fetchone()
    try:
        if already_liked:
            # убрать лайк
            cursor.execute('DELETE FROM VenueLikes WHERE user_id = ? AND venue_id = ?', (user_id, venue_id))
            cursor.execute('UPDATE Venue SET likes = likes - 1 WHERE id = ? AND likes > 0', (venue_id,))
            connection.commit()
            cursor.execute('SELECT likes FROM Venue WHERE id = ?', (venue_id,))
            likes = cursor.fetchone()[0]
            connection.close()
            return jsonify({'success': True, 'likes': likes, 'liked': False})
        else:
            # добавить лайк
            cursor.execute('INSERT INTO VenueLikes (user_id, venue_id) VALUES (?, ?)', (user_id, venue_id))
            cursor.execute('UPDATE Venue SET likes = likes + 1 WHERE id = ?', (venue_id,))
            connection.commit()
            cursor.execute('SELECT likes FROM Venue WHERE id = ?', (venue_id,))
            likes = cursor.fetchone()[0]
            connection.close()
            return jsonify({'success': True, 'likes': likes, 'liked': True})
    except Exception as e:
        connection.close()
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)