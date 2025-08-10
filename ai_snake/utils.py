"""
Utility Functions and Constants

This module provides helper functions and type definitions used throughout the game.
It contains the core direction constants and utility functions for position calculations.
"""
from __future__ import annotations

from collections import deque
from typing import Deque, Tuple

# Type aliases for better code readability
Pos = Tuple[int, int]      # Represents a 2D position (x, y)
Path = list[Pos]           # Represents a sequence of positions forming a path

# Direction constants for grid movement
# Each direction is a tuple of (dx, dy) representing movement in x and y coordinates
UP: Pos = (0, -1)          # Move up (decrease y)
DOWN: Pos = (0, 1)         # Move down (increase y)
LEFT: Pos = (-1, 0)        # Move left (decrease x)
RIGHT: Pos = (1, 0)        # Move right (increase x)
DIRS: tuple[Pos, ...] = (UP, DOWN, LEFT, RIGHT)  # All available directions


def add(a: Pos, b: Pos) -> Pos:
    """
    Add two position vectors together.
    
    This is useful for calculating new positions when moving in a direction.
    For example: add((5, 3), (1, 0)) returns (6, 3) - moving right from position (5, 3)
    
    Args:
        a: First position vector
        b: Second position vector (usually a direction)
        
    Returns:
        New position after adding the vectors
    """
    return (a[0] + b[0], a[1] + b[1])


def deque_copy(dq: Deque[Pos]) -> Deque[Pos]:
    """
    Create a shallow copy of a deque containing positions.
    
    This helper ensures consistent copying behavior across the codebase.
    We convert to list first to avoid any potential issues with deque copying.
    
    Args:
        dq: The deque to copy
        
    Returns:
        A new deque with the same elements
    """
    return deque(list(dq))
