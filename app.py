from flask import Flask, redirect, request, render_template
import requests

app = Flask(__name__)

@app.route('/auth/yandex/callback')
def yandex_callback():
    code = request.args.get('code')
    
    # 1. Получаем OAuth-токен
    token_url = 'https://oauth.yandex.ru/token'
    data = {
        'grant_type': 'authorization_code',
        'code': code,
        'client_id': '0aea89d8864b4ddd9544708d0b19846b',
        'client_secret': 'c61032a2a85a42a49716b3b670f3b853'
    }
    response = requests.post(token_url, data=data)
    access_token = response.json().get('access_token')

    # 2. Получаем данные пользователя
    user_url = 'https://login.yandex.ru/info'
    headers = {'Authorization': f'OAuth {access_token}'}
    user_data = requests.get(user_url, headers=headers).json()

    print('Данные пользователя:', user_data)
    return redirect('/profile?auth=success')



@app.route("/")
def index():
    return render_template("index.html")

@app.route("/about")
def about():
    return render_template("about.html")


if __name__ == "__main__":
    app.run(debug=True)


