import datetime
from flask import Flask, render_template, request, redirect, url_for
from sqlalchemy import create_engine, text
from flask import session
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'mySuperSecretKey1234567890'

# *** Connect Database ***
conn_str = "mysql+pymysql://root:Ky31ik3$m0s$;@localhost/egarden"
engine = create_engine(conn_str, echo=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
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
            existing = conn.execute(
                text('SELECT * FROM users WHERE username = :username OR email = :email'),
                {'username': username, 'email': email}
            ).fetchone()

            if existing:
                msg = 'Account already exists'
            else:
                # Insert into users table
                conn.execute(
                    text('''
                        INSERT INTO users (username, password, first_name, last_name, user_type, email) 
                        VALUES (:username, :password, :first_name, :last_name, :user_type, :email)
                    '''),
                    {
                        'username': username,
                        'password': hashed_password,
                        'first_name': firstName,
                        'last_name': lastName,
                        'user_type': userType,
                        'email': email
                    }
                )

                # Get the newly inserted user's ID
                user_id = conn.execute(
                    text('SELECT user_id FROM users WHERE username = :username'),
                    {'username': username}
                ).scalar()

                # If user is a vendor, insert into vendor table
                if userType.lower() == 'vendor':
                    conn.execute(
                        text('INSERT INTO vendor (user_id) VALUES (:user_id)'),
                        {'user_id': user_id}
                    )

                msg = 'You have successfully signed up! You can now log in.'

    return render_template('register.html', msg=msg)


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
    reviews = []
    if 'username' in session:
        with engine.begin() as conn:
            result = conn.execute(text("""
                SELECT r.review_text, r.rating, u.username, r.review_date
                FROM reviews r
                JOIN users u ON r.user_id = u.user_id
                JOIN vendor v ON r.vendor_id = v.vendor_id
                JOIN users vu ON v.user_id = vu.user_id
                WHERE vu.username = :vendor_username
                ORDER BY r.review_date DESC
            """), {'vendor_username': session['username']})

            reviews = result.fetchall()

    return render_template('vendor.html', reviews=reviews)

@app.route('/vendor/products')
def modify_products():
    return render_template('modify_products.html')

@app.route('/vendor/products/add_product', methods=["GET",'POST'])
def add_product():
    # if 'username' not in session:
    #     return redirect(url_for('login'))
    if request.method == "POST":
        product_name = request.form['product_name']
        product_desc = request.form['product_desc']
        product_color = request.form['product_color']
        product_sizes = request.form['product_sizes']
        product_quantity= request.form['product_quantity']
        original_price = request.form['original_price']
        discount_price= request.form['discount_price']

        with engine.begin() as conn:
            conn.execute(text('INSERT INTO products (product_name, product_desc, product_color, product_sizes, product_quantity, original_price, discount_price) VALUES (:product_name, :product_desc, :product_color, :product_sizes, :product_quantity, :original_price, :discount_price)'), {
                'product_name': product_name,
                'product_desc': product_desc,
                'product_color': product_color,
                'product_sizes': product_sizes,
                'product_quantity':product_quantity,
                'original_price': original_price,
                'discount_price': discount_price
            })

            msg = 'You have successfully added a product.'
            return render_template('add_product.html',msg=msg)
    return render_template('add_product.html')



@app.route('/vendor/prices')
def update_prices():
    return render_template('update_prices.html')

@app.route('/vendor/chat', methods=['GET', 'POST'])
def chat():
    messages = []
    user_type = None

    if 'username' in session:
        with engine.begin() as conn:
            # Get user type
            user = conn.execute(
                text("SELECT user_type, user_id FROM users WHERE username = :username"),
                {'username': session['username']}
            ).fetchone()

            if user:
                user_type = user.user_type
                user_id = user.user_id

                if request.method == 'POST':
                    content = request.form['message']
                    conn.execute(
                        text("""
                            INSERT INTO chat (user_id, content, timestamp)
                            VALUES (:user_id, :content, NOW())
                        """),
                        {'user_id': user_id, 'content': content}
                    )

                result = conn.execute(
                    text("""
                        SELECT u.username, c.content, c.timestamp
                        FROM chat c
                        JOIN users u ON c.user_id = u.user_id
                        ORDER BY c.timestamp DESC
                    """)
                )
                messages = result.fetchall()

    return render_template('chat.html', messages=messages, user_type=user_type)


# *** Run & Debug ***
if __name__ == '__main__':
    app.run(debug=True)