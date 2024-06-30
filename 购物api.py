from flask import Flask, request, jsonify
import sqlite3

app = Flask(__name__)

# 连接 SQLite 数据库
conn = sqlite3.connect('shopping_platform.db')
cursor = conn.cursor()

# 创建表格，如果不存在
cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,  -- 用户 ID
        username TEXT,  -- 用户名
        password TEXT,  -- 密码
        email TEXT,  -- 电子邮件
        address TEXT,  -- 地址
        phone TEXT  -- 电话
    )
''')
cursor.execute('''
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY,  -- 产品 ID
        name TEXT,  -- 产品名称
        price REAL,  -- 产品价格
        description TEXT,  -- 产品描述
        image_url TEXT,  -- 产品图片 URL
        stock INTEGER  -- 产品库存
    )
''')
cursor.execute('''
    CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY,  -- 订单 ID
        user_id INTEGER,  -- 用户 ID
        product_id INTEGER,  -- 产品 ID
        quantity INTEGER,  -- 数量
        total_price REAL,  -- 总价格
        order_status TEXT,  -- 订单状态
        created_at TEXT,  -- 创建时间
        updated_at TEXT,  -- 更新时间
        FOREIGN KEY (user_id) REFERENCES users (id),
        FOREIGN KEY (product_id) REFERENCES products (id)
    )
''')
cursor.execute('''
    CREATE TABLE IF NOT EXISTS order_items (
        id INTEGER PRIMARY KEY,  -- 订单项 ID
        order_id INTEGER,  -- 订单 ID
        product_id INTEGER,  -- 产品 ID
        quantity INTEGER,  -- 数量
        price REAL,  -- 价格
        FOREIGN KEY (order_id) REFERENCES orders (id),
        FOREIGN KEY (product_id) REFERENCES products (id)
    )
''')
conn.commit()

# API 路由

# 获取所有用户
@app.route('/users', methods=['GET'])
def get_users():
    cursor.execute('SELECT * FROM users')
    users = cursor.fetchall()
    return jsonify([{'id': u[0], 'username': u[1], 'email': u[3], 'address': u[4], 'phone': u[5]} for u in users])

# 获取单个用户
@app.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
    user = cursor.fetchone()
    if user:
        return jsonify({'id': user[0], 'username': user[1], 'email': user[3], 'address': user[4], 'phone': user[5]})
    else:
        return jsonify({'error': '用户不存在'}), 404

# 获取所有产品
@app.route('/products', methods=['GET'])
def get_products():
    cursor.execute('SELECT * FROM products')
    products = cursor.fetchall()
    return jsonify([{'id': p[0], 'name': p[1], 'price': p[2], 'description': p[3], 'image_url': p[4], 'stock': p[5]} for p in products])

# 获取单个产品
@app.route('/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    cursor.execute('SELECT * FROM products WHERE id = ?', (product_id,))
    product = cursor.fetchone()
    if product:
        return jsonify({'id': product[0], 'name': product[1], 'price': product[2], 'description': product[3], 'image_url': product[4], 'stock': product[5]})
    else:
        return jsonify({'error': '产品不存在'}), 404

# 创建新订单
@app.route('/orders', methods=['POST'])
def create_order():
    data = request.get_json()
    cursor.execute('INSERT INTO orders (user_id, product_id, quantity, total_price, order_status, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?)',
                   (data['user_id'], data['product_id'], data['quantity'], data['total_price'], 'pending', datetime.now(), datetime.now()))
    conn.commit()
    order_id = cursor.lastrowid
    cursor.execute('INSERT INTO order_items (order_id, product_id, quantity, price) VALUES (?, ?, ?, ?)',
                   (order_id, data['product_id'], data['quantity'], data['total_price']))
    conn.commit()
    return jsonify({'id': order_id, 'user_id': data['user_id'], 'product_id': data['product_id'], 'quantity': data['quantity'], 'total_price': data['total_price']})

# 获取所有订单
@app.route('/orders', methods=['GET'])
def get_orders():
    cursor.execute('SELECT * FROM orders')
    orders = cursor.fetchall()
    return jsonify([{'id': o[0], 'user_id': o[1], 'product_id': o[2], 'quantity': o[3], 'total_price': o[4], 'order_status': o[5], 'created_at': o[6], 'updated_at': o[7]} for o in orders])

# 获取单个订单
@app.route('/orders/<int:order_id>', methods=['GET'])
def get_order(order_id):
    cursor.execute('SELECT * FROM orders WHERE id = ?', (order_id,))
    order = cursor.fetchone()
    if order:
        return jsonify({'id': order[0], 'user_id': order[1], 'product_id': order[2], 'quantity': order[3], 'total_price': order[4], 'order_status': order[5], 'created_at': order[6], 'updated_at': order[7]})
    else:
        return jsonify({'error': '订单不存在'}), 404

# 更新订单状态
@app.route('/orders/<int:order_id>', methods=['PUT'])
def update_order_status(order_id):
    data = request.get_json()
    cursor.execute('UPDATE orders SET order_status = ? WHERE id = ?', (data['order_status'], order_id))
    conn.commit()
    return jsonify({'id': order_id, 'order_status': data['order_status']})

# 删除订单
@app.route('/orders/<int:order_id>', methods=['DELETE'])
def delete_order(order_id):
    cursor.execute('DELETE FROM orders WHERE id = ?', (o
