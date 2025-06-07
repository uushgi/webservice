from flask import *
from db import *
import requests

date = '579'

app = Flask(__name__)
app.secret_key = '1221212121'  # Важно: замените на реальный секретный ключ!

CLIENT_ID = '4004acc77b2b4dbba0c4fa8208583ac6'
CLIENT_SECRET = '2abc3be40fec4ccbba24572a9235260e'


@app.route('/', methods=["POST", "GET"])
def index():

    # Проверяем статус авторизации
    auth_status = session.get('authenticated', False)
    user_data = session.get('user_data', None)

    # Проверяем параметр успешной авторизации из URL
    auth_success = request.args.get('auth_success', False)

    if True == 0:
        nameOfForm = ''
        #if request.form[nameOfForm] == "POST":
        startTime = 'time_13_00'
        endTime = 'time_14_30'
        email = 'max lox'
        flag = False

        while True:
            Update_element_db('TimeBook', startTime, 'day', email, date)
            if startTime[8:] == '30':
                startTime = startTime.replace(startTime[5:7], str(int(startTime[5:7]) + 1))
                startTime = startTime.replace(startTime[8:], '00')
            else:
                startTime = startTime.replace(startTime[8:], '30')

            if flag == True:
                break

            if startTime == endTime:
                flag = True

        return render_template("index.html")


    elif 'fff' in request.form:
        print(22)
        return redirect(url_for('about'))

    return render_template('index.html',
                           auth_status=auth_status,
                           user_data=user_data,
                           auth_success=auth_success,
                           CLIENT_ID=CLIENT_ID)

@app.route("/about")
def about():
    if 1 == 1:
        return render_template("about.html")


@app.route("/profile")
def profile():
    if 1 == 1:
        return render_template("profile_html")



@app.route('/yandex-auth')
def yandex_auth():
    # Получаем код от Яндекс OAuth
    code = request.args.get('code')

    if not code:
        return redirect('/')

    try:
        # 1. Получаем OAuth-токен
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

        # 2. Получаем данные пользователя
        user_url = 'https://login.yandex.ru/info'
        headers = {'Authorization': f'OAuth {access_token}'}
        user_response = requests.get(user_url, headers=headers)
        user_response.raise_for_status()

        user_data = user_response.json()
        print("\n--- Данные пользователя ---")
        print(f"ID: {user_data.get('id')}")
        print(f"Логин: {user_data.get('login')}")
        print(f"Email: {user_data.get('default_email')}")

        # Сохраняем данные в сессии
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
    # Очищаем сессию
    session.pop('authenticated', None)
    session.pop('user_data', None)
    return redirect(url_for('index'))



if __name__ == '__main__':
    app.run(debug=True)