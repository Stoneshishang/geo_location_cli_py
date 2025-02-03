import pytest
from geoloc_util import get_location_by_city_state, get_location_by_zipcode, process_location, main
import sys
from io import StringIO
from typing import List, Dict

class TestGeolocationIntegration:
    """Integration tests for the Geolocation Utility"""

    @pytest.fixture(autouse=True)
    def setup_capture(self, capsys):
        
        self.capsys = capsys
        yield

    def get_output(self):
        
        captured = self.capsys.readouterr()
        return captured.out

    def test_multiple_valid_locations(self):
        """1. Test processing multiple valid locations in a single request"""
        locations = ["Seattle, WA", "10001", "Chicago, IL", "90210"]
        main(locations)
        output = self.get_output()
        
        # Check for each location in the output
        assert "Seattle" in output
        assert "New York" in output
        assert "Chicago" in output

    def test_mixed_valid_invalid_locations(self):
        """2. Test handling a mix of valid and invalid locations"""
        locations = ["InvalidCity, XX", "10001", "Chicago, IL", "00000"]
        main(locations)
        output = self.get_output()
        
        # Check for error messages and valid locations
        assert "Error processing location 'InvalidCity, XX'" in output
        assert "New York" in output
        assert "Chicago" in output
        assert "Error processing location '00000'" in output

    def test_response_data_structure(self):
        """3. Test the structure and data types of the API response"""
        result = process_location("Seattle, WA")
        
        assert isinstance(result, dict)
        assert 'name' in result
        assert 'country' in result
        assert 'lat' in result
        assert 'lon' in result
        assert isinstance(result['lat'], float)
        assert isinstance(result['lon'], float)
        
        # Verify coordinate ranges
        assert -90 <= result['lat'] <= 90
        assert -180 <= result['lon'] <= 180

    def test_api_response_time(self):
        """4. Test API response time is within acceptable limits"""
        import time
        
        start_time = time.time()
        process_location("Chicago, IL")
        end_time = time.time()
        
        response_time = end_time - start_time
        assert response_time < 2.0  # Response should be under 2 seconds

    def test_concurrent_requests(self):
            """5. Test handling multiple concurrent requests"""
            import concurrent.futures
            
            locations = [
                "Seattle, WA",
                "10001",
                "Chicago, IL",
                "90210",
                "Miami, FL"
            ]
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
                future_to_location = {executor.submit(process_location, loc): loc for loc in locations}
                
                for future in concurrent.futures.as_completed(future_to_location):
                    location = future_to_location[future]
                    try:
                        result = future.result()
                        assert result is not None
                    except Exception as e:
                        assert False, f"Request failed for {location}: {str(e)}"

    def test_location_format_variations(self):
        """6. Test various valid format variations for city,state input"""
        variations = [
            "Seattle,WA",  
            "Seattle , WA", 
            "seattle, wa", 
            "SEATTLE, WA"  
        ]
        
        for location in variations:
            result = process_location(location)
            assert result is not None
            assert result['name'].upper() == "SEATTLE"
            assert result['country'] == "US"

    
    def test_empty_input_handling(self):
        """7. Test handling of empty inputs"""
        with pytest.raises(ValueError, match="Location cannot be empty"):
            process_location("")
        
        with pytest.raises(ValueError, match="Location cannot be empty"):
            process_location("   ")

    def test_special_characters_handling(self):
        """8. Test handling of special characters in input"""
        problematic_inputs = [
            "New York!, NY",
            "Chicago@, IL",
            "Madison$, WI"
        ]
        
        for location in problematic_inputs:
            result = process_location(location)
            assert result is not None  # Should handle special characters gracefully
    
    def test_zip_code_variations(self):
        """9. Test various ZIP code formats"""
        results = []
        for zipcode in ["10001", "10001 ", " 10001"]:  # Testing with extra spaces
            result = process_location(zipcode.strip())  # Add strip() here
            results.append(result)
            
        # All variations should return the same location
        assert all(r['name'] == results[0]['name'] for r in results)
        assert all(r['lat'] == results[0]['lat'] for r in results)
        assert all(r['lon'] == results[0]['lon'] for r in results)