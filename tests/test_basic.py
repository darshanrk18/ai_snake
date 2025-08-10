"""
Basic tests for AI Snake game
"""
import pytest
from ai_snake.game import SnakeGame
from ai_snake.utils import Pos, add


def test_snake_game_initialization():
    """Test that SnakeGame initializes correctly"""
    game = SnakeGame(10, 10)
    assert game.w == 10
    assert game.h == 10
    assert len(game.snake) == 3
    assert game.score == 0
    assert not game.game_over


def test_valid_cell():
    """Test valid_cell function"""
    game = SnakeGame(5, 5)
    
    # Test valid cells
    assert game.valid_cell((0, 0))
    assert game.valid_cell((4, 4))
    
    # Test invalid cells (out of bounds)
    assert not game.valid_cell((-1, 0))
    assert not game.valid_cell((5, 0))
    assert not game.valid_cell((0, -1))
    assert not game.valid_cell((0, 5))
    
    # Test cells occupied by snake
    assert not game.valid_cell(game.snake[0])  # Head
    assert not game.valid_cell(game.snake[1])  # Body


def test_utility_functions():
    """Test utility functions"""
    # Test add function
    assert add((1, 2), (3, 4)) == (4, 6)
    assert add((0, 0), (5, -3)) == (5, -3)
    
    # Test Pos type (should work as tuple)
    pos: Pos = (1, 1)
    assert pos[0] == 1
    assert pos[1] == 1


def test_food_spawning():
    """Test food spawning logic"""
    game = SnakeGame(3, 3)
    
    # Food should be spawned initially
    assert game.food is not None
    
    # Food should not be on snake
    assert game.food not in game.snake
    
    # Food should be within bounds
    assert 0 <= game.food[0] < 3
    assert 0 <= game.food[1] < 3


if __name__ == "__main__":
    pytest.main([__file__])
