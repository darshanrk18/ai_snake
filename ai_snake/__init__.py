"""
AI Snake - A* Pathfinding Game Package

This package contains a complete Snake game implementation with an intelligent AI agent
that uses A* pathfinding algorithm to play the game. The AI makes strategic decisions
to avoid self-trapping while efficiently collecting food.

Main entry point: play() function to start the game
"""
from .main import play

__all__ = ["play"]