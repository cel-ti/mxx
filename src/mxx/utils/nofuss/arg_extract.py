"""Extract and parse --var arguments from sys.argv before Click processes them."""

import sys
from typing import Dict, List, Tuple


# Global storage for parsed vars
_parsed_vars: Dict[str, str] = {}


def extract_var_args(argv: List[str] = None) -> Tuple[List[str], Dict[str, str]]:
    """Extract --var arguments from sys.argv and parse them.
    
    This function should be called BEFORE Click processes the arguments.
    It extracts all --var x=y arguments, parses them, and returns a cleaned
    argv list without the --var arguments.
    
    Args:
        argv: Argument list to parse (defaults to sys.argv)
        
    Returns:
        Tuple of (cleaned_argv, vars_dict) where:
        - cleaned_argv: argv with --var arguments removed
        - vars_dict: Dictionary of parsed key=value pairs from --var
        
    Example:
        >>> extract_var_args(['mxx', 'run', 'up', '--var', 'x=1', '--var', 'y=2', 'profile'])
        (['mxx', 'run', 'up', 'profile'], {'x': '1', 'y': '2'})
        >>> extract_var_args(['mxx', 'run', 'up', '--var', 'debug', '--var', 'x=1', 'profile'])
        (['mxx', 'run', 'up', 'profile'], {'debug': 'true', 'x': '1'})
    """
    if argv is None:
        argv = sys.argv.copy()
    
    cleaned_argv = []
    vars_dict = {}
    
    i = 0
    while i < len(argv):
        arg = argv[i]
        
        if arg == '--var':
            # Next argument should be the x=y value or just x (bool=true)
            if i + 1 < len(argv):
                var_value = argv[i + 1]
                if '=' in var_value:
                    key, value = var_value.split('=', 1)
                    vars_dict[key.strip()] = value.strip()
                else:
                    # No '=' means it's a boolean flag, set to 'true'
                    vars_dict[var_value.strip()] = 'true'
                i += 2  # Skip both --var and its value
            else:
                # --var without value, just skip it
                i += 1
        elif arg.startswith('--var='):
            # Handle --var=x=y or --var=x format
            var_value = arg[6:]  # Remove '--var=' prefix
            if '=' in var_value:
                key, value = var_value.split('=', 1)
                vars_dict[key.strip()] = value.strip()
            else:
                # No '=' means it's a boolean flag, set to 'true'
                vars_dict[var_value.strip()] = 'true'
            i += 1
        else:
            # Keep this argument
            cleaned_argv.append(arg)
            i += 1
    
    # Store in global for easy access
    global _parsed_vars
    _parsed_vars = vars_dict
    
    return cleaned_argv, vars_dict


def get_parsed_vars() -> Dict[str, str]:
    """Get the parsed --var arguments.
    
    Returns:
        Dictionary of parsed variables from --var arguments
    """
    return _parsed_vars.copy()


def set_parsed_vars(vars_dict: Dict[str, str]) -> None:
    """Set the parsed vars (useful for testing or manual override).
    
    Args:
        vars_dict: Dictionary of variables to set
    """
    global _parsed_vars
    _parsed_vars = vars_dict.copy()
