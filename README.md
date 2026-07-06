# Asteroids

A classic Asteroids arcade game built with Python and pygame. Pilot a triangle ship, dodge incoming asteroids, and shoot them apart before they hit you.

## Tech stack

| Tool | Version | Purpose |
|------|---------|---------|
| [Python](https://www.python.org/) | 3.13+ | Language runtime |
| [pygame](https://www.pygame.org/) | 2.6.1 | Graphics, input, and game loop |
| [uv](https://docs.astral.sh/uv/) | latest | Dependency management and running the game |

## Prerequisites

- [uv](https://docs.astral.sh/uv/getting-started/installation/) installed and available on your PATH

If `uv` is not recognized after installing it, restart your terminal or add its install directory to PATH (on Windows, typically `C:\Users\<you>\.local\bin`).

## Quick start

1. **Clone the repo** (or open the project folder if you already have it locally).

2. **Install dependencies** — this creates a `.venv` virtual environment and installs pygame:

   ```bash
   uv sync
   ```

3. **Run the game**:

   ```bash
   uv run asteroids
   ```

   Or run the entry script directly:

   ```bash
   uv run main.py
   ```

That's it — a game window should open at 1280×720.

## Controls

| Key | Action |
|-----|--------|
| `W` | Thrust forward |
| `S` | Thrust backward |
| `A` | Rotate left |
| `D` | Rotate right |
| `Space` | Shoot |
| Close window | Quit |

## How to play

- Asteroids spawn from the edges of the screen and drift toward the center.
- If an asteroid collides with your ship, it's game over.
- Shooting an asteroid splits it into two smaller pieces (until they reach the minimum size).
- There is no score screen yet — survive as long as you can.

## Project structure

```
asteroids/
├── main.py           # Game loop, collision handling, entry point
├── player.py         # Player ship (movement, rotation, shooting)
├── asteroid.py       # Asteroid behavior and splitting
├── asteroidfield.py  # Spawns asteroids at screen edges
├── shot.py           # Projectile fired by the player
├── circleshape.py    # Base class for circular game objects
├── constants.py      # Screen size, speeds, spawn rates, etc.
├── logger.py         # Writes game_state.jsonl and game_events.jsonl
├── pyproject.toml    # Project metadata and dependencies
└── uv.lock           # Locked dependency versions
```

## Log files (JSONL)

Each run of the game writes two log files in the project root. Both use [JSON Lines](https://jsonlines.org/) format — one JSON object per line, easy to parse with standard tools.

These files are gitignored and are recreated on every run.

### `game_state.jsonl`

Periodic snapshots of the game world, written about once per second for the first 16 seconds of a session. Each line includes:

- `timestamp` — time of the snapshot
- `elapsed_s` — seconds since the game started
- `frame` — current frame number
- `screen_size` — window dimensions
- Sprite groups (`updatable`, `drawable`, `asteroids`, `shots`) with counts and sample sprite data (position, velocity, radius, rotation)

Useful for debugging movement, spawn rates, and overall game state over time.

### `game_events.jsonl`

Discrete events as they happen during gameplay. Each line includes:

- `timestamp`, `elapsed_s`, `frame` — same as above
- `type` — the event name

Known event types:

| Event | When it fires |
|-------|---------------|
| `player_hit` | The player collides with an asteroid (game over) |
| `asteroid_shot` | A shot destroys an asteroid |
| `asteroid_split` | An asteroid breaks into smaller pieces |

## Configuration

Game tuning values (screen size, speeds, spawn rate, etc.) live in `constants.py`:

| Constant | Default | Description |
|----------|---------|-------------|
| `SCREEN_WIDTH` / `SCREEN_HEIGHT` | 1280 × 720 | Window size |
| `PLAYER_SPEED` | 200 | Ship thrust speed |
| `PLAYER_TURN_SPEED` | 300 | Degrees per second |
| `PLAYER_SHOOT_COOLDOWN_SECONDS` | 0.3 | Minimum time between shots |
| `ASTEROID_SPAWN_RATE_SECONDS` | 0.8 | Time between asteroid spawns |
| `ASTEROID_KINDS` | 3 | Size tiers (large → small) |

## License

No license specified yet.
