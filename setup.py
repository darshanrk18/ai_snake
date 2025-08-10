from setuptools import setup, find_packages
import os

setup(
    name="ai_snake",
    version="1.0.0",
    description="AI Snake game using A* pathfinding with safety checks",
    long_description=open("README.md").read() if os.path.exists("README.md") else "AI Snake game using A* pathfinding",
    author="Darshan Ravindra Konnur",
    packages=find_packages(),
    install_requires=["pygame"],
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "ai-snake=ai_snake.main:play",
        ],
    },
) 