from flask import Flask, jsonify, request
from flask_cors import CORS
import mysql.connector
import os
import socket

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

def get_db_connection():
    """Establish a database connection using environment variables."""
    connection = mysql.connector.connect(
        host=os.getenv('DB_HOST', 'localhost'),  
        user=os.getenv('DB_USER', 'root'),
        password=os.getenv('DB_PASSWORD', ''),
        database=os.getenv('DB_NAME', 'msdatabase')
    )
    return connection

@app.route('/orders/health', methods=['GET'])
def health_check():
    """Check API and database health."""
    try:
        server_ip = socket.gethostbyname(socket.gethostname())
        #connection = get_db_connection()
        #cursor = connection.cursor()
        #cursor.execute("SELECT 1")
        #cursor.fetchall()
        #cursor.close()
        #connection.close()
        return jsonify({"status": "healthy", "server_ip-V2": server_ip}), 200
    except Exception as e:
        return jsonify({"status": "unhealthy", "error": str(e)}), 500

@app.route('/orders/list_orders', methods=['GET'])
def get_orders():
    """Fetch all orders with product and user details."""
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        query = """
            SELECT 
                orders.id AS order_id, 
                orders.quantity AS ordered_quantity, 
                orders.created_at AS order_date, 
                products.name AS product_name, 
                products.price AS product_price, 
                users.username AS ordered_by
            FROM orders
            JOIN products ON orders.product_id = products.id
            JOIN users ON orders.user_id = users.id
            ORDER BY orders.created_at DESC
        """

        cursor.execute(query)
        orders = cursor.fetchall()

        cursor.close()
        connection.close()

        return jsonify(orders)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/orders/add_order', methods=['POST'])
def add_order():
    """Place an order and deduct stock from the product table."""
    product_id = request.json.get('product_id')
    quantity = request.json.get('quantity')
    user_id = request.json.get('user_id')

    if not all([product_id, quantity, user_id]):
        return jsonify({"error": "Missing fields"}), 400

    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        # Check if product exists and has enough stock
        cursor.execute("SELECT quantity FROM products WHERE id = %s FOR UPDATE", (product_id,))
        product = cursor.fetchone()

        if not product:
            return jsonify({"error": "Product not found"}), 404

        available_stock = product[0]
        if available_stock < quantity:
            return jsonify({"error": "Not enough stock available"}), 400

        # Reduce stock in products table
        cursor.execute("UPDATE products SET quantity = quantity - %s WHERE id = %s", (quantity, product_id))

        # Insert order into orders table
        cursor.execute("INSERT INTO orders (product_id, quantity, user_id) VALUES (%s, %s, %s)",
                       (product_id, quantity, user_id))

        connection.commit()  # Commit both operations

        return jsonify({"message": "Order placed successfully!"}), 201

    except Exception as e:
        connection.rollback()  # Rollback if any error occurs
        return jsonify({"error": str(e)}), 500

    finally:
        cursor.close()
        connection.close()

@app.route('/orders/delete_order/<int:order_id>', methods=['DELETE'])
def delete_order(order_id):
    """Delete an order."""
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute("DELETE FROM orders WHERE id = %s", (order_id,))
        connection.commit()

        cursor.close()
        connection.close()

        return jsonify({"message": "Order deleted successfully!"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)

