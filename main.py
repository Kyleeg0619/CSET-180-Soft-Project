import datetime
from flask import Flask, render_template, request, redirect, url_for
from sqlalchemy import create_engine, text
from flask import session
from werkzeug.security import generate_password_hash, check_password_hash
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = 'mySuperSecretKey1234567890'

# *** Connect Database ***
conn_str = "mysql+pymysql://root:CSET115@localhost/egarden"
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
    account = None

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']

        if username == 'admin' and password == 'admin':
            return redirect(url_for('admin'))
        else:
            with engine.begin() as conn:
                account = conn.execute(
                    text('SELECT * FROM Users WHERE username = :username OR email = :email'),
                    {'username': username, 'email': email}
                ).fetchone()

            if account and check_password_hash(account.password, password):
                session['loggedin'] = True
                session['username'] = account.username
                session['user_id'] = account.user_id
                session['user_type'] = account.user_type
                session['cart'] = []
                print("Session set: ", session.get('username'))

                if account.user_type == 'Vendor':
                    return redirect(url_for('vendor'))
                else:
                    return redirect(url_for('customer'))
            else:
                msg = 'Incorrect username, email or password.'  # <-- correctly here

    return render_template('login.html', msg=msg, account=account)

@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('username', None)
    session.pop('user_id', None)
    session.pop('user_type', None)
    # DO NOT pop 'cart'
    return redirect(url_for('index'))



# *** ADMIN FUNCTIONALITY ***
@app.route('/admin')
def admin():
        return render_template('admin.html')
# *** END OF ADMIN FUNCTIONALITY ***
  
# *** VENDOR FUNCTIONALITY ***
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

        colors = request.form.getlist('colors')
        sizes = request.form.getlist('sizes')
        colors_str = ','.join(colors)
        sizes_str = ','.join(sizes)

        with engine.begin() as conn:
            conn.execute(text('INSERT INTO products (product_name, product_desc, product_color, product_sizes, product_quantity, original_price, discount_price, discount_date_end, product_warranty, vendor_username) VALUES (:product_name, :product_desc, :product_color, :product_sizes, :product_quantity, :original_price, :discount_price, :discount_date_end, :product_warranty, :vendor_username)'), {
                'product_name': product_name,
                'product_desc': product_desc,
                'product_color': colors_str,
                'product_sizes': sizes_str,
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

    return render_template(
        'edit_product.html',
        product=product
    )

@app.route('/edit_product_submit/<int:product_id>', methods=['POST'])
def edit_product_submit(product_id):
    if request.method == "POST":
        product_name = request.form['product_name']
        product_desc = request.form['product_desc']
        product_quantity = request.form['product_quantity']
        original_price_raw = request.form['original_price'].strip()
        discount_price_raw = request.form['discount_price'].strip()
        discount_date_end_raw = request.form['discount_date_end'].strip()
        product_warranty_raw = request.form['product_warranty'].strip()
        colors = request.form.getlist('colors')
        sizes = request.form.getlist('sizes')
        colors_str = ','.join(colors)
        sizes_str = ','.join(sizes)

        # Fix to handle 'None' string and empty fields for prices
        original_price = float(original_price_raw) if original_price_raw and original_price_raw != 'None' else None
        discount_price = float(discount_price_raw) if discount_price_raw and discount_price_raw != 'None' else None
        discount_date_end = discount_date_end_raw if discount_date_end_raw else None
        product_warranty = product_warranty_raw if product_warranty_raw else None

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
                'product_color': colors_str,
                'product_sizes': sizes_str,
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
# *** END OF VENDOR FUNCTIONALITY ***

# *** CUSTOMER FUNCTIONALITY ***
@app.route('/customer')
@app.route('/customer/<page>')
def customer(page=1):
    username = session['username']

    page = int(page)
    per_page = 6
    page_limit = (page-1)*per_page

    with engine.begin() as conn:

        account = conn.execute(text('SELECT * FROM users WHERE username = :username'), {'username':username}).fetchone()
        
        products = conn.execute(text('SELECT * FROM products LIMIT :per_page OFFSET :page'),{'per_page':per_page,'page':page_limit}).fetchall()

    return render_template('customer.html', account=account, products=products, page=page, per_page=per_page)

@app.route('/search', methods=['POST'])
def search():
    search_query = request.form.get('query','').strip()
    print(search_query)
    
    with engine.begin() as conn:
        username = session['username']
        account = conn.execute(text('SELECT * FROM users WHERE username = :username'), {'username':username}).fetchone()

        if search_query=='':
            return redirect(url_for('customer'))

        products = conn.execute(text('SELECT * FROM products WHERE product_name LIKE :search_query OR product_desc LIKE :search_query OR vendor_username LIKE :search_query'),{'search_query':f'%{search_query}%'}).fetchall()

        return render_template('customer.html', account=account, page=1, search_query=search_query, products=products)

@app.route('/product/<int:product_id>', methods=['GET','POST'])
def product(product_id):
# select info from the products table using product id
    with engine.begin() as conn:
        products = conn.execute(text('SELECT * FROM products WHERE product_id =:product_id'),{'product_id':product_id}).fetchone()
# had to change product_id=product_id to product=product because the page needs all the product info and i was getting error
    return render_template('product.html', product=products)



@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    if 'username' not in session:
        return redirect(url_for('login'))

    product_id = request.form['product_id']
    size = request.form['size']
    color = request.form['color']
    quantity = int(request.form['quantity'])
    user_id = session['user_id']

    with engine.begin() as conn:
        product = conn.execute(
            text('SELECT product_quantity, original_price, discount_price FROM products WHERE product_id = :product_id'),
            {'product_id': product_id}
        ).fetchone()

        if not product or product.product_quantity < quantity:
            return "Error: Product is sold out or not enough stock."

        price = float(product.discount_price) if product.discount_price else float(product.original_price)

        conn.execute(
            text('''
                INSERT INTO cart_items (user_id, product_id, size, color, quantity, price)
                VALUES (:user_id, :product_id, :size, :color, :quantity, :price)
            '''),
            {
                'user_id': user_id,
                'product_id': product_id,
                'size': size,
                'color': color,
                'quantity': quantity,
                'price': price
            }
        )

    return redirect(url_for('product', product_id=product_id))


@app.route('/cart')
def view_cart():
    if 'username' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']

    with engine.begin() as conn:
        cart_items = conn.execute(
            text('SELECT * FROM cart_items WHERE user_id = :user_id'),
            {'user_id': user_id}
        ).fetchall()

    total_price = sum(item.price * item.quantity for item in cart_items)

    return render_template('cart.html', cart_items=cart_items, total_price=total_price)



@app.route('/remove_from_cart', methods=['POST'])
def remove_from_cart():
    cart_item_id = int(request.form['cart_item_id'])

    with engine.begin() as conn:
        conn.execute(
            text('DELETE FROM cart_items WHERE cart_item_id = :cart_item_id'),
            {'cart_item_id': cart_item_id}
        )

    return redirect(url_for('view_cart'))


@app.route('/checkout')
def checkout():
    if 'username' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']

    with engine.begin() as conn:
        cart_items = conn.execute(
            text('SELECT * FROM cart_items WHERE user_id = :user_id'),
            {'user_id': user_id}
        ).fetchall()

    if not cart_items:
        return redirect(url_for('view_cart'))

    total_price = sum(item.price * item.quantity for item in cart_items)

    return render_template('checkout.html', cart_items=cart_items, total_price=total_price)


@app.route('/place_order', methods=['GET', 'POST'])
def place_order():
    full_name = request.form['full_name']
    address = request.form['address']
    payment_info = request.form['payment_info']
    user_id = session['user_id']
    now = datetime.datetime.now()

    with engine.begin() as conn:
        cart_items = conn.execute(text('''
            SELECT ci.*, p.product_name, p.product_quantity
            FROM cart_items ci
            JOIN products p ON ci.product_id = p.product_id
            WHERE ci.user_id = :user_id
        '''), {'user_id': user_id}).fetchall()

        if not cart_items:
            return redirect(url_for('view_cart'))

        total_price = sum(item.price * item.quantity for item in cart_items)

        # Insert the order
        conn.execute(text('''
            INSERT INTO orders (user_id, full_name, address, payment_info, order_date, total_items)
            VALUES (:user_id, :full_name, :address, :payment_info, :order_date, :total_items)
        '''), {
            'user_id': user_id,
            'full_name': full_name,
            'address': address,
            'payment_info': payment_info,
            'order_date': now,
            'total_items': len(cart_items)
        })

        # Update product quantities
        for item in cart_items:
            conn.execute(
                text('''
                    UPDATE products
                    SET product_quantity = product_quantity - :qty
                    WHERE product_id = :pid AND product_quantity >= :qty
                '''),
                {'qty': item.quantity, 'pid': item.product_id}
            )

        # Clear cart
        conn.execute(
            text('DELETE FROM cart_items WHERE user_id = :user_id'),
            {'user_id': user_id}
        )

    return render_template(
        'thank_you.html',
        full_name=full_name,
        cart_items=cart_items,
        total_price=total_price,
        card_number=payment_info,
        order_date=now.strftime("%B %d, %Y")
    )

@app.route('/thank_you')
def thank_you():
    return render_template('thank_you.html')

@app.route('/orders')
def view_orders():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']

    with engine.begin() as conn:
        # Get all past orders for this user
        orders = conn.execute(text('''
            SELECT * FROM orders 
            WHERE user_id = :user_id
            ORDER BY order_date DESC
        '''), {'user_id': user_id}).fetchall()

    return render_template('view_orders.html', orders=orders)


# *** END OF CUSTOMER FUNCTIONALITY ***

# *** Run & Debug ***
if __name__ == '__main__':
    app.run(debug=True)