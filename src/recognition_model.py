import cv2
import mediapipe as mp
from ultralytics import YOLO
import numpy as np

# VISIBILITY_THRESHOLD = 0.5  # Set to 0.5 for now
model = YOLO('yolo12x.pt')

def detect_ball(frame):
    '''
    INPUT: 
    frame: frame in video
    OUTPUT:
    ball[0] the most likely xy coordinate to be the ball
    '''
    image_height = frame.shape[0]
    results = model(frame, conf=0.25, iou=0.45, augment=True, verbose=False)
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

def detect_side(right_shoulder, right_elbow, right_wrist, left_shoulder, left_elbow, left_wrist):
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

def eye_level_measurement(eye, mouth, ball, wrist, height):
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
    if eye is not None and mouth is None:
        eye_x, eye_y = eye
        mouth_x, mouth_y = mouth
        if ball is not None:
            ball_x, ball_y = ball
            ball[1] = height - ball_y
            if ball_y < (2 * eye_y) - mouth_y and ball_y > (2 * mouth_y) - eye_y:
            # if ball_y < eye_y and ball_y > mouth_y:
                frame_flag = True
        #  如果球不存在，那么看手腕的高度
        elif wrist is not None:
            wrist_x, wrist_y = wrist
            if wrist_y < (2 * eye_y) - mouth_y and wrist_y > (2 * mouth_y) - eye_y:
                frame_flag = True
    return frame_flag


# TODO: NOT DONE
def waist_level_measurement(hip, wrist, shoulder, ball, height):
    frame_flag = False
    if hip is not None and shoulder is None:
        hip_x, hip_y = hip
        shoulder_x, shoulder_y = shoulder
        if ball is not None:
            ball_x, ball_y = ball
            ball[1] = height - ball_y
            if ball_y < shoulder_y and ball_y > hip_y:
                frame_flag = True
        elif wrist is not None:
            wrist_x, wrist_y = wrist
            if wrist_y < shoulder_y and wrist_y > hip_y:
                frame_flag = True
    return frame_flag
                

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
    eye_level_data = {}
    waist_level_data = {}

    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            break

        rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = pose.process(rgb_image)

        # Convert back to BGR for consistent processing (even if not displayed)
        # annotated_image = cv2.cvtColor(rgb_image, cv2.COLOR_RGB2BGR)

        frame_data = {}

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

            ball    = detect_ball(frame)
            eye     = choose_valid_side(left_eye, right_eye)
            mouth   = choose_valid_side(left_mouth, right_mouth)
            wrist   = choose_valid_side(left_wrist, right_wrist)
            pinky   = choose_valid_side(left_pinky, right_pinky)
            hip     = choose_valid_side(left_hip, right_hip)
            shoulder= choose_valid_side(left_shoulder, right_shoulder)
            side    = detect_side(right_shoulder, right_elbow, right_wrist, left_shoulder, left_elbow, left_wrist)
            
            eye_flag = eye_level_measurement(eye, mouth, ball, wrist, h)
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
                        "ball"            : ball            ,
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
                        "ball"            : ball            ,
                        "Side"            : side            ,
                        "frame"           : frame_index     ,
                        "postion"         : "WAIST"
                    } 
                waist_level_data[frame_index] = frame_data
            # waist_leve_data = waist_level_measurement(wrist, ball, hip)
            # print(f"Output Data:{eye_level_data}")
                    
            

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
    if len(eye_level_data) != 0 and len(waist_level_data) != 0:
        min_waist = min(waist_level_data.keys())
        max_key = max(eye_level_data.keys())
        fps = cap.get(cv2.CAP_PROP_FPS)
        offset_frame = int(max_key + fps * 0.1)
        cap = cv2.VideoCapture(video_path)
        cap.set(cv2.CAP_PROP_POS_FRAMES, offset_frame)
        success, frame = cap.read()
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
            ball    = detect_ball(frame)
            eye     = choose_valid_side(left_eye, right_eye)
            mouth   = choose_valid_side(left_mouth, right_mouth)
            wrist   = choose_valid_side(left_wrist, right_wrist)
            pinky   = choose_valid_side(left_pinky, right_pinky)
            hip     = choose_valid_side(left_hip, right_hip)
            shoulder= choose_valid_side(left_shoulder, right_shoulder)
            side    = detect_side(right_shoulder, right_elbow, right_wrist, left_shoulder, left_elbow, left_wrist)
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
                        "ball"            : ball            ,
                        "Side"            : side            ,
                        "frame"           : frame_index     ,
                        "postion"         : "AFTER_EYE"
                    } 
        max_value = eye_level_data[max_key]
        min_value = waist_level_data[min_waist]
        # return eye_level_data
        return min_value, max_value, frame_data
    else:
        return None

