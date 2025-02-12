import cv2
import mediapipe as mp
import math

def calculate_angle(a, b, c):
    AB = (a[0] - b[0], a[1] - b[1])
    CB = (c[0] - b[0], c[1] - b[1])
    
    dot_product = AB[0]*CB[0] + AB[1]*CB[1]
    AB_magnitude = math.sqrt(AB[0]**2 + AB[1]**2)
    CB_magnitude = math.sqrt(CB[0]**2 + CB[1]**2)
    
    if AB_magnitude == 0 or CB_magnitude == 0:
        return 0.0
    
    cos_value = max(min(dot_product / (AB_magnitude * CB_magnitude), 1.0), -1.0)
    return math.degrees(math.acos(cos_value))

mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose

# PATH of the VIDEO FILE
cap = cv2.VideoCapture("your_video.mp4")

with mp_pose.Pose(static_image_mode=False, model_complexity=1, smooth_landmarks=True, enable_segmentation=False, min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
    
    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            break
        
        frame = cv2.flip(frame, 1)
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = pose.process(image)
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        
        if results.pose_landmarks:
            landmarks = results.pose_landmarks.landmark
            h, w, _ = image.shape
            
            left_shoulder = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value]
            left_elbow = landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value]
            left_wrist = landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value]
            
            shoulder_coord = (int(left_shoulder.x * w), int(left_shoulder.y * h))
            elbow_coord = (int(left_elbow.x * w), int(left_elbow.y * h))
            wrist_coord = (int(left_wrist.x * w), int(left_wrist.y * h))
            
            angle = calculate_angle(shoulder_coord, elbow_coord, wrist_coord)
            
            mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS, mp_drawing.DrawingSpec(color=(245,117,66), thickness=2, circle_radius=4), mp_drawing.DrawingSpec(color=(245,66,230), thickness=2, circle_radius=2))
            
            cv2.putText(image, f"Angle: {int(angle)}", (elbow_coord[0], elbow_coord[1]-20), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
            
            if angle > 160:
                action = "Arm Extended"
            elif angle < 60:
                action = "Arm Bent"
            else:
                action = "Neutral"
            
            cv2.putText(image, action, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        
        cv2.imshow('Pose Detection', image)
        
        if cv2.waitKey(1) & 0xFF == 27:
            break

cap.release()
cv2.destroyAllWindows()
