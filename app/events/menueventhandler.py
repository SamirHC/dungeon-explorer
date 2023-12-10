from app.events.eventhandler import EventHandler
from app.events.event import Event


class MenuEventHandler(EventHandler):
    def __init__(self, menu):
        self.menu = menu

    def handle_event(event: Event):
        pass
