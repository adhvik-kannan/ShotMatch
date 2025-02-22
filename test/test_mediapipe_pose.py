import pytest
import cv2
import mediapipe as mp
from unittest.mock import MagicMock, patch
from src.generate_front_statistics import calculate_angle

mp_pose = mp.solutions.pose

@pytest.fixture
def mock_pose_landmarks():
    mock_landmarks = MagicMock()
    mock_landmarks.landmark = [MagicMock(x=0.5, y=0.5, z=0) for _ in range(33)]
    return mock_landmarks

@patch("mediapipe.solutions.pose.Pose.process")
def test_pose_recognition(mock_process, mock_pose_landmarks):
    mock_process.return_value = MagicMock(pose_landmarks=mock_pose_landmarks)

    frame = cv2.imread("./test/test_image.jpg") 
    if frame is None:
        pytest.fail("Test image not found")

    with mp_pose.Pose(static_image_mode=True) as pose:
        image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = pose.process(image_rgb)

        mock_process.assert_called_once()

        assert results.pose_landmarks is not None, "Pose landmarks Recognition failed"
        assert len(results.pose_landmarks.landmark) == 33, "Landmark number is not correct"

        left_shoulder = results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_SHOULDER.value]
        left_elbow = results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_ELBOW.value]
        left_wrist = results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_WRIST.value]

        assert 0 <= left_shoulder.x <= 1, "Left Shoulder X Coordinate is not correct"
        assert 0 <= left_shoulder.y <= 1, "Left Shoulder Y Coordinate is not correct"

        shoulder_coord = (int(left_shoulder.x * 100), int(left_shoulder.y * 100))
        elbow_coord = (int(left_elbow.x * 100), int(left_elbow.y * 100))
        wrist_coord = (int(left_wrist.x * 100), int(left_wrist.y * 100))

        angle = calculate_angle(shoulder_coord, elbow_coord, wrist_coord)
        assert 0 <= angle <= 180, f"Angle Calculation not correct: {angle}"

