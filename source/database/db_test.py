import mysql.connector
import os

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

def get_db_connection():
    connection = mysql.connector.connect(
        host=os.getenv('DB_HOST', ''),  # Default to 'localhost' if environment variable is not set
        user=os.getenv('DB_USER', ''),
        password=os.getenv('DB_PASSWORD', ''),
        database=os.getenv('DB_NAME', '')
    )
    return connection

def health_check():
    try:
        # Attempt to connect to the database
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT 1")
        cursor.close()
        connection.close()

        return jsonify({"status": "healthy"}), 200
    except Exception as e:
        return jsonify({"status": "unhealthy", "error": str(e)}), 500


print(health_check())
