# utils.py

""" 
This module contains general-purpose utility functions used by other modules.
"""

def check_prob(name: str, p: float) -> None:
    """Checks if a prob p is in [0, 1]

    Args:
        name (str): Name of the parameter (e.g., p_SI)
        p (float): The prob value.

    Raises:
        ValueError.
    """
    if not (0.0 <= p <= 1.0):
        raise ValueError(f"{name} must be in [0, 1], got {p}.")
