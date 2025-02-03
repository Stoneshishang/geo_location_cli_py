# test_geoloc_util.py
import pytest
from geoloc_util import get_location_by_city_state, get_location_by_zipcode, process_location

def test_valid_city_state():
    """Test a valid city,state combination."""
    result = get_location_by_city_state("Madison, WI")
    assert result['name'] == "Madison"
    assert result['state'] == "Wisconsin"
    assert result['country'] == "US"
    assert isinstance(result['lat'], float)
    assert isinstance(result['lon'], float)

def test_valid_zipcode():
    """Test a valid zipcode."""
    result = get_location_by_zipcode("10001")
    assert result['name'] == "New York"
    assert result['country'] == "US"
    assert isinstance(result['lat'], float)
    assert isinstance(result['lon'], float)

def test_invalid_city_state():
    """Test an invalid city,state combination."""
    with pytest.raises(ValueError):
        get_location_by_city_state("NonExistent, XX")

def test_invalid_zipcode():
    """Test an invalid zipcode."""
    with pytest.raises(ValueError):
        get_location_by_zipcode("00000")

def test_process_location_city_state():
    """Test processing a city,state input."""
    result = process_location("Chicago, IL")
    assert result is not None
    assert result['name'] == "Chicago"

def test_process_location_zipcode():
    """Test processing a zipcode input."""
    result = process_location("10001")
    assert result is not None
    assert result['name'] == "New York"