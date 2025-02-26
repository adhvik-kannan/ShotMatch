import cv2
import mediapipe as mp
from ultralytics import YOLO
import numpy as np

# VISIBILITY_THRESHOLD = 0.5  # Set to 0.5 for now
model = YOLO('yolo12x.pt')


def detect_ball(frame):
    image_height = frame.shape[0]
    results = model(frame, conf=0.25, iou=0.45, augment=True, verbose=False)
    ball = []
    for result in results:
        boxes = result.boxes
        for box in boxes:
            cls_id = int(box.cls[0])
            conf = float(box.conf[0])
            if cls_id == 32 and conf > 0.25: # COCO classID
                x1, y1, x2, y2 = box.xyxy[0]
                x_center = (x1 + x2) / 2
                y_center = (y1 + y2) / 2
                ball.append([int(x_center), int(image_height - y_center)])
    if len(ball) == 0:
        return None
    return ball[0]


def get_landmark_xy(landmarks, index, image_width, image_height):
    VISIBILITY_THRESHOLD = 0.5
    landmark = landmarks[index]
    if landmark.visibility < VISIBILITY_THRESHOLD:
        return "NONE" # use string to make life easier
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
    # output_data = []
    output_data = {}

    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            break

        rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = pose.process(rgb_image)

        # Convert back to BGR for consistent processing (even if not displayed)
        annotated_image = cv2.cvtColor(rgb_image, cv2.COLOR_RGB2BGR)

        frame_data = {}

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

            left_pinky = get_landmark_xy(landmarks, mp_pose.PoseLandmark.LEFT_PINKY.value, w, h)
            right_pinky = get_landmark_xy(landmarks, mp_pose.PoseLandmark.RIGHT_PINKY.value, w, h)

            right_eye = get_landmark_xy(landmarks, mp_pose.PoseLandmark.RIGHT_EYE.value, w, h)
            left_eye = get_landmark_xy(landmarks, mp_pose.PoseLandmark.LEFT_EYE.value, w, h)
            
            right_ear = get_landmark_xy(landmarks, mp_pose.PoseLandmark.RIGHT_EAR.value, w, h)
            left_ear = get_landmark_xy(landmarks, mp_pose.PoseLandmark.LEFT_EAR.value, w, h)

            right_mouth = get_landmark_xy(landmarks, 10, w, h)
            left_mouth = get_landmark_xy(landmarks, 9, w, h)

            ball = detect_ball(frame)

            if right_eye != "NONE":
                eye_level = right_eye
            elif left_eye != "NONE":
                eye_level = left_eye
            # elif right_ear != "NONE":
            #     eye_level = right_ear
            # elif left_ear != "NONE":
            #     eye_level = left_ear
            else:
                eye_level = None

            if right_mouth != "NONE":
                mouth_level = right_mouth
            elif left_mouth != "NONE":
                mouth_level = left_mouth
            else:
                mouth_level = None
            
            if ball is not None and eye_level is not None and mouth_level is not None:
                ball_x, ball_y = ball
                ball[1] = h - ball_y
                eye_level_x, eye_level_y = eye_level
                mouth_level_x, mouth_level_y = mouth_level
                # print(ball_y, eye_level_y, mouth_level_y)
                # if ball_y < 2 * eye_level_y - mouth_level_y and ball_y > 2 * mouth_level_y - eye_level_y:
                if ball_y < eye_level_y and ball_y > mouth_level_y:
                    frame_data = {
                        "left_shoulder": left_shoulder,
                        "right_shoulder": right_shoulder,
                        "left_elbow": left_elbow,
                        "right_elbow": right_elbow,
                        "left_wrist": left_wrist,
                        "right_wrist": right_wrist,
                        "left_hip": left_hip,
                        "right_hip": right_hip,
                        # can take mean for waist value
                        "ball": ball,
                        # "eye_level": eye_level,
                        # "mouth_level": mouth_level,
                        "frame": frame_index
                    }
                    # output_data.append(frame_data)
                    output_data[frame_index] = frame_data

        #===================================== start of comment ===============================
        #     mp_drawing.draw_landmarks(
        #         annotated_image,
        #         results.pose_landmarks,
        #         mp_pose.POSE_CONNECTIONS,
        #         mp_drawing.DrawingSpec(color=(245,117,66), thickness=2, circle_radius=4),
        #         mp_drawing.DrawingSpec(color=(245,66,230), thickness=2, circle_radius=2)
        #     )
        #     if ball is not None:
        #         # for b in ball_boxes:
        #         #     center = b['center']
        #         cv2.circle(annotated_image, ball, 5, (0, 255, 255), -1)
        # cv2.imshow('Pose Detection', annotated_image)
        # if cv2.waitKey(1) & 0xFF == 27:
        #     break
        #===================================== end of comment ==================================

        frame_index += 1
    cap.release()
    #===================================== start of comment ===============================
    # cv2.destroyAllWindows()
    #===================================== end of comment =================================
    if len(output_data) != 0:
        max_key = max(output_data.keys())
        max_value = output_data[max_key]
        # return output_data
        return max_value
    else:
        return None

# example usage:
if __name__ == "__main__":
    pose_data = analyze_video("test_video.mp4")  # Replace with your video path
    # for frame_info in pose_data:
    #     print(frame_info)
    print(pose_data)