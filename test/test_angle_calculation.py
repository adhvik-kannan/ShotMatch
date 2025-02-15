import pytest
import math
from src.OCR_mediapipe import calculate_angle 

def test_calculate_angle():
    assert math.isclose(calculate_angle((0, 1), (0, 0), (1, 0)), 90.0, rel_tol=1e-5)
    
    assert math.isclose(calculate_angle((-1, 0), (0, 0), (1, 0)), 180.0, rel_tol=1e-5)
    
    assert math.isclose(calculate_angle((1, 1), (0, 0), (1, 0)), 45.0, rel_tol=1e-5)
    
    assert math.isclose(calculate_angle((1, 0), (0, 0), (-1, 0)), 180.0, rel_tol=1e-5)
    
    assert math.isclose(calculate_angle((0, 0), (0, 0), (1, 1)), 0.0, rel_tol=1e-5)
    
    assert math.isclose(calculate_angle((0, 0), (0, 0), (0, 0)), 0.0, rel_tol=1e-5)
    
if __name__ == "__main__":
    pytest.main()