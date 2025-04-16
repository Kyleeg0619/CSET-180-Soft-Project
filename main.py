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

@app.route('/register', methods=['GET','POST'])
def register():
    msg = ''
    if request.method == 'POST':
        userType = request.form['user_type']
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        firstName = request.form['first_name']
        lastName = request.form['last_name']
        hashed_password = generate_password_hash(password)
        
        with engine.begin() as conn:
            existing = conn.execute(text('SELECT * FROM users WHERE username = :username OR email = :email'),{'username':username, 'email':email}).fetchone()

            if existing:
                msg = 'Account already exists'
            else:
                conn.execute(text('INSERT INTO users (username, password, first_name, last_name, user_type, email) VALUES (:username, :password, :first_name, :last_name, :user_type, :email)'), {
                    'username': username,
                    'password': hashed_password,
                    'first_name': firstName,
                    'last_name': lastName,
                    'user_type': userType,
                    'email': email
                })

                msg = 'You have successfully signed up! You can now log in.'
    return render_template('register.html',msg=msg)

@app.route('/login', methods=['GET', 'POST'])
def login():
    msg = ''
    account = None  # Ensure 'account' is initialized
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']

        if username == 'admin' and password == 'admin':
            return redirect(url_for('admin'))
        else:
            with engine.begin() as conn:
                account = conn.execute(text('SELECT * FROM Users WHERE username = :username OR email = :email'), {'username': username,'email':email}).fetchone()

                if account and check_password_hash(account.password, password):
                    session['loggedin'] = True
                    session['username'] = account.username
                    if account.user_type == 'Vendor':
                        return redirect(url_for('Vendor'))
                    else:
                        return redirect(url_for('Customer'))
                else:
                    msg = 'Incorrect username, email or password.'

    return render_template('login.html', msg=msg, account=account)
  
# *** Admin Page ***
@app.route('/admin')
def admin():
        return render_template('admin.html')

@app.route('/vendor')
def vendor(): 
    return render_template('vendor.html')

@app.route('/vendor/products')
def manage_products():
    return render_template('manage_products.html')


# *** Run & Debug ***
if __name__ == '__main__':
    app.run(debug=True)