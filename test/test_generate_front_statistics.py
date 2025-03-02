import math
import numpy as np
import pytest
from scipy.stats import beta

# Import functions from your module.
# Adjust the import if your file is in a different location.
from src.generate_front_statistics import calculate_angle, get_elbow, compare_front

@pytest.fixture
def dummy_front_data():
    """
    Provides dummy front-view data.
    For this example, each key is assumed to contain a single coordinate (list of two numbers).
    """
    return {
        "hip": [90, 180],
        "shoulder": [100, 200],
        "left_elbow": [110, 250],
        "right_elbow": [115, 255],
        "wrist": [120, 300],
        "pinky": [125, 305]
    }

@pytest.fixture
def dummy_front_params():
    """
    Dummy Beta distribution parameters for each front metric.
    These parameters are chosen arbitrarily.
    """
    hse_params = {"mean": 30.0, "std": 4.0, "alpha": 1.5, "beta": 2.0}
    sew_params = {"mean": 45.0, "std": 5.0, "alpha": 2.0, "beta": 3.0}
    ewp_params = {"mean": 60.0, "std": 6.0, "alpha": 2.5, "beta": 3.5}
    # For the elbow comparison, since values are ratios in [0,1]:
    ec_params = {"mean": 0.1, "std": 0.05, "alpha": 2.0, "beta": 8.0}
    return hse_params, sew_params, ewp_params, ec_params

def test_get_elbow(dummy_front_data):
    """
    Test that the get_elbow function returns a value in [0,1].
    """
    # For our dummy data, get_elbow expects left and right elbow data;
    # For testing, we adjust the dummy data so that left_elbow and right_elbow are lists.
    test_data = dummy_front_data.copy()
    # Here we assume that for get_elbow the data is a single coordinate,
    # so we wrap it in a list.
    test_data["left_elbow"] = [test_data["left_elbow"]]
    test_data["right_elbow"] = [test_data["right_elbow"]]
    # Also, wrist should be wrapped as a list.
    test_data["wrist"] = [test_data["wrist"]]
    elbow_ratio = get_elbow(test_data)
    assert elbow_ratio is not None, "Elbow ratio should not be None"
    assert 0 <= elbow_ratio <= 1, f"Elbow ratio {elbow_ratio} not in [0,1]"

def test_compare_front(dummy_front_data, dummy_front_params):
    """
    Test that compare_front returns all expected keys and the scores are within 0-100.
    """
    hse_params, sew_params, ewp_params, ec_params = dummy_front_params
    scores = compare_front(dummy_front_data, hse_params, sew_params, ewp_params, ec_params)
    expected_keys = ["hse_score", "sew_score", "ewp_score", "ec_score"]
    for key in expected_keys:
        assert key in scores, f"Missing {key} in output"
        assert 0 <= scores[key] <= 100, f"{key} out of range: {scores[key]}"
