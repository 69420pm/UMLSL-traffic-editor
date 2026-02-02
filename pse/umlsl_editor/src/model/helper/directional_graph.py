from enum import Enum


class Direction(Enum):
    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)

    @property
    def opposite(self):
        """Returns the opposite direction of the current one."""
        if self == Direction.UP: return Direction.DOWN
        if self == Direction.DOWN: return Direction.UP
        if self == Direction.LEFT: return Direction.RIGHT
        if self == Direction.RIGHT: return Direction.LEFT
        return None


class DirectionalGraph:
    def __init__(self):
        # Structure: {
        #   'node_uid': { Direction.UP: 'neighbor_uid', Direction.LEFT: '...' }
        # }
        self._adj = {}

    def add_node(self, uid: str):
        if uid not in self._adj:
            self._adj[uid] = {}

    def add_edge(self, u: str, v: str, direction: Direction):
        """
        Connects u to v in the specified 'direction'.
        Automatically connects v to u in the 'opposite' direction.
        Raises an error if the slot is already taken.
        """
        self.add_node(u)
        self.add_node(v)

        # 1. Check if 'u' already has a neighbor in that direction
        if direction in self._adj[u]:
            existing = self._adj[u][direction]
            if existing == v:
                return  # Connection already exists, do nothing
            raise ValueError(f"Node '{u}' already has a neighbor '{existing}' to the {direction.name}")

        # 2. Check if 'v' has space in the opposite direction
        opp_dir = direction.opposite
        if opp_dir in self._adj[v]:
            existing = self._adj[v][opp_dir]
            if existing == u:
                return
            raise ValueError(f"Node '{v}' already has a neighbor '{existing}' to the {opp_dir.name}")

        # 3. Create the bidirectional link
        self._adj[u][direction] = v
        self._adj[v][opp_dir] = u

    # --- Read/Get Methods ---

    def get_neighbor(self, uid: str, direction: Direction) -> str:
        """Returns the UID of the neighbor in a specific direction, or None."""
        if uid not in self._adj:
            raise ValueError(f"Node '{uid}' does not exist in the graph.")
        return self._adj[uid].get(direction)

    def get_all_neighbors(self, uid: str) -> dict:
        """Returns the full dictionary of directions -> neighbors."""
        return self._adj.get(uid, {}).copy()

    def __str__(self):
        result = []
        for node, neighbors in self._adj.items():
            connections = ", ".join([f"{d.name}:{n}" for d, n in neighbors.items()])
            result.append(f"{node} -> [{connections}]")
        return "\n".join(result)
