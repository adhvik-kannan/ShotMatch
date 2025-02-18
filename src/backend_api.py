from flask import Flask, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime
from functools import wraps
from database import connect_to_mongodb, add_user, get_all_users, get_user_by_hash, remove_user_by_name, get_user_by_email
import time

# Constants
SECRET_KEY = "your_secret_key"
DB_NAME = "auth_db"

# Initialize Flask App
app = Flask(__name__)

# Connect to MongoDB
success, db = connect_to_mongodb(DB_NAME)
if not success:
    raise Exception("Failed to connect to MongoDB")
users_collection = db["users"]

# Helper Functions
def create_jwt_token(username):
    expiration = datetime.datetime.utcnow() + datetime.timedelta(hours=2)
    token = jwt.encode({"sub": username, "exp": expiration}, SECRET_KEY, algorithm="HS256")
    return token

def decode_jwt_token(token):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload["sub"]
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get("Authorization")
        if not token:
            return jsonify({"message": "Token is missing!"}), 401
        try:
            token = token.split()[1]
            username = decode_jwt_token(token)
            if not username:
                return jsonify({"message": "Invalid token!"}), 401
        except:
            return jsonify({"message": "Token is invalid!"}), 401
        return f(username, *args, **kwargs)
    return decorated

# Routes
@app.route("/signup", methods=["POST"])
def signup():
    data = request.json
    print(data)
    success, response = add_user(users_collection, data["email"], generate_password_hash(data["password"]), False, "default")
    if not success:
        return jsonify({"message": response}), 400
    return jsonify({"message": "User created successfully"})

@app.route("/login", methods=["POST"])
def login():
    data = request.json
    success, user = get_user_by_email(users_collection, data["email"])
    print(success, user)
    if not success or not check_password_hash(user["userHash"], data["password"]):
        return jsonify({"message": "Invalid credentials"}), 401
    token = create_jwt_token(user["username"])
    return jsonify({"access_token": token, "token_type": "bearer"})

@app.route("/protected", methods=["GET"])
@token_required
def protected_route(username):
    return jsonify({"message": "You are authorized", "user": username})

@app.route("/process_videos", methods=["POST"])
def process_videos():
    data = request.get_json()
    videos = data.get("videos")
    if not videos or not isinstance(videos, list):
        return jsonify({"message": "No videos provided or invalid format"}), 400

    # Process each video (add your processing logic here)
    # For example, you might store the videos or trigger a video processing task.
    processed_count = len(videos)
    time.sleep(60)
    return jsonify({
        "message": "Videos processed successfully",
        "processed_count": processed_count
    }), 200

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')
