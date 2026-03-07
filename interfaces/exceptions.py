class GraphSourceExhausted(Exception):
    """Raised when a graph source has no more graphs to provide."""

    def __init__(self, loaded: int, requested: int):
        self.loaded = loaded
        self.requested = requested
        super().__init__(
            f"Graph source exhausted: provided {loaded} graphs, but {requested} were requested."
        )
