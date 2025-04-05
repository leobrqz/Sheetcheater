from typing import List, Optional, Tuple, Any
from datetime import datetime
import re
from logger import get_logger

# Get logger instance
logger = get_logger(__name__)

class LogQueryBuilder:
    def __init__(self):
        self.conditions: List[str] = []
        self.parameters: List[Any] = []
    
    def _sanitize_string(self, value: str) -> str:
        """
        Sanitize string input to prevent SQL injection.
        
        Args:
            value: String to sanitize
            
        Returns:
            Sanitized string
        """
        # Remove any SQL injection attempts
        value = re.sub(r'[\'";\\]', '', value)
        return value.strip()
    
    def _validate_date(self, date_str: str) -> bool:
        """
        Validate date string format.
        
        Args:
            date_str: Date string to validate
            
        Returns:
            True if valid, False otherwise
        """
        try:
            datetime.fromisoformat(date_str)
            return True
        except ValueError:
            return False
    
    def _validate_numeric_range(self, min_val: float, max_val: float) -> bool:
        """
        Validate numeric range.
        
        Args:
            min_val: Minimum value
            max_val: Maximum value
            
        Returns:
            True if valid, False otherwise
        """
        return min_val <= max_val
    
    def add_date_range(self, start_date: str, end_date: str) -> 'LogQueryBuilder':
        """
        Adds date range filter to the query.
        
        Args:
            start_date: Start date in ISO format
            end_date: End date in ISO format
            
        Returns:
            self for method chaining
            
        Raises:
            ValueError: If dates are invalid
        """
        if not (self._validate_date(start_date) and self._validate_date(end_date)):
            raise ValueError("Invalid date format. Use ISO format (YYYY-MM-DD)")
            
        self.conditions.append("timestamp BETWEEN ? AND ?")
        self.parameters.extend([start_date, end_date])
        return self
    
    def add_function_filter(self, function_name: str) -> 'LogQueryBuilder':
        """
        Adds function name filter to the query.
        
        Args:
            function_name: Name of the function to filter by
            
        Returns:
            self for method chaining
            
        Raises:
            ValueError: If function name is invalid
        """
        sanitized_name = self._sanitize_string(function_name)
        if not sanitized_name:
            raise ValueError("Invalid function name")
            
        self.conditions.append("function_name = ?")
        self.parameters.append(sanitized_name)
        return self
    
    def add_token_range(self, min_tokens: int, max_tokens: int) -> 'LogQueryBuilder':
        """
        Adds token range filter to the query.
        
        Args:
            min_tokens: Minimum number of tokens
            max_tokens: Maximum number of tokens
            
        Returns:
            self for method chaining
            
        Raises:
            ValueError: If token range is invalid
        """
        if not self._validate_numeric_range(min_tokens, max_tokens):
            raise ValueError("Invalid token range: min must be less than or equal to max")
            
        self.conditions.append("total_tokens BETWEEN ? AND ?")
        self.parameters.extend([min_tokens, max_tokens])
        return self
    
    def add_cost_range(self, min_cost: float, max_cost: float) -> 'LogQueryBuilder':
        """
        Adds cost range filter to the query.
        
        Args:
            min_cost: Minimum cost
            max_cost: Maximum cost
            
        Returns:
            self for method chaining
            
        Raises:
            ValueError: If cost range is invalid
        """
        if not self._validate_numeric_range(min_cost, max_cost):
            raise ValueError("Invalid cost range: min must be less than or equal to max")
            
        self.conditions.append("cost BETWEEN ? AND ?")
        self.parameters.extend([min_cost, max_cost])
        return self
    
    def build(self, limit: Optional[int] = None) -> Tuple[str, List[Any]]:
        """
        Builds the final SQL query.
        
        Args:
            limit: Optional limit for the number of results
            
        Returns:
            Tuple of (SQL query, parameters)
            
        Raises:
            ValueError: If limit is invalid
        """
        if limit is not None and limit < 0:
            raise ValueError("Limit must be a positive number")
            
        query = "SELECT timestamp, function_name, prompt_tokens, completion_tokens, total_tokens, cost, output FROM token_logs"
        
        if self.conditions:
            query += " WHERE " + " AND ".join(self.conditions)
        
        query += " ORDER BY timestamp DESC"
        
        if limit:
            query += " LIMIT ?"
            self.parameters.append(limit)
        
        logger.debug(f"Built query: {query} with parameters: {self.parameters}")
        return query, self.parameters 