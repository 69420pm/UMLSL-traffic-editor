class TrafficSnapshot:
    """Root data object (The 'Document')."""
    def __init__(self):
        self.roads: Dict[str, Road] = {}
        self.cars: Dict[str, Car] = {}
        self.queries: List['UMLSLQuery'] = []
        self.settings: SimulationSettings = SimulationSettings()