"""
NK's Yams - Backend API
Auth: JWT (register/login), Neon PostgreSQL, WhatsApp via Green API
"""

# ============================================================
# IMPORTS
# ============================================================
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from functools import wraps
import os, uuid, re, threading, bcrypt, psycopg2, psycopg2.extras
from datetime import datetime, timezone
from dotenv import load_dotenv
import jwt as pyjwt
import requests as http_requests

load_dotenv()

# ============================================================
# CONFIG
# ============================================================
app = Flask(__name__, static_folder='public', static_url_path='')
CORS(app, resources={r"/api/*": {"origins": "*"}})

JWT_SECRET        = os.environ.get('JWT_SECRET', 'nkyam_jwt_super_secret_change_in_prod')
JWT_EXPIRY_HOURS  = 24 * 7   # 7 days

ADMIN_TOKEN       = os.environ.get('ADMIN_TOKEN', '7Xk9mP2nQ8rS5tU3vW7yZ4bC6dF8gH1jL9')
DATABASE_URL      = os.environ.get('DATABASE_URL', '')

# Green API WhatsApp
GREEN_ID          = os.environ.get('GREEN_API_ID', '7107601889')
GREEN_TOKEN       = os.environ.get('GREEN_API_TOKEN', '5e85cf0d650b451cb3ea6c15bfdde997ae51787937b149c198')
GREEN_URL         = f'https://7107.api.greenapi.com/waInstance{GREEN_ID}/sendMessage/{GREEN_TOKEN}'
ADMIN_WA_NUMBER   = os.environ.get('ADMIN_WHATSAPP', '2347034547179@c.us')
WHATSAPP_ENABLED  = os.environ.get('WHATSAPP_ENABLED', 'true').lower() == 'true'

VALID_YAM_TYPES   = ['Water Yam', 'Yellow Yam', 'White Yam']
VALID_STATUSES    = ['pending', 'confirmed', 'dispatched', 'delivered', 'cancelled']
MIN_PRICE, MAX_PRICE = 1000, 3000

# ============================================================
# CORS HEADERS
# ============================================================
@app.after_request
def add_cors(response):
    response.headers['Access-Control-Allow-Origin']  = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET,POST,PUT,DELETE,OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization,X-Admin-Token'
    return response

@app.route('/api/<path:path>', methods=['OPTIONS'])
def options_handler(path):
    return jsonify({}), 200

# ============================================================
# DATABASE — NEON POSTGRESQL
# ============================================================
def get_db():
    """Get a new database connection."""
    if not DATABASE_URL:
        raise RuntimeError('DATABASE_URL not set. Add it to your .env file.')
    conn = psycopg2.connect(DATABASE_URL, cursor_factory=psycopg2.extras.RealDictCursor)
    return conn