# example usage:
if __name__ == "__main__":
    # pose_data = analyze_video("nba_1.mp4")  
    # print(f"nba_1: {pose_data}")
    # pose_data = analyze_video("nba_2.mp4")
    # print(f"nba_2: {pose_data}")
    # pose_data = analyze_video("nba_3.mp4")
    # print(f"nba_3: {pose_data}")
    # pose_data = analyze_video("nba_4.mp4")
    # print(f"nba_4: {pose_data}")
    # pose_data = analyze_video("nba_5.mp4")
    # print(f"nba_5: {pose_data}")
    # pose_data = analyze_video("nba_6.mp4")
    # print(f"nba_6: {pose_data}")
    # pose_data = analyze_video("nba_7.mp4")
    # print(f"nba_7: {pose_data}")
    # pose_data = analyze_video("nba_8.mp4")
    # print(f"nba_8: {pose_data}")
    # pose_data = analyze_video("nba_9.mp4")
    # print(f"nba_9: {pose_data}")
    # pose_data = analyze_video("nba_10.mp4")
    # print(f"nba_10: {pose_data}")
    # pose_data = analyze_video("nba_11.mp4")
    # print(f"nba_11: {pose_data}")
    # pose_data = analyze_video("nba_12.mp4")
    # print(f"nba_12: {pose_data}")
    # pose_data = analyze_video("nba_13.mp4")
    # print(f"nba_13: {pose_data}")
    # pose_data = analyze_video("nba_14.mp4")
    # print(f"nba_14: {pose_data}")
    # pose_data = analyze_video("nba_15.mp4")
    # print(f"nba_15: {pose_data}")
    # pose_data = analyze_video("nba_16.mp4")
    # print(f"nba_16: {pose_data}")
    # pose_data = analyze_video("nba_17.mp4")
    # print(f"nba_17: {pose_data}")
    # pose_data = analyze_video("nba_18.mp4")
    # print(f"nba_18: {pose_data}")
    pose_data = analyze_video("nba_19.mp4")
    print(f"nba_19: {pose_data}")
    # pose_data = analyze_video("nba_20.mp4")
    # print(f"nba_20: {pose_data}")
    # pose_data = analyze_video("nba_21.mp4")
    # print(f"nba_21: {pose_data}")
    pose_data = analyze_video("nba_22.mp4")
    print(f"nba_22: {pose_data}")
    # pose_data = analyze_video("nba_23.mp4")
    # print(f"nba_23: {pose_data}")
    # pose_data = analyze_video("nba_24.mp4")
    # print(f"nba_24: {pose_data}")
    # pose_data = analyze_video("nba_25.mp4")
    # print(f"nba_25: {pose_data}")
    # pose_data = analyze_video("nba_26.mp4")
    # print(f"nba_26: {pose_data}")
    # pose_data = analyze_video("nba_27.mp4")
    # print(f"nba_27: {pose_data}")
    # pose_data = analyze_video("nba_29.mp4")
    # print(f"klay: {pose_data}")
