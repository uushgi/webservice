from flask import *
from db import *
import requests

app = Flask(__name__)
app.secret_key = '324235515436'

CLIENT_ID = '4004acc77b2b4dbba0c4fa8208583ac6'
CLIENT_SECRET = '2abc3be40fec4ccbba24572a9235260e'


@app.route('/get-booked-slots', methods=['GET'])
def get_booked_slots():
    venue = request.args.get('venue')
    date = request.args.get('date')

    if not venue or not date:
        return jsonify({'error': 'Missing venue or date'}), 400

    venue_to_table = {
        'Дюшес': 'DushesTime',
        'Sticker': 'StickerTime',
        'Euphoria': 'EuphoriaTime',
        'InSpo': 'InSpoTime'
    }

    table_name = venue_to_table.get(venue)

    row = Take_out_element_db(table_name, '*', 'day', date)
    if not row:
        return jsonify({'booked_slots': []})

    booked_slots = []
    for i in range(1, len(row), 2):  # временная штука, пока у нас бронь по часу. по 2 шагает и проверяет оба
        if row[i] is not None and row[i + 1] is not None:
            hour = 10 + ((i - 1) // 2)
            booked_slots.append(f"{hour:02d}:00")

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
        time = request.form.get('time')

        if not all([venue, date, time]):
            session['error_message'] = 'Пожалуйста, выберите дату и время'
            return redirect(url_for('index'))

        venue_to_table = {
            'Дюшес': 'DushesTime',
            'Sticker': 'StickerTime',
            'Euphoria': 'EuphoriaTime',
            'InSpo': 'InSpoTime'
        }

        table_name = venue_to_table.get(venue)

        hour = time.split(':')[0]  # берем только часы пока что
        time_column_1 = f"time_{hour}_00"
        time_column_2 = f"time_{hour}_30"

        row = Take_out_element_db(table_name, f"{time_column_1}, {time_column_2}", 'day', date)
        if row and (row[0] is not None or row[1] is not None):
            session['error_message'] = 'Это время уже забронировано'
            return redirect(url_for('index'))

        Update_element_db(table_name, time_column_1, 'day', user_data['email'], date)
        Update_element_db(table_name, time_column_2, 'day', user_data['email'], date)

        print(f"бронь: {user_data['email']} | {venue} | {date} | {time}")

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
    tableName = 'DushesTime'
    email = 'max loh'
    Get_user_bookings(tableName, email)
    return render_template("profile_html")



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
        print(f"Логин: {user_data.get('login')}")
        print(f"Email: {user_data.get('default_email')}")

        session['authenticated'] = True
        session['user_data'] = {
            'id': user_data.get('id'),
            'login': user_data.get('login'),
            'email': user_data.get('default_email')
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

if __name__ == '__main__':
    Create_TimeBook_db('DushesTime')
    Create_TimeBook_db('StickerTime')
    Create_TimeBook_db('InSpoTime')
    Create_TimeBook_db('EuphoriaTime')
    app.run(debug=True)