import cv2
import numpy as np
import mediapipe as mp
import torch
from ultralytics import YOLO

try:
    device = "cuda" if torch.cuda.is_available() else "cpu"
    yolo_model = YOLO('yolo12x.pt')
    yolo_model.to(device)
    yolo_model.eval()
except:
    yolo_model = None
    device = "cpu"

def get_coordinate(landmarks, index, image_width, image_height):
    '''
    INPUT:
    landmarks: the human body parts
    index: index of body parts
    image_width: the x resolution of image
    image_height: the y resolution of image
    OUTPUT:
    [x_coord, y_coord] the xy coordinate of the body part, it needs to be above visibility threshold to get a value or it will return None
    '''
    landmark = landmarks[index]
    if landmark.visibility < 0.5: # threshold
        return None
    x_coord = int(landmark.x * image_width)
    y_coord = int((1 - landmark.y) * image_height)
    return [x_coord, y_coord]

def choose_valid_side(left_side, right_side):
    ''' 
    INPUT: 
    left_side: left side data (as a list coordinate)
    right_side: right side data (as a list coordinate)
    OUTPUT:
    side: the value chosen, the right side will be prioritized if right side has the value
    '''
    side = None
    if right_side is not None:
        side = right_side
    elif left_side is not None:
        side = left_side
    return side

def detect_side(right_shoulder, right_elbow, right_wrist, left_shoulder, left_elbow, left_wrist):
    '''
    A simple side detection: if the right shoulder's x is smaller, user is oriented RIGHT, else LEFT.
    '''
    side = None
    if right_shoulder == None or right_elbow == None or right_wrist == None:
        if left_shoulder != None and left_elbow != None and left_wrist != None:
            side = "LEFT"
    elif left_shoulder == None or left_elbow == None or left_wrist == None:
        if right_shoulder != None and right_elbow != None and right_wrist != None:
            side = "RIGHT"
    else:
        side = "FRONT"
    return side

def detect_ball(frame):
    '''
    INPUT: 
    frame: frame in video
    OUTPUT:
    ball[0] the most likely xy coordinate to be the ball
    '''
    image_height = frame.shape[0]
    results = yolo_model(frame, conf=0.25, iou=0.45, augment=True, verbose=False)
    ball = []
    for result in results:
        boxes = result.boxes
        for box in boxes:
            class_id = int(box.cls[0])
            confidence = float(box.conf[0])
            if class_id == 32 and confidence > 0.25: # COCO classID
                x1, y1, x2, y2 = box.xyxy[0]
                x_center = (x1 + x2) / 2
                y_center = (y1 + y2) / 2
                ball.append([int(x_center), int(image_height - y_center)])
    if len(ball) == 0:
        return None
    return ball[0]

def eye_level_measurement(eye, wrist, mouth, frame_height):
    '''
    INPUT: 
    eye: eye level coordinate
    mouth: mouth level coordinate
    ball: ball level coordinate
    wrist: wrist level coordinate
    height: image height
    OUTPUT:
    frame_flag: if the value is set to be True then it means that the ball is at the eye level
    else it means that the ball is not at the eye level
    '''
    frame_flag = False
    #  球在眼睛的高度
    if eye is not None and mouth is not None:
        eye_x, eye_y = eye
        mouth_x, mouth_y = mouth
        if wrist is not None:
            wrist_x, wrist_y = wrist
            if wrist_y < (2 * eye_y) - mouth_y and wrist_y > (2 * mouth_y) - eye_y:
                frame_flag = True
    return frame_flag

def waist_level_measurement(hip, wrist, shoulder, frame_height):
    '''
    Returns True if wrist is near the hip (within 5% of frame height).
    '''
    if wrist and hip:
        if abs(wrist[1] - hip[1]) < (0.05 * frame_height):
            return True
    return False

