# Zombie Simulation – CPS 310 Midterm #1

**Author:** Reese Franklin

## The Problem
The simulation keeps track of state: the agents (humans and zombies), the
environment (world size), and the runtime (the frame timer). That state could
be stored many ways: in-memory data structures, a database, files, and so on.
The goal is to keep the simulation logic independent of the storage choice,
so changing how state is stored never requires changing the simulation code.

## The Design: Three Layers

    main.py          ->  Display layer: window, drawing, input.
         |               Chooses which storage to use (one line).
         v
    simulation.py    ->  Simulation layer: the rules (movement, chasing,
         |               fights, timer). Talks ONLY to the StateStore interface.
         v
    storage.py       ->  Storage layer: the StateStore interface plus two
                         storage options that follow it.

### 1. The interface: `StateStore`
`StateStore` is an abstract base class (Python `abc`). It defines the rules
every storage option must follow, without saying how they are done:

| Method | Purpose |
|---|---|
| `add_agent(data)` | Store a new agent, return its id |
| `update_agent(data)` | Save an agent's changes (e.g. new position) |
| `remove_agent(agent_id)` | Delete an agent |
| `get_agents(kind)` | Get all humans or all zombies |
| `set_value(key, value)` / `get_value(key)` | Environment and runtime values |
| `clear()` | Reset everything for a new game |
| `save()` | Make all changes since the last save permanent |

Every method is marked `@abstractmethod`, so Python refuses to create a
storage class that is missing any of them.

### 2. Two storage options
- **`InMemoryStore`** keeps state in Python dictionaries in RAM. Fast and
  simple, but the state is gone when the program closes.
- **`SQLiteStore`** keeps state in a SQLite database file (`zombie_state.db`)
  with two tables: `agents` (one row per agent) and `runtime` (one row per
  named value). It uses SQL `INSERT`, `UPDATE`, `DELETE`, and `SELECT`, and
  the state stays in the file after the program closes.

### 3. The simulation only knows the interface
The `Simulation` class receives a storage object when it is created:

    store = SQLiteStore()      # or InMemoryStore()
    sim = Simulation(store)

It never creates a storage object itself and never checks which kind it has.
Each frame follows the same pattern: **load state, apply the rules, save
state**, all through the interface methods.

## Why This Design Decouples the Two Layers
1. **`simulation.py` never imports `storage.py`.** The simulation code has no
   reference to dictionaries, SQL, or any specific storage. It only calls the
   interface methods.
2. **Agents are stored as plain data.** `Human` and `Zombie` convert
   themselves to and from simple dictionaries with `to_dict()` and
   `from_dict()`. The storage layer never sees the `Human` or `Zombie`
   classes, so either layer can change without breaking the other.
3. **The interface is enforced.** Because `StateStore` uses
   `@abstractmethod`, every storage option is guaranteed to have every method
   the simulation needs.
4. **Storage-specific details stay hidden.** A database needs transactions and
   commits, and RAM does not. The interface's `save()` method hides that
   difference: `SQLiteStore` commits, and `InMemoryStore` does nothing. The
   simulation just calls `save()` once per frame without knowing which one
   it is talking to.
5. **Switching storage is one line.** Changing `store = InMemoryStore()` to
   `store = SQLiteStore()` in `main.py` switches the whole game's storage.
   `simulation.py` does not change at all.
6. **Adding a new storage option is easy.** A third option (for example, a
   JSON file) only needs a new class that follows `StateStore`. No existing
   code has to change.

## How to Run
1. Install Python 3 and pygame-ce: `pip install pygame-ce`
2. Run: `python main.py`
3. To switch storage, edit the `store = ...` line in `main.py`.

## How the Simulation Works
- 20 humans (blue) wander at random speeds; 3 zombies (green) chase the
  nearest human.
- When a zombie touches a human, they fight: 40% chance the human destroys
  the zombie, 60% chance the human becomes a zombie.
- The game ends when one side is wiped out, or after 45 seconds
  ("Rescue arrived!").
- Press R to restart.

