import pytest
import cv2
import numpy as np
from unittest.mock import patch, MagicMock
from src.recognition_model import detect_ball, get_landmark_xy, analyze_video

@pytest.fixture
def sample_frame():
    """Generates a blank test frame for testing."""
    return np.zeros((480, 640, 3), dtype=np.uint8)

@pytest.fixture
def mock_video():
    """Mocks cv2.VideoCapture to return frames without needing an actual video file."""
    cap_mock = MagicMock()
    cap_mock.isOpened.side_effect = [True, True, False]  # Simulate 2 frames
    cap_mock.read.side_effect = [(True, np.zeros((480, 640, 3), dtype=np.uint8)), (True, np.zeros((480, 640, 3), dtype=np.uint8)), (False, None)]
    return cap_mock


# test the detect_ball function is correctly display ball coordinate or not
# When YOLOV11X is trying to recognize the object, it will have xyxy which will return the top left xy coordinate and bottom right xy coordinate
def test_detect_ball(sample_frame):
    # Mock YOLO model to avoid loading the model
    with patch("src.recognition_model.model") as mock_model:
        mock_result = MagicMock()
        mock_box = MagicMock()
        mock_box.cls = [32]
        mock_box.conf = [0.9] # my threshold for this model is 0.25 (because balls are blocked by the hand so I set it pretty low)
        mock_box.xyxy = [[100, 100, 150, 150]] # top left corner and bottom right corner of basketball
        mock_result.boxes = [mock_box]
        mock_model.return_value = [mock_result]
        detected_balls = detect_ball(sample_frame)
        assert detected_balls is not None, "Ball detection should return valid results"
        assert isinstance(detected_balls, list), "Output should be a list"
        assert len(detected_balls) == 2, "Detected ball should have [x, y] coordinates"
        assert all(isinstance(coord, int) for coord in detected_balls), "Checking integer coordinates"


# test landmark function is correctly returning expected data
def test_get_landmark_xy():
    class MockLandmark:
        def __init__(self, x, y, visibility):
            self.x = x
            self.y = y
            self.visibility = visibility

    # input landmark with visibility data
    mock_landmarks = [MockLandmark(0.5, 0.5, 1.0), MockLandmark(0.2, 0.8, 0.2)]
    image_width, image_height = 640, 480 # just some random value for now, because this part involves scaling depending on the resolution of video
    visible_landmark = get_landmark_xy(mock_landmarks, 0, image_width, image_height)
    hidden_landmark = get_landmark_xy(mock_landmarks, 1, image_width, image_height)
    assert visible_landmark != "NONE", "Visible landmark should return coordinates"
    assert isinstance(visible_landmark, list) and len(visible_landmark) == 2, "Returned value should be a list of [x_coordinate, y_coordinate]"
    assert hidden_landmark == "NONE", "Non-visible landmark should return string 'NONE'"


# Test on analyze the mock video
def test_analyze_video(mock_video):
    with patch("cv2.VideoCapture", return_value=mock_video):
        output_data = analyze_video("mock_video.mp4")
        assert isinstance(output_data, list), "Output should be a list"
        if len(output_data) > 0: # only when it gets the data
            assert "left_shoulder" in output_data[0], "Frame data should contain left_shoulder"
            assert "ball" in output_data[0], "Frame data should contain ball"

if __name__ == "__main__":
    pytest.main()