def analyze_video(video_path):
    mp_drawing = mp.solutions.drawing_utils
    mp_pose = mp.solutions.pose
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        return None

    pose = mp_pose.Pose(
        static_image_mode=False,
        model_complexity=1,
        smooth_landmarks=True,
        enable_segmentation=False,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
    )

    eye_level_data = {}
    waist_level_data = {}
    frame_index = 0
    max_hand_y = None
    max_hand_frame_data = None

    while True:
        success, frame = cap.read()
        if not success:
            break

        rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = pose.process(rgb_image)
        if results.pose_landmarks:
            landmarks = results.pose_landmarks.landmark
            h, w, _ = frame.shape
            nose             = get_coordinate(landmarks, mp_pose.PoseLandmark.NOSE.value, w, h)
            left_eye_inner   = get_coordinate(landmarks, mp_pose.PoseLandmark.LEFT_EYE_INNER.value, w, h)
            left_eye         = get_coordinate(landmarks, mp_pose.PoseLandmark.LEFT_EYE.value, w, h)
            left_eye_outer   = get_coordinate(landmarks, mp_pose.PoseLandmark.LEFT_EYE_OUTER.value, w, h)
            right_eye_inner  = get_coordinate(landmarks, mp_pose.PoseLandmark.RIGHT_EYE_INNER.value, w, h)
            right_eye        = get_coordinate(landmarks, mp_pose.PoseLandmark.RIGHT_EYE.value, w, h)
            right_eye_outer  = get_coordinate(landmarks, mp_pose.PoseLandmark.RIGHT_EYE_OUTER.value, w, h)
            left_ear         = get_coordinate(landmarks, mp_pose.PoseLandmark.LEFT_EAR.value, w, h)
            right_ear        = get_coordinate(landmarks, mp_pose.PoseLandmark.RIGHT_EAR.value, w, h)
            left_mouth       = get_coordinate(landmarks, mp_pose.PoseLandmark.MOUTH_LEFT.value, w, h)
            right_mouth      = get_coordinate(landmarks, mp_pose.PoseLandmark.MOUTH_RIGHT.value, w, h)
            left_shoulder    = get_coordinate(landmarks, mp_pose.PoseLandmark.LEFT_SHOULDER.value, w, h)
            right_shoulder   = get_coordinate(landmarks, mp_pose.PoseLandmark.RIGHT_SHOULDER.value, w, h)
            left_elbow       = get_coordinate(landmarks, mp_pose.PoseLandmark.LEFT_ELBOW.value, w, h)
            right_elbow      = get_coordinate(landmarks, mp_pose.PoseLandmark.RIGHT_ELBOW.value, w, h)
            left_wrist       = get_coordinate(landmarks, mp_pose.PoseLandmark.LEFT_WRIST.value, w, h)
            right_wrist      = get_coordinate(landmarks, mp_pose.PoseLandmark.RIGHT_WRIST.value, w, h)
            left_pinky       = get_coordinate(landmarks, mp_pose.PoseLandmark.LEFT_PINKY.value, w, h)
            right_pinky      = get_coordinate(landmarks, mp_pose.PoseLandmark.RIGHT_PINKY.value, w, h)
            left_index       = get_coordinate(landmarks, mp_pose.PoseLandmark.LEFT_INDEX.value, w, h)
            right_index      = get_coordinate(landmarks, mp_pose.PoseLandmark.RIGHT_INDEX.value, w, h)
            left_thumb       = get_coordinate(landmarks, mp_pose.PoseLandmark.LEFT_THUMB.value, w, h)
            right_thumb      = get_coordinate(landmarks, mp_pose.PoseLandmark.RIGHT_THUMB.value, w, h)
            left_hip         = get_coordinate(landmarks, mp_pose.PoseLandmark.LEFT_HIP.value, w, h)
            right_hip        = get_coordinate(landmarks, mp_pose.PoseLandmark.RIGHT_HIP.value, w, h)
            left_knee        = get_coordinate(landmarks, mp_pose.PoseLandmark.LEFT_KNEE.value, w, h)
            right_knee       = get_coordinate(landmarks, mp_pose.PoseLandmark.RIGHT_KNEE.value, w, h)
            left_ankle       = get_coordinate(landmarks, mp_pose.PoseLandmark.LEFT_ANKLE.value, w, h)
            right_ankle      = get_coordinate(landmarks, mp_pose.PoseLandmark.RIGHT_ANKLE.value, w, h)
            left_heel        = get_coordinate(landmarks, mp_pose.PoseLandmark.LEFT_HEEL.value, w, h)
            right_heel       = get_coordinate(landmarks, mp_pose.PoseLandmark.RIGHT_HEEL.value, w, h)
            left_foot_index  = get_coordinate(landmarks, mp_pose.PoseLandmark.LEFT_FOOT_INDEX.value, w, h)
            right_foot_index = get_coordinate(landmarks, mp_pose.PoseLandmark.RIGHT_FOOT_INDEX.value, w, h)

            # ball = detect_ball(frame)

            eye      = choose_valid_side(left_eye, right_eye)
            mouth    = choose_valid_side(left_mouth, right_mouth)
            wrist    = choose_valid_side(left_wrist, right_wrist)
            pinky    = choose_valid_side(left_pinky, right_pinky)
            hip      = choose_valid_side(left_hip, right_hip)
            shoulder = choose_valid_side(left_shoulder, right_shoulder)

            side = detect_side(right_shoulder, right_elbow, right_wrist, left_shoulder, left_elbow, left_wrist)

            eye_flag = eye_level_measurement(eye, wrist, mouth, h)
            if eye_flag is True:
                frame_data = {
                    "nose"            : nose            ,
                    "left_eye_inner"  : left_eye_inner  ,
                    "left_eye"        : left_eye        ,
                    "left_eye_outer"  : left_eye_outer  ,
                    "right_eye_inner" : right_eye_inner ,
                    "right_eye"       : right_eye       ,
                    "right_eye_outer" : right_eye_outer ,
                    "left_ear"        : left_ear        ,
                    "right_ear"       : right_ear       ,
                    "left_mouth"      : left_mouth      ,
                    "right_mouth"     : right_mouth     ,
                    "left_shoulder"   : left_shoulder   ,
                    "right_shoulder"  : right_shoulder  ,
                    "left_elbow"      : left_elbow      ,
                    "right_elbow"     : right_elbow     ,
                    "left_wrist"      : left_wrist      ,
                    "right_wrist"     : right_wrist     ,
                    "left_pinky"      : left_pinky      ,
                    "right_pinky"     : right_pinky     ,
                    "left_index"      : left_index      ,
                    "right_index"     : right_index     ,
                    "left_thumb"      : left_thumb      ,
                    "right_thumb"     : right_thumb     ,
                    "left_hip"        : left_hip        ,
                    "right_hip"       : right_hip       ,
                    "left_knee"       : left_knee       ,
                    "right_knee"      : right_knee      ,
                    "left_ankle"      : left_ankle      ,
                    "right_ankle"     : right_ankle     ,
                    "left_heel"       : left_heel       ,
                    "right_heel"      : right_heel      ,
                    "left_foot_index" : left_foot_index ,
                    "right_foot_index": right_foot_index,
                    # "ball"            : ball            ,
                    "Side"            : side            ,
                    "frame"           : frame_index     ,
                    "postion"         : "EYE"
                } 
                eye_level_data[frame_index] = frame_data

            waist_flag = waist_level_measurement(hip, wrist, shoulder, h)
            if waist_flag is True:
                frame_data = {
                    "nose"            : nose            ,
                    "left_eye_inner"  : left_eye_inner  ,
                    "left_eye"        : left_eye        ,
                    "left_eye_outer"  : left_eye_outer  ,
                    "right_eye_inner" : right_eye_inner ,
                    "right_eye"       : right_eye       ,
                    "right_eye_outer" : right_eye_outer ,
                    "left_ear"        : left_ear        ,
                    "right_ear"       : right_ear       ,
                    "left_mouth"      : left_mouth      ,
                    "right_mouth"     : right_mouth     ,
                    "left_shoulder"   : left_shoulder   ,
                    "right_shoulder"  : right_shoulder  ,
                    "left_elbow"      : left_elbow      ,
                    "right_elbow"     : right_elbow     ,
                    "left_wrist"      : left_wrist      ,
                    "right_wrist"     : right_wrist     ,
                    "left_pinky"      : left_pinky      ,
                    "right_pinky"     : right_pinky     ,
                    "left_index"      : left_index      ,
                    "right_index"     : right_index     ,
                    "left_thumb"      : left_thumb      ,
                    "right_thumb"     : right_thumb     ,
                    "left_hip"        : left_hip        ,
                    "right_hip"       : right_hip       ,
                    "left_knee"       : left_knee       ,
                    "right_knee"      : right_knee      ,
                    "left_ankle"      : left_ankle      ,
                    "right_ankle"     : right_ankle     ,
                    "left_heel"       : left_heel       ,
                    "right_heel"      : right_heel      ,
                    "left_foot_index" : left_foot_index ,
                    "right_foot_index": right_foot_index,
                    # "ball"            : ball            ,
                    "Side"            : side            ,
                    "frame"           : frame_index     ,
                    "postion"         : "WAIST"
                } 
                waist_level_data[frame_index] = frame_data

            if wrist is not None:
                if max_hand_y is None or wrist[1] < max_hand_y:
                    max_hand_y = wrist[1]
                    max_hand_frame_data = {
                        "nose"            : nose            ,
                        "left_eye_inner"  : left_eye_inner  ,
                        "left_eye"        : left_eye        ,
                        "left_eye_outer"  : left_eye_outer  ,
                        "right_eye_inner" : right_eye_inner ,
                        "right_eye"       : right_eye       ,
                        "right_eye_outer" : right_eye_outer ,
                        "left_ear"        : left_ear        ,
                        "right_ear"       : right_ear       ,
                        "left_mouth"      : left_mouth      ,
                        "right_mouth"     : right_mouth     ,
                        "left_shoulder"   : left_shoulder   ,
                        "right_shoulder"  : right_shoulder  ,
                        "left_elbow"      : left_elbow      ,
                        "right_elbow"     : right_elbow     ,
                        "left_wrist"      : left_wrist      ,
                        "right_wrist"     : right_wrist     ,
                        "left_pinky"      : left_pinky      ,
                        "right_pinky"     : right_pinky     ,
                        "left_index"      : left_index      ,
                        "right_index"     : right_index     ,
                        "left_thumb"      : left_thumb      ,
                        "right_thumb"     : right_thumb     ,
                        "left_hip"        : left_hip        ,
                        "right_hip"       : right_hip       ,
                        "left_knee"       : left_knee       ,
                        "right_knee"      : right_knee      ,
                        "left_ankle"      : left_ankle      ,
                        "right_ankle"     : right_ankle     ,
                        "left_heel"       : left_heel       ,
                        "right_heel"      : right_heel      ,
                        "left_foot_index" : left_foot_index ,
                        "right_foot_index": right_foot_index,
                        # "ball"            : ball            ,
                        "Side"            : side            ,
                        "frame"           : frame_index     ,
                        "postion"         : "MAX_HAND"
                    } 

        frame_index += 1

    cap.release()

    if len(eye_level_data) > 0:
        earliest_eye_index = min(eye_level_data.keys())
        latest_eye_index = max(eye_level_data.keys())
        latest_eye_frame = eye_level_data[latest_eye_index]
        waist_before_index = None
        for w_i in waist_level_data.keys():
            if w_i < earliest_eye_index:
                if waist_before_index is None or w_i > waist_before_index:
                    waist_before_index = w_i
        waist_frame_before_eye = waist_level_data[waist_before_index] if waist_before_index is not None else None
    else:
        # earliest_eye_frame = None
        latest_eye_frame = None
        waist_frame_before_eye = None
    # if earliest_eye_frame is not None and waist_frame_before_eye is not None and max_hand_frame_data is not None:
    if latest_eye_frame is not None and waist_frame_before_eye is not None and max_hand_frame_data is not None:
        return waist_frame_before_eye, latest_eye_frame, max_hand_frame_data
    else:
        return None

if __name__ == "__main__":
    pose_data_waist, pose_data_eye, pose_data_high_hand= analyze_video("nba_1.mp4")  
    print(f"nba_1 waist: {pose_data_waist}\n nba_1 eye: {pose_data_eye}\n nba_1 max hand: {pose_data_high_hand}")
    pass
