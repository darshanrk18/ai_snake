"""
Core Game Logic and AI Decision Making

This module contains the heart of the Snake game - the game mechanics, A* pathfinding
algorithm, and the intelligent decision-making system that prevents the AI from
trapping itself while efficiently collecting food.

The AI uses a sophisticated multi-tier strategy:
1. Try to find safe paths to food that guarantee survival after eating
2. Fall back to following the tail to buy time when no safe food path exists
3. Use more lenient safety checks after detecting repetitive behavior
4. Take calculated risks when the situation becomes desperate
5. Use any available move as a last resort

This creates a deterministic, explainable AI that plays intelligently without
using machine learning or complex heuristics.
"""
from __future__ import annotations

import logging
import heapq
import random
from collections import deque
from typing import Deque, Dict, List, Optional, Set, Tuple

from .config import GRID_W, GRID_H
from .utils import DIRS, Pos, Path, add, deque_copy

logger = logging.getLogger(__name__)


class SnakeGame:
    """
    The main game engine that manages the Snake game state and AI decisions.
    
    This class encapsulates everything needed to run a game of Snake:
    - Board state (snake position, food location, score)
    - Game mechanics (movement, collision detection, growth)
    - A* pathfinding for intelligent movement
    - Multi-tier decision making for optimal gameplay
    
    The AI makes decisions by simulating different moves and evaluating
    their safety using pathfinding algorithms.
    """

    def __init__(self, w: int = GRID_W, h: int = GRID_H) -> None:
        """
        Initialize a new Snake game with the specified dimensions.
        
        Args:
            w: Width of the game grid in cells
            h: Height of the game grid in cells
        """
        self.w, self.h = w, h
        self.reset()

    def reset(self) -> None:
        """
        Reset the game to a fresh state for a new game.
        
        Creates a new snake in the center of the board, spawns food,
        and resets all game metrics and tracking variables.
        """
        # Start snake in the center of the board, facing right
        mid = (self.w // 2, self.h // 2)
        self.snake: Deque[Pos] = deque([mid, (mid[0] - 1, mid[1]), (mid[0] - 2, mid[1])])
        self.direction: Pos = (1, 0)  # Start moving RIGHT
        
        # Initialize game state
        self.spawn_food()
        self.score = 0
        self.game_over = False
        self.win = False

        # Visual and debugging features
        self.current_path: Optional[Path] = None
        self.show_path = True

        # Tail-chase loop detection (prevents infinite orbiting)
        self.tch_in = False
        self.tch_anchor: Optional[Tuple[Pos, Pos, int]] = None  # (head_pos, dir, length)
        self.tch_steps = 0
        self.tch_loops = 0
        self.tch_max_loops = 2  # Maximum loops before switching strategies

    # ==================== GAME MECHANICS ====================
    
    def spawn_food(self) -> None:
        """
        Place food on a random empty cell, or mark the game as won.
        
        Food is spawned on any cell that isn't occupied by the snake.
        If no empty cells exist, the player has filled the entire board
        and wins the game.
        """
        # Find all possible positions on the board
        all_cells: Set[Pos] = {(x, y) for x in range(self.w) for y in range(self.h)}
        # Remove positions occupied by the snake
        occupied: Set[Pos] = set(self.snake)
        # Choose from remaining empty positions
        available_positions: List[Pos] = list(all_cells - occupied)
        
        if available_positions:
            self.food: Optional[Pos] = random.choice(available_positions)
        else:
            # No space left - the player/AI wins!
            self.food = None
            self.game_over = True
            self.win = True
            logger.debug("Board full: win state reached.")

    def valid_cell(self, p: Pos, *, allow_tail: bool = False) -> bool:
        """
        Check if a position is a valid cell to move into.
        
        A cell is valid if it's within bounds and not occupied by the snake.
        The allow_tail parameter is useful during planning - it treats the
        current tail position as free since the tail will move forward
        unless the snake eats food.
        
        Args:
            p: Position to check
            allow_tail: If True, treat current tail as free space
            
        Returns:
            True if the position is valid to move into
        """
        x, y = p
        
        # Check if position is within board boundaries
        if not (0 <= x < self.w and 0 <= y < self.h):
            return False

        # Get snake body positions (excluding tail if allow_tail is True)
        body = list(self.snake)
        if allow_tail and p == body[-1]:
            return True
            
        # Check if position is occupied by snake body
        return p not in body[:-1]

    def step(self, direction: Pos) -> None:
        """
        Advance the game by one step in the specified direction.
        
        This function handles all the core game mechanics:
        - Prevents immediate 180-degree reversals
        - Detects wall and body collisions
        - Handles food collection and snake growth
        - Updates game metrics and loop tracking
        
        Args:
            direction: The direction to move (dx, dy)
        """
        if self.game_over:
            return

        # Prevent 180-degree reversals that would cause immediate collision
        if len(self.snake) > 1:
            head, neck = self.snake[0], self.snake[1]
            if add(head, direction) == neck:
                direction = self.direction

        # Calculate new head position and update direction
        new_head = add(self.snake[0], direction)
        self.direction = direction
        tail_pos = self.snake[-1]
        
        # Check if this move will result in eating food
        will_eat = (self.food is not None and new_head == self.food)
        stepping_on_tail = (new_head == tail_pos)

        # Check for collisions
        # Wall collision
        if not (0 <= new_head[0] < self.w and 0 <= new_head[1] < self.h):
            self.game_over = True
            logger.debug("Collision with wall at %s", new_head)
            return
            
        # Body collision (stepping on tail is allowed only if tail will move)
        if new_head in self.snake and not (stepping_on_tail and not will_eat):
            self.game_over = True
            logger.debug("Collision with body at %s", new_head)
            return

        # Move the snake forward
        self.snake.appendleft(new_head)
        
        if will_eat:
            # Food collected - grow the snake and update metrics
            self.score += 1
            
            # Spawn new food and reset orbit tracking
            self.spawn_food()
            self.tch_in = False
            self.tch_anchor = None
            self.tch_steps = 0
            self.tch_loops = 0
        else:
            # Normal move - tail advances (snake doesn't grow)
            self.snake.pop()

    # ==================== A* PATHFINDING ====================
    
    def astar(self, start: Pos, goal: Optional[Pos], *, allow_tail: bool = True) -> Optional[Path]:
        """
        Find the shortest path from start to goal using the A* algorithm.
        
        A* is an informed search algorithm that uses a heuristic to guide
        the search toward the goal. It's guaranteed to find the optimal path
        and is much more efficient than uninformed search algorithms.
        
        The algorithm works by:
        1. Starting from the start position
        2. Exploring neighboring cells using a priority queue
        3. Using Manhattan distance as a heuristic to guide the search
        4. Building a path by following parent pointers back to start
        
        Args:
            start: Starting position
            goal: Goal position (None if no goal available)
            allow_tail: If True, treat current tail as free space during planning
            
        Returns:
            List of positions forming the path from start to goal, or None if no path exists
        """
        if goal is None:
            return None
        if start == goal:
            return [start]

        def h(p: Pos) -> int:
            """
            Heuristic function: Manhattan distance to goal.
            
            This is admissible (never overestimates) and consistent,
            which guarantees A* will find the optimal path.
            """
            return abs(p[0] - goal[0]) + abs(p[1] - goal[1])

        # A* algorithm implementation
        g: Dict[Pos, int] = {start: 0}  # Cost from start to each position
        parent: Dict[Pos, Optional[Pos]] = {start: None}  # Parent pointers for path reconstruction
        openh: List[Tuple[int, int, Pos]] = [(h(start), 0, start)]  # Priority queue: (f_score, g_score, position)
        closed: Set[Pos] = set()  # Already explored positions

        while openh:
            # Get the position with the lowest f_score
            f, gc, cur = heapq.heappop(openh)
            if cur in closed:
                continue
            closed.add(cur)

            # Goal reached - reconstruct the path
            if cur == goal:
                path: Path = []
                while cur is not None:
                    path.append(cur)
                    cur = parent[cur]
                return list(reversed(path))

            # Explore all four directions from current position
            for d in DIRS:
                nxt = add(cur, d)
                
                # Skip invalid cells
                if not self.valid_cell(nxt, allow_tail=allow_tail):
                    continue

                # Calculate cost to reach this neighbor
                tentative = g[cur] + 1
                
                # Update if we found a better path
                if tentative < g.get(nxt, 10**9):
                    g[nxt] = tentative
                    parent[nxt] = cur
                    # Add to priority queue with f_score = g_score + heuristic
                    heapq.heappush(openh, (tentative + h(nxt), tentative, nxt))

        # No path found
        return None

    # ==================== AI DECISION MAKING ====================
    
    def _enter_tail_chase_if_needed(self, using_tail_path: bool) -> None:
        """
        Track tail-chasing behavior to detect and prevent infinite loops.
        
        When the AI can't find a safe path to food, it follows its tail
        to buy time. However, this can lead to infinite orbiting behavior.
        This function detects such loops and caps them to force the AI
        to try alternative strategies.
        
        A loop is detected when the snake returns to approximately the
        same position with the same direction and length after moving
        roughly the length of the snake.
        
        Args:
            using_tail_path: True if currently following a tail path
        """
        if using_tail_path:
            if not self.tch_in:
                # Start tracking a new tail-chase session
                self.tch_in = True
                self.tch_anchor = (self.snake[0], self.direction, len(self.snake))
                self.tch_steps = 0
            else:
                # Continue tracking existing session
                self.tch_steps += 1
                
                # Check for loop completion
                if self.tch_steps >= len(self.snake):
                    # Check if we're back to the anchor state
                    same_pos = (self.snake[0] == self.tch_anchor[0])
                    same_dir = (self.direction == self.tch_anchor[1])
                    same_len = (len(self.snake) == self.tch_anchor[2])
                    
                    if same_pos and same_dir and same_len:
                        # Loop detected - increment counter and reset step counter
                        self.tch_loops += 1
                        self.tch_steps = 0
        else:
            # Not using tail path - reset tracking
            self.tch_in = False
            self.tch_anchor = None
            self.tch_steps = 0

    def _lenient_food_attempt(self) -> Tuple[Optional[Pos], Optional[Path]]:
        """
        Try to find a food path using more lenient safety checks.
        
        After detecting too many tail-chase loops, the AI becomes more
        willing to take calculated risks. This function uses allow_tail=True
        when checking post-eat survival, making it more permissive about
        paths that might be safe if the tail moves out of the way.
        
        Returns:
            Tuple of (best_move, best_path) or (None, None) if no path found
        """
        head = self.snake[0]
        tail = self.snake[-1]
        best_move: Optional[Pos] = None
        best_path: Optional[Path] = None
        best_len = 10**9

        # Try all possible first moves
        for d in DIRS:
            # Skip immediate reversals
            if len(self.snake) > 1 and add(self.snake[0], d) == self.snake[1]:
                continue

            first = add(head, d)
            
            # Check if first move is valid
            if not self.valid_cell(first, allow_tail=True):
                continue
                
            # Special case: can't step on tail if it's also food (tail won't vacate)
            if first == tail and first == self.food:
                continue

            # Simulate the first step
            sim_snake = deque_copy(self.snake)
            sim_snake.appendleft(first)
            if first != self.food:
                sim_snake.pop()

            # Plan path to food from simulated state
            sim_head = sim_snake[0]
            sim_plan = SnakeGame(self.w, self.h)
            sim_plan.snake = deque_copy(sim_snake)
            sim_plan.food = self.food
            
            path_after = sim_plan.astar(sim_head, self.food, allow_tail=True)
            if path_after is None:
                continue

            # Simulate the entire path to food
            sim2 = SnakeGame(self.w, self.h)
            sim2.snake = deque_copy(sim_snake)
            sim2.food = self.food
            
            for idx in range(1, len(path_after)):
                step_cell = path_after[idx]
                sim2.snake.appendleft(step_cell)
                if step_cell != sim2.food:
                    sim2.snake.pop()

            # Check post-eat survival using lenient rules
            sim_head2, sim_tail2 = sim2.snake[0], sim2.snake[-1]
            sim_check = SnakeGame(self.w, self.h)
            sim_check.snake = deque_copy(sim2.snake)
            
            to_tail_after = sim_check.astar(sim_head2, sim_tail2, allow_tail=True)
            if to_tail_after:
                # Found a valid path - update best if this is shorter
                total_len = 1 + max(0, len(path_after) - 1)
                if total_len < best_len:
                    best_len = total_len
                    best_move = d
                    best_path = [head] + path_after

        return best_move, best_path

    def decide_astar_safe(self) -> "Pos":
        """
        Make the next move decision using a sophisticated multi-tier strategy.
        
        This is the core AI decision function that determines where the snake
        should move next. It implements a hierarchical approach that tries
        increasingly risky strategies only when safer ones fail.
        
        Strategy hierarchy:
        1. STRICT-SAFE FOOD: Find paths to food that guarantee survival after eating
        2. TAIL-CHASE: Follow tail to buy time when no safe food path exists
        3. LENIENT-SAFE FOOD: Use more permissive safety checks after loop detection
        4. YOLO MODE: Take calculated risks when tail-chasing becomes hopeless
        5. ANY NON-LOSING MOVE: Use any available move as a last resort
        
        Returns:
            The chosen movement direction (dx, dy)
        """
        # Quick exit if no food (game won or over)
        if self.food is None:
            return self.direction

        head: "Pos" = self.snake[0]
        tail: "Pos" = self.snake[-1]
        self.current_path = None  # Reset path for visualization

        # ==================== HELPER FUNCTIONS ====================
        # These are defined locally to avoid polluting the class namespace
        
        def strict_safe_food_candidate(first_move: "Pos") -> tuple["Pos", "Path", int] | None:
            """
            Check if a first move leads to a strictly safe food path.
            
            A path is strictly safe if:
            1. The first move is valid
            2. A path exists from the new position to food
            3. After eating, the snake can reach its tail (survival guaranteed)
            
            Args:
                first_move: The direction to check
                
            Returns:
                Tuple of (move, full_path, total_length) if safe, None otherwise
            """
            # Skip immediate reversals
            if len(self.snake) > 1 and add(self.snake[0], first_move) == self.snake[1]:
                return None

            first_cell = add(head, first_move)
            
            # Check if first move is valid
            if not self.valid_cell(first_cell, allow_tail=True):
                return None
                
            # Can't step on tail if it's also food (tail won't vacate on growth)
            if first_cell == tail and first_cell == self.food:
                return None

            # Simulate the first step
            sim_snake = deque(list(self.snake))
            sim_snake.appendleft(first_cell)
            if first_cell != self.food:
                sim_snake.pop()

            # Plan path to food from simulated state
            sim_head = sim_snake[0]
            sim_plan = SnakeGame(self.w, self.h)
            sim_plan.snake = deque(list(sim_snake))
            sim_plan.food = self.food
            
            path_after = sim_plan.astar(sim_head, self.food, allow_tail=True)
            if path_after is None:
                return None

            # Simulate the entire path to food
            sim2 = SnakeGame(self.w, self.h)
            sim2.snake = deque(list(sim_snake))
            sim2.food = self.food
            
            for i in range(1, len(path_after)):
                step_cell = path_after[i]
                sim2.snake.appendleft(step_cell)
                if step_cell != sim2.food:
                    sim2.snake.pop()

            # STRICT post-eat survival check: can head reach tail after eating?
            sim_head2, sim_tail2 = sim2.snake[0], sim2.snake[-1]
            sim_check = SnakeGame(self.w, self.h)
            sim_check.snake = deque(list(sim2.snake))
            
            to_tail_after = sim_check.astar(sim_head2, sim_tail2, allow_tail=False)
            if to_tail_after:
                total_len = 1 + max(0, len(path_after) - 1)
                full_path_for_viz: "Path" = [head] + path_after
                return (first_move, full_path_for_viz, total_len)
                
            return None

        def strict_safe_food_exists_from(game_obj: "SnakeGame") -> bool:
            """
            Check if any strict-safe food plan exists from the given game state.
            
            This is used during horizon analysis to determine if a situation
            is hopeless or if waiting might reveal a safe opportunity.
            
            Args:
                game_obj: The game state to check from
                
            Returns:
                True if any strict-safe food path exists
            """
            g = game_obj
            h, t = g.snake[0], g.snake[-1]
            
            for d in DIRS:
                # Mirror the candidate logic from strict_safe_food_candidate
                if len(g.snake) > 1 and add(g.snake[0], d) == g.snake[1]:
                    continue
                    
                first_cell = add(h, d)
                if not g.valid_cell(first_cell, allow_tail=True):
                    continue
                    
                if first_cell == t and first_cell == g.food:
                    continue

                sim_snake = deque(list(g.snake))
                sim_snake.appendleft(first_cell)
                if first_cell != g.food:
                    sim_snake.pop()

                sim_head = sim_snake[0]
                sim_plan = SnakeGame(g.w, g.h)
                sim_plan.snake = deque(list(sim_snake))
                sim_plan.food = g.food
                
                path_after = sim_plan.astar(sim_head, g.food, allow_tail=True)
                if path_after is None:
                    continue

                sim2 = SnakeGame(g.w, g.h)
                sim2.snake = deque(list(sim_snake))
                sim2.food = g.food
                
                for i in range(1, len(path_after)):
                    step_cell = path_after[i]
                    sim2.snake.appendleft(step_cell)
                    if step_cell != sim2.food:
                        sim2.snake.pop()

                sim_head2, sim_tail2 = sim2.snake[0], sim2.snake[-1]
                sim_check = SnakeGame(g.w, g.h)
                sim_check.snake = deque(list(sim2.snake))
                
                if sim_check.astar(sim_head2, sim_tail2, allow_tail=False):
                    return True
                    
            return False

        def hopeless_tail_chase(horizon_steps: int) -> bool:
            """
            Determine if tail-chasing is hopeless by looking ahead.
            
            This function simulates tail-chasing for a limited number of steps
            to see if any safe food opportunities arise. If none appear within
            the horizon, the situation is considered hopeless and the AI should
            take more aggressive action.
            
            Args:
                horizon_steps: Number of steps to look ahead
                
            Returns:
                True if tail-chasing appears hopeless
            """
            # Clone current state for simulation
            sim = SnakeGame(self.w, self.h)
            sim.snake = deque(list(self.snake))
            sim.direction = self.direction
            sim.food = self.food

            for _ in range(max(1, horizon_steps)):
                # If a strict-safe food plan becomes available, it's not hopeless
                if strict_safe_food_exists_from(sim):
                    return False

                # Try to advance one tail-chase step
                path_to_tail = sim.astar(sim.snake[0], sim.snake[-1], allow_tail=False)
                if not path_to_tail or len(path_to_tail) < 2:
                    # Can't even reach tail - situation is hopeless
                    return True

                # Apply the tail-chase step
                nxt = path_to_tail[1]
                move = (nxt[0] - sim.snake[0][0], nxt[1] - sim.snake[0][1])
                
                # Simulate the step without food respawn effects
                new_head = nxt
                will_eat = (sim.food is not None and new_head == sim.food)
                sim.snake.appendleft(new_head)
                if not will_eat:
                    sim.snake.pop()
                    
                # Keep same food during simulation to check if THIS food becomes reachable

            # Exhausted horizon with no safe opportunities
            return True

        # ==================== STRATEGY IMPLEMENTATION ====================
        
        # ---------- 1) STRICT-SAFE FOOD (Primary Strategy) ----------
        # Find the shortest safe path to food among all possible first moves
        best: tuple["Pos", "Path", int] | None = None
        for d in DIRS:
            candidate = strict_safe_food_candidate(d)
            if candidate is None:
                continue
            if best is None or candidate[2] < best[2]:
                best = candidate

        if best is not None:
            # Found a safe path - use it and reset tail-chase tracking
            move, path_for_viz, _ = best
            self.tch_in = False
            self.tch_steps = 0
            self.current_path = path_for_viz
            return move

        # ---------- 2) TAIL-CHASE FALLBACK ----------
        # No safe food path exists - follow tail to buy time
        path_to_tail = self.astar(head, tail, allow_tail=False)
        if path_to_tail and len(path_to_tail) >= 2:
            self.current_path = path_to_tail
            nxt = path_to_tail[1]
            move = (nxt[0] - head[0], nxt[1] - head[1])
            
            # Track this tail-chase session
            self._enter_tail_chase_if_needed(using_tail_path=True)

            # ---------- 3) LENIENT-SAFE FOOD after loop cap ----------
            # If we've been tail-chasing too long, try more permissive safety checks
            if self.tch_loops >= self.tch_max_loops:
                lenient_move, lenient_path = self._lenient_food_attempt()
                if lenient_move is not None:
                    self.current_path = lenient_path
                    # Reset tail-chase tracking on successful food attempt
                    self.tch_in = False
                    self.tch_loops = 0
                    self.tch_steps = 0
                    self.tch_anchor = None
                    return lenient_move

            # ---------- 4) YOLO MODE when tail-chase is hopeless ----------
            # If tail-chasing won't yield safe opportunities soon, take calculated risks
            HORIZON = max(len(self.snake) * 2, 20)  # Look ahead based on snake length
            if hopeless_tail_chase(HORIZON):
                # Go directly for food, accepting potential future death
                direct_food = self.astar(head, self.food, allow_tail=True)
                if direct_food and len(direct_food) >= 2:
                    self.current_path = [head] + direct_food
                    return (direct_food[1][0] - head[0], direct_food[1][1] - head[1])

            return move

        # ---------- 5) ANY NON-LOSING MOVE (Last Resort) ----------
        # Can't even reach tail - use any available move
        self._enter_tail_chase_if_needed(using_tail_path=False)
        
        for d in DIRS:
            next_head = add(head, d)
            if self.valid_cell(next_head, allow_tail=True):
                return d

        # No legal moves available - keep current direction (collision will be handled by step())
        return self.direction
