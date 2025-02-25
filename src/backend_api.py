import os
import base64
from flask import Flask, request, jsonify
import datetime
import jwt
from functools import wraps
import time
from recognition_model import analyze_video
from werkzeug.security import generate_password_hash, check_password_hash
from database import connect_to_mongodb, add_user, get_user_by_email

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
    data_json = request.get_json()
    videos = data_json.get("videos")
    if not videos or not isinstance(videos, list):
        return jsonify({"message": "No videos provided or invalid format"}), 400

    processed_results = []  # List to hold each video's OCR output
    processed_count = len(videos)

    for video in videos:
        video_uri = video.get("videoUri")
        base64_data = video.get("base64Data")
        if not base64_data:
            return jsonify({"message": "Missing base64 data for video", "video": video_uri}), 400

        print(f"Processing video {video_uri}")
        try:
            # Decode the base64 video and write to a temporary file
            temp_file_path = f"/tmp/{os.path.basename(video_uri)}"
            with open(temp_file_path, "wb") as f:
                f.write(base64.b64decode(base64_data))
            
            # Run OCR analysis on the temporary file
            ocr_result = analyze_video(temp_file_path)
            print(f"Processed video {video_uri} with data: {ocr_result}")

            if not ocr_result:
                return jsonify({
                    "message": "Failed to process video",
                    "video": video_uri,
                    "data": None
                }), 500

            processed_results.append(ocr_result)
        except Exception as e:
            print(f"Error processing video {video_uri}: {e}")
            return jsonify({
                "message": "Error during video processing",
                "video": video_uri,
                "error": str(e)
            }), 500
        finally:
            # Clean up the temporary file if it exists
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)

    return jsonify({
        "message": "Videos processed successfully",
        "processed_count": processed_count,
        "data": processed_results
    }), 200

@app.route("/process_consistency_videos", methods=["POST"])
def process_consistency_videos():
    data_json = request.get_json()
    front_videos = data_json.get("frontVideos")
    side_videos = data_json.get("sideVideos")
    
    if not front_videos or not isinstance(front_videos, list):
        return jsonify({"message": "No front videos provided or invalid format"}), 400
    if not side_videos or not isinstance(side_videos, list):
        return jsonify({"message": "No side videos provided or invalid format"}), 400

    front_results = []
    side_results = []

    # Process front videos
    for video in front_videos:
        video_uri = video.get("videoUri")
        base64_data = video.get("base64Data")
        if not base64_data:
            return jsonify({"message": "Missing base64 data for front video", "video": video_uri}), 400

        print(f"Processing front video {video_uri}")
        try:
            temp_file_path = f"/tmp/{os.path.basename(video_uri)}"
            with open(temp_file_path, "wb") as f:
                f.write(base64.b64decode(base64_data))
            
            ocr_result = analyze_video(temp_file_path)
            print(f"Processed front video {video_uri} with data: {ocr_result}")
            
            if not ocr_result:
                return jsonify({
                    "message": "Failed to process front video",
                    "video": video_uri,
                    "data": None
                }), 500
            
            front_results.append(ocr_result)
        except Exception as e:
            print(f"Error processing front video {video_uri}: {e}")
            return jsonify({
                "message": "Error during front video processing",
                "video": video_uri,
                "error": str(e)
            }), 500
        finally:
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)

    # Process side videos
    for video in side_videos:
        video_uri = video.get("videoUri")
        base64_data = video.get("base64Data")
        if not base64_data:
            return jsonify({"message": "Missing base64 data for side video", "video": video_uri}), 400

        print(f"Processing side video {video_uri}")
        try:
            temp_file_path = f"/tmp/{os.path.basename(video_uri)}"
            with open(temp_file_path, "wb") as f:
                f.write(base64.b64decode(base64_data))
            
            ocr_result = analyze_video(temp_file_path)
            print(f"Processed side video {video_uri} with data: {ocr_result}")
            
            if not ocr_result:
                return jsonify({
                    "message": "Failed to process side video",
                    "video": video_uri,
                    "data": None
                }), 500
            
            side_results.append(ocr_result)
        except Exception as e:
            print(f"Error processing side video {video_uri}: {e}")
            return jsonify({
                "message": "Error during side video processing",
                "video": video_uri,
                "error": str(e)
            }), 500
        finally:
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)

    return jsonify({
        "message": "Consistency videos processed successfully",
        "front_processed_count": len(front_videos),
        "side_processed_count": len(side_videos),
        "front_data": front_results,
        "side_data": side_results
    }), 200
    
if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')