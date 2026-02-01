class UndirectedGraph:
    def __init__(self):
        # Core storage: A dictionary where Key = Node UID, Value = Set of Neighbor UIDs
        self._adj = dict[str, set[str]]()

    # --- Write Methods ---

    def add_node(self, uid: str):
        """Adds a node to the graph if it doesn't already exist."""
        if uid not in self._adj:
            self._adj[uid] = set()

    def add_edge(self, u: str, v: str):
        """Adds an undirected edge between u and v. Creates nodes if missing."""
        # Ensure both nodes exist first
        self.add_node(u)
        self.add_node(v)

        # Add the connection in BOTH directions (Symmetry)
        self._adj[u].add(v)
        self._adj[v].add(u)

    def remove_edge(self, u: str, v: str):
        """Removes the connection between u and v."""
        if u in self._adj and v in self._adj[u]:
            self._adj[u].remove(v)
        if v in self._adj and u in self._adj[v]:
            self._adj[v].remove(u)

    # --- Read/Get Methods ---

    def get_neighbors(self, uid: str) -> set:
        """Returns a set of all UIDs connected to the given node."""
        # We return a copy so the user can't accidentally modify the internal graph
        return self._adj.get(uid, set()).copy()

    def has_edge(self, u: str, v: str) -> bool:
        """Checks if an edge exists between u and v."""
        return u in self._adj and v in self._adj[u]

    def get_all_nodes(self) -> list:
        """Returns a list of all node UIDs."""
        return list(self._adj.keys())

    def get_all_edges(self) -> list:
        """
        Returns a list of unique edges as tuples.
        Because the graph is undirected, (A, B) and (B, A) are treated as the same edge.
        """
        edges = []
        seen_pairs = set()

        for u in self._adj:
            for v in self._adj[u]:
                # Sort the pair to ensure (A, B) is treated same as (B, A)
                pair = tuple(sorted((u, v)))

                if pair not in seen_pairs:
                    edges.append(pair)
                    seen_pairs.add(pair)

        return edges

    def __str__(self):
        return f"Graph with {len(self._adj)} nodes and {len(self.get_all_edges())} edges."
