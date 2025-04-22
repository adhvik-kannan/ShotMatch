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

# For new server setup

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
    hand_frame_data = {}
    side = None

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

            eye_flag = eye_level_measurement(eye, wrist, mouth, h)
            if eye_flag is True:
                # side = detect_side(right_shoulder, right_elbow, right_wrist, left_shoulder, left_elbow, left_wrist)
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
                    # "wrist"           : wrist,
                    # "ball"            : ball            ,
                    # "Side"            : side            ,
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
                    # "wrist"           : wrist,
                    # "ball"            : ball            ,
                    # "Side"            : side            ,
                    "frame"           : frame_index     ,
                    "postion"         : "WAIST"
                } 
                waist_level_data[frame_index] = frame_data

            # if wrist is not None:
            #     if max_hand_y is None or wrist[1] < max_hand_y:
            #         max_hand_y = wrist[1]
            #         max_hand_frame_data = {
            #             "nose"            : nose            ,
            #             "left_eye_inner"  : left_eye_inner  ,
            #             "left_eye"        : left_eye        ,
            #             "left_eye_outer"  : left_eye_outer  ,
            #             "right_eye_inner" : right_eye_inner ,
            #             "right_eye"       : right_eye       ,
            #             "right_eye_outer" : right_eye_outer ,
            #             "left_ear"        : left_ear        ,
            #             "right_ear"       : right_ear       ,
            #             "left_mouth"      : left_mouth      ,
            #             "right_mouth"     : right_mouth     ,
            #             "left_shoulder"   : left_shoulder   ,
            #             "right_shoulder"  : right_shoulder  ,
            #             "left_elbow"      : left_elbow      ,
            #             "right_elbow"     : right_elbow     ,
            #             "left_wrist"      : left_wrist      ,
            #             "right_wrist"     : right_wrist     ,
            #             "left_pinky"      : left_pinky      ,
            #             "right_pinky"     : right_pinky     ,
            #             "left_index"      : left_index      ,
            #             "right_index"     : right_index     ,
            #             "left_thumb"      : left_thumb      ,
            #             "right_thumb"     : right_thumb     ,
            #             "left_hip"        : left_hip        ,
            #             "right_hip"       : right_hip       ,
            #             "left_knee"       : left_knee       ,
            #             "right_knee"      : right_knee      ,
            #             "left_ankle"      : left_ankle      ,
            #             "right_ankle"     : right_ankle     ,
            #             "left_heel"       : left_heel       ,
            #             "right_heel"      : right_heel      ,
            #             "left_foot_index" : left_foot_index ,
            #             "right_foot_index": right_foot_index,
            #             # "ball"            : ball            ,
            #             "Side"            : side            ,
            #             "frame"           : frame_index     ,
            #             "postion"         : "MAX_HAND"
            #         } 
            if wrist is not None:
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
                    # "wrist"           : wrist,
                    # "ball"            : ball            ,
                    # "Side"            : side            ,
                    "frame"           : frame_index     ,
                    "postion"         : "HAND"
                } 
                hand_frame_data[frame_index] = frame_data

        frame_index += 1

    cap.release()
    # print(f"hand_frame_data: {hand_frame_data}")
    # print(f"waist_level_data: {waist_level_data}")
    # print(f"eye_level_data:{eye_level_data}")
    # if len(eye_level_data) > 0:
    #     earliest_eye_index = min(eye_level_data.keys())
    #     latest_eye_index = max(eye_level_data.keys())
    #     latest_eye_frame = eye_level_data[latest_eye_index]
    #     waist_before_index = None
    #     for w_i in waist_level_data.keys():
    #         if w_i < earliest_eye_index:
    #             if waist_before_index is None or w_i > waist_before_index:
    #                 waist_before_index = w_i
    #     waist_frame_before_eye = waist_level_data[waist_before_index] if waist_before_index is not None else None
    # else:
    #     # earliest_eye_frame = None
    #     latest_eye_frame = None
    #     waist_frame_before_eye = None
    # # if earliest_eye_frame is not None and waist_frame_before_eye is not None and max_hand_frame_data is not None:
    # if latest_eye_frame is not None and waist_frame_before_eye is not None and max_hand_frame_data is not None:
    #     return waist_frame_before_eye, latest_eye_frame, max_hand_frame_data
    # else:
    #     return None
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
        hand_after_index = None
        max_wrist_y = None
        for h_i in hand_frame_data.keys():
            if h_i > latest_eye_index:
                wrist = choose_valid_side(hand_frame_data[h_i]["left_wrist"], hand_frame_data[h_i]["right_wrist"])
                wrist_y = wrist[1] if wrist is not None else float('inf')
                if max_wrist_y is None or wrist_y > max_wrist_y:
                    max_wrist_y = wrist_y
                    hand_after_index = h_i
        max_hand_frame_data = hand_frame_data[hand_after_index] if hand_after_index is not None else None
    else:
        latest_eye_frame = None
        waist_frame_before_eye = None
        max_hand_frame_data = None

    if latest_eye_frame is not None or waist_frame_before_eye is not None or max_hand_frame_data is not None:
        return waist_frame_before_eye, latest_eye_frame, max_hand_frame_data
    else:
        return None, None, None

