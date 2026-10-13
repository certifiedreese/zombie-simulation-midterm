# ============================================================
# storage.py - State storage layer
#
# StateStore is the INTERFACE: the list of rules every storage
# option must follow. The simulation only talks to these methods,
# so it never knows HOW or WHERE the state is actually stored.
# ============================================================

from abc import ABC, abstractmethod


class StateStore(ABC):
    """Rules every storage option must follow."""

    # ---------- AGENTS ----------
    # Agents are stored as plain dictionaries, for example:
    # {"id": 1, "kind": "human", "x": 100, "y": 200, "dx": 1.0, "dy": -0.5, "speed": 0}

    @abstractmethod
    def add_agent(self, data):
        """Store a new agent and return its new id."""

    @abstractmethod
    def update_agent(self, data):
        """Save an agent's changed data (like a new position)."""

    @abstractmethod
    def remove_agent(self, agent_id):
        """Delete an agent."""

    @abstractmethod
    def get_agents(self, kind):
        """Return a list of all agents of one kind ("human" or "zombie")."""

    # ---------- ENVIRONMENT AND RUNTIME ----------
    # Simple named values, like "frames" or "width".

    @abstractmethod
    def set_value(self, key, value):
        """Save a named value."""

    @abstractmethod
    def get_value(self, key, default=None):
        """Read a named value, or return default if it isn't saved yet."""

    # ---------- RESET ----------

    @abstractmethod
    def clear(self):
        """Delete everything, for starting a new game."""