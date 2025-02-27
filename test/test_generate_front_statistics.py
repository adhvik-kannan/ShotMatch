import pytest
import math
import numpy as np
from scipy.stats import beta
from generate_front_statistics import calculate_angle, get_elbow, compare_front

@pytest.fixture
def dummy_data():
    return {
        "left_shoulder": [256, 666],
        "right_shoulder": [186, 675],
        "left_elbow": [294, 669],
        "right_elbow": [201, 666],
        "left_wrist": [277, 731],
        "right_wrist": [214, 732],
        "left_hip": [242, 513],
        "right_hip": [195, 516],
        "right_pinky": [220, 750],
        "right_thumb": [230, 745],
        "left_pinky": [280, 770],
        "ball": None,
        "Side": "FRONT",
        "frame": 21
    }

@pytest.fixture
def dummy_params():
    """ Return dummy Beta distribution parameters for testing. """
    return {
        "alpha": 2.0,
        "beta": 2.5,
        "mean": 45.0,
        "std": 5.0
    }

def test_calculate_angle():
    """ Test angle calculations using three fixed coordinate points. """
    a = [0, 0]
    vertex = [0, 1]
    b = [1, 1]
    
    angle = calculate_angle(vertex, a, b)
    expected_angle = 45.0  # Expected angle for these coordinates
    
    assert math.isclose(angle, expected_angle, abs_tol=1.0), f"Expected {expected_angle}, got {angle}"

def test_get_elbow(dummy_data):
    """ Test elbow height calculation and normalization. """
    elbow_ratio = get_elbow(dummy_data)
    
    assert elbow_ratio is not None, "Elbow ratio should not be None"
    assert 0 <= elbow_ratio <= 1, f"Elbow ratio out of expected range: {elbow_ratio}"

def test_compare_front(dummy_data, dummy_params):
    """ Test front view angle scoring using dummy data. """
    scores = compare_front(
        dummy_data, 
        dummy_params, dummy_params,  # hse params
        dummy_params, dummy_params,  # sew params
        dummy_params, dummy_params,  # ewa and ewp params
        dummy_params                 # elbow params
    )
    
    assert isinstance(scores, dict), "Output should be a dictionary"
    
    for key, value in scores.items():
        assert 0 <= value <= 100, f"{key} score out of range: {value}"

