from flask import Flask, render_template
from db import Add_to_db


app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/about")
def about():
    return render_template("about.html")

if __name__ == "__main__":
    Add_to_db('Users', 'dddd')
    Add_to_db('Users', 'dfff')
    app.run(debug=True)