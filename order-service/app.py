import os
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)
CORS(app)

DATABASE_URL = os.getenv('DATABASE_URL')
API_GATEWAY_URL = os.getenv('API_GATEWAY_URL', 'http://api-gateway')


class ProductServiceError(Exception):
    pass


class InsufficientStockError(ProductServiceError):
    pass


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


def gateway_url(path):
    return f"{API_GATEWAY_URL.rstrip('/')}{path}"


def parse_quantity(value, field_name='quantity'):
    if value is None or isinstance(value, bool):
        raise ValueError(f'{field_name} is required')

    try:
        quantity = int(value)
    except (TypeError, ValueError):
        raise ValueError(f'{field_name} must be a valid integer')

    if quantity < 1:
        raise ValueError(f'{field_name} must be greater than or equal to 1')

    return quantity


def fetch_product(product_id):
    response = requests.get(gateway_url(f'/api/products/{product_id}'), timeout=5)
    if response.status_code == 404:
        return None
    if response.status_code >= 400:
        raise ProductServiceError(f'Product service returned {response.status_code}')
    return response.json()


def ensure_product_available(product_id, quantity):
    product = fetch_product(product_id)
    if product is None:
        return None

    stock = int(product.get('stock') or 0)
    if quantity > stock:
        raise InsufficientStockError(f'Only {stock} item(s) available in stock')

    return product


def patch_product_stock(product_id, delta):
    response = requests.patch(
        gateway_url(f'/api/products/{product_id}/stock'),
        json={'delta': delta},
        timeout=5,
    )

    if response.status_code == 200:
        return response.json()

    if response.status_code == 400:
        payload = response.json() if response.content else {}
        raise InsufficientStockError(payload.get('error', 'Insufficient stock'))

    raise ProductServiceError(f'Product service returned {response.status_code}')


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
    data = request.get_json(silent=True)
    if not data:
        return jsonify({'error': 'JSON body required'}), 400

    product_id = data.get('product_id')
    if product_id in (None, ''):
        return jsonify({'error': 'product_id is required'}), 400

    try:
        quantity = parse_quantity(data.get('quantity'))
    except ValueError as exc:
        return jsonify({'error': str(exc)}), 400

    try:
        product = ensure_product_available(product_id, quantity)
    except InsufficientStockError as exc:
        return jsonify({'error': str(exc)}), 400
    except requests.RequestException:
        return jsonify({'error': 'Product service unavailable'}), 502
    except ProductServiceError:
        return jsonify({'error': 'Product service unavailable'}), 502

    if product is None:
        return jsonify({'error': 'Product not found'}), 404

    conn = get_conn()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute(
        'INSERT INTO orders (product_id, quantity, status) VALUES (%s, %s, %s) RETURNING *',
        (str(product_id), quantity, 'pending')
    )
    order = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()
    return jsonify(order), 201


@app.route('/orders/<int:order_id>', methods=['PUT'])
def update_order(order_id):
    data = request.get_json(silent=True) or {}
    if not data:
        return jsonify({'error': 'JSON body required'}), 400

    if 'product_id' not in data or 'quantity' not in data:
        return jsonify({'error': 'product_id and quantity are required'}), 400

    product_id = data.get('product_id')
    if product_id in (None, ''):
        return jsonify({'error': 'product_id is required'}), 400

    try:
        quantity = parse_quantity(data.get('quantity'))
    except ValueError as exc:
        return jsonify({'error': str(exc)}), 400

    status = data.get('status', 'pending')
    if status not in {'pending', 'completed'}:
        return jsonify({'error': 'status must be pending or completed'}), 400

    conn = get_conn()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute('SELECT * FROM orders WHERE id=%s', (order_id,))
    order = cur.fetchone()
    cur.close()
    conn.close()

    if not order:
        return jsonify({'error': 'Order not found'}), 404

    existing_status = str(order.get('status') or 'pending')
    product_id_str = str(product_id)
    current_product_id = str(order.get('product_id'))
    current_quantity = int(order.get('quantity') or 0)

    if existing_status == 'completed' and status == 'completed':
        return jsonify(order)

    if existing_status == 'pending' and (product_id_str != current_product_id or quantity != current_quantity):
        try:
            product = ensure_product_available(product_id_str, quantity)
        except InsufficientStockError as exc:
            return jsonify({'error': str(exc)}), 400
        except requests.RequestException:
            return jsonify({'error': 'Product service unavailable'}), 502
        except ProductServiceError:
            return jsonify({'error': 'Product service unavailable'}), 502

        if product is None:
            return jsonify({'error': 'Product not found'}), 404

    if existing_status == 'pending' and status == 'completed':
        try:
            patch_product_stock(product_id_str, -quantity)
        except InsufficientStockError as exc:
            return jsonify({'error': str(exc)}), 400
        except requests.RequestException:
            return jsonify({'error': 'Product service unavailable'}), 502
        except ProductServiceError:
            return jsonify({'error': 'Product service unavailable'}), 502

        try:
            conn = get_conn()
            cur = conn.cursor(cursor_factory=RealDictCursor)
            cur.execute(
                'UPDATE orders SET product_id=%s, quantity=%s, status=%s WHERE id=%s RETURNING *',
                (product_id_str, quantity, 'completed', order_id)
            )
            updated_order = cur.fetchone()
            conn.commit()
            cur.close()
            conn.close()

            if not updated_order:
                try:
                    patch_product_stock(product_id_str, quantity)
                except Exception:
                    app.logger.exception('Compensating stock adjustment failed after order update failure')
                return jsonify({'error': 'Order not found'}), 404

            return jsonify(updated_order)
        except Exception:
            app.logger.exception('Failed to complete order %s; attempting compensation', order_id)
            try:
                patch_product_stock(product_id_str, quantity)
            except Exception:
                app.logger.exception('Compensating stock adjustment failed for order %s', order_id)
            return jsonify({'error': 'Could not update order'}), 500

    conn = get_conn()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute(
        'UPDATE orders SET product_id=%s, quantity=%s, status=%s WHERE id=%s RETURNING *',
        (product_id_str, quantity, status, order_id)
    )
    updated_order = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()

    if not updated_order:
        return jsonify({'error': 'Order not found'}), 404

    return jsonify(updated_order)


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

    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute('SELECT setval(pg_get_serial_sequence(\'orders\', \'id\'), COALESCE((SELECT MAX(id) FROM orders), 0), true)')
        conn.commit()
        cur.close()
        conn.close()
    except Exception:
        app.logger.exception('Failed to reset order id sequence after delete')

    return jsonify({'deleted': True, 'order': deleted})


@app.route('/orders/complete', methods=['POST'])
def clear_completed_orders():
    conn = get_conn()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute('DELETE FROM orders WHERE status=%s RETURNING *', ('completed',))
    deleted = cur.fetchall()
    conn.commit()
    cur.close()
    conn.close()

    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute('SELECT setval(pg_get_serial_sequence(\'orders\', \'id\'), 0, true)')
        conn.commit()
        cur.close()
        conn.close()
    except Exception:
        app.logger.exception('Failed to reset order sequence after clearing completed orders')

    return jsonify({'deleted': len(deleted), 'orders': deleted})


if __name__ == '__main__':
    init_db()
    port = int(os.getenv('PORT', 4002))
    app.run(host='0.0.0.0', port=port, debug=True)