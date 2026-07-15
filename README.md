# NFA Chess Simulator 

A Python-based 4x4 chess simulation that mathematically models board mechanics and valid player movements as a Non-Deterministic Finite Automaton (NFA). The project features automated decision-making algorithms and real-time graphical rendering of state transitions.

## Features
* **NFA Modeling:** The 4x4 board is represented as an NFA with 16 states and 8-directional valid transitions based on odd/even parity checks.
* **Algorithmic Pathfinding:** Implements a Depth-First Search (DFS) algorithm with depth limits to generate and evaluate all possible movement sequences.
* **Heuristic Optimization:** Uses a Manhattan distance heuristic to filter and select optimal moves, ensuring the automated players progress toward their goals efficiently.
* **Dynamic Visualization:** Leverages Pygame to render both the physical board state and the layered NFA state transition diagrams in real-time.
* **Data Logging:** Automatically exports all generated paths, winning sequences to `.txt` files, and final NFA diagrams to `.png`.

## Tech Stack
* **Language:** Python 3
* **Libraries:** Pygame, Sys, Random, Time

## How to Run
Ensure you have Python and Pygame installed:
```bash
pip install pygame
python main.py
