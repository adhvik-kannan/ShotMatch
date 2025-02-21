import json
import os
import pytest
from generate_bell_curves import main

@pytest.fixture
def dummy_arm_data():
    # Dummy data for left arm with 3 frames (use more frames in a real scenario)
    left_data = {
        "shoulder": [[100, 200], [101, 201], [102, 202]],
        "elbow": [[110, 250], [111, 251], [112, 252]],
        "wrist": [[120, 300], [121, 301], [122, 302]],
        "pinky": [[125, 305], [126, 306], [127, 307]],
        "index": [[123, 307], [124, 308], [125, 309]]
    }
    # Dummy data for right arm with 3 frames
    right_data = {
        "shoulder": [[200, 200], [201, 201], [202, 202]],
        "elbow": [[210, 250], [211, 251], [212, 252]],
        "wrist": [[220, 300], [221, 301], [222, 302]],
        "pinky": [[225, 305], [226, 306], [227, 307]],
        "index": [[223, 307], [224, 308], [225, 309]]
    }
    return left_data, right_data

def test_generate_bell_curves(tmp_path, dummy_arm_data, monkeypatch):
    # Change working directory to the temporary directory.
    monkeypatch.chdir(tmp_path)
    
    left_data, right_data = dummy_arm_data
    
    # Write the dummy data to JSON files in the temporary directory.
    left_file = tmp_path / "left_arm_data.json"
    right_file = tmp_path / "right_arm_data.json"
    
    left_file.write_text(json.dumps(left_data))
    right_file.write_text(json.dumps(right_data))
    
    # Run the main() function from the generate_bell_curve module.
    main()
    
    # Define the expected output file names.
    left_distribution_file = tmp_path / "left_arm_angle_distribution.json"
    right_distribution_file = tmp_path / "right_arm_angle_distribution.json"
    left_plot_file = tmp_path / "left_arm_bell_curve.png"
    right_plot_file = tmp_path / "right_arm_bell_curve.png"
    
    # Check that the output files exist.
    assert left_distribution_file.exists(), "Left arm distribution JSON not found."
    assert right_distribution_file.exists(), "Right arm distribution JSON not found."
    assert left_plot_file.exists(), "Left arm plot image not found."
    assert right_plot_file.exists(), "Right arm plot image not found."
    
    # Load the distribution parameters and verify they have the expected structure.
    with open(left_distribution_file, "r") as f:
        left_distribution = json.load(f)
    with open(right_distribution_file, "r") as f:
        right_distribution = json.load(f)
    
    for dist in (left_distribution, right_distribution):
        assert "shoulder_elbow_wrist" in dist, "Missing key 'shoulder_elbow_wrist'"
        assert "elbow_wrist_avg_pinky_index" in dist, "Missing key 'elbow_wrist_avg_pinky_index'"
        for key in ["shoulder_elbow_wrist", "elbow_wrist_avg_pinky_index"]:
            assert "mean" in dist[key], f"Missing 'mean' in {key}"
            assert "std" in dist[key], f"Missing 'std' in {key}"
            assert "alpha" in dist[key], f"Missing 'alpha' in {key}"
            assert "beta" in dist[key], f"Missing 'beta' in {key}"
