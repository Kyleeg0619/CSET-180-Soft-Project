import datetime
from flask import Flask, render_template, request, redirect, url_for, jsonify
from sqlalchemy import create_engine, text
from flask import session
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'mySuperSecretKey1234567890'

# *** Connect Database ***
conn_str = "mysql+pymysql://root:CSET115@localhost/egardens"
engine = create_engine(conn_str, echo=True)

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/vendor')
def vendor(): 
    return render_template('vendor.html')

# *** Run & Debug ***
if __name__ == '__main__':
    app.run(debug=True)