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

        if (username == 'admin' and password == 'admin') or (username == 'admin2' and password == 'admin2'):
            session['loggedin'] = True
            session['username'] = 'admin'
            session['user_type'] = 'admin'
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
    if 'username' not in session:
        return redirect(url_for('login'))
    with engine.begin() as conn:
        reviews = conn.execute(text('SELECT * FROM reviews')).fetchall()
        products = conn.execute(text('SELECT * FROM products')).fetchall()

    return render_template('admin.html', products=products, reviews=reviews)

@app.route('/admin/products/admin_add_product', methods=["GET", "POST"])
def admin_add_product():
    with engine.begin() as conn:
        user_type = 'vendor'
        vendors = conn.execute(text('SELECT username FROM users WHERE user_type = :user_type'),
                       {'user_type': user_type}).fetchall()
        vendors = [vendor[0] for vendor in vendors]

    if request.method == "POST":
        vendor_username = request.form.get('vendor_username', '').strip()
        if not vendor_username:
            flash("Please select a vendor.")
            return redirect(url_for('admin_add_product'))

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
                'discount_date_end': discount_date_end, 'product_warranty':product_warranty, 'vendor_username':vendor_username
            })

        msg = 'You have successfully added a product.'
        return redirect(url_for('admin'))

    return render_template('admin_add_product.html', vendors=vendors)

@app.route('/admin/products/admin_edit_product/<int:product_id>', methods=["GET", "POST"])
def admin_edit_product(product_id):
    with engine.begin() as conn:
        product = conn.execute(
            text('SELECT * FROM products WHERE product_id = :product_id'),
            {'product_id': product_id}
        ).fetchone()

        if not product:
            return 'Product not found.', 404

    return render_template(
        'admin_edit_product.html',
        product=product
    )

@app.route('/admin_edit_product_submit/<int:product_id>', methods=['POST'])
def admin_edit_product_submit(product_id):
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

# vendor order process
@app.route('/vendor/orders', methods=["GET", "POST"])
def orders():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    with engine.begin() as conn:
        orders_pending = conn.execute(text('SELECT * FROM orders WHERE order_status = "pending"')).fetchall()
        orders_confirmed = conn.execute(text('SELECT * FROM orders WHERE order_status = "confirmed"')).fetchall()
        orders_handed = conn.execute(text('SELECT * FROM orders WHERE order_status = "handed"')).fetchall()
        orders_shipped = conn.execute(text('SELECT * FROM orders WHERE order_status = "shipped"')).fetchall()

    return render_template('orders.html',  orders_pending=orders_pending,
        orders_confirmed=orders_confirmed,
        orders_handed=orders_handed,
        orders_shipped=orders_shipped)

# pend order function
@app.route('/orders_pending/<int:order_id>', methods=['POST'])
def orders_pending(order_id):
    if 'username' not in session:
        return redirect(url_for('login'))
    
    with engine.begin() as conn:
        conn.execute(
            text('UPDATE orders SET order_status = "confirmed" WHERE order_id = :order_id'),
            {'order_id': order_id}
        )
    
    return redirect(url_for('orders'))

# confirm order function
@app.route('/orders_confirmed/<int:order_id>', methods=['POST'])
def orders_confirmed(order_id):
    if 'username' not in session:
        return redirect(url_for('login'))
    
    with engine.begin() as conn:
        conn.execute(
            text('UPDATE orders SET order_status = "handed" WHERE order_id = :order_id'),
            {'order_id': order_id}
        )
    
    return redirect(url_for('orders'))

# handed order function
@app.route('/orders_handed/<int:order_id>', methods=['POST'])
def orders_handed(order_id):
    if 'username' not in session:
        return redirect(url_for('login'))
    
    with engine.begin() as conn:
        conn.execute(
            text('UPDATE orders SET order_status = "shipped" WHERE order_id = :order_id'),
            {'order_id': order_id}
        )
    
    return redirect(url_for('orders'))
    
