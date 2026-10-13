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
        

class InMemoryStore(StateStore):
    """Storage option 1: keeps all state in Python dictionaries (in RAM)."""

    def __init__(self):
        self.agents = {}   # agent id -> agent dictionary
        self.values = {}   # name -> value (like "frames")
        self.next_id = 1   # the id the next new agent will get

    def add_agent(self, data):
        agent_id = self.next_id
        self.next_id += 1
        data = dict(data)           # make our own copy
        data["id"] = agent_id
        self.agents[agent_id] = data
        return agent_id

    def update_agent(self, data):
        self.agents[data["id"]] = dict(data)

    def remove_agent(self, agent_id):
        self.agents.pop(agent_id, None)  # None = don't crash if it's already gone

    def get_agents(self, kind):
        # Return copies of every agent whose kind matches
        return [dict(a) for a in self.agents.values() if a["kind"] == kind]

    def set_value(self, key, value):
        self.values[key] = value

    def get_value(self, key, default=None):
        return self.values.get(key, default)

    def clear(self):
        self.agents.clear()
        self.values.clear()
        self.next_id = 1