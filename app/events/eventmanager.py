from app.events.event import Event


class EventManager:
    def __init__(self):
        self.listeners: dict[Event, list] = {}

    def add_listener(self, event_type, listener):
        if event_type in self.listeners:
            self.listeners[event_type].append(listener)
        else:
            self.listeners[event_type] = [listener]

    def remove_listener(self, event_type, listener):
        if event_type in self.listeners and listener in self.listeners[event_type]:
            self.listeners[event_type].remove(listener)

    def dispatch_event(self, event_type, data=None):
        if event_type in self.listeners:
            for listener in self.listeners[event_type]:
                listener.handle_event(data)
