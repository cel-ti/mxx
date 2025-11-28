"""Pattern matching utilities for config keys with wildcard support."""

import fnmatch
from typing import List


def matches_pattern(key: str, pattern: str) -> bool:
    """Check if a key matches a pattern with wildcard support.
    
    Supports wildcards:
    - * matches any sequence of characters
    - ? matches any single character
    - [seq] matches any character in seq
    - [!seq] matches any character not in seq
    
    Args:
        key: The key to test
        pattern: Pattern with wildcards (e.g., "wxx*.set*")
        
    Returns:
        True if key matches pattern
        
    Examples:
        >>> matches_pattern("wxx_auto.settings", "wxx*.set*")
        True
        >>> matches_pattern("other.key", "wxx*.set*")
        False
    """
    return fnmatch.fnmatch(key, pattern)


def matches_any_pattern(key: str, patterns: List[str]) -> bool:
    """Check if a key matches any of the given patterns.
    
    Args:
        key: The key to test
        patterns: List of patterns with wildcards
        
    Returns:
        True if key matches any pattern
        
    Examples:
        >>> matches_any_pattern("wxx.settings", ["wxx*", "config*"])
        True
        >>> matches_any_pattern("other", ["wxx*", "config*"])
        False
    """
    return any(matches_pattern(key, pattern) for pattern in patterns)


def filter_keys_by_pattern(keys: List[str], pattern: str, exclude: bool = False) -> List[str]:
    """Filter a list of keys by a pattern.
    
    Args:
        keys: List of keys to filter
        pattern: Pattern with wildcards
        exclude: If True, exclude matching keys; if False, include only matching keys
        
    Returns:
        Filtered list of keys
        
    Examples:
        >>> filter_keys_by_pattern(["wxx.a", "wxx.b", "other"], "wxx*")
        ['wxx.a', 'wxx.b']
        >>> filter_keys_by_pattern(["wxx.a", "wxx.b", "other"], "wxx*", exclude=True)
        ['other']
    """
    if exclude:
        return [k for k in keys if not matches_pattern(k, pattern)]
    else:
        return [k for k in keys if matches_pattern(k, pattern)]
