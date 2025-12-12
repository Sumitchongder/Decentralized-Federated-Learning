class EventListener:
    """
    Simulated blockchain event listener for FL updates
    """
    def __init__(self):
        self.listeners = []

    def register_listener(self, callback):
        self.listeners.append(callback)

    def trigger_event(self, event_type, data):
        for callback in self.listeners:
            callback(event_type, data)