def init_db():
    """Create tables if they don't exist."""
    conn = get_db()
    cur  = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id              SERIAL PRIMARY KEY,
            user_id         VARCHAR(36)  UNIQUE NOT NULL,
            full_name       VARCHAR(120) NOT NULL,
            email           VARCHAR(180) UNIQUE NOT NULL,
            phone           VARCHAR(20),
            whatsapp_number VARCHAR(20),
            password_hash   TEXT         NOT NULL,
            role            VARCHAR(20)  NOT NULL DEFAULT 'customer',
            created_at      TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
            updated_at      TIMESTAMPTZ
        );
    """)

    # Add whatsapp_number column to existing tables that were created before this migration
    cur.execute("""
        ALTER TABLE users ADD COLUMN IF NOT EXISTS whatsapp_number VARCHAR(20);
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id              SERIAL PRIMARY KEY,
            order_id        VARCHAR(8)   UNIQUE NOT NULL,
            user_id         VARCHAR(36)  REFERENCES users(user_id) ON DELETE SET NULL,
            customer_name   VARCHAR(120) NOT NULL,
            phone           VARCHAR(20)  NOT NULL,
            delivery_address TEXT        NOT NULL,
            yam_type        VARCHAR(50)  NOT NULL,
            price_per_tuber INT          NOT NULL,
            quantity        INT          NOT NULL,
            total_price     INT          NOT NULL,
            status          VARCHAR(30)  NOT NULL DEFAULT 'pending',
            notes           TEXT,
            created_at      TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
            updated_at      TIMESTAMPTZ
        );
    """)

    conn.commit()
    cur.close()
    conn.close()
    print('✅  Database tables ready.')

# ============================================================
# JWT HELPERS
# ============================================================
def create_token(user_id, role):
    from datetime import timedelta
    payload = {
        'sub':  user_id,
        'role': role,
        'iat':  datetime.now(timezone.utc),
        'exp':  datetime.now(timezone.utc) + timedelta(hours=JWT_EXPIRY_HOURS)
    }
    return pyjwt.encode(payload, JWT_SECRET, algorithm='HS256')

def decode_token(token):
    return pyjwt.decode(token, JWT_SECRET, algorithms=['HS256'])

def jwt_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.headers.get('Authorization', '')
        if not auth.startswith('Bearer '):
            return jsonify({'success': False, 'message': 'Missing or invalid token'}), 401
        try:
            payload = decode_token(auth.split(' ', 1)[1])
            request.user_id = payload['sub']
            request.user_role = payload['role']
        except pyjwt.ExpiredSignatureError:
            return jsonify({'success': False, 'message': 'Token expired. Please log in again.'}), 401
        except pyjwt.InvalidTokenError:
            return jsonify({'success': False, 'message': 'Invalid token'}), 401
        return f(*args, **kwargs)
    return decorated

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('X-Admin-Token')
        if not token or token != ADMIN_TOKEN:
            return jsonify({'success': False, 'message': 'Admin access required'}), 401
        return f(*args, **kwargs)
    return decorated

# ============================================================
# HELPERS
# ============================================================
def gen_order_id():
    return str(uuid.uuid4())[:8].upper()

def gen_user_id():
    return str(uuid.uuid4())

def order_row_to_dict(row):
    """Convert a DB row to a JSON-serialisable dict."""
    d = dict(row)
    for k, v in d.items():
        if isinstance(v, datetime):
            d[k] = v.isoformat()
    # camelCase aliases the frontend expects
    return {
        'orderId':         d.get('order_id'),
        'userId':          d.get('user_id'),
        'customerName':    d.get('customer_name'),
        'phone':           d.get('phone'),
        'deliveryAddress': d.get('delivery_address'),
        'yamType':         d.get('yam_type'),
        'pricePerTuber':   d.get('price_per_tuber'),
        'quantity':        d.get('quantity'),
        'totalPrice':      d.get('total_price'),
        'status':          d.get('status'),
        'notes':           d.get('notes'),
        'createdAt':       d.get('created_at'),
        'updatedAt':       d.get('updated_at'),
    }

def user_row_to_dict(row, include_private=False):
    d = dict(row)
    for k, v in d.items():
        if isinstance(v, datetime):
            d[k] = v.isoformat()
    out = {
        'userId':          d.get('user_id'),
        'fullName':        d.get('full_name'),
        'email':           d.get('email'),
        'phone':           d.get('phone'),
        'whatsappNumber':  d.get('whatsapp_number'),
        'role':            d.get('role'),
        'createdAt':       d.get('created_at'),
    }
    return out

def send_whatsapp(order):
    if not WHATSAPP_ENABLED:
        return
    msg = (
        f"NEW ORDER!\n\n"
        f"Order ID: #{order['orderId']}\n"
        f"Customer: {order['customerName']}\n"
        f"Phone: {order['phone']}\n"
        f"Address: {order['deliveryAddress']}\n"
        f"Yam Type: {order['yamType']}\n"
        f"Price/tuber: NGN{order['pricePerTuber']:,}\n"
        f"Quantity: {order['quantity']}\n"
        f"Total: NGN{order['totalPrice']:,}\n"
        f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    )
    try:
        http_requests.post(GREEN_URL, json={'chatId': ADMIN_WA_NUMBER, 'message': msg},
                           timeout=10)
    except Exception as e:
        print(f'WhatsApp error: {e}')

# ============================================================
# STATIC ROUTES
# ============================================================
@app.route('/')
def serve_index():
    return send_from_directory('public', 'index.html')

@app.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory('public', filename)

# ============================================================
# HEALTH
# ============================================================
@app.route('/health')
def health():
    return jsonify({'status': 'OK', 'timestamp': datetime.now().isoformat()})

# ============================================================
# AUTH — REGISTER
# ============================================================
@app.route('/api/auth/register', methods=['POST'])
def register():
    data = request.get_json() or {}
    full_name       = data.get('fullName', '').strip()
    email           = data.get('email', '').strip().lower()
    phone           = data.get('phone', '').strip()
    whatsapp_number = data.get('whatsappNumber', '').strip()
    password        = data.get('password', '')

    # Validation
    if not full_name or len(full_name) < 2:
        return jsonify({'success': False, 'message': 'Full name is required (min 2 chars)'}), 400
    if not email or not re.match(r'^[^@]+@[^@]+\.[^@]+$', email):
        return jsonify({'success': False, 'message': 'A valid email address is required'}), 400
    if not password or len(password) < 6:
        return jsonify({'success': False, 'message': 'Password must be at least 6 characters'}), 400
    if phone and len(phone) > 11:
        return jsonify({'success': False, 'message': 'Phone number must not exceed 11 digits'}), 400
    if whatsapp_number and len(whatsapp_number) > 11:
        return jsonify({'success': False, 'message': 'WhatsApp number must not exceed 11 digits'}), 400

    pw_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    uid     = gen_user_id()

    try:
        conn = get_db()
        cur  = conn.cursor()
        cur.execute(
            """INSERT INTO users (user_id, full_name, email, phone, whatsapp_number, password_hash, role)
               VALUES (%s,%s,%s,%s,%s,%s,'customer') RETURNING *""",
            (uid, full_name, email, phone or None, whatsapp_number or phone or None, pw_hash)
        )
        user = user_row_to_dict(cur.fetchone())
        conn.commit()
        cur.close(); conn.close()
    except psycopg2.errors.UniqueViolation:
        return jsonify({'success': False, 'message': 'An account with that email already exists'}), 409
    except Exception as e:
        print(f'Register error: {e}')
        return jsonify({'success': False, 'message': 'Server error. Try again.'}), 500

    token = create_token(uid, 'customer')
    return jsonify({'success': True, 'message': 'Account created!', 'token': token, 'user': user}), 201

# ============================================================
# AUTH — LOGIN
# ============================================================
@app.route('/api/auth/login', methods=['POST'])
def login():
    data     = request.get_json() or {}
    email    = data.get('email', '').strip().lower()
    password = data.get('password', '')

    if not email or not password:
        return jsonify({'success': False, 'message': 'Email and password are required'}), 400

    try:
        conn = get_db()
        cur  = conn.cursor()
        cur.execute('SELECT * FROM users WHERE email = %s', (email,))
        row  = cur.fetchone()
        cur.close(); conn.close()
    except Exception as e:
        print(f'Login DB error: {e}')
        return jsonify({'success': False, 'message': 'Server error. Try again.'}), 500

    if not row:
        return jsonify({'success': False, 'message': 'Invalid email or password'}), 401

    if not bcrypt.checkpw(password.encode(), row['password_hash'].encode()):
        return jsonify({'success': False, 'message': 'Invalid email or password'}), 401

    user  = user_row_to_dict(row)
    token = create_token(row['user_id'], row['role'])
    return jsonify({'success': True, 'message': 'Logged in!', 'token': token, 'user': user})

# ============================================================
# AUTH — GET CURRENT USER
# ============================================================
@app.route('/api/auth/me', methods=['GET'])
@jwt_required
def me():
    try:
        conn = get_db()
        cur  = conn.cursor()
        cur.execute('SELECT * FROM users WHERE user_id = %s', (request.user_id,))
        row  = cur.fetchone()
        cur.close(); conn.close()
    except Exception as e:
        return jsonify({'success': False, 'message': 'Server error'}), 500

    if not row:
        return jsonify({'success': False, 'message': 'User not found'}), 404
    return jsonify({'success': True, 'user': user_row_to_dict(row)})

# ============================================================
# ORDERS — CREATE (requires JWT)
# ============================================================
@app.route('/api/orders', methods=['POST'])
@jwt_required
def create_order():
    data = request.get_json() or {}

    # Validate
    errors = []
    name    = data.get('customerName', '').strip()
    phone   = data.get('phone', '').strip()
    address = data.get('deliveryAddress', '').strip()
    yam     = data.get('yamType')
    price   = data.get('pricePerTuber')
    qty     = data.get('quantity')

    if not name or len(name) < 2:        errors.append('Full name required')
    if not phone or len(phone) < 7:      errors.append('Valid phone required')
    if not address or len(address) < 5:  errors.append('Delivery address required')
    if yam not in VALID_YAM_TYPES:       errors.append('Invalid yam type')
    if not isinstance(price, (int,float)) or not (MIN_PRICE <= price <= MAX_PRICE):
        errors.append(f'Price must be between NGN{MIN_PRICE} and NGN{MAX_PRICE}')
    if not isinstance(qty, int) or qty < 1:
        errors.append('Quantity must be at least 1')

    if errors:
        return jsonify({'success': False, 'message': errors[0]}), 400

    order_id    = gen_order_id()
    total_price = int(price) * int(qty)

    try:
        conn = get_db()
        cur  = conn.cursor()
        cur.execute(
            """INSERT INTO orders
               (order_id, user_id, customer_name, phone, delivery_address,
                yam_type, price_per_tuber, quantity, total_price, status)
               VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,'pending') RETURNING *""",
            (order_id, request.user_id, name, phone, address,
             yam, int(price), int(qty), total_price)
        )
        order = order_row_to_dict(cur.fetchone())
        conn.commit()
        cur.close(); conn.close()
    except Exception as e:
        print(f'Create order error: {e}')
        return jsonify({'success': False, 'message': 'Server error'}), 500

    thread = threading.Thread(target=send_whatsapp, args=(order,), daemon=True)
    thread.start()

    return jsonify({'success': True, 'message': 'Order placed!', 'orderId': order_id, 'order': order}), 201

# ============================================================
# ORDERS — GET MY ORDERS (JWT)
# ============================================================
@app.route('/api/orders/mine', methods=['GET'])
@jwt_required
def my_orders():
    try:
        conn = get_db()
        cur  = conn.cursor()
        cur.execute('SELECT * FROM orders WHERE user_id=%s ORDER BY created_at DESC', (request.user_id,))
        rows = [order_row_to_dict(r) for r in cur.fetchall()]
        cur.close(); conn.close()
    except Exception as e:
        return jsonify({'success': False, 'message': 'Server error'}), 500
    return jsonify({'success': True, 'orders': rows})

# ============================================================
# ORDERS — TRACK BY ID (public)
# ============================================================
@app.route('/api/orders/<order_id>', methods=['GET'])
def track_order(order_id):
    try:
        conn = get_db()
        cur  = conn.cursor()
        cur.execute('SELECT * FROM orders WHERE order_id=%s', (order_id.upper(),))
        row  = cur.fetchone()
        cur.close(); conn.close()
    except Exception as e:
        return jsonify({'success': False, 'message': 'Server error'}), 500
    if not row:
        return jsonify({'success': False, 'message': 'Order not found'}), 404
    return jsonify({'success': True, 'order': order_row_to_dict(row)})

# ============================================================
# ADMIN — GET ALL ORDERS
# ============================================================
@app.route('/api/admin/orders', methods=['GET'])
@admin_required
def admin_get_orders():
    status_f = request.args.get('status')
    search   = request.args.get('search', '').strip()
    try:
        conn = get_db()
        cur  = conn.cursor()
        q    = 'SELECT * FROM orders WHERE 1=1'
        params = []
        if status_f and status_f != 'all':
            q += ' AND status=%s'; params.append(status_f)
        if search:
            q += ' AND (customer_name ILIKE %s OR phone ILIKE %s OR order_id ILIKE %s)'
            s = f'%{search}%'
            params += [s, s, s]
        q += ' ORDER BY created_at DESC'
        cur.execute(q, params)
        rows = [order_row_to_dict(r) for r in cur.fetchall()]
        cur.close(); conn.close()
    except Exception as e:
        print(f'Admin orders error: {e}')
        return jsonify({'success': False, 'message': 'Server error'}), 500
    return jsonify({'success': True, 'count': len(rows), 'orders': rows})

# ============================================================
# ADMIN — UPDATE ORDER STATUS
# ============================================================
@app.route('/api/admin/orders/<order_id>/status', methods=['POST'])
@admin_required
def admin_update_status(order_id):
    data   = request.get_json() or {}
    status = data.get('status')
    notes  = data.get('notes', '')
    if status not in VALID_STATUSES:
        return jsonify({'success': False, 'message': 'Invalid status'}), 400
    try:
        conn = get_db()
        cur  = conn.cursor()
        cur.execute(
            """UPDATE orders SET status=%s, notes=%s, updated_at=NOW()
               WHERE order_id=%s RETURNING *""",
            (status, notes or None, order_id.upper())
        )
        row = cur.fetchone()
        conn.commit()
        cur.close(); conn.close()
    except Exception as e:
        return jsonify({'success': False, 'message': 'Server error'}), 500
    if not row:
        return jsonify({'success': False, 'message': 'Order not found'}), 404
    return jsonify({'success': True, 'order': order_row_to_dict(row)})

# ============================================================
# ADMIN — DELETE ORDER
# ============================================================
@app.route('/api/admin/orders/<order_id>', methods=['DELETE'])
@admin_required
def admin_delete_order(order_id):
    try:
        conn = get_db()
        cur  = conn.cursor()
        cur.execute('DELETE FROM orders WHERE order_id=%s RETURNING order_id', (order_id.upper(),))
        deleted = cur.fetchone()
        conn.commit()
        cur.close(); conn.close()
    except Exception as e:
        return jsonify({'success': False, 'message': 'Server error'}), 500
    if not deleted:
        return jsonify({'success': False, 'message': 'Order not found'}), 404
    return jsonify({'success': True, 'message': 'Order deleted'})

# ============================================================
# ADMIN — GET ALL USERS
# ============================================================
@app.route('/api/admin/users', methods=['GET'])
@admin_required
def admin_get_users():
    search = request.args.get('search', '').strip()
    try:
        conn = get_db()
        cur  = conn.cursor()
        q    = 'SELECT * FROM users WHERE 1=1'
        params = []
        if search:
            q += ' AND (full_name ILIKE %s OR email ILIKE %s)'
            s  = f'%{search}%'
            params += [s, s]
        q += ' ORDER BY created_at DESC'
        cur.execute(q, params)
        rows = [user_row_to_dict(r) for r in cur.fetchall()]
        cur.close(); conn.close()
    except Exception as e:
        print(f'Admin users error: {e}')
        return jsonify({'success': False, 'message': 'Server error'}), 500
    return jsonify({'success': True, 'count': len(rows), 'users': rows})

# ============================================================
# ADMIN — DELETE USER
# ============================================================
@app.route('/api/admin/users/<user_id>', methods=['DELETE'])
@admin_required
def admin_delete_user(user_id):
    try:
        conn = get_db()
        cur  = conn.cursor()
        cur.execute('DELETE FROM users WHERE user_id=%s RETURNING user_id', (user_id,))
        deleted = cur.fetchone()
        conn.commit()
        cur.close(); conn.close()
    except Exception as e:
        return jsonify({'success': False, 'message': 'Server error'}), 500
    if not deleted:
        return jsonify({'success': False, 'message': 'User not found'}), 404
    return jsonify({'success': True, 'message': 'User deleted'})

# ============================================================
# ADMIN — STATS
# ============================================================
@app.route('/api/admin/stats', methods=['GET'])
@admin_required
def admin_stats():
    try:
        conn = get_db()
        cur  = conn.cursor()
        cur.execute('SELECT COUNT(*) as total FROM orders')
        total_orders = cur.fetchone()['total']
        cur.execute('SELECT COALESCE(SUM(total_price),0) as rev FROM orders WHERE status != %s', ('cancelled',))
        revenue = cur.fetchone()['rev']
        cur.execute("SELECT COUNT(*) as c FROM orders WHERE status='pending'")
        pending = cur.fetchone()['c']
        cur.execute("SELECT COUNT(*) as c FROM orders WHERE status='delivered'")
        delivered = cur.fetchone()['c']
        cur.execute("SELECT COUNT(*) as c FROM orders WHERE status='dispatched'")
        dispatched = cur.fetchone()['c']
        cur.execute("SELECT COUNT(*) as c FROM orders WHERE status='cancelled'")
        cancelled = cur.fetchone()['c']
        cur.execute('SELECT COUNT(*) as c FROM users')
        total_users = cur.fetchone()['c']
        cur.execute("SELECT COUNT(*) as c FROM orders WHERE created_at >= NOW() - INTERVAL '7 days'")
        week_orders = cur.fetchone()['c']
        cur.close(); conn.close()
    except Exception as e:
        print(f'Stats error: {e}')
        return jsonify({'success': False, 'message': 'Server error'}), 500
    return jsonify({
        'success':     True,
        'totalOrders': int(total_orders),
        'revenue':     int(revenue),
        'pending':     int(pending),
        'delivered':   int(delivered),
        'dispatched':  int(dispatched),
        'cancelled':   int(cancelled),
        'totalUsers':  int(total_users),
        'weekOrders':  int(week_orders),
    })

# ============================================================
# ERROR HANDLERS
# ============================================================
@app.errorhandler(404)
def not_found(e):
    return jsonify({'success': False, 'message': 'Not found'}), 404

@app.errorhandler(500)
def server_error(e):
    return jsonify({'success': False, 'message': 'Internal server error'}), 500

# ============================================================
# STARTUP
# ============================================================
if __name__ == '__main__':
    print('\n' + '='*52)
    print("   NK's YAMS — API SERVER")
    print('='*52)
    if DATABASE_URL:
        try:
            init_db()
        except Exception as e:
            print(f'DB init warning: {e}')
    else:
        print('WARNING: DATABASE_URL not set — DB features disabled.')
    print(f'  http://localhost:5000')
    print('='*52 + '\n')
    app.run(debug=True, host='0.0.0.0', port=5000)
