import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)
CORS(app)

DATABASE_URL = os.getenv('DATABASE_URL')

def get_conn():
    return psycopg2.connect(DATABASE_URL)

def init_db():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id SERIAL PRIMARY KEY,
            product_id VARCHAR(100) NOT NULL,
            quantity INTEGER NOT NULL,
            status VARCHAR(50) DEFAULT 'pending'
        )
    ''')
    conn.commit()
    cur.close()
    conn.close()

@app.route('/health')
def health():
    return jsonify({'status': 'ok', 'service': 'order-service'})

@app.route('/orders', methods=['GET'])
def get_orders():
    conn = get_conn()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute('SELECT * FROM orders')
    orders = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify(orders)

@app.route('/orders', methods=['POST'])
def create_order():
    data = request.get_json()
    conn = get_conn()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute(
        'INSERT INTO orders (product_id, quantity) VALUES (%s, %s) RETURNING *',
        (data['product_id'], data['quantity'])
    )
    order = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()
    return jsonify(order), 201

@app.route('/orders/<int:order_id>', methods=['PUT'])
def update_order(order_id):
    data = request.get_json() or {}
    product_id = data.get('product_id')
    quantity = data.get('quantity')
    status = data.get('status', 'pending')

    if product_id is None or quantity is None:
        return jsonify({'error': 'product_id and quantity are required'}), 400

    conn = get_conn()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute(
        'UPDATE orders SET product_id=%s, quantity=%s, status=%s WHERE id=%s RETURNING *',
        (product_id, quantity, status, order_id)
    )
    order = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()

    if not order:
        return jsonify({'error': 'Order not found'}), 404

    return jsonify(order)

@app.route('/orders/<int:order_id>', methods=['DELETE'])
def delete_order(order_id):
    conn = get_conn()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute('DELETE FROM orders WHERE id=%s RETURNING *', (order_id,))
    deleted = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()

    if not deleted:
        return jsonify({'error': 'Order not found'}), 404

    return jsonify({'deleted': True, 'order': deleted})

if __name__ == '__main__':
    init_db()
    port = int(os.getenv('PORT', 4002))
    app.run(host='0.0.0.0', port=port, debug=True)