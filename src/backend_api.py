import os
import base64
from flask import Flask, request, jsonify
import datetime
import jwt
from functools import wraps
import time
from recognition_model import analyze_video
from generate_front_statistics import compare_front
from generate_side_statistics import compare_side_ra
from compare_consistency_front import get_consistency_front
from compare_consistency_side import get_consistency_side
from werkzeug.security import generate_password_hash, check_password_hash
from database import connect_to_mongodb, add_user, get_user_by_email, get_data_by_name_or_hash, add_new_data
import json
import time
import ast
# Swagger imports
from flasgger import Swagger

# Constants
SECRET_KEY = "your_secret_key"
DB_NAME = "auth_db"

# Initialize Flask App
app = Flask(__name__)
swagger = Swagger(app)

# Connect to MongoDB
success, db = connect_to_mongodb(DB_NAME)
success2, db2 = connect_to_mongodb("nba_players")
success3, db3 = connect_to_mongodb("player_data")

if not success or not success2 or not success3:
    raise Exception("Failed to connect to MongoDB")
users_collection = db["users"]
nba_players_collection = db2["stephen_curry"]
player_data_collection = db3["player_data"]

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
    """
    User Signup endpoint.
    ---
    tags:
      - Authentication
    parameters:
      - name: body
        in: body
        required: true
        description: User signup data
        schema:
          type: object
          properties:
            email:
              type: string
            password:
              type: string
    responses:
      200:
        description: User created successfully.
      400:
        description: Error in user creation.
    """
    data = request.json
    print(data)
    success, response = add_user(users_collection, data["email"], generate_password_hash(data["password"]), False, "default")
    if not success:
        return jsonify({"message": response}), 400
    return jsonify({"message": "User created successfully"})

@app.route("/login", methods=["POST"])
def login():
    """
    User Login endpoint.
    ---
    tags:
      - Authentication
    parameters:
      - name: body
        in: body
        required: true
        description: User login credentials
        schema:
          type: object
          properties:
            email:
              type: string
            password:
              type: string
    responses:
      200:
        description: Successful login with access token.
      401:
        description: Invalid credentials.
    """
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
    """
    Protected endpoint that requires a valid JWT token.
    ---
    tags:
      - Authentication
    parameters:
      - name: Authorization
        in: header
        type: string
        required: true
        description: Bearer token for authentication.
    responses:
      200:
        description: You are authorized.
      401:
        description: Token is missing or invalid.
    """
    return jsonify({"message": "You are authorized", "user": username})