if __name__ == "__main__":
    # pose_data_waist, pose_data_eye, pose_data_high_hand= analyze_video("nba_1.mp4")  
    # print(f"nba_1 waist: {pose_data_waist}\nnba_1 eye: {pose_data_eye}\nnba_1 max hand: {pose_data_high_hand}")
    # print('\n')
    # pose_data_waist, pose_data_eye, pose_data_high_hand= analyze_video("nba_2.mp4")  
    # print(f"nba_2 waist: {pose_data_waist}\nnba_2 eye: {pose_data_eye}\nnba_2 max hand: {pose_data_high_hand}")
    # print('\n')
    # pose_data_waist, pose_data_eye, pose_data_high_hand= analyze_video("nba_3.mp4")  
    # print(f"nba_3 waist: {pose_data_waist}\nnba_3 eye: {pose_data_eye}\nnba_3 max hand: {pose_data_high_hand}")
    # print('\n')
    # pose_data_waist, pose_data_eye, pose_data_high_hand= analyze_video("nba_4.mp4")  
    # print(f"nba_4 waist: {pose_data_waist}\nnba_4 eye: {pose_data_eye}\nnba_4 max hand: {pose_data_high_hand}")
    # print('\n')
    # pose_data_waist, pose_data_eye, pose_data_high_hand= analyze_video("nba_5.mp4")  
    # print(f"nba_5 waist: {pose_data_waist}\nnba_5 eye: {pose_data_eye}\nnba_5 max hand: {pose_data_high_hand}")
    # print('\n')
    # pose_data_waist, pose_data_eye, pose_data_high_hand= analyze_video("nba_6.mp4")  
    # print(f"nba_6 waist: {pose_data_waist}\nnba_6 eye: {pose_data_eye}\nnba_6 max hand: {pose_data_high_hand}")
    # print('\n')
    # pose_data_waist, pose_data_eye, pose_data_high_hand= analyze_video("nba_7.mp4")  
    # print(f"nba_7 waist: {pose_data_waist}\nnba_7 eye: {pose_data_eye}\nnba_7 max hand: {pose_data_high_hand}")
    # print('\n')
    # pose_data_waist, pose_data_eye, pose_data_high_hand= analyze_video("nba_8.mp4")  
    # print(f"nba_8 waist: {pose_data_waist}\nnba_8 eye: {pose_data_eye}\nnba_8 max hand: {pose_data_high_hand}")
    # print('\n')
    # pose_data_waist, pose_data_eye, pose_data_high_hand= analyze_video("nba_9.mp4")  
    # print(f"nba_9 waist: {pose_data_waist}\nnba_9 eye: {pose_data_eye}\nnba_9 max hand: {pose_data_high_hand}")
    # print('\n')
    # pose_data_waist, pose_data_eye, pose_data_high_hand= analyze_video("nba_10.mp4")  
    # print(f"nba_10 waist: {pose_data_waist}\nnba_10 eye: {pose_data_eye}\nnba_10 max hand: {pose_data_high_hand}")
    # print('\n')
    # pose_data_waist, pose_data_eye, pose_data_high_hand= analyze_video("nba_11.mp4")  
    # print(f"nba_11 waist: {pose_data_waist}\nnba_11 eye: {pose_data_eye}\nnba_11 max hand: {pose_data_high_hand}")
    # print('\n')
    # pose_data_waist, pose_data_eye, pose_data_high_hand= analyze_video("nba_12.mp4")  
    # print(f"nba_12 waist: {pose_data_waist}\nnba_12 eye: {pose_data_eye}\nnba_12 max hand: {pose_data_high_hand}")
    # print('\n')
    # pose_data_waist, pose_data_eye, pose_data_high_hand= analyze_video("nba_13.mp4")  
    # print(f"nba_13 waist: {pose_data_waist}\nnba_13 eye: {pose_data_eye}\nnba_13 max hand: {pose_data_high_hand}")
    # print('\n')
    # pose_data_waist, pose_data_eye, pose_data_high_hand= analyze_video("nba_14.mp4")  
    # print(f"nba_14 waist: {pose_data_waist}\nnba_14 eye: {pose_data_eye}\nnba_14 max hand: {pose_data_high_hand}")
    # print('\n')
    # pose_data_waist, pose_data_eye, pose_data_high_hand= analyze_video("nba_15.mp4")  
    # print(f"nba_15 waist: {pose_data_waist}\nnba_15 eye: {pose_data_eye}\nnba_15 max hand: {pose_data_high_hand}")
    # print('\n')
    # pose_data_waist, pose_data_eye, pose_data_high_hand= analyze_video("nba_16.mp4")  
    # print(f"nba_16 waist: {pose_data_waist}\nnba_16 eye: {pose_data_eye}\nnba_16 max hand: {pose_data_high_hand}")
    # print('\n')
    # pose_data_waist, pose_data_eye, pose_data_high_hand= analyze_video("nba_17.mp4")  
    # print(f"nba_17 waist: {pose_data_waist}\nnba_17 eye: {pose_data_eye}\nnba_17 max hand: {pose_data_high_hand}")
    # print('\n')
    # pose_data_waist, pose_data_eye, pose_data_high_hand= analyze_video("nba_18.mp4")  
    # print(f"nba_18 waist: {pose_data_waist}\nnba_18 eye: {pose_data_eye}\nnba_18 max hand: {pose_data_high_hand}")
    # print('\n')
    # pose_data_waist, pose_data_eye, pose_data_high_hand= analyze_video("nba_19.mp4")  
    # print(f"nba_19 waist: {pose_data_waist}\nnba_19 eye: {pose_data_eye}\nnba_19 max hand: {pose_data_high_hand}")
    # print('\n')
    # pose_data_waist, pose_data_eye, pose_data_high_hand= analyze_video("nba_20.mp4")  
    # print(f"nba_20 waist: {pose_data_waist}\nnba_20 eye: {pose_data_eye}\nnba_20 max hand: {pose_data_high_hand}")
    # print('\n')
    # pose_data_waist, pose_data_eye, pose_data_high_hand= analyze_video("nba_21.mp4")  
    # print(f"nba_21 waist: {pose_data_waist}\nnba_21 eye: {pose_data_eye}\nnba_21 max hand: {pose_data_high_hand}")
    # print('\n')
    # pose_data_waist, pose_data_eye, pose_data_high_hand= analyze_video("nba_22.mp4")  
    # print(f"nba_22 waist: {pose_data_waist}\nnba_22 eye: {pose_data_eye}\nnba_22 max hand: {pose_data_high_hand}")
    # print('\n')
    # pose_data_waist, pose_data_eye, pose_data_high_hand= analyze_video("nba_23.mp4")  
    # print(f"nba_23 waist: {pose_data_waist}\nnba_23 eye: {pose_data_eye}\nnba_23 max hand: {pose_data_high_hand}")
    # print('\n')
    # pose_data_waist, pose_data_eye, pose_data_high_hand= analyze_video("nba_24.mp4")  
    # print(f"nba_24 waist: {pose_data_waist}\nnba_24 eye: {pose_data_eye}\nnba_24 max hand: {pose_data_high_hand}")
    # print('\n')
    # pose_data_waist, pose_data_eye, pose_data_high_hand= analyze_video("nba_25.mp4")  
    # print(f"nba_25 waist: {pose_data_waist}\nnba_25 eye: {pose_data_eye}\nnba_25 max hand: {pose_data_high_hand}")
    # print('\n')
    # pose_data_waist, pose_data_eye, pose_data_high_hand= analyze_video("nba_26.mp4")  
    # print(f"nba_26 waist: {pose_data_waist}\nnba_26 eye: {pose_data_eye}\nnba_26 max hand: {pose_data_high_hand}")
    # print('\n')
    # pose_data_waist, pose_data_eye, pose_data_high_hand= analyze_video("nba_27.mp4")  
    # print(f"nba_27 waist: {pose_data_waist}\nnba_27 eye: {pose_data_eye}\nnba_27 max hand: {pose_data_high_hand}")
    # print('\n')
    # pose_data_waist, pose_data_eye, pose_data_high_hand= analyze_video("nba_28.mp4")  
    # print(f"nba_28 waist: {pose_data_waist}\nnba_28 eye: {pose_data_eye}\nnba_28 max hand: {pose_data_high_hand}")
    # print('\n')
    # pose_data_waist, pose_data_eye, pose_data_high_hand= analyze_video("nba_29.mp4")  
    # print(f"nba_29 waist: {pose_data_waist}\nnba_29 eye: {pose_data_eye}\nnba_29 max hand: {pose_data_high_hand}")
    pose_data_waist, pose_data_eye, pose_data_high_hand= analyze_video("/root/ShotMatch/video/klay/klay_front_01.mp4")  
    print(f"klay_front_01 waist: {pose_data_waist}\nklay_front_01 eye: {pose_data_eye}\nklay_front_01 max_hand: {pose_data_high_hand}")
    print('\n')
    pose_data_waist, pose_data_eye, pose_data_high_hand= analyze_video("/root/ShotMatch/video/klay/klay_front_02.mp4")  
    print(f"klay_front_02 waist: {pose_data_waist}\nklay_front_02 eye: {pose_data_eye}\nklay_front_02 max_hand: {pose_data_high_hand}")
    print('\n')
    pose_data_waist, pose_data_eye, pose_data_high_hand= analyze_video("/root/ShotMatch/video/klay/klay_front_03.mp4")  
    print(f"klay_front_03 waist: {pose_data_waist}\nklay_front_03 eye: {pose_data_eye}\nklay_front_03 max_hand: {pose_data_high_hand}")
    print('\n')
    pose_data_waist, pose_data_eye, pose_data_high_hand= analyze_video("/root/ShotMatch/video/klay/klay_front_04.mp4")  
    print(f"klay_front_04 waist: {pose_data_waist}\nklay_front_04 eye: {pose_data_eye}\nklay_front_04 max_hand: {pose_data_high_hand}")
    print('\n')
    pose_data_waist, pose_data_eye, pose_data_high_hand= analyze_video("/root/ShotMatch/video/klay/klay_front_05.mp4")  
    print(f"klay_front_05 waist: {pose_data_waist}\nklay_front_05 eye: {pose_data_eye}\nklay_front_05 max_hand: {pose_data_high_hand}")
    print('\n')
    pose_data_waist, pose_data_eye, pose_data_high_hand= analyze_video("/root/ShotMatch/video/klay/klay_front_06.mp4")  
    print(f"klay_front_06 waist: {pose_data_waist}\nklay_front_06 eye: {pose_data_eye}\nklay_front_06 max_hand: {pose_data_high_hand}")
    print('\n')
    pose_data_waist, pose_data_eye, pose_data_high_hand= analyze_video("/root/ShotMatch/video/klay/klay_front_07.mp4")  
    print(f"klay_front_07 waist: {pose_data_waist}\nklay_front_07 eye: {pose_data_eye}\nklay_front_07 max_hand: {pose_data_high_hand}")
    print('\n')
    pose_data_waist, pose_data_eye, pose_data_high_hand= analyze_video("/root/ShotMatch/video/klay/klay_front_08.mp4")  
    print(f"klay_front_08 waist: {pose_data_waist}\nklay_front_08 eye: {pose_data_eye}\nklay_front_08 max_hand: {pose_data_high_hand}")
    print('\n')
    pose_data_waist, pose_data_eye, pose_data_high_hand= analyze_video("/root/ShotMatch/video/klay/klay_front_09.mp4")  
    print(f"klay_front_09 waist: {pose_data_waist}\nklay_front_09 eye: {pose_data_eye}\nklay_front_09 max_hand: {pose_data_high_hand}")
    print('\n')
    pose_data_waist, pose_data_eye, pose_data_high_hand= analyze_video("/root/ShotMatch/video/klay/klay_front_10.mp4")  
    print(f"klay_front_10 waist: {pose_data_waist}\nklay_front_10 eye: {pose_data_eye}\nklay_front_10 max_hand: {pose_data_high_hand}")
    print('\n')
    pose_data_waist, pose_data_eye, pose_data_high_hand= analyze_video("/root/ShotMatch/video/klay/klay_front_11.mp4")  
    print(f"klay_front_11 waist: {pose_data_waist}\nklay_front_11 eye: {pose_data_eye}\nklay_front_11 max_hand: {pose_data_high_hand}")
    print('\n')
    pose_data_waist, pose_data_eye, pose_data_high_hand= analyze_video("/root/ShotMatch/video/klay/klay_front_12.mp4")  
    print(f"klay_front_12 waist: {pose_data_waist}\nklay_front_12 eye: {pose_data_eye}\nklay_front_12 max_hand: {pose_data_high_hand}")
    print('\n')
    pose_data_waist, pose_data_eye, pose_data_high_hand= analyze_video("/root/ShotMatch/video/klay/klay_front_13.mp4")  
    print(f"klay_front_13 waist: {pose_data_waist}\nklay_front_13 eye: {pose_data_eye}\nklay_front_13 max_hand: {pose_data_high_hand}")
    print('\n')
    pose_data_waist, pose_data_eye, pose_data_high_hand= analyze_video("/root/ShotMatch/video/klay/klay_front_14.mp4")  
    print(f"klay_front_14 waist: {pose_data_waist}\nklay_front_14 eye: {pose_data_eye}\nklay_front_14 max_hand: {pose_data_high_hand}")
    print('\n')
    pose_data_waist, pose_data_eye, pose_data_high_hand= analyze_video("/root/ShotMatch/video/klay/klay_front_15.mp4")  
    print(f"klay_front_15 waist: {pose_data_waist}\nklay_front_15 eye: {pose_data_eye}\nklay_front_15 max_hand: {pose_data_high_hand}")
    print('\n')
    pose_data_waist, pose_data_eye, pose_data_high_hand= analyze_video("/root/ShotMatch/video/klay/klay_front_16.mp4")  
    print(f"klay_front_16 waist: {pose_data_waist}\nklay_front_16 eye: {pose_data_eye}\nklay_front_16 max_hand: {pose_data_high_hand}")
    print('\n')
    pose_data_waist, pose_data_eye, pose_data_high_hand= analyze_video("/root/ShotMatch/video/klay/klay_front_17.mp4")  
    print(f"klay_front_17 waist: {pose_data_waist}\nklay_front_17 eye: {pose_data_eye}\nklay_front_17 max_hand: {pose_data_high_hand}")
    print('\n')
    pose_data_waist, pose_data_eye, pose_data_high_hand= analyze_video("/root/ShotMatch/video/klay/klay_side_ra_01.mp4")  
    print(f"klay_side_ra_01 waist: {pose_data_waist}\nklay_side_ra_01 eye: {pose_data_eye}\nklay_side_ra_01 max_hand: {pose_data_high_hand}")
    print('\n')
    pose_data_waist, pose_data_eye, pose_data_high_hand= analyze_video("/root/ShotMatch/video/klay/klay_side_ra_02.mp4")  
    print(f"klay_side_ra_02 waist: {pose_data_waist}\nklay_side_ra_02 eye: {pose_data_eye}\nklay_side_ra_02 max_hand: {pose_data_high_hand}")
    print('\n')
    pose_data_waist, pose_data_eye, pose_data_high_hand= analyze_video("/root/ShotMatch/video/klay/klay_side_ra_03.mp4")  
    print(f"klay_side_ra_03 waist: {pose_data_waist}\nklay_side_ra_03 eye: {pose_data_eye}\nklay_side_ra_03 max_hand: {pose_data_high_hand}")
    print('\n')
    pose_data_waist, pose_data_eye, pose_data_high_hand= analyze_video("/root/ShotMatch/video/klay/klay_side_ra_04.mp4")  
    print(f"klay_side_ra_04 waist: {pose_data_waist}\nklay_side_ra_04 eye: {pose_data_eye}\nklay_side_ra_04 max_hand: {pose_data_high_hand}")
    print('\n')
    pose_data_waist, pose_data_eye, pose_data_high_hand= analyze_video("/root/ShotMatch/video/klay/klay_side_ra_05.mp4")  
    print(f"klay_side_ra_05 waist: {pose_data_waist}\nklay_side_ra_05 eye: {pose_data_eye}\nklay_side_ra_05 max_hand: {pose_data_high_hand}")
    print('\n')
    pose_data_waist, pose_data_eye, pose_data_high_hand= analyze_video("/root/ShotMatch/video/klay/klay_side_ra_06.mp4")  
    print(f"klay_side_ra_06 waist: {pose_data_waist}\nklay_side_ra_06 eye: {pose_data_eye}\nklay_side_ra_06 max_hand: {pose_data_high_hand}")
    print('\n')
    pose_data_waist, pose_data_eye, pose_data_high_hand= analyze_video("/root/ShotMatch/video/klay/klay_side_ra_07.mp4")  
    print(f"klay_side_ra_07 waist: {pose_data_waist}\nklay_side_ra_07 eye: {pose_data_eye}\nklay_side_ra_07 max_hand: {pose_data_high_hand}")
    print('\n')
    pose_data_waist, pose_data_eye, pose_data_high_hand= analyze_video("/root/ShotMatch/video/klay/klay_side_ra_08.mp4")  
    print(f"klay_side_ra_08 waist: {pose_data_waist}\nklay_side_ra_08 eye: {pose_data_eye}\nklay_side_ra_08 max_hand: {pose_data_high_hand}")
    print('\n')
    pose_data_waist, pose_data_eye, pose_data_high_hand= analyze_video("/root/ShotMatch/video/klay/klay_side_ra_09.mp4")  
    print(f"klay_side_ra_09 waist: {pose_data_waist}\nklay_side_ra_09 eye: {pose_data_eye}\nklay_side_ra_09 max_hand: {pose_data_high_hand}")
    print('\n')
    pose_data_waist, pose_data_eye, pose_data_high_hand= analyze_video("/root/ShotMatch/video/klay/klay_side_ra_10.mp4")  
    print(f"klay_side_ra_10 waist: {pose_data_waist}\nklay_side_ra_10 eye: {pose_data_eye}\nklay_side_ra_10 max_hand: {pose_data_high_hand}")
    print('\n')


    '''
    pose_data_waist, pose_data_eye, pose_data_high_hand= analyze_video("/root/ShotMatch/video/lebron/lebron_front_01.mp4")  
    print(f"lebron_front_01 waist: {pose_data_waist}\nlebron_front_01 eye: {pose_data_eye}\nlebron_front_01 max_hand: {pose_data_high_hand}")
    print('\n')
    pose_data_waist, pose_data_eye, pose_data_high_hand= analyze_video("/root/ShotMatch/video/lebron/lebron_front_02.mp4")  
    print(f"lebron_front_02 waist: {pose_data_waist}\nlebron_front_02 eye: {pose_data_eye}\nlebron_front_02 max_hand: {pose_data_high_hand}")
    print('\n')
    pose_data_waist, pose_data_eye, pose_data_high_hand= analyze_video("/root/ShotMatch/video/lebron/lebron_front_03.mp4")  
    print(f"lebron_front_03 waist: {pose_data_waist}\nlebron_front_03 eye: {pose_data_eye}\nlebron_front_03 max_hand: {pose_data_high_hand}")
    print('\n')
    pose_data_waist, pose_data_eye, pose_data_high_hand= analyze_video("/root/ShotMatch/video/lebron/lebron_front_04.mp4")  
    print(f"lebron_front_04 waist: {pose_data_waist}\nlebron_front_04 eye: {pose_data_eye}\nlebron_front_04 max_hand: {pose_data_high_hand}")
    print('\n')
    pose_data_waist, pose_data_eye, pose_data_high_hand= analyze_video("/root/ShotMatch/video/lebron/lebron_front_05.mp4")  
    print(f"lebron_front_05 waist: {pose_data_waist}\nlebron_front_05 eye: {pose_data_eye}\nlebron_front_05 max_hand: {pose_data_high_hand}")
    print('\n')
    pose_data_waist, pose_data_eye, pose_data_high_hand= analyze_video("/root/ShotMatch/video/lebron/lebron_front_06.mp4")  
    print(f"lebron_front_06 waist: {pose_data_waist}\nlebron_front_06 eye: {pose_data_eye}\nlebron_front_06 max_hand: {pose_data_high_hand}")
    print('\n')
    pose_data_waist, pose_data_eye, pose_data_high_hand= analyze_video("/root/ShotMatch/video/lebron/lebron_front_07.mp4")  
    print(f"lebron_front_07 waist: {pose_data_waist}\nlebron_front_07 eye: {pose_data_eye}\nlebron_front_07 max_hand: {pose_data_high_hand}")
    print('\n')
    pose_data_waist, pose_data_eye, pose_data_high_hand= analyze_video("/root/ShotMatch/video/lebron/lebron_front_08.mp4")  
    print(f"lebron_front_08 waist: {pose_data_waist}\nlebron_front_08 eye: {pose_data_eye}\nlebron_front_08 max_hand: {pose_data_high_hand}")
    print('\n')
    pose_data_waist, pose_data_eye, pose_data_high_hand= analyze_video("/root/ShotMatch/video/lebron/lebron_front_09.mp4")  
    print(f"lebron_front_09 waist: {pose_data_waist}\nlebron_front_09 eye: {pose_data_eye}\nlebron_front_09 max_hand: {pose_data_high_hand}")
    print('\n')
    pose_data_waist, pose_data_eye, pose_data_high_hand= analyze_video("/root/ShotMatch/video/lebron/lebron_front_10.mp4")  
    print(f"lebron_front_10 waist: {pose_data_waist}\nlebron_front_10 eye: {pose_data_eye}\nlebron_front_10 max_hand: {pose_data_high_hand}")
    print('\n')
    pose_data_waist, pose_data_eye, pose_data_high_hand= analyze_video("/root/ShotMatch/video/lebron/lebron_side_ra_01.mp4")  
    print(f"lebron_side_ra_01 waist: {pose_data_waist}\nlebron_side_ra_01 eye: {pose_data_eye}\nlebron_side_ra_01 max_hand: {pose_data_high_hand}")
    print('\n')
    pose_data_waist, pose_data_eye, pose_data_high_hand= analyze_video("/root/ShotMatch/video/lebron/lebron_side_ra_02.mp4")  
    print(f"lebron_side_ra_02 waist: {pose_data_waist}\nlebron_side_ra_02 eye: {pose_data_eye}\nlebron_side_ra_02 max_hand: {pose_data_high_hand}")
    print('\n')
    pose_data_waist, pose_data_eye, pose_data_high_hand= analyze_video("/root/ShotMatch/video/lebron/lebron_side_ra_03.mp4")  
    print(f"lebron_side_ra_03 waist: {pose_data_waist}\nlebron_side_ra_03 eye: {pose_data_eye}\nlebron_side_ra_03 max_hand: {pose_data_high_hand}")
    print('\n')
    pose_data_waist, pose_data_eye, pose_data_high_hand= analyze_video("/root/ShotMatch/video/lebron/lebron_side_ra_04.mp4")  
    print(f"lebron_side_ra_04 waist: {pose_data_waist}\nlebron_side_ra_04 eye: {pose_data_eye}\nlebron_side_ra_04 max_hand: {pose_data_high_hand}")
    print('\n')
    pose_data_waist, pose_data_eye, pose_data_high_hand= analyze_video("/root/ShotMatch/video/lebron/lebron_side_ra_05.mp4")  
    print(f"lebron_side_ra_05 waist: {pose_data_waist}\nlebron_side_ra_05 eye: {pose_data_eye}\nlebron_side_ra_05 max_hand: {pose_data_high_hand}")
    print('\n')
    pose_data_waist, pose_data_eye, pose_data_high_hand= analyze_video("/root/ShotMatch/video/lebron/lebron_side_ra_06.mp4")  
    print(f"lebron_side_ra_06 waist: {pose_data_waist}\nlebron_side_ra_06 eye: {pose_data_eye}\nlebron_side_ra_06 max_hand: {pose_data_high_hand}")
    print('\n')
    '''
    pass
