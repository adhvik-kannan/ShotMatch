import pytest
import math
from scipy.stats import beta
from generate_side_statistics import calculate_angle, compare_side_ra, compare_side_la

@pytest.fixture
def dummy_data():
    """ Returns dummy joint data for a side view test """
    return {
        "left_shoulder": [256, 666],
        "right_shoulder": [186, 675],
        "left_elbow": [294, 669],
        "right_elbow": [201, 666],
        "left_wrist": [277, 731],
        "right_wrist": [214, 732],
        "left_pinky": [280, 770],
        "right_pinky": [220, 750],
        "left_thumb": [285, 760],
        "ball": None,
        "Side": "SIDE",
        "frame": 21
    }

@pytest.fixture
def dummy_params():
    """ Returns dummy Beta distribution parameters """
    return {"mean": 45.0, "std": 5.0, "alpha": 2.0, "beta": 2.5}

def test_calculate_angle():
    """ Tests the angle calculation function """
    a = [0, 0]
    vertex = [0, 1]
    b = [1, 1]
    
    angle = calculate_angle(vertex, a, b)
    expected_angle = 45.0  # Expected angle for these coordinates
    
    assert math.isclose(angle, expected_angle, abs_tol=1.0), f"Expected {expected_angle}, got {angle}"

def test_compare_side_ra(dummy_data, dummy_params):
    """ Tests right-arm comparison function """
    scores = compare_side_ra(dummy_data, dummy_params, dummy_params)
    
    assert isinstance(scores, dict)
    assert "sew_ra_score" in scores and "ewp_ra_score" in scores
    assert 0 <= scores["sew_ra_score"] <= 100
    assert 0 <= scores["ewp_ra_score"] <= 100

def test_compare_side_la(dummy_data, dummy_params):
    """ Tests left-arm comparison function """
    scores = compare_side_la(dummy_data, dummy_params, dummy_params)
    
    assert isinstance(scores, dict)
    assert "sew_la_score" in scores and "ewa_la_score" in scores
    assert 0 <= scores["sew_la_score"] <= 100
    assert 0 <= scores["ewa_la_score"] <= 100