@app.route("/process_videos", methods=["POST"])
def process_videos():
    """
    Process Videos endpoint.
    ---
    tags:
      - Video Processing
    parameters:
      - name: body
        in: body
        required: true
        description: JSON payload containing list of videos, selected player, and user.
        schema:
          type: object
          properties:
            videos:
              type: array
              items:
                type: object
                properties:
                  videoUri:
                    type: string
                  base64Data:
                    type: string
            selectedPlayer:
              type: object
              properties:
                name:
                  type: string
            user:
              type: string
    responses:
      200:
        description: Videos processed successfully.
      400:
        description: Missing video data or invalid video format.
      500:
        description: Failed video processing or error during processing.
    """
    timer = time.time()
    data_json = request.get_json()
    videos = data_json.get("videos")
    player = data_json.get("selectedPlayer")
    user = data_json.get("user")
    print(player, flush=True)
    processed_results = []  # List to hold each video's OCR output.
    processed_count = len(videos)

    for video in videos:
        video_uri = video.get("videoUri")
        base64_data = video.get("base64Data")
        if not base64_data:
            return jsonify({"message": "Missing base64 data for video", "video": video_uri}), 400

        # print(f"Processing video {video_uri}", flush=True)
        try:
            # Decode the base64 video and write to a temporary file.
            temp_file_path = f"/tmp/{os.path.basename(video_uri)}"
            with open(temp_file_path, "wb") as f:
                f.write(base64.b64decode(base64_data))
            
            # Run OCR analysis on the temporary file.
            # print(temp_file_path)
            ocr_result = analyze_video(temp_file_path)
            # print(f"Processed video {video_uri} with data: {ocr_result}", flush=True)

            if not ocr_result:
                print(f"Failed to process video {video_uri}", flush=True)
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
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)
    
    # Generate statistics for the videos.
    found, player_data = get_data_by_name_or_hash(nba_players_collection, player["name"])
    if not found:
        return jsonify({"message": "Player not found"}), 404

    # # -----------------------------------------------------
    # # LOADING MAX PARAMS
    # # -----------------------------------------------------
    # max_f_hew_ra = ast.literal_eval(player_data[0]["max_f_hew_ra"])
    # max_f_hew_la = ast.literal_eval(player_data[0]["max_f_hew_la"])
    # max_f_sew_ra = ast.literal_eval(player_data[0]["max_f_sew_ra"]) 
    # max_f_sew_la = ast.literal_eval(player_data[0]["max_f_sew_la"])
    # max_f_ewa_ra = ast.literal_eval(player_data[0]["max_f_ewa_ra"])
    # max_f_ewp_la = ast.literal_eval(player_data[0]["max_f_ewp_la"])
    # max_f_elbow_diff = ast.literal_eval(player_data[0]["max_f_elbow_diff"])

    # max_s_ewp_ra = ast.literal_eval(player_data[0]["max_s_ewp_ra"])
    # max_s_sew_ra = ast.literal_eval(player_data[0]["max_s_sew_ra"])
    # max_s_hse_ra = ast.literal_eval(player_data[0]["max_s_hse_ra"])


    # # -----------------------------------------------------
    # # LOADING EYE PARAMS
    # # -----------------------------------------------------
    # eye_f_hew_ra = ast.literal_eval(player_data[0]["eye_f_hew_ra"])
    # eye_f_hew_la = ast.literal_eval(player_data[0]["eye_f_hew_la"])
    # eye_f_sew_ra = ast.literal_eval(player_data[0]["eye_f_sew_ra"]) 
    # eye_f_sew_la = ast.literal_eval(player_data[0]["eye_f_sew_la"])
    # eye_f_ewa_ra = ast.literal_eval(player_data[0]["eye_f_ewa_ra"])
    # eye_f_ewp_la = ast.literal_eval(player_data[0]["eye_f_ewp_la"])
    # eye_f_elbow_diff = ast.literal_eval(player_data[0]["eye_f_elbow_diff"])

    # eye_s_ewp_ra = ast.literal_eval(player_data[0]["eye_s_ewp_ra"])
    # eye_s_sew_ra = ast.literal_eval(player_data[0]["eye_s_sew_ra"])
    # eye_s_hse_ra = ast.literal_eval(player_data[0]["eye_s_hse_ra"])


    # # -----------------------------------------------------
    # # LOADING WAIST PARAMS
    # # -----------------------------------------------------
    # waist_f_hew_ra = ast.literal_eval(player_data[0]["waist_f_hew_ra"])
    # waist_f_hew_la = ast.literal_eval(player_data[0]["waist_f_hew_la"])
    # waist_f_sew_ra = ast.literal_eval(player_data[0]["waist_f_sew_ra"]) 
    # waist_f_sew_la = ast.literal_eval(player_data[0]["waist_f_sew_la"])
    # waist_f_ewa_ra = ast.literal_eval(player_data[0]["waist_f_ewa_ra"])
    # waist_f_ewp_la = ast.literal_eval(player_data[0]["waist_f_ewp_la"])
    # waist_f_elbow_diff = ast.literal_eval(player_data[0]["waist_f_elbow_diff"])

    # waist_s_ewp_ra = ast.literal_eval(player_data[0]["waist_s_ewp_ra"])
    # waist_s_sew_ra = ast.literal_eval(player_data[0]["waist_s_sew_ra"])
    # waist_s_hse_ra = ast.literal_eval(player_data[0]["waist_s_hse_ra"])

    # -----------------------------------------------------
    # LOADING MAX PARAMS
    # -----------------------------------------------------
    if player_data[0]["max_f_hew_ra"]:
        max_f_hew_ra = ast.literal_eval(player_data[0]["max_f_hew_ra"])
    else:
        max_f_hew_ra = {'mean': 0, 'std': 0, 'alpha': 0, 'beta': 0}

    if player_data[0]["max_f_hew_la"]:
        max_f_hew_la = ast.literal_eval(player_data[0]["max_f_hew_la"])
    else:
        max_f_hew_la = {'mean': 0, 'std': 0, 'alpha': 0, 'beta': 0}

    if player_data[0]["max_f_sew_ra"]:
        max_f_sew_ra = ast.literal_eval(player_data[0]["max_f_sew_ra"])
    else:
        max_f_sew_ra = {'mean': 0, 'std': 0, 'alpha': 0, 'beta': 0}

    if player_data[0]["max_f_sew_la"]:
        max_f_sew_la = ast.literal_eval(player_data[0]["max_f_sew_la"])
    else:
        max_f_sew_la = {'mean': 0, 'std': 0, 'alpha': 0, 'beta': 0}

    if player_data[0]["max_f_ewa_ra"]:
        max_f_ewa_ra = ast.literal_eval(player_data[0]["max_f_ewa_ra"])
    else:
        max_f_ewa_ra = {'mean': 0, 'std': 0, 'alpha': 0, 'beta': 0}

    if player_data[0]["max_f_ewp_la"]:
        max_f_ewp_la = ast.literal_eval(player_data[0]["max_f_ewp_la"])
    else:
        max_f_ewp_la = {'mean': 0, 'std': 0, 'alpha': 0, 'beta': 0}

    if player_data[0]["max_f_elbow_diff"]:
        max_f_elbow_diff = ast.literal_eval(player_data[0]["max_f_elbow_diff"])
    else:
        max_f_elbow_diff = {'mean': 0, 'std': 0, 'alpha': 0, 'beta': 0}

    if player_data[0]["max_s_ewp_ra"]:
        max_s_ewp_ra = ast.literal_eval(player_data[0]["max_s_ewp_ra"])
    else:
        max_s_ewp_ra = {'mean': 0, 'std': 0, 'alpha': 0, 'beta': 0}

    if player_data[0]["max_s_sew_ra"]:
        max_s_sew_ra = ast.literal_eval(player_data[0]["max_s_sew_ra"])
    else:
        max_s_sew_ra = {'mean': 0, 'std': 0, 'alpha': 0, 'beta': 0}

    if player_data[0]["max_s_hse_ra"]:
        max_s_hse_ra = ast.literal_eval(player_data[0]["max_s_hse_ra"])
    else:
        max_s_hse_ra = {'mean': 0, 'std': 0, 'alpha': 0, 'beta': 0}

    # -----------------------------------------------------
    # LOADING EYE PARAMS
    # -----------------------------------------------------
    if player_data[0]["eye_f_hew_ra"]:
        eye_f_hew_ra = ast.literal_eval(player_data[0]["eye_f_hew_ra"])
    else:
        eye_f_hew_ra = {'mean': 0, 'std': 0, 'alpha': 0, 'beta': 0}

    if player_data[0]["eye_f_hew_la"]:
        eye_f_hew_la = ast.literal_eval(player_data[0]["eye_f_hew_la"])
    else:
        eye_f_hew_la = {'mean': 0, 'std': 0, 'alpha': 0, 'beta': 0}

    if player_data[0]["eye_f_sew_ra"]:
        eye_f_sew_ra = ast.literal_eval(player_data[0]["eye_f_sew_ra"])
    else:
        eye_f_sew_ra = {'mean': 0, 'std': 0, 'alpha': 0, 'beta': 0}

    if player_data[0]["eye_f_sew_la"]:
        eye_f_sew_la = ast.literal_eval(player_data[0]["eye_f_sew_la"])
    else:
        eye_f_sew_la = {'mean': 0, 'std': 0, 'alpha': 0, 'beta': 0}

    if player_data[0]["eye_f_ewa_ra"]:
        eye_f_ewa_ra = ast.literal_eval(player_data[0]["eye_f_ewa_ra"])
    else:
        eye_f_ewa_ra = {'mean': 0, 'std': 0, 'alpha': 0, 'beta': 0}

    if player_data[0]["eye_f_ewp_la"]:
        eye_f_ewp_la = ast.literal_eval(player_data[0]["eye_f_ewp_la"])
    else:
        eye_f_ewp_la = {'mean': 0, 'std': 0, 'alpha': 0, 'beta': 0}

    if player_data[0]["eye_f_elbow_diff"]:
        eye_f_elbow_diff = ast.literal_eval(player_data[0]["eye_f_elbow_diff"])
    else:
        eye_f_elbow_diff = {'mean': 0, 'std': 0, 'alpha': 0, 'beta': 0}

    if player_data[0]["eye_s_ewp_ra"]:
        eye_s_ewp_ra = ast.literal_eval(player_data[0]["eye_s_ewp_ra"])
    else:
        eye_s_ewp_ra = {'mean': 0, 'std': 0, 'alpha': 0, 'beta': 0}

    if player_data[0]["eye_s_sew_ra"]:
        eye_s_sew_ra = ast.literal_eval(player_data[0]["eye_s_sew_ra"])
    else:
        eye_s_sew_ra = {'mean': 0, 'std': 0, 'alpha': 0, 'beta': 0}

    if player_data[0]["eye_s_hse_ra"]:
        eye_s_hse_ra = ast.literal_eval(player_data[0]["eye_s_hse_ra"])
    else:
        eye_s_hse_ra = {'mean': 0, 'std': 0, 'alpha': 0, 'beta': 0}

    # -----------------------------------------------------
    # LOADING WAIST PARAMS
    # -----------------------------------------------------
    if player_data[0]["waist_f_hew_ra"]:
        waist_f_hew_ra = ast.literal_eval(player_data[0]["waist_f_hew_ra"])
    else:
        waist_f_hew_ra = {'mean': 0, 'std': 0, 'alpha': 0, 'beta': 0}

    if player_data[0]["waist_f_hew_la"]:
        waist_f_hew_la = ast.literal_eval(player_data[0]["waist_f_hew_la"])
    else:
        waist_f_hew_la = {'mean': 0, 'std': 0, 'alpha': 0, 'beta': 0}

    if player_data[0]["waist_f_sew_ra"]:
        waist_f_sew_ra = ast.literal_eval(player_data[0]["waist_f_sew_ra"])
    else:
        waist_f_sew_ra = {'mean': 0, 'std': 0, 'alpha': 0, 'beta': 0}

    if player_data[0]["waist_f_sew_la"]:
        waist_f_sew_la = ast.literal_eval(player_data[0]["waist_f_sew_la"])
    else:
        waist_f_sew_la = {'mean': 0, 'std': 0, 'alpha': 0, 'beta': 0}

    if player_data[0]["waist_f_ewa_ra"]:
        waist_f_ewa_ra = ast.literal_eval(player_data[0]["waist_f_ewa_ra"])
    else:
        waist_f_ewa_ra = {'mean': 0, 'std': 0, 'alpha': 0, 'beta': 0}

    if player_data[0]["waist_f_ewp_la"]:
        waist_f_ewp_la = ast.literal_eval(player_data[0]["waist_f_ewp_la"])
    else:
        waist_f_ewp_la = {'mean': 0, 'std': 0, 'alpha': 0, 'beta': 0}

    if player_data[0]["waist_f_elbow_diff"]:
        waist_f_elbow_diff = ast.literal_eval(player_data[0]["waist_f_elbow_diff"])
    else:
        waist_f_elbow_diff = {'mean': 0, 'std': 0, 'alpha': 0, 'beta': 0}

    if player_data[0]["waist_s_ewp_ra"]:
        waist_s_ewp_ra = ast.literal_eval(player_data[0]["waist_s_ewp_ra"])
    else:
        waist_s_ewp_ra = {'mean': 0, 'std': 0, 'alpha': 0, 'beta': 0}

    if player_data[0]["waist_s_sew_ra"]:
        waist_s_sew_ra = ast.literal_eval(player_data[0]["waist_s_sew_ra"])
    else:
        waist_s_sew_ra = {'mean': 0, 'std': 0, 'alpha': 0, 'beta': 0}

    if player_data[0]["waist_s_hse_ra"]:
        waist_s_hse_ra = ast.literal_eval(player_data[0]["waist_s_hse_ra"])
    else:
        waist_s_hse_ra = {'mean': 0, 'std': 0, 'alpha': 0, 'beta': 0}

    # -----------------------------------------------------
    # COMPARISON 
    # -----------------------------------------------------
    # print("Hello: ", processed_results[0], flush=True)
    max_front_results = compare_front(processed_results[0][2], max_f_hew_ra, max_f_hew_la, max_f_sew_ra, max_f_sew_la, max_f_ewa_ra, max_f_ewp_la, max_f_elbow_diff)
    max_side_results = compare_side_ra(processed_results[1][2], max_s_ewp_ra, max_s_hse_ra, max_s_sew_ra)
    eye_front_results = compare_front(processed_results[0][1], eye_f_hew_ra, eye_f_hew_la, eye_f_sew_ra, eye_f_sew_la, eye_f_ewa_ra, eye_f_ewp_la, eye_f_elbow_diff)
    eye_side_results = compare_side_ra(processed_results[1][1], eye_s_ewp_ra, eye_s_hse_ra, eye_s_sew_ra)
    waist_front_results = compare_front(processed_results[0][0], waist_f_hew_ra, waist_f_hew_la, waist_f_sew_ra, waist_f_sew_la, waist_f_ewa_ra, waist_f_ewp_la, waist_f_elbow_diff)
    waist_side_results = compare_side_ra(processed_results[1][0], waist_s_ewp_ra, waist_s_hse_ra, waist_s_sew_ra)
    # NEED TO CHANGE THIS PROCESSED RESULTS FOR EACH MAX_HAND, EYE, AND WAIST DATA processed_results[X]
    # AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA

    max_front_overall_score = (
        max_front_results["Hip->Elbow->Wrist Score (Right Arm)"] + max_front_results["Hip->Elbow->Wrist Score (Left Arm)"] +
        max_front_results["Shoulder->Elbow->Wrist Score (Right Arm)"] + max_front_results["Elbow->Wrist->Fingers Score (Right Arm)"] +
        max_front_results["Elbow->Wrist->Pinky Score (Left Arm)"] + max_front_results["Elbow Alignment Score"]
    ) / 6
    eye_front_overall_score = (
        eye_front_results["Hip->Elbow->Wrist Score (Right Arm)"] + eye_front_results["Hip->Elbow->Wrist Score (Left Arm)"] +
        eye_front_results["Shoulder->Elbow->Wrist Score (Right Arm)"] + eye_front_results["Elbow->Wrist->Fingers Score (Right Arm)"] +
        eye_front_results["Elbow->Wrist->Pinky Score (Left Arm)"] + eye_front_results["Elbow Alignment Score"]
    ) / 6
    waist_front_overall_score = (
        waist_front_results["Hip->Elbow->Wrist Score (Right Arm)"] + waist_front_results["Hip->Elbow->Wrist Score (Left Arm)"] +
        waist_front_results["Shoulder->Elbow->Wrist Score (Right Arm)"] + waist_front_results["Elbow->Wrist->Fingers Score (Right Arm)"] +
        waist_front_results["Elbow->Wrist->Pinky Score (Left Arm)"] + waist_front_results["Elbow Alignment Score"]
    ) / 6

