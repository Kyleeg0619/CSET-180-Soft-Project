import datetime
from flask import Flask, render_template, request, redirect, url_for
from sqlalchemy import create_engine, text
from flask import session
from werkzeug.security import generate_password_hash, check_password_hash
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = 'mySuperSecretKey1234567890'

# *** Connect Database ***
conn_str = "mysql+pymysql://root:password@localhost/egarden" # Ky31ik3$m0s$; <-- change back 
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
            session['loggedin'] = True
            session['username'] = 'admin'
            return redirect(url_for('admin'))
        else:
            with engine.begin() as conn:
                account = conn.execute(text('SELECT * FROM Users WHERE username = :username OR email = :email'), {'username': username,'email':email}).fetchone()

                if account and check_password_hash(account.password, password):
                    session['loggedin'] = True
                    session['username'] = account.username
                    session['user_id'] = account.user_id
                    print("Session set: ", session.get('username'))
                    if account.user_type == 'Vendor':
                        return redirect(url_for('vendor'))
                    else:
                        return redirect(url_for('customer'))
                else:
                    msg = 'Incorrect username, email or password.'

    return render_template('login.html', msg=msg, account=account)
  
# *** Admin Page ***
@app.route('/admin')
def admin():
    if 'username' not in session:
        return redirect(url_for('login'))
    with engine.begin() as conn:
        reviews = conn.execute(text('SELECT * FROM reviews')).fetchall()
        products = conn.execute(text('SELECT * FROM products')).fetchall()

    return render_template('admin.html', products=products, reviews=reviews)

@app.route('/admin/products/admin_modify_product')
def admin_modify_product():
    return render_template('admin_modify_product.html')

@app.route('/admin/products/admin_add_product', methods=["GET", "POST"])
def admin_add_product():
    if request.method == "POST":
        product_name = request.form['product_name']
        product_desc = request.form['product_desc']
        product_quantity = request.form['product_quantity']
        original_price_raw = request.form['original_price'].strip()
        discount_price_raw = request.form['discount_price'].strip()
        discount_date_end_raw = request.form['discount_date_end'].strip()
        product_warranty_raw = request.form['product_warranty'].strip()

        discount_date_end = discount_date_end_raw if discount_date_end_raw else None
        product_warranty = product_warranty_raw if product_warranty_raw else None
        original_price = float(original_price_raw) if original_price_raw else None
        discount_price = float(discount_price_raw) if discount_price_raw else None
        

        colors_json = json.dumps([c.strip() for c in request.form['product_color'].split(',')])
        sizes_json = json.dumps([c.strip() for c in request.form['product_sizes'].split(',')])

        with engine.begin() as conn:
            conn.execute(text('''
                INSERT INTO products 
                (product_name, product_desc, product_color, product_sizes, product_quantity, original_price, discount_price, discount_date_end, product_warranty, vendor_username) 
                VALUES 
                (:product_name, :product_desc, :product_color, :product_sizes, :product_quantity, :original_price, :discount_price, :discount_date_end, :product_warranty, :vendor_username)
            '''), {
                'product_name': product_name,
                'product_desc': product_desc,
                'product_color': colors_json,
                'product_sizes': sizes_json,
                'product_quantity': product_quantity,
                'original_price': original_price,
                'discount_price': discount_price,
                'discount_date_end': discount_date_end,
                'product_warranty': product_warranty,
                'vendor_username': request.form['vendor_username']                                       
            })

        msg = 'You have successfully added a product.'
        return redirect(url_for('admin'))

    return render_template('admin_add_product.html')

@app.route('/admin/products/admin_edit_product/<int:product_id>', methods=["GET", "POST"])
def admin_edit_product(product_id):
    with engine.begin() as conn:
        product = conn.execute(
            text('SELECT * FROM products WHERE product_id = :product_id'),
            {'product_id': product_id}
        ).fetchone()

        if not product:
            return 'Product not found.', 404

        product_colors = json.loads(product.product_color)
        product_sizes = json.loads(product.product_sizes)

    return render_template(
        'admin_edit_product.html',
        product=product,
        product_colors=product_colors,
        product_sizes=product_sizes, json=json
    )

