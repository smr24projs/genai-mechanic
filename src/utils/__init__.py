"""
Utils Package - Utility modules for diagnostic platform
"""

from src.utils.config_manager import CONFIG, AppConfig
from src.utils.error_handlers import (
    DiagnosticError,
    VisionExtractionError,
    AgentExecutionError,
    DataValidationError,
    APIError,
    DatabaseError,
    retry_with_backoff,
    handle_streamlit_error,
)
from src.utils.logger_setup import setup_logging, get_logger, perf_logger
from src.utils.validators import (
    validate_sensor_value,
    validate_all_sensors,
    validate_dtc_code,
    validate_vehicle_model,
    sanitize_text_input,
    extract_json_from_response,
    InputValidator,
)
from src.utils.diagnostic_history import diagnostic_history, DiagnosticHistory

__all__ = [
    'CONFIG',
    'AppConfig',
    'DiagnosticError',
    'VisionExtractionError',
    'AgentExecutionError',
    'DataValidationError',
    'APIError',
    'DatabaseError',
    'retry_with_backoff',
    'handle_streamlit_error',
    'setup_logging',
    'get_logger',
    'perf_logger',
    'validate_sensor_value',
    'validate_all_sensors',
    'validate_dtc_code',
    'validate_vehicle_model',
    'sanitize_text_input',
    'extract_json_from_response',
    'InputValidator',
    'diagnostic_history',
    'DiagnosticHistory',
]