<<<<<<< HEAD

    overall_score = (0.4 * max_overall_score) + (0.5 * eye_overall_score) + (0.1 * waist_overall_score)
=======
    max_side_overall_score = (
        max_side_results["Shoulder->Elbow->Wrist Score (Right Arm)"] + max_side_results["Elbow->Wrist->Fingers Score (Right Arm)"]
    ) / 2
    eye_side_overall_score = (
        eye_side_results["Shoulder->Elbow->Wrist Score (Right Arm)"] + eye_side_results["Elbow->Wrist->Fingers Score (Right Arm)"]
    ) / 2
    waist_side_overall_score = (
        waist_side_results["Shoulder->Elbow->Wrist Score (Right Arm)"] + waist_side_results["Elbow->Wrist->Fingers Score (Right Arm)"]
    ) / 2

    front_overall_score = (0.4 * max_front_overall_score) + (0.5 * eye_front_overall_score) + (0.1 * waist_front_overall_score)
    side_overall_score = (0.4 * max_side_overall_score) + (0.5 * eye_side_overall_score) + (0.1 * waist_side_overall_score)
    overall_score = (0.5 * front_overall_score) + (0.5 * side_overall_score)
>>>>>>> integration/adam/stat-models
    

    try:
        now = datetime.datetime.now()
        timestamp = {
            "year": now.year,
            "month": now.month,
            "day": now.day,
            "hour": now.hour,
            "minute": now.minute,
            "second": now.second
        }
        added, inserted_data = add_new_data(player_data_collection, user, eye_front_results, eye_side_results, overall_score, "Compare", timestamp)
    except Exception as e:
        print(f"Error inserting data into MongoDB: {e}")
        return jsonify({"message": "Error inserting data into MongoDB"}), 50

    timer_end = time.time()
    print(f"Time taken: {timer_end - timer}")
    return jsonify({
        "message": "Videos processed successfully",
        "processed_count": processed_count,
        "max_front_metrics": max_front_results,
        "eye_front_metrics": eye_front_results,
        "waist_front_metrics": waist_front_results,
        "max_side_metrics": max_side_results,
        "eye_side_metrics": eye_side_results,
        "waist_side_metrics": waist_side_results,
        "overallScore": overall_score
    }), 200

