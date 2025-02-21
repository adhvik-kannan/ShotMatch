import json
import numpy as np
import pytest
from pathlib import Path
from generate_side_bell_curves import (
    calculate_angle,
    process_arm_data,
    calculate_distribution_parameters,
    generate_plot,
    main
)

def test_calculate_angle():
    # Test a known angle.
    # For example, for points (0,0), (1,0), (1,1) the angle at (1,0) should be 45 degrees.
    a = [0, 0]
    vertex = [1, 0]
    b = [1, 1]
    angle = calculate_angle(vertex, a, b)
    assert abs(angle) == 90, f"Expected 90, got {angle}"

def test_process_arm_data():
    # Dummy data for 3 frames.
    shoulder = [[100,200], [101,201], [102,202]]
    elbow    = [[110,250], [111,251], [112,252]]
    wrist    = [[120,300], [121,301], [122,302]]
    pinky    = [[125,305], [126,306], [127,307]]
    index    = [[123,307], [124,308], [125,309]]
    
    sew, ewa = process_arm_data(shoulder, elbow, wrist, pinky, index)
    # Check that outputs are numpy arrays with the same number of frames.
    assert isinstance(sew, np.ndarray)
    assert isinstance(ewa, np.ndarray)
    assert sew.shape[0] == 3
    assert ewa.shape[0] == 3

def test_calculate_distribution_parameters():
    # Create a dummy angles array.
    angles = np.array([45, 47, 50])
    params = calculate_distribution_parameters(angles)
    # Check that required keys exist.
    for key in ["mean", "std", "alpha", "beta"]:
        assert key in params, f"Missing key {key} in distribution parameters"

