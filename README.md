# Python Chess Suite

A complete, lightweight chess application featuring a robust Python-based chess engine and a Pygame-powered GUI. Play full, regulation chess with move validation, special rules (castling, en passant), and a clean, interactive interface.

---

## Key Features

- ♟️ Full Move Generation & Validation  
- 👾 Interactive Drag-and-Drop GUI  
- 🖼️ High-Quality Piece Sprites (PNG)  
- ⚙️ Clean Configuration Module for Easy Tuning  
- 📦 Modular Design: Engine & GUI Decoupled  
- 🐍 Pure Python (Requires only `numpy` & `pygame`)

---

## Architecture Overview

At a high level, the system consists of:

- **User Interface** (`src/main.py`, `src/graphics.py`)  
- **Configuration** (`src/config.py`)  
- **Chess Engine** (`chess/engine.py`, `chess/pieces.py`, `chess/utils.py`)  
- **Assets** (`images/`)  
- **External Dependencies**: Pygame, NumPy  

```mermaid
flowchart TD
    U[User] -->|interacts| GUI[Main GUI (src/main.py)]
    GUI -->|loads config| CFG[Config (src/config.py)]
    GUI -->|renders board & pieces| GFX[Graphics (src/graphics.py)]
    GUI -->|sends moves to| ENG[Engine (chess/engine.py)]
    ENG -->|uses| PCS[Pieces (chess/pieces.py)]
    ENG -->|uses| UTL[Utils (chess/utils.py)]
    GFX -->|loads images| IMG[(images/ folder)]
    ENG -->|maintains| BS[(Board State)]
    subgraph Dependencies
      PYG[Pygame]
      NUM[NumPy]
    end
    GUI --> PYG
    ENG --> NUM
```

---

## Getting Started

### Prerequisites

- Python 3.8 or newer  
- pip  

### Installation

1. Clone the repository  
   ```bash
   git clone https://github.com/your-org/python-chess-suite.git
   cd python-chess-suite
   ```
2. Create & activate a virtual environment (optional but recommended)  
   ```bash
   python -m venv venv
   source venv/bin/activate    # Linux/macOS
   venv\Scripts\activate       # Windows
   ```
3. Install dependencies  
   ```bash
   pip install -r requirements.txt
   ```

### Running the Application

```bash
python src/main.py
```

This launches the Pygame window. Drag and drop pieces to play against the built-in engine.

### Using the Engine Standalone

```python
from chess.engine import Engine
from chess.utils import piece_name

engine = Engine()
board = engine.board

print(piece_name(board, (0, 1)))  # ⇒ 'wN' (white knight on b1)
moves = engine.get_valid_moves((1, 0))
engine.make_move(moves[0])
```

---

## API Reference

### Engine (chess/engine.py)

- `Engine()`  
  Initializes a new game.
- `engine.board`  
  8×8 matrix of piece codes (`"wP"`, `"bK"`, `"--"`, etc.).
- `engine.get_valid_moves(position: Tuple[int, int]) -> List[Move]`  
  Returns all legal moves for the piece at `position`.
- `engine.make_move(move: Move)`  
  Executes the selected move and updates `engine.board`.

### Pieces (chess/pieces.py)

- Abstract `Piece` base class  
- Subclasses: `Pawn`, `Knight`, `Bishop`, `Rook`, `Queen`, `King`

### Utils (chess/utils.py)

- `piece_name(board, coord) -> str`  
- Helper functions for coordinate conversion, move notation.

### Graphics (src/graphics.py)

- `load_pieces() -> Dict[str, Surface]`  
- `load_grid(screen)`  
- `update_pieces(screen, board)`  
- `highlight_squares(screen, moves)`

---

## Configuration

All rendering and engine constants live in [`src/config.py`](src/config.py):

```python
WIDTH = 864           # Window width (pixels)
HEIGHT = 864          # Window height
BOARD_SIZE = 8
TILE_SIZE = WIDTH // BOARD_SIZE
PIECE_SIZE = int(TILE_SIZE * 0.9)
MAX_FPS = 60
EMPTY = "--"
```

Adjust these values to change window size, FPS, piece scale, etc.

---

## Contributing & Development

1. Fork the repository  
2. Create a feature branch (`git checkout -b feature/YourFeature`)  
3. Install dependencies (see Getting Started)  
4. Run the GUI or import engine modules in your tests  
5. Submit a pull request against `main`

### Key Files

- [`src/main.py`](src/main.py) – Application entry point  
- [`src/config.py`](src/config.py) – All constants in one place  
- [`src/graphics.py`](src/graphics.py) – Rendering pipeline  
- [`chess/engine.py`](chess/engine.py) – Core game logic  
- [`chess/pieces.py`](chess/pieces.py) – Piece move definitions  
- [`chess/utils.py`](chess/utils.py) – Helper utilities  

We welcome issues, feature requests, and pull requests. See [LICENSE](LICENSE) for usage terms. Enjoy coding—and checkmate your way to victory!