@app.route("/process_consistency_videos", methods=["POST"])
def process_consistency_videos():
    """
    Process Consistency Videos endpoint.
    ---
    tags:
      - Video Processing
    parameters:
      - name: body
        in: body
        required: true
        description: JSON payload containing lists of front and side videos.
        schema:
          type: object
          properties:
            frontVideos:
              type: array
              items:
                type: object
                properties:
                  videoUri:
                    type: string
                  base64Data:
                    type: string
            sideVideos:
              type: array
              items:
                type: object
                properties:
                  videoUri:
                    type: string
                  base64Data:
                    type: string
    responses:
      200:
        description: Consistency videos processed successfully.
      400:
        description: Missing or invalid video data.
      500:
        description: Error during video processing.
    """
    data_json = request.get_json()
    front_videos = data_json.get("frontVideos")
    side_videos = data_json.get("sideVideos")
    
    if not front_videos or not isinstance(front_videos, list):
        return jsonify({"message": "No front videos provided or invalid format"}), 400
    if not side_videos or not isinstance(side_videos, list):
        return jsonify({"message": "No side videos provided or invalid format"}), 400

    max_front_results = []
    eye_front_results = []
    waist_front_results = []
    max_side_results = []
    eye_side_results = []
    waist_side_results = []

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
            
            waist_data, eye_data, max_data = analyze_video(temp_file_path)
            print(f"Processed front video {video_uri}")
            
            if not waist_data or not eye_data or not max_data:
                return jsonify({
                    "message": "Failed to process front video",
                    "video": video_uri,
                    "data": None
                }), 500
            
            max_front_results.append(max_data)
            eye_front_results.append(eye_data)
            waist_front_results.append(waist_data)

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
            
            waist_data, eye_data, max_data = analyze_video(temp_file_path)
            print(f"Processed front video {video_uri}")
            
            if not waist_data or not eye_data or not max_data:
                return jsonify({
                    "message": "Failed to process side video",
                    "video": video_uri,
                    "data": None
                }), 500
            
            max_side_results.append(max_data)
            eye_side_results.append(eye_data)
            waist_side_results.append(waist_data)

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

    max_front_score = get_consistency_front(max_front_results)
    eye_front_score = get_consistency_front(eye_front_results)
    waist_front_score = get_consistency_front(waist_front_results)
    max_side_score = get_consistency_side(max_side_results)
    eye_side_score = get_consistency_side(eye_side_results)
    waist_side_score = get_consistency_side(waist_side_results)

    overall_score = (
        (0.2 * max_front_score) + (0.3 * eye_front_score) + 
        (0.05 * waist_front_score) + (0.1 * max_side_score) + 
        (0.3 * eye_side_score) + (0.05 * waist_side_score)
    )
    
    return jsonify({
        "message": "Consistency videos processed successfully",
        "front_processed_count": len(front_videos),
        "side_processed_count": len(side_videos),
        "max_front_score": max_front_score,
        "eye_front_score": eye_front_score,
        "waist_front_score": waist_front_score,
        "max_side_score": max_side_score,
        "eye_side_score": eye_side_score,
        "waist_side_score": waist_side_score,
        "overall_score": overall_score
    }), 200

@app.route("/player_data", methods=["POST"])
def get_player_data_by_user():
    """
    Get Player Data endpoint.
    ---
    tags:
      - Data Retrieval
    parameters:
      - name: body
        in: body
        required: true
        description: JSON payload containing the user and mode.
        schema:
          type: object
          properties:
            user:
              type: string
            mode:
              type: string
    responses:
      200:
        description: Player data retrieved successfully.
      400:
        description: Missing user parameter.
      500:
        description: Error retrieving player data.
    """
    data_json = request.get_json()
    user = data_json.get("user")
    mode = data_json.get("mode")
    if not user:
        return jsonify({"message": "Missing user parameter"}), 400
    try:
        data = list(player_data_collection.find({"name": user}))
        for record in data:
            record["_id"] = str(record["_id"])  # Convert ObjectId to string for JSON serialization.
        return jsonify({"player_data": data}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=8080)