@app.route('/admin_edit_product_submit/<int:product_id>', methods=['POST'])
def admin_edit_product_submit(product_id):
    if request.method == "POST":
        product_name = request.form['product_name']
        product_desc = request.form['product_desc']
        product_color_raw = request.form['product_color'].split(', ')
        product_sizes_raw = request.form['product_sizes'].split(', ')
        product_quantity = request.form['product_quantity']
        original_price_raw = request.form['original_price'].strip()
        discount_price_raw = request.form['discount_price'].strip()
        discount_date_end_raw = request.form['discount_date_end'].strip()
        product_warranty_raw = request.form['product_warranty'].strip()

        # Handle the colors and sizes if empty or None
        if not product_color_raw:
            product_color = []  # or empty list if you're saving it as a JSON field
        else:
            product_color = [color.strip() for color in product_color_raw]

        if not product_sizes_raw:
            product_sizes = []  # or empty list
        else:
            product_sizes = [size.strip() for size in product_sizes_raw]

        # Fix to handle 'None' string and empty fields for prices
        original_price = float(original_price_raw) if original_price_raw and original_price_raw != 'None' else None
        discount_price = float(discount_price_raw) if discount_price_raw and discount_price_raw != 'None' else None
        discount_date_end = discount_date_end_raw if discount_date_end_raw else None
        product_warranty = product_warranty_raw if product_warranty_raw else None

        # Convert colors and sizes to JSON format
        colors_json = json.dumps([color.strip() for color in product_color])
        sizes_json = json.dumps([size.strip() for size in product_sizes])

        with engine.begin() as conn:
            conn.execute(text('''
                UPDATE products 
                SET 
                    product_name = :product_name, 
                    product_desc = :product_desc, 
                    product_color = :product_color, 
                    product_sizes = :product_sizes, 
                    product_quantity = :product_quantity, 
                    original_price = :original_price, 
                    discount_price = :discount_price, 
                    discount_date_end = :discount_date_end, 
                    product_warranty = :product_warranty 
                WHERE product_id = :product_id AND vendor_username = :vendor_username
            '''),
            {
                'product_name': product_name,
                'product_desc': product_desc,
                'product_color': colors_json,
                'product_sizes': sizes_json,
                'product_quantity': product_quantity,
                'original_price': original_price,
                'discount_price': discount_price,
                'discount_date_end': discount_date_end,
                'product_warranty': product_warranty,
                'vendor_username': session['username'],
                'product_id': product_id
            })
            return redirect(url_for('admin'))

@app.route('/admin_handle_product_action', methods=['POST'])
def admin_handle_product_action():
    product_id = request.form['product_id']
    action = request.form['action']

    if action == 'delete': 
        with engine.begin() as conn:
            conn.execute(text('DELETE FROM products WHERE product_id = :product_id'), {
                'product_id': product_id
            })
        return redirect(url_for('admin'))
    
    if action == 'edit':
        return redirect(url_for('admin_edit_product', product_id=product_id))
    
# *** Vendor Page ***
@app.route('/vendor')
def vendor():
    username = session['username']
    user_id = session['user_id']

    with engine.begin() as conn:
        reviews = conn.execute(text('SELECT * FROM reviews WHERE vendor_id = :vendor_id'),{'vendor_id':user_id}).fetchall()

        products = conn.execute(text('SELECT * FROM products WHERE vendor_username = :username'),{'username':username}).fetchall()

    return render_template('vendor.html', reviews=reviews, products=products, username=username)

@app.route('/vendor/products/modify_product')
def modify_products():
    return render_template('modify_products.html')

@app.route('/vendor/products/add_product', methods=["GET",'POST'])
def add_product():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    if request.method == "POST":
        product_name = request.form['product_name']
        product_desc = request.form['product_desc']
        product_quantity= request.form['product_quantity']
        original_price_raw = request.form['original_price'].strip()
        discount_price_raw = request.form['discount_price'].strip()
        discount_date_end_raw = request.form['discount_date_end'].strip()
        product_warranty_raw = request.form['product_warranty'].strip()

        discount_date_end = discount_date_end_raw if discount_date_end_raw else None
        product_warranty = product_warranty_raw if product_warranty_raw else None
        original_price = float(original_price_raw) if original_price_raw else None
        discount_price = float(discount_price_raw) if discount_price_raw else None

        colors_json = json.dumps([c.strip() for c in request.form['product_color'].split(',')])
        sizes_json = json.dumps([c.strip() for c in request.form['product_sizes'].split(',')])

        with engine.begin() as conn:
            conn.execute(text('INSERT INTO products (product_name, product_desc, product_color, product_sizes, product_quantity, original_price, discount_price, discount_date_end, product_warranty, vendor_username) VALUES (:product_name, :product_desc, :product_color, :product_sizes, :product_quantity, :original_price, :discount_price, :discount_date_end, :product_warranty, :vendor_username)'), {
                'product_name': product_name,
                'product_desc': product_desc,
                'product_color': colors_json,
                'product_sizes': sizes_json,
                'product_quantity':product_quantity,
                'original_price': original_price,
                'discount_price': discount_price,
                'discount_date_end': discount_date_end, 'product_warranty':product_warranty, 'vendor_username':session['username']
            })

            msg = 'You have successfully added a product.'
            return redirect(url_for('vendor'))
    return render_template('add_product.html')



@app.route('/vendor/products/edit_product/<int:product_id>', methods=["GET", "POST"])
def edit_product(product_id):
    with engine.begin() as conn:
        product = conn.execute(
            text('SELECT * FROM products WHERE product_id = :product_id AND vendor_username = :vendor_username'),
            {'product_id': product_id, 'vendor_username': session['username']}
        ).fetchone()

        if not product:
            return 'Product not found or you don\'t have permission.', 403

        product_colors = json.loads(product.product_color)
        product_sizes = json.loads(product.product_sizes)

    return render_template(
        'edit_product.html',
        product=product,
        product_colors=product_colors,
        product_sizes=product_sizes, json=json
    )

@app.route('/edit_product_submit/<int:product_id>', methods=['POST'])
def edit_product_submit(product_id):
    if request.method == "POST":
        product_name = request.form['product_name']
        product_desc = request.form['product_desc']
        product_color_raw = request.form['product_color'].split(', ')
        product_sizes_raw = request.form['product_sizes'].split(', ')
        product_quantity = request.form['product_quantity']
        original_price_raw = request.form['original_price'].strip()
        discount_price_raw = request.form['discount_price'].strip()
        discount_date_end_raw = request.form['discount_date_end'].strip()
        product_warranty_raw = request.form['product_warranty'].strip()

        # Handle the colors and sizes if empty or None
        if not product_color_raw:
            product_color = []  # or empty list if you're saving it as a JSON field
        else:
            product_color = [color.strip() for color in product_color_raw]

        if not product_sizes_raw:
            product_sizes = []  # or empty list
        else:
            product_sizes = [size.strip() for size in product_sizes_raw]

        # Fix to handle 'None' string and empty fields for prices
        original_price = float(original_price_raw) if original_price_raw and original_price_raw != 'None' else None
        discount_price = float(discount_price_raw) if discount_price_raw and discount_price_raw != 'None' else None
        discount_date_end = discount_date_end_raw if discount_date_end_raw else None
        product_warranty = product_warranty_raw if product_warranty_raw else None

        # Convert colors and sizes to JSON format
        colors_json = json.dumps([color.strip() for color in product_color])
        sizes_json = json.dumps([size.strip() for size in product_sizes])

        with engine.begin() as conn:
            conn.execute(text('''
                UPDATE products 
                SET 
                    product_name = :product_name, 
                    product_desc = :product_desc, 
                    product_color = :product_color, 
                    product_sizes = :product_sizes, 
                    product_quantity = :product_quantity, 
                    original_price = :original_price, 
                    discount_price = :discount_price, 
                    discount_date_end = :discount_date_end, 
                    product_warranty = :product_warranty 
                WHERE product_id = :product_id AND vendor_username = :vendor_username
            '''),
            {
                'product_name': product_name,
                'product_desc': product_desc,
                'product_color': colors_json,
                'product_sizes': sizes_json,
                'product_quantity': product_quantity,
                'original_price': original_price,
                'discount_price': discount_price,
                'discount_date_end': discount_date_end,
                'product_warranty': product_warranty,
                'vendor_username': session['username'],
                'product_id': product_id
            })
            return redirect(url_for('vendor'))

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

@app.route('/handle_product_action', methods=['POST'])
def handle_product_action():
    product_id = request.form['product_id']
    action = request.form['action']

    if action == 'delete':
        with engine.begin() as conn:
            conn.execute(text('DELETE FROM products WHERE product_id = :product_id AND vendor_username = :vendor_username'), {
                'product_id': product_id,
                'vendor_username': session['username']
            })
        return redirect(url_for('vendor'))
    
    if action == 'edit':
        return redirect(url_for('edit_product', product_id=product_id))






# *** Run & Debug ***
if __name__ == '__main__':
    app.run(debug=True)