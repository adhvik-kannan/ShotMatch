import pytest
import numpy as np
from generate_side_bell_curves import calculate_angle, generate_side_la_parameters, generate_side_ra_parameters, get_parameters

@pytest.fixture
def dummy_data():
    """ Returns dummy joint data for side view angle generation """
    return {
        "left_shoulder": [[256, 666], [260, 680]],
        "right_shoulder": [[186, 675], [192, 690]],
        "left_elbow": [[294, 669], [300, 690]],
        "right_elbow": [[201, 666], [210, 685]],
        "left_wrist": [[277, 731], [285, 750]],
        "right_wrist": [[214, 732], [220, 745]],
        "left_pinky": [[280, 770], [290, 780]],
        "right_pinky": [[220, 750], [230, 765]],
        "left_thumb": [[285, 760], [295, 775]],
        "ball": [None, None],
        "Side": ["SIDE", "SIDE"],
        "frame": [21, 25]
    }

def test_calculate_angle():
    """ Tests basic angle calculation """
    a = [0, 0]
    vertex = [0, 1]
    b = [1, 1]
    
    angle = calculate_angle(vertex, a, b)
    expected_angle = 45.0
    
    assert np.isclose(angle, expected_angle, atol=1.0)

def test_generate_side_la_parameters(dummy_data):
    """ Tests left-arm parameter generation """
    sew_la, ewa_la = generate_side_la_parameters(dummy_data)
    
    assert isinstance(sew_la, dict) and isinstance(ewa_la, dict)
    assert "mean" in sew_la and "std" in sew_la
    assert "alpha" in sew_la and "beta" in sew_la
    assert "mean" in ewa_la and "std" in ewa_la
    assert "alpha" in ewa_la and "beta" in ewa_la

def test_generate_side_ra_parameters(dummy_data):
    """ Tests right-arm parameter generation """
    sew_ra, ewp_ra = generate_side_ra_parameters(dummy_data)
    
    assert isinstance(sew_ra, dict) and isinstance(ewp_ra, dict)
    assert "mean" in sew_ra and "std" in sew_ra
    assert "alpha" in sew_ra and "beta" in sew_ra
    assert "mean" in ewp_ra and "std" in ewp_ra
    assert "alpha" in ewp_ra and "beta" in ewp_ra

def test_get_parameters():
    """ Tests statistical parameter generation """
    test_angles = [30, 45, 60, 75]
    params = get_parameters(test_angles)
    
    assert isinstance(params, dict)
    assert "mean" in params and "std" in params
    assert "alpha" in params and "beta" in params
