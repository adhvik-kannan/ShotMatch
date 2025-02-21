import cv2
import mediapipe as mp
import math

# VISIBILITY_THRESHOLD = 0.5  # Set to 0.5 for now

# def __init__(self):
#     self.mp_drawing = mp.solutions.drawing_utils
#     self.mp_pose = mp.solutions.pose
#     self.pose = self.mp_pose.Pose(
#         static_image_mode=False,
#         model_complexity=1,
#         smooth_landmarks=True,
#         enable_segmentation=False,
#         min_detection_confidence=0.5,
#         min_tracking_confidence=0.5
#     )

def calculate_angle(a, b, c):
    AB = (a[0] - b[0], a[1] - b[1])
    CB = (c[0] - b[0], c[1] - b[1])

    dot_product = AB[0] * CB[0] + AB[1] * CB[1]
    AB_magnitude = math.sqrt(AB[0]**2 + AB[1]**2)
    CB_magnitude = math.sqrt(CB[0]**2 + CB[1]**2)

    if AB_magnitude == 0 or CB_magnitude == 0:
        return 0.0

    cos_value = max(min(dot_product / (AB_magnitude * CB_magnitude), 1.0), -1.0)
    return math.degrees(math.acos(cos_value))

def get_landmark_xy(landmarks, index, image_width, image_height):
    VISIBILITY_THRESHOLD = 0.5
    landmark = landmarks[index]
    if landmark.visibility < VISIBILITY_THRESHOLD:
        return "NONE"
    x_coord = int(landmark.x * image_width)
    y_coord = int((1 - landmark.y) * image_height)
    return [x_coord, y_coord]

def analyze_video(video_path):
    mp_drawing = mp.solutions.drawing_utils
    mp_pose = mp.solutions.pose
    pose = mp_pose.Pose(
        static_image_mode=False,
        model_complexity=1,
        smooth_landmarks=True,
        enable_segmentation=False,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
    )
    cap = cv2.VideoCapture(video_path)
    frame_index = 0
    output_data = []

    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            break

        rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = pose.process(rgb_image)

        # Convert back to BGR for consistent processing (even if not displayed)
        annotated_image = cv2.cvtColor(rgb_image, cv2.COLOR_RGB2BGR)

        frame_data = {
            "left_shoulder": "NONE",
            "right_shoulder": "NONE",
            "left_elbow": "NONE",
            "right_elbow": "NONE",
            "left_wrist": "NONE",
            "right_wrist": "NONE",
            # "elbow": "NONE",
            # "wrist": "NONE",
            "time": frame_index
        }

        if results.pose_landmarks:
            landmarks = results.pose_landmarks.landmark
            h, w, _ = frame.shape

            left_shoulder = get_landmark_xy(landmarks, mp_pose.PoseLandmark.LEFT_SHOULDER.value, w, h)
            right_shoulder = get_landmark_xy(landmarks, mp_pose.PoseLandmark.RIGHT_SHOULDER.value, w, h)
            
            left_elbow = get_landmark_xy(landmarks, mp_pose.PoseLandmark.LEFT_ELBOW.value, w, h)
            right_elbow = get_landmark_xy(landmarks, mp_pose.PoseLandmark.RIGHT_ELBOW.value, w, h)

            left_wrist = get_landmark_xy(landmarks, mp_pose.PoseLandmark.LEFT_WRIST.value, w, h)
            right_wrist = get_landmark_xy(landmarks, mp_pose.PoseLandmark.RIGHT_WRIST.value, w, h)

            left_hip = get_landmark_xy(landmarks, mp_pose.PoseLandmark.LEFT_HIP.value, w, h)
            right_hip = get_landmark_xy(landmarks, mp_pose.PoseLandmark.RIGHT_HIP.value, w, h)

            frame_data = {
                # "shoulder": [left_shoulder, right_shoulder],
                # "elbow": [left_elbow, right_elbow],
                # "wrist": [left_wrist, right_wrist],
                "left_shoulder": left_shoulder,
                "right_shoulder": right_shoulder,
                "left_elbow": left_elbow,
                "right_elbow": right_elbow,
                "left_wrist": left_wrist,
                "right_wrist": right_wrist,
                "left_hip": left_hip,
                "right_hip": right_hip,
                # can take mean for waist value
                "time": frame_index
            }

            # Landmark drawing commented out for server use
            # self.mp_drawing.draw_landmarks(
            #     annotated_image,
            #     results.pose_landmarks,
            #     self.mp_pose.POSE_CONNECTIONS,
            #     self.mp_drawing.DrawingSpec(color=(245,117,66), thickness=2, circle_radius=4),
            #     self.mp_drawing.DrawingSpec(color=(245,66,230), thickness=2, circle_radius=2)
            # )

        output_data.append(frame_data)

        # Display commented out for server use
        # cv2.imshow('Pose Detection', annotated_image)

        frame_index += 1
        # if cv2.waitKey(1) & 0xFF == 27:
        #     break

    cap.release()
    # Window cleanup commented out
    # cv2.destroyAllWindows()
    
    return output_data

# example usage:
pose_data = analyze_video("nba_test.mp4")  # Replace with your video path
for frame_info in pose_data:
    print(frame_info)