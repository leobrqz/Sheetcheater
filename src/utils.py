from datetime import datetime
import logging
from logger import setup_logging

# Set up logging
setup_logging()
logger = logging.getLogger(__name__)

def validate_date_format(date_str: str) -> str:
    """
    Validates and normalizes date string to ISO format.
    
    Args:
        date_str: Date string in YYYY-MM-DD format
        
    Returns:
        Normalized ISO format date string
        
    Raises:
        ValueError: If date format is invalid
    """
    try:
        # Parse the date string
        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        # Return ISO format string
        return date_obj.isoformat()
    except ValueError as e:
        logger.error(f"Invalid date format: {date_str}")
        raise ValueError(f"Invalid date format. Use YYYY-MM-DD. Error: {str(e)}")

def format_date_for_display(iso_date: str) -> str:
    """
    Formats ISO date string for display.
    
    Args:
        iso_date: ISO format date string
        
    Returns:
        Formatted date string (YYYY-MM-DD)
    """
    try:
        date_obj = datetime.fromisoformat(iso_date)
        return date_obj.strftime("%Y-%m-%d")
    except ValueError as e:
        logger.error(f"Invalid ISO date format: {iso_date}")
        return iso_date  # Return original if parsing fails 