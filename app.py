from flask import *
from db import *

date = '579'

app = Flask(__name__)

@app.route("/", methods=["POST", "GET"])
def index():
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


    elif True == False:
        return redirect(url_for('profile'))

    elif True == False:
        return redirect(url_for('index'))

    elif 'b' in request.form:
        print(22)
        return redirect(url_for('about'))

    return render_template("index.html")



@app.route("/about")
def about():
    if 1 == 1:
        return render_template("about.html")
    elif True == False:
        return redirect(url_for('index'))



@app.route("/profile")
def profile():
    if 1 == 1:
        return render_template("profile_html")
    elif True == False:
        return redirect(url_for('index'))


if __name__ == "__main__":
    #Add_to_db('Users', 'dfff')
    #Delete_from_db('Users', 2)
    #Update_element_db('Users', 'login', 3, 'rrrr')
    app.run()