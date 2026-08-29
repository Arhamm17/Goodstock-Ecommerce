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

if __name__ == '__main__':
    init_db()
    port = int(os.getenv('PORT', 4002))
    app.run(host='0.0.0.0', port=port, debug=True)