from flask import Flask, request, jsonify
import sqlite3

app = Flask(__name__)

# 连接 SQLite 数据库
conn = sqlite3.connect('restaurant.db')
cursor = conn.cursor()

# 创建表格，如果不存在
cursor.execute('''
    CREATE TABLE IF NOT EXISTS restaurants (
        id INTEGER PRIMARY KEY,  -- 餐厅 ID
        name TEXT,  -- 餐厅名称
        address TEXT,  -- 餐厅地址
        phone TEXT  -- 餐厅电话
    )
''')
cursor.execute('''
    CREATE TABLE IF NOT EXISTS menu_items (
        id INTEGER PRIMARY KEY,  -- 菜单项 ID
        restaurant_id INTEGER,  -- 所属餐厅 ID
        name TEXT,  -- 菜单项名称
        price REAL,  -- 菜单项价格
        FOREIGN KEY (restaurant_id) REFERENCES restaurants (id)  -- 外键关联餐厅
    )
''')
conn.commit()

# API 路由

# 获取所有餐厅
@app.route('/restaurants', methods=['GET'])
def get_restaurants():
    cursor.execute('SELECT * FROM restaurants')
    restaurants = cursor.fetchall()
    return jsonify([{'id': r[0], 'name': r[1], 'address': r[2], 'phone': r[3]} for r in restaurants])

# 获取单个餐厅
@app.route('/restaurants/<int:restaurant_id>', methods=['GET'])
def get_restaurant(restaurant_id):
    cursor.execute('SELECT * FROM restaurants WHERE id = ?', (restaurant_id,))
    restaurant = cursor.fetchone()
    if restaurant:
        return jsonify({'id': restaurant[0], 'name': restaurant[1], 'address': restaurant[2], 'phone': restaurant[3]})
    else:
        return jsonify({'error': '餐厅不存在'}), 404

# 获取餐厅菜单
@app.route('/restaurants/<int:restaurant_id>/menu', methods=['GET'])
def get_menu(restaurant_id):
    cursor.execute('SELECT * FROM menu_items WHERE restaurant_id = ?', (restaurant_id,))
    menu_items = cursor.fetchall()
    return jsonify([{'id': mi[0], 'name': mi[2], 'price': mi[3]} for mi in menu_items])

# 创建新餐厅
@app.route('/restaurants', methods=['POST'])
def create_restaurant():
    data = request.get_json()
    cursor.execute('INSERT INTO restaurants (name, address, phone) VALUES (?, ?, ?)',
                   (data['name'], data['address'], data['phone']))
    conn.commit()
    return jsonify({'id': cursor.lastrowid, 'name': data['name'], 'address': data['address'], 'phone': data['phone']})

# 创建新菜单项
@app.route('/restaurants/<int:restaurant_id>/menu', methods=['POST'])
def create_menu_item(restaurant_id):
    data = request.get_json()
    cursor.execute('INSERT INTO menu_items (restaurant_id, name, price) VALUES (?, ?, ?)',
                   (restaurant_id, data['name'], data['price']))
    conn.commit()
    return jsonify({'id': cursor.lastrowid, 'name': data['name'], 'price': data['price']})

# 更新餐厅信息
@app.route('/restaurants/<int:restaurant_id>', methods=['PUT'])
def update_restaurant(restaurant_id):
    data = request.get_json()
    cursor.execute('UPDATE restaurants SET name = ?, address = ?, phone = ? WHERE id = ?',
                   (data['name'], data['address'], data['phone'], restaurant_id))
    conn.commit()
    return jsonify({'id': restaurant_id, 'name': data['name'], 'address': data['address'], 'phone': data['phone']})

# 删除餐厅
@app.route('/restaurants/<int:restaurant_id>', methods=['DELETE'])
def delete_restaurant(restaurant_id):
    cursor.execute('DELETE FROM restaurants WHERE id = ?', (restaurant_id,))
    conn.commit()
    return jsonify({'message': '餐厅删除成功'})

# 更新菜单项
@app.route('/restaurants/<int:restaurant_id>/menu/<int:menu_item_id>', methods=['PUT'])
def update_menu_item(restaurant_id, menu_item_id):
    data = request.get_json()
    cursor.execute('UPDATE menu_items SET name = ?, price = ? WHERE id = ? AND restaurant_id = ?',
                   (data['name'], data['price'], menu_item_id, restaurant_id))
    conn.commit()
    return jsonify({'id': menu_item_id, 'name': data['name'], 'price': data['price']})

# 删除菜单项
@app.route('/restaurants/<int:restaurant_id>/menu/<int:menu_item_id>', methods=['DELETE'])
def delete_menu_item(restaurant_id, menu_item_id):
    cursor.execute('DELETE FROM menu_items WHERE id = ? AND restaurant_id = ?', (menu_item_id, restaurant_id))
    conn.commit()
    return jsonify({'message': '菜单项删除成功'})

if __name__ == '__main__':
    app.run(debug=True)
