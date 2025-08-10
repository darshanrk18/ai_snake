"""
Game Configuration Settings

This module contains all the configurable constants that control the game's appearance,
performance, and behavior. Modify these values to customize your gaming experience.
"""
from __future__ import annotations

# Grid dimensions and timing
CELL: int = 50          # Size of each grid cell in pixels
GRID_W: int = 10        # Number of columns in the game grid
GRID_H: int = 10        # Number of rows in the game grid
FPS: int = 10           # Game speed in frames per second

# Color scheme for the game interface
# These colors are carefully chosen for good contrast against the dark background
BG_COLOR = (25, 27, 30)        # Dark background color
SNAKE_COLOR = (80, 200, 120)   # Body segments color (green)
HEAD_COLOR  = (190, 240, 190)  # Snake head color (bright green)
FOOD_COLOR  = (240, 120, 80)   # Food item color (orange)
GRID_COLOR  = (50, 55, 60)     # Grid lines color (subtle gray)
TEXT_COLOR  = (230, 230, 230)  # Text color (white)
PATH_COLOR  = (120, 160, 240, 120)  # Path visualization color (blue with transparency)