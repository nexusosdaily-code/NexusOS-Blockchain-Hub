"""
NexusOS Input Validators
========================

Centralized validation functions for user input fields.
Ensures consistent validation across all modules.
"""

import re
from typing import Tuple, Optional


def validate_nxs_address(address: str) -> Tuple[bool, str]:
    """
    Validate NexusOS wallet address format.
    
    Valid formats:
    - NXS followed by alphanumeric characters (40+ chars total)
    - Special system addresses: VALIDATOR_POOL, TREASURY, ECOSYSTEM_FUND
    
    Args:
        address: The address string to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not address:
        return False, "Address is required"
    
    address = address.strip()
    
    system_addresses = {'VALIDATOR_POOL', 'TREASURY', 'ECOSYSTEM_FUND'}
    if address in system_addresses:
        return True, ""
    
    if not address.startswith('NXS'):
        return False, "Address must start with 'NXS'"
    
    if len(address) < 40:
        return False, f"Address too short (minimum 40 characters, got {len(address)})"
    
    if len(address) > 64:
        return False, f"Address too long (maximum 64 characters, got {len(address)})"
    
    address_body = address[3:]
    if not re.match(r'^[A-Za-z0-9]+$', address_body):
        return False, "Address contains invalid characters (only alphanumeric allowed after NXS)"
    
    return True, ""


def validate_phone_e164(phone: str) -> Tuple[bool, str]:
    """
    Validate phone number in E.164 international format.
    
    E.164 format:
    - Starts with + followed by country code
    - Contains only digits after +
    - Total length 8-15 digits (excluding +)
    
    Examples:
    - +14155551234 (US)
    - +447911123456 (UK)
    - +8613812345678 (China)
    
    Args:
        phone: The phone number string to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not phone:
        return False, "Phone number is required"
    
    phone = phone.strip()
    
    if not phone.startswith('+'):
        return False, "Phone must start with '+' (E.164 format, e.g., +14155551234)"
    
    digits = phone[1:]
    if not digits.isdigit():
        return False, "Phone number must contain only digits after '+'"
    
    if len(digits) < 8:
        return False, f"Phone number too short (minimum 8 digits, got {len(digits)})"
    
    if len(digits) > 15:
        return False, f"Phone number too long (maximum 15 digits, got {len(digits)})"
    
    return True, ""


def normalize_phone_e164(phone: str) -> Optional[str]:
    """
    Normalize a phone number to E.164 format.
    
    Handles common input variations:
    - Removes spaces, dashes, parentheses
    - Adds + if missing
    - Validates and returns normalized format
    
    Args:
        phone: Raw phone input
        
    Returns:
        Normalized E.164 phone number or None if invalid
    """
    if not phone:
        return None
    
    cleaned = re.sub(r'[\s\-\(\)\.]', '', phone.strip())
    
    if not cleaned.startswith('+'):
        if cleaned.startswith('00'):
            cleaned = '+' + cleaned[2:]
        elif len(cleaned) >= 10 and cleaned[0].isdigit():
            cleaned = '+' + cleaned
    
    is_valid, _ = validate_phone_e164(cleaned)
    return cleaned if is_valid else None


def validate_amount(amount: float, min_val: float = 0.0, max_val: float = 1e12) -> Tuple[bool, str]:
    """
    Validate transaction amount.
    
    Args:
        amount: The amount to validate
        min_val: Minimum allowed value (default 0)
        max_val: Maximum allowed value (default 1 trillion)
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if amount <= min_val:
        return False, f"Amount must be greater than {min_val}"
    
    if amount > max_val:
        return False, f"Amount exceeds maximum ({max_val:,.0f})"
    
    return True, ""


def validate_message_content(content: str, max_chars: int = 280) -> Tuple[bool, str]:
    """
    Validate message content.
    
    Args:
        content: The message content
        max_chars: Maximum character limit
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not content or not content.strip():
        return False, "Message content is required"
    
    if len(content) > max_chars:
        return False, f"Message too long (max {max_chars} characters)"
    
    return True, ""
