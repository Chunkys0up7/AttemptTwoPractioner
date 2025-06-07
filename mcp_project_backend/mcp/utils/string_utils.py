def camel_to_snake(camel_str: str) -> str:
    """
    Convert a camelCase string to snake_case.
    
    Args:
        camel_str: The camelCase string to convert
        
    Returns:
        The converted snake_case string
    """
    return ''.join(['_' + i.lower() if i.isupper() else i for i in camel_str]).lstrip('_')

def snake_to_camel(snake_str: str) -> str:
    """
    Convert a snake_case string to camelCase.
    
    Args:
        snake_str: The snake_case string to convert
        
    Returns:
        The converted camelCase string
    """
    return ''.join(word.capitalize() or '_' for word in snake_str.split('_'))

def remove_special_chars(input_str: str, allowed_chars: str = "") -> str:
    """
    Remove special characters from a string, optionally keeping allowed characters.
    
    Args:
        input_str: The string to clean
        allowed_chars: Special characters to keep
        
    Returns:
        The cleaned string
    """
    return ''.join(c for c in input_str if c.isalnum() or c in allowed_chars)

def truncate_string(input_str: str, max_length: int, ellipsis: str = "...") -> str:
    """
    Truncate a string to a maximum length, adding an ellipsis if truncated.
    
    Args:
        input_str: The string to truncate
        max_length: Maximum length of the string
        ellipsis: String to add when truncating
        
    Returns:
        The truncated string
    """
    if len(input_str) <= max_length:
        return input_str
    return input_str[:max_length - len(ellipsis)] + ellipsis

def is_valid_uuid(uuid_str: str) -> bool:
    """
    Validate if a string is a valid UUID.
    
    Args:
        uuid_str: The string to validate
        
    Returns:
        True if the string is a valid UUID, False otherwise
    """
    try:
        uuid.UUID(uuid_str)
        return True
    except ValueError:
        return False