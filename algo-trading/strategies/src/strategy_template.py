class StrategyTemplate:
    def __init__(self, parameters):
        self.parameters = parameters

    def generate_signal(self, data):
        raise NotImplementedError("Subclass must implement abstract method")
