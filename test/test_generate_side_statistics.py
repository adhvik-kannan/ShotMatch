import math
import numpy as np
import pytest
from scipy.stats import beta

# Import functions from your side statistics module.
from src.generate_side_statistics import calculate_angle, compare_side_ra, compare_side_la

@pytest.fixture
def dummy_side_data():
    """
    Provides dummy side-view data.
    For testing, we assume each key holds a list of coordinates (one per frame).
    Here, we simulate 2 frames.
    """
    return {
        "left_shoulder": [[256, 666], [260, 680]],
        "right_shoulder": [[186, 675], [190, 685]],
        "left_elbow": [[294, 669], [300, 690]],
        "right_elbow": [[201, 666], [205, 670]],
        "left_wrist": [[277, 731], [280, 740]],
        "right_wrist": [[214, 732], [220, 738]],
        "left_pinky": [[280, 770], [285, 775]],
        "left_thumb": [[265, 760], [270, 765]],
        "right_pinky": [[220, 750], [225, 755]],
        "ball": [None, None],
        "Side": ["SIDE", "SIDE"],
        "frame": [21, 22]
    }

@pytest.fixture
def dummy_side_params():
    """
    Dummy Beta distribution parameters for the side view metrics.
    """
    # For right arm (RA) parameters:
    sew_ra_params = {"mean": 80.0, "std": 15.0, "alpha": 4.0, "beta": 5.0}
    ewp_ra_params = {"mean": 168.0, "std": 8.0, "alpha": 10.0, "beta": 2.0}
    # For left arm (LA) parameters:
    sew_la_params = {"mean": 60.0, "std": 20.0, "alpha": 3.0, "beta": 4.0}
    ewa_la_params = {"mean": 170.0, "std": 10.0, "alpha": 12.0, "beta": 3.0}
    return sew_ra_params, ewp_ra_params, sew_la_params, ewa_la_params

def test_compare_side_ra(dummy_side_data, dummy_side_params):
    sew_ra_params, ewp_ra_params, _, _ = dummy_side_params
    scores = compare_side_ra(dummy_side_data, sew_ra_params, ewp_ra_params)
    assert isinstance(scores, dict)
    assert "sew_ra_score" in scores and "ewp_ra_score" in scores
    for score in scores.values():
        assert 0 <= score <= 100, f"Score out of range: {score}"

def test_compare_side_la(dummy_side_data, dummy_side_params):
    _, _, sew_la_params, ewa_la_params = dummy_side_params
    scores = compare_side_la(dummy_side_data, sew_la_params, ewa_la_params)
    assert isinstance(scores, dict)
    assert "sew_la_score" in scores and "ewa_la_score" in scores
    for score in scores.values():
        assert 0 <= score <= 100, f"Score out of range: {score}"
