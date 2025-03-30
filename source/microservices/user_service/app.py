from flask import Flask, jsonify, request, send_from_directory,send_file
from flask_cors import CORS
import mysql.connector
import bcrypt
import os

app = Flask(__name__)
CORS(app)
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def get_db_connection():
    connection = mysql.connector.connect(
        host=os.getenv('DB_HOST', '192.168.0.99'),  # Default to 'localhost' if environment variable is not set
        user=os.getenv('DB_USER', 'msuser'),
        password=os.getenv('DB_PASSWORD', 'mspassword'),
        database=os.getenv('DB_NAME', 'msdatabase')
    )
    return connection

@app.route('/health', methods=['GET'])
def health_check():
    try:
        # Attempt to connect to the database
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT 1")
        cursor.fetchall()
        cursor.close()
        connection.close()

        return jsonify({"status": "healthy V2"}), 200
    except Exception as e:
        return jsonify({"status": "unhealthy", "error": str(e)}), 500

# Create User
@app.route('/signup', methods=['POST'])
def signup():
    # Get form fields from the request
    username = request.form.get('username')
    first_name = request.form.get('firstName')
    last_name = request.form.get('lastName')
    email = request.form.get('email')
    mobile = request.form.get('mobile')
    password = request.form.get('password')

    # Validate required fields
    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400

    # Handle profile picture upload
    profile_pic = request.files.get('profilePic')
    profile_pic_filename = None

    if profile_pic and profile_pic.filename:
        profile_pic_filename = f"{username}_{profile_pic.filename}"
        profile_pic_path = os.path.join(UPLOAD_FOLDER, profile_pic_filename)
        profile_pic.save(profile_pic_path)

    # Hash the password before storing it
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    # Store user in the database
    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        cursor.execute("""
            INSERT INTO users (username, first_name, last_name, email, mobile, password, profile_pic) 
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (username, first_name, last_name, email, mobile, hashed_password, profile_pic_filename))
        
        connection.commit()
        return jsonify({"message": "User created successfully!"}), 201
    except mysql.connector.Error as err:
        return jsonify({"error": str(err)}), 500
    finally:
        cursor.close()
        connection.close()


@app.route('/profile-pic/<username>', methods=['GET'])
def get_profile_pic(username):
    print(username)
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("SELECT profile_pic FROM users WHERE username = %s", (username,))
    user = cursor.fetchone()

    cursor.close()
    connection.close()
    if user and user['profile_pic']:
        image_path = os.path.join(UPLOAD_FOLDER, user['profile_pic'])
        if os.path.exists(image_path):
            return send_from_directory(UPLOAD_FOLDER, user['profile_pic'])
        else:
            return jsonify({"error": "Image not found"}), 404
    else:
        return jsonify({"error": "User or profile picture not found"}), 404

@app.route('/login', methods=['POST'])
def login():
    username = request.json.get('username')
    password = request.json.get('password')

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    
    cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
    user = cursor.fetchone()
    
    cursor.close()
    connection.close()

    if user and bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
        return jsonify({"message": "Login successful!"}), 200
    else:
        return jsonify({"message": "Invalid username or password."}), 401

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
