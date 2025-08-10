# AI Snake - A* Pathfinding Implementation

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Pygame](https://img.shields.io/badge/Pygame-2.0+-green.svg)](https://www.pygame.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A fully-documented implementation of a Snake-playing agent that uses **A\* pathfinding** with sophisticated safety checks. This project demonstrates advanced AI decision-making without machine learning.

## Features

- **Pure A\* Implementation**: No machine learning, just deterministic pathfinding
- **Safety-First Strategy**: Multiple fallback strategies to avoid self-trapping
- **Visual Path Display**: See the AI's planned route in real-time
- **Performance Metrics**: Track efficiency and success rates
- **Configurable Grid**: Adjustable board size and game speed
- **Multiple Control Modes**: AI autoplay, manual control, or hybrid

## Quick Start

### Prerequisites
- Python 3.8 or higher
- Pygame 2.0 or higher

### Installation

#### Option 1: Development Install (Recommended)
```bash
git clone https://github.com/darshankonnur/ai_snake.git
cd ai_snake
pip install -e .
```

#### Option 2: Direct Run
```bash
git clone https://github.com/darshankonnur/ai_snake.git
cd ai_snake
pip install -r requirements.txt
```

## Usage

### Command Line Interface
```bash
# Start with AI autoplay
ai-snake --auto

# Custom grid size and speed
ai-snake --auto --grid 20 20 --fps 15

# Manual control mode
ai-snake
```

### Python Module
```bash
# Run as module
python -m ai_snake.main --auto

# Import and use
python -c "from ai_snake import play; play()"
```

## Controls

- **A**: Toggle AI autoplay
- **P**: Toggle path visualization
- **R**: Reset game
- **Esc**: Quit
- **Arrow keys**: Manual control (when AI is off)

## AI Strategy

The AI uses a sophisticated **5-tier decision tree**:

1. **Strict-Safe Food**: Plan A* route to food with guaranteed post-eat survival
2. **Tail-Chase**: If no safe food path, follow tail to buy time
3. **Lenient-Safe Food**: After loop detection, try more permissive safety checks
4. **YOLO Mode**: When tail-chasing is hopeless, go for food anyway
5. **Fallback**: Any non-losing move as last resort

### How It Works
- **A\* Pathfinding**: Finds optimal routes using Manhattan distance heuristic
- **Safety Simulation**: Simulates moves to ensure survival after eating
- **Loop Detection**: Prevents infinite orbiting behavior
- **Horizon Analysis**: Looks ahead to assess future opportunities

## Project Structure

```
ai_snake/
├── ai_snake/           # Main package
│   ├── __init__.py     # Package initialization
│   ├── config.py       # Game configuration
│   ├── game.py         # Core game logic & AI
│   ├── main.py         # Entry point & CLI
│   ├── render.py       # Graphics & visualization
│   └── utils.py        # Utility functions
├── pyproject.toml      # Project configuration
├── setup.py           # Package setup
├── requirements.txt   # Runtime dependencies
└── README.md         # This file
```

### Adding Features
This is a personal project for learning purposes. Feel free to fork and experiment with:
- Different pathfinding algorithms (Dijkstra, RRT, etc.)
- Alternative AI strategies
- New game mechanics
- Performance optimizations

## Learning Resources

- [A* Pathfinding Algorithm](https://en.wikipedia.org/wiki/A*_search_algorithm)
- [Pygame Documentation](https://www.pygame.org/docs/)
- [Game AI Programming](https://www.gameaipro.com/)
- [Python Type Hints](https://docs.python.org/3/library/typing.html)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## About

**Created by**: Darshan Ravindra Konnur  
**Purpose**: Coursework project for Northeastern University  
**Course**: FAI (Foundations of Artificial Intelligence)  
**Semester**: Summer 2025  

This project demonstrates:
- Advanced algorithm implementation
- Professional Python development practices
- Game AI design principles
- Software engineering best practices

---

⭐ **Star this repository** if you find it helpful for your learning journey! 