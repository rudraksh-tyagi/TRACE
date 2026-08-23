import sys
import os
import math

# Add src/ folder to Python system path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from drift import compass_to_math_radians, update_position

def test_compass_to_math_radians():
    # North (0 deg compass) should equal 90 deg math (pi / 2 rad)
    assert math.isclose(compass_to_math_radians(0.0), math.pi / 2, abs_tol=1e-5)
    # East (90 deg compass) should equal 0 deg math (0 rad)
    assert math.isclose(compass_to_math_radians(90.0), 0.0, abs_tol=1e-5)

def test_update_position():
    lat, lon = 20.0, 70.0
    v_x, v_y = 0.0, 0.0  # Zero velocity means zero movement
    dt = 3600
    r_earth = 6371000.0
    
    # Passing all 6 expected arguments
    new_lat, new_lon = update_position(lat, lon, v_x, v_y, dt, r_earth)
    assert new_lat == 20.0
    assert new_lon == 70.0

if __name__ == "__main__":
    test_compass_to_math_radians()
    test_update_position()
    print("All unit tests passed successfully!")