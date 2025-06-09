from flask import *
from db import *
import requests

app = Flask(__name__)
app.secret_key = '1221212121'

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
    if not table_name:
        return jsonify({'error': 'Invalid venue'}), 400
    
    try:
        connection = connect('db/dushess.db')
        cursor = connection.cursor()
        
        cursor.execute(f'''
            SELECT time_10_00, time_10_30, time_11_00, time_11_30,
                   time_12_00, time_12_30, time_13_00, time_13_30,
                   time_14_00, time_14_30, time_15_00, time_15_30,
                   time_16_00, time_16_30, time_17_00, time_17_30,
                   time_18_00, time_18_30, time_19_00, time_19_30,
                   time_20_00, time_20_30, time_21_00, time_21_30,
                   time_22_00
            FROM {table_name}
            WHERE day = ?
        ''', (date,))
        
        row = cursor.fetchone()
        if not row:
            return jsonify({'booked_slots': []})
            
        booked_slots = []
        for i in range(0, len(row), 2):  # временная штука, пока у нас бронь по часу. по 2 шагает и проверяет оба
            if row[i] is not None and row[i+1] is not None: 
                hour = 10 + (i // 2)
                booked_slots.append(f"{hour:02d}:00")
                
        connection.close()
        return jsonify({'booked_slots': booked_slots})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

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
        {'date': '6.6.2025', 'title': 'Lorem ipsum', 'text': 'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt'},
        {'date': '5.6.2025', 'title': 'Lorem ipsum', 'text': 'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt'},
        {'date': '4.6.2025', 'title': 'Lorem ipsum', 'text': 'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt'}
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
        
        connection = connect('db/dushess.db')
        cursor = connection.cursor()
            
        formatted_date = date.replace('-', '-')
            
        cursor.execute(f'''
            SELECT {time_column_1}, {time_column_2}
            FROM {table_name}
            WHERE day = ?
            ''', (formatted_date,))
            
        result = cursor.fetchone()
        if result and (result[0] is not None or result[1] is not None):
            session['error_message'] = 'Это время уже забронировано'
            return redirect(url_for('index'))
            
        cursor.execute(f'''
            UPDATE {table_name}
            SET {time_column_1} = ?, {time_column_2} = ?
            WHERE day = ?
            ''', (user_data['email'], user_data['email'], formatted_date))
            
        connection.commit()
        connection.close()
            
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