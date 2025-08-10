"""
Main Game Entry Point

This module contains the main game loop and entry point for the Snake AI game.
It handles command line arguments, pygame initialization, event processing,
and coordinates between the game logic and rendering systems.

Usage:
    python -m ai_snake.main --auto --fps 14 --grid 20 20 --log WARNING

Controls:
- A: toggle AI autoplay
- P: toggle path visualization  
- R: reset game
- Esc: quit
- Arrow keys: manual control (when AI is off)
"""
from __future__ import annotations

import argparse
import logging
import os

import pygame

from .config import CELL, FPS as DEFAULT_FPS, GRID_H as DEFAULT_H, GRID_W as DEFAULT_W
from .game import SnakeGame
from .render import draw_game


def parse_args() -> argparse.Namespace:
    """
    Parse command line arguments for customizing the game experience.
    
    Returns:
        Parsed command line arguments with sensible defaults
    """
    parser = argparse.ArgumentParser(description="Snake — A* Only (Safety + Path Viz + Metrics)")
    
    # Game mode options
    parser.add_argument("--auto", action="store_true", 
                       help="Start in AI autoplay mode (default: manual control)")
    
    # Performance and display options
    parser.add_argument("--fps", type=int, default=DEFAULT_FPS, 
                       help=f"Game speed in frames per second (default: {DEFAULT_FPS})")
    parser.add_argument("--grid", type=int, nargs=2, metavar=("W", "H"), 
                       default=(DEFAULT_W, DEFAULT_H),
                       help=f"Grid dimensions width x height (default: {DEFAULT_W} {DEFAULT_H})")
    
    # Debugging options
    parser.add_argument("--log", type=str, 
                       default=os.getenv("SNAKE_LOG_LEVEL", "WARNING"),
                       help="Logging level (DEBUG, INFO, WARNING, ERROR)")
    
    return parser.parse_args()


def setup_logging(level: str) -> None:
    """
    Configure logging system for the game.
    
    Sets up basic logging with a clean format that shows the level,
    module name, and message for debugging purposes.
    
    Args:
        level: Logging level as a string (e.g., "DEBUG", "WARNING")
    """
    logging.basicConfig(
        level=level.upper(),
        format="%(levelname)s:%(name)s:%(message)s"
    )


def play() -> None:
    """
    Launch the pygame window and run the main game loop.
    
    This function initializes pygame, creates the game window, sets up
    the game state, and runs the main event loop that handles user input,
    AI decisions, and rendering updates.
    """
    # Parse command line arguments
    args = parse_args()
    setup_logging(args.log)

    # Extract configuration from arguments
    grid_w, grid_h = args.grid
    fps = args.fps
    auto = args.auto

    # Initialize pygame and create the game window
    pygame.init()
    window_width = grid_w * CELL
    window_height = grid_h * CELL + 50  # Extra 50 pixels for HUD text
    screen = pygame.display.set_mode((window_width, window_height))
    pygame.display.set_caption("AI Snake - A* Pathfinding")
    
    # Set up game timing and fonts
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("consolas", 18)  # Monospace font for clean HUD

    # Create the main game instance
    game = SnakeGame(w=grid_w, h=grid_h)

    # Main game loop
    running = True
    while running:
        # Control game speed
        clock.tick(fps)

        # Process all pending events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                # Handle keyboard input
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_r:
                    game.reset()
                elif event.key == pygame.K_a:
                    auto = not auto  # Toggle between AI and manual control
                elif event.key == pygame.K_p:
                    game.show_path = not game.show_path  # Toggle path visualization
                elif not auto:
                    # Manual control only when AI is disabled
                    if event.key == pygame.K_UP:
                        game.step((0, -1))
                    if event.key == pygame.K_DOWN:
                        game.step((0, 1))
                    if event.key == pygame.K_LEFT:
                        game.step((-1, 0))
                    if event.key == pygame.K_RIGHT:
                        game.step((1, 0))

        # AI decision making and game progression
        if auto and not game.game_over and game.food is not None:
            # Get AI's next move decision
            next_move = game.decide_astar_safe()
            # Apply the move to advance the game
            game.step(next_move)

        # Render the current game state
        draw_game(screen, game, font)

        # Show game over message if applicable
        if game.game_over:
            if game.win:
                banner = "You filled the board! You win!"
            else:
                banner = "Game Over — Press R to restart"
            
            game_over_text = font.render(banner, True, (255, 180, 180))
            screen.blit(game_over_text, (10, 10))

        # Update the display
        pygame.display.flip()

    # Clean up pygame resources
    pygame.quit()


if __name__ == "__main__":
    play()
