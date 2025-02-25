import pytest
from src.generate_side_statistics import compare_side

def test_compare_arm_with_own_dummy_data():
    # Dummy distribution parameters for the left arm.
    left_sew_params = {"mean": 45.0, "std": 5.0, "alpha": 2.0, "beta": 3.0}
    left_ewa_params = {"mean": 50.0, "std": 6.0, "alpha": 2.5, "beta": 3.5}
    
    # Dummy distribution parameters for the right arm.
    right_sew_params = {"mean": 40.0, "std": 4.0, "alpha": 1.8, "beta": 2.8}
    right_ewa_params = {"mean": 55.0, "std": 7.0, "alpha": 3.0, "beta": 4.0}
    
    # Dummy new shot data for both arms combined in a single dictionary.
    new_arm_data = {
        "left_shoulder": [100, 200],
        "left_elbow": [110, 250],
        "left_wrist": [120, 300],
        "left_pinky": [125, 305],
        "left_index": [123, 307],
        "right_shoulder": [200, 200],
        "right_elbow": [210, 250],
        "right_wrist": [220, 300],
        "right_pinky": [225, 305],
        "right_index": [223, 307]
    }
    
    # Compute similarity scores for left arm.
    left_result = compare_side(new_arm_data, "left", left_sew_params, left_ewa_params)
    # Compute similarity scores for right arm.
    right_result = compare_side(new_arm_data, "right", right_sew_params, right_ewa_params)
    
    # Verify that each result dictionary contains the expected keys.
    for result, arm in [(left_result, "left"), (right_result, "right")]:
        assert "sew_score" in result, f"Missing 'sew_score' in {arm} arm result."
        assert "ewa_score" in result, f"Missing 'ewa_score' in {arm} arm result."
        # Check that the scores are within the valid range (0-100).
        assert 0 <= result["sew_score"] <= 100, f"{arm} arm sew_score out of bounds: {result['sew_score']}"
        assert 0 <= result["ewa_score"] <= 100, f"{arm} arm ewa_score out of bounds: {result['ewa_score']}"
