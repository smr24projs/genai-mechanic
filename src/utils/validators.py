"""
Data Validation Module
Input validation and data sanitation utilities
"""

import re
from typing import Dict, Any, Tuple, Optional
from src.utils.error_handlers import DataValidationError


# ==========================================
# SENSOR DATA RANGES
# ==========================================
SENSOR_RANGES = {
    'rpm': (0, 8000),           # RPM range
    'speed': (0, 300),          # Speed in km/h
    'load': (0, 100),           # Engine load percentage
    'temp': (-40, 130),         # Temperature in Celsius
}


def validate_sensor_value(sensor_name: str, value: Any) -> int:
    """
    Validate and convert sensor value to integer
    
    Args:
        sensor_name: Name of the sensor (e.g., 'rpm', 'speed')
        value: The value to validate
    
    Returns:
        Validated integer value
    
    Raises:
        DataValidationError: If value is invalid
    """
    if sensor_name not in SENSOR_RANGES:
        raise DataValidationError(f"Unknown sensor: {sensor_name}")
    
    min_val, max_val = SENSOR_RANGES[sensor_name]
    
    try:
        # Extract integer from value
        if value is None or value == "":
            int_value = 0
        else:
            # Try to find first integer in the string
            nums = re.findall(r'-?\d+', str(value))
            int_value = int(nums[0]) if nums else 0
        
        # Validate range
        if not (min_val <= int_value <= max_val):
            raise DataValidationError(
                f"{sensor_name} value {int_value} out of valid range [{min_val}, {max_val}]"
            )
        return int_value
    
    except (ValueError, TypeError) as e:
        raise DataValidationError(f"Failed to parse {sensor_name} value: {str(e)}")


def validate_all_sensors(sensor_data: Dict[str, Any]) -> Dict[str, int]:
    """
    Validate all sensor readings
    
    Args:
        sensor_data: Dictionary of sensor readings
    
    Returns:
        Dictionary of validated sensor values
    
    Raises:
        DataValidationError: If any sensor value is invalid
    """
    validated = {}
    for sensor_name in ['rpm', 'speed', 'load', 'temp']:
        validated[sensor_name] = validate_sensor_value(
            sensor_name,
            sensor_data.get(sensor_name, 0)
        )
    return validated


def validate_dtc_code(dtc: str) -> bool:
    """
    Validate Diagnostic Trouble Code format
    Valid formats: P0100, B1234, C5678, U9999, etc.
    """
    pattern = r'^[PBCU]\d{4}$'
    return bool(re.match(pattern, str(dtc).upper()))


def validate_vehicle_model(model: str) -> bool:
    """
    Basic validation for vehicle model string
    """
    if not model or not isinstance(model, str):
        return False
    return len(model.strip()) > 0


def sanitize_text_input(text: str, max_length: int = 1000) -> str:
    """
    Sanitize user text input
    
    Args:
        text: Input text
        max_length: Maximum allowed length
    
    Returns:
        Sanitized text
    
    Raises:
        DataValidationError: If text is invalid
    """
    if not isinstance(text, str):
        raise DataValidationError("Input must be a string")
    
    # Strip whitespace
    text = text.strip()
    
    # Check length
    if len(text) > max_length:
        raise DataValidationError(f"Input exceeds maximum length of {max_length}")
    
    # Remove suspicious characters
    text = re.sub(r'[^\w\s.,!?\'-]', '', text)
    
    return text


def validate_json_response(data: Any, required_keys: list) -> bool:
    """
    Validate JSON response has required keys
    
    Args:
        data: Data to validate (should be dict)
        required_keys: List of required keys
    
    Returns:
        True if valid
    
    Raises:
        DataValidationError: If validation fails
    """
    if not isinstance(data, dict):
        raise DataValidationError("Response must be a dictionary")
    
    missing_keys = [key for key in required_keys if key not in data]
    if missing_keys:
        raise DataValidationError(f"Missing required keys: {missing_keys}")
    
    return True


def extract_json_from_response(response_text: str) -> Dict:
    """
    Extract JSON from LLM response text
    Handles markdown code blocks and extra text
    
    Args:
        response_text: Raw LLM response
    
    Returns:
        Parsed JSON dictionary
    
    Raises:
        DataValidationError: If JSON cannot be extracted
    """
    import json
    import re
    
    # Remove markdown code blocks
    text = response_text.replace('```json', '').replace('```', '')
    
    # Find JSON object
    json_match = re.search(r'\{.*\}', text, re.DOTALL)
    
    if not json_match:
        raise DataValidationError("No JSON object found in response")
    
    try:
        return json.loads(json_match.group())
    except json.JSONDecodeError as e:
        raise DataValidationError(f"Invalid JSON in response: {str(e)}")


# ==========================================
# BATCH VALIDATORS
# ==========================================
class InputValidator:
    """Comprehensive input validation helper"""
    
    @staticmethod
    def validate_diagnostic_input(
        vehicle_model: str,
        dtc_code: Optional[str],
        symptom: str,
        sensor_data: Dict[str, Any]
    ) -> Tuple[bool, str]:
        """
        Validate complete diagnostic input
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            # Validate vehicle model
            if not validate_vehicle_model(vehicle_model):
                return False, "Vehicle model is required"
            
            # Validate DTC if provided
            if dtc_code and not validate_dtc_code(dtc_code):
                return False, f"Invalid DTC code format: {dtc_code}"
            
            # Validate symptom
            if symptom:
                sanitize_text_input(symptom)
            
            # Validate sensor data
            validate_all_sensors(sensor_data)
            
            return True, "All inputs valid"
        
        except DataValidationError as e:
            return False, str(e)