# shipped order function
@app.route('/orders_shipped/<int:order_id>', methods=['POST'])
def orders_shipped(order_id):
    if 'username' not in session:
        return redirect(url_for('login'))
    
    with engine.begin() as conn:
        conn.execute(
            text('UPDATE orders SET order_status = "completed" WHERE order_id = :order_id'),
            {'order_id': order_id}
        )
    
    return redirect(url_for('orders'))


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

        current_date = datetime.datetime.now()

    return render_template('customer.html', account=account, products=products, page=page, per_page=per_page, current_date=current_date)

@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        data = request.form
    else:
        data = request.args

    search_query = data.get('query', '').strip()
    color_filter = data.get('color-filter', '').strip()
    size_filter = data.get('size-filter', '').strip()
    stock_filter = data.get('stock-filter', '').strip()
    
    with engine.begin() as conn:
        username = session['username']
        account = conn.execute(text('SELECT * FROM users WHERE username = :username'), {'username':username}).fetchone()

        if not search_query and not color_filter and not size_filter and not stock_filter:
            return redirect(url_for('customer'))

        sql = 'SELECT * FROM products WHERE 1=1'
        params = {}

        if search_query:
            sql += ' AND (product_name LIKE :search_query OR product_desc LIKE :search_query OR vendor_username LIKE :search_query)'
            params['search_query'] = f'%{search_query}%'

        if color_filter:
            sql += ' AND product_color = :color_filter'
            params['color_filter'] = color_filter

        if size_filter:
            sql += ' AND product_sizes = :size_filter'
            params['size_filter'] = size_filter

        if stock_filter:
            if stock_filter == 'available':
                sql += ' AND product_quantity > 0'
            else:
                sql += ' AND product_quantity = 0'

        products = conn.execute(text(sql), params).fetchall()

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

    return redirect(url_for('customer'))


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

        cart_item_ids = conn.execute(
            text('SELECT product_id FROM cart_items WHERE user_id = :user_id'),
            {'user_id': user_id}
        ).fetchall()

        product_ids = [row[0] for row in cart_item_ids]
        product_list = ','.join(map(str,product_ids))

        if not cart_items:
            return redirect(url_for('view_cart'))

        total_price = sum(item.price * item.quantity for item in cart_items)

        # Insert the order
        conn.execute(text('''
            INSERT INTO orders (user_id, full_name, address, payment_info, order_date, total_items,item_list)
            VALUES (:user_id, :full_name, :address, :payment_info, :order_date, :total_items,:item_list)
        '''), {
            'user_id': user_id,
            'full_name': full_name,
            'address': address,
            'payment_info': payment_info,
            'order_date': now,
            'total_items': len(cart_items),
            'item_list':product_list
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

@app.route('/complaints/<int:order_id>', methods=['GET', 'POST'])
def complaint(order_id):
    complaint_validity = ''
    rejected = 'rejected'

    with engine.begin() as conn:
        order = conn.execute(
            text('SELECT * FROM orders WHERE order_id = :order_id'),
            {'order_id': order_id}
        ).fetchone()

    if request.method == 'POST':
        complaint_date = datetime.datetime.now().date()
        complaint_title = request.form['complaint_title']
        complaint_desc = request.form['complaint_desc']
        complaint_demand = request.form['complaint_demand']

        with engine.begin() as conn:
            order = conn.execute(
            text('SELECT * FROM orders WHERE order_id = :order_id'),
            {'order_id': order_id}
        ).fetchone()
            
            product_list = order.item_list.split(',')
            print(product_list)
            for product_id in product_list:
                warranty = conn.execute(text('SELECT product_warranty FROM products WHERE product_id = :product_id'),{'product_id':product_id}).fetchone()
                print(warranty)
                warranty_str = warranty[0]
                print(warranty_str)
                print(complaint_date)

                if warranty_str < complaint_date and complaint_demand == 'warranty':
                    complaint_validity = 'invalid'
                    break
                else:
                    complaint_validity = 'valid'

                if complaint_validity == 'valid':
                    conn.execute(
                    text('''
                        INSERT INTO complaints (
                            order_id, order_date, complaint_date,
                            complaint_title, complaint_desc, complaint_demand
                        )
                        VALUES (
                            :order_id, :order_date, :complaint_date,
                            :complaint_title, :complaint_desc, :complaint_demand
                        )
                    '''), {
                        'order_id': order_id,
                        'order_date': order.order_date,
                        'complaint_date': complaint_date,
                        'complaint_title': complaint_title,
                        'complaint_desc': complaint_desc,
                        'complaint_demand': complaint_demand
                    }
                )
                elif complaint_validity == 'invalid':
                    conn.execute(
                    text('''
                        INSERT INTO complaints (
                            order_id, order_date, complaint_date,
                            complaint_title, complaint_desc, complaint_demand, complaint_status
                        )
                        VALUES (
                            :order_id, :order_date, :complaint_date,
                            :complaint_title, :complaint_desc, :complaint_demand, :complaint_status
                        )
                    '''), {
                        'order_id': order_id,
                        'order_date': order.order_date,
                        'complaint_date': complaint_date,
                        'complaint_title': complaint_title,
                        'complaint_desc': complaint_desc,
                        'complaint_demand': complaint_demand,
                        'complaint_status': rejected
                    }
                )
        return redirect(url_for('customer'))

    return render_template('complaint.html', order=order)

@app.route('/vendor/complaints', methods=['GET','POST'])
def complaint_status():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    with engine.begin() as conn:
        complaints_rejected = conn.execute(text('SELECT * FROM complaints WHERE complaint_status ="rejected"')).fetchall()
        complaints_pending = conn.execute(text('SELECT * FROM complaints WHERE complaint_status = "pending"')).fetchall()
        complaints_confirmed = conn.execute(text('SELECT * FROM complaints WHERE complaint_status = "confirmed"')).fetchall()
        complaints_complete = conn.execute(text('SELECT * FROM complaints WHERE complaint_status = "complete"')).fetchall()
    
    return render_template('vendor_complaints.html', complaints_rejected=complaints_rejected,complaints_pending=complaints_pending,complaints_confirmed=complaints_confirmed,complaints_complete=complaints_complete)

@app.route('/complaints_pending',methods=['POST'])
def complaints_pending():
    order_id = request.form['order_id']
    complaint_id = request.form['complaint_id']
    with engine.begin() as conn:
        if request.method == 'POST':
            action = request.form.get('action')
            if action == 'confirm':
                conn.execute(text('UPDATE complaints SET complaint_status = "confirmed" WHERE order_id = :order_id AND complaint_id = :complaint_id'),{'order_id':order_id,'complaint_id':complaint_id})
            elif action == 'reject':
                conn.execute(text('UPDATE complaints SET complaint_status = "rejected" WHERE order_id = :order_id AND complaint_id = :complaint_id'),{'order_id':order_id,'complaint_id':complaint_id})
            return redirect(url_for('complaint_status'))

@app.route('/complaints_confirmed',methods=['POST'])
def complaints_confirmed():
    order_id = request.form['order_id']
    complaint_id = request.form['complaint_id']
    with engine.begin() as conn:
        conn.execute(text('UPDATE complaints SET complaint_status = "complete" WHERE order_id = :order_id AND complaint_id = :complaint_id'),{'order_id':order_id,'complaint_id':complaint_id})
    return redirect(url_for('complaint_status'))

@app.route('/complaints_rejected',methods=['POST'])
def complaints_rejected():
    order_id = request.form['order_id']
    complaint_id = request.form['complaint_id']
    with engine.begin() as conn:
        conn.execute(text('UPDATE complaints SET complaint_status = "rejected" WHERE order_id = :order_id AND complaint_id = :complaint_id'),{'order_id':order_id,'complaint_id':complaint_id})
    return redirect(url_for('complaint_status'))
# *** END OF CUSTOMER FUNCTIONALITY ***

# *** Run & Debug ***
if __name__ == '__main__':
    app.run(debug=True)