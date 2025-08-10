"""
Game Rendering Module

This module handles all the visual aspects of the game using pygame.
It includes functions for drawing the game board, snake, food, and path visualization.
"""
from __future__ import annotations

import pygame
from typing import Optional

from .config import (
    BG_COLOR,
    CELL,
    FOOD_COLOR,
    GRID_COLOR,
    GRID_H,
    GRID_W,
    HEAD_COLOR,
    PATH_COLOR,
    SNAKE_COLOR,
    TEXT_COLOR,
)
from .utils import Path


def draw_grid(surf: "pygame.Surface") -> None:
    """
    Draw the background grid lines for visual reference.
    
    Creates a subtle grid pattern that helps players see the boundaries
    of each cell. The grid lines are drawn in a dark gray color to
    not interfere with the main game elements.
    
    Args:
        surf: The pygame surface to draw on
    """
    for x in range(GRID_W):
        pygame.draw.line(surf, GRID_COLOR, (x * CELL, 0), (x * CELL, GRID_H * CELL))
    for y in range(GRID_H):
        pygame.draw.line(surf, GRID_COLOR, (0, y * CELL), (GRID_W * CELL, y * CELL))


def draw_path_overlay(screen: "pygame.Surface", path: Optional[Path]) -> None:
    """
    Draw the AI's planned path as a visual overlay.
    
    Shows the route the AI plans to take by drawing semi-transparent
    blue squares along the path. This helps players understand the
    AI's decision-making process.
    
    Args:
        screen: The pygame surface to draw on
        path: List of positions representing the planned path, or None if no path
    """
    if not path or len(path) < 2:
        return
    
    # Create a transparent surface for the path overlay
    overlay = pygame.Surface((GRID_W * CELL, GRID_H * CELL), pygame.SRCALPHA)
    
    # Draw path segments (skip the first position since it's the current head)
    for (x, y) in path[1:]:
        pygame.draw.rect(overlay, PATH_COLOR, (x * CELL + 4, y * CELL + 4, CELL - 8, CELL - 8), border_radius=6)
    
    # Apply the overlay to the main screen
    screen.blit(overlay, (0, 0))


def draw_game(screen: "pygame.Surface", game, font: "pygame.font.Font") -> None:
    """
    Render the complete game frame including all visual elements.
    
    This is the main rendering function that draws everything on screen:
    background, grid, food, snake, path visualization, and HUD information.
    
    Args:
        screen: The pygame surface to draw on
        game: The SnakeGame instance containing current game state
        font: The font to use for text rendering
    """
    # Clear the screen with background color
    screen.fill(BG_COLOR)
    
    # Draw the background grid
    draw_grid(screen)

    # Draw the food item
    if game.food:
        fx, fy = game.food
        pygame.draw.rect(screen, FOOD_COLOR, (fx * CELL + 2, fy * CELL + 2, CELL - 4, CELL - 4), border_radius=6)

    # Draw the AI's planned path if enabled
    if game.show_path and game.current_path:
        draw_path_overlay(screen, game.current_path)

    # Draw the snake body
    for i, (x, y) in enumerate(game.snake):
        # Use different colors for head vs body
        color = HEAD_COLOR if i == 0 else SNAKE_COLOR
        pygame.draw.rect(screen, color, (x * CELL + 2, y * CELL + 2, CELL - 4, CELL - 4), border_radius=6)

    # Draw the HUD (Heads Up Display) with game information
    # Position the text below the game grid
    info1 = f"Score: {game.score} | Path Viz (P): {'ON' if game.show_path else 'OFF'} | Reset (R)"
    info2 = f"Toggle Path Viz (P) | Toggle AI/Human (A)"
    
    text1 = font.render(info1, True, TEXT_COLOR)
    text2 = font.render(info2, True, TEXT_COLOR)
    
    # Position text below the game grid
    screen.blit(text1, (10, GRID_H * CELL + 4))
    screen.blit(text2, (10, GRID_H * CELL + 24))
