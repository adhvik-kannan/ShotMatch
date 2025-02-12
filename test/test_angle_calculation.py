import pytest
import math
from OCR_mediapipe import calculate_angle 

def test_calculate_angle():
    # 90度角
    assert math.isclose(calculate_angle((0, 1), (0, 0), (1, 0)), 90.0, rel_tol=1e-5)
    
    # 180度角
    assert math.isclose(calculate_angle((-1, 0), (0, 0), (1, 0)), 180.0, rel_tol=1e-5)
    
    # 45度角
    assert math.isclose(calculate_angle((1, 1), (0, 0), (1, 0)), 45.0, rel_tol=1e-5)
    
    # 0度角
    assert math.isclose(calculate_angle((1, 0), (0, 0), (-1, 0)), 180.0, rel_tol=1e-5)
    
    # 直线角度为0
    assert math.isclose(calculate_angle((0, 0), (0, 0), (1, 1)), 0.0, rel_tol=1e-5)
    
    # 点重叠的情况
    assert math.isclose(calculate_angle((0, 0), (0, 0), (0, 0)), 0.0, rel_tol=1e-5)
    
if __name__ == "__main__":
    pytest.main()