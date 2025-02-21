import json
import pytest
from pathlib import Path
from generate_statistics import main  # Adjust the import if your file name is different

@pytest.fixture
def dummy_distribution_data():
    # Dummy distribution parameters for left and right arms.
    # These values are chosen arbitrarily for testing.
    left_distribution = {
        "shoulder_elbow_wrist": {"mean": 45.0, "std": 5.0},
        "elbow_wrist_avg_pinky_index": {"mean": 50.0, "std": 6.0}
    }
    right_distribution = {
        "shoulder_elbow_wrist": {"mean": 40.0, "std": 4.0},
        "elbow_wrist_avg_pinky_index": {"mean": 55.0, "std": 7.0}
    }
    return left_distribution, right_distribution

@pytest.fixture
def dummy_new_shot_data():
    # Dummy new shot data that contains keys for both arms.
    data = {
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
    return data

def test_compare_shot(tmp_path, dummy_distribution_data, dummy_new_shot_data, monkeypatch):
    # Change working directory to the temporary directory.
    monkeypatch.chdir(tmp_path)
    
    # Unpack dummy distribution data.
    left_distribution, right_distribution = dummy_distribution_data

    # Create dummy distribution JSON files.
    left_dist_file = tmp_path / "left_arm_angle_distribution.json"
    right_dist_file = tmp_path / "right_arm_angle_distribution.json"
    left_dist_file.write_text(json.dumps(left_distribution))
    right_dist_file.write_text(json.dumps(right_distribution))
    
    # Create dummy new shot data JSON file.
    new_shot_file = tmp_path / "new_shot_data.json"
    new_shot_file.write_text(json.dumps(dummy_new_shot_data))
    
    # Run the main function from the compare shot script.
    main()
    
    # Check that the output file "shot_similarity_statistics.json" was created.
    output_file = tmp_path / "shot_similarity_statistics.json"
    assert output_file.exists(), "Output JSON file was not created."
    
    # Load the output file and verify its structure.
    with open(output_file, "r") as f:
        output_data = json.load(f)
    
    # Check for left and right arm keys.
    assert "left_arm" in output_data, "Missing 'left_arm' key in output."
    assert "right_arm" in output_data, "Missing 'right_arm' key in output."
    
    # For each arm, check that the expected keys exist and that scores are between 1 and 100.
    for arm in ["left_arm", "right_arm"]:
        arm_data = output_data[arm]
        assert "shoulder_elbow_wrist_score" in arm_data, f"Missing 'shoulder_elbow_wrist_score' for {arm}."
        assert "elbow_wrist_avg_pinky_index_score" in arm_data, f"Missing 'elbow_wrist_avg_pinky_index_score' for {arm}."
        sew_score = arm_data["shoulder_elbow_wrist_score"]
        ewa_score = arm_data["elbow_wrist_avg_pinky_index_score"]
        assert 1 <= sew_score <= 100, f"{arm} sew score out of bounds: {sew_score}"
        assert 1 <= ewa_score <= 100, f"{arm} ewa score out of bounds: {ewa_score}"
