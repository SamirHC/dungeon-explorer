from abc import ABC, abstractmethod

from app.events.event import Event


class EventHandler(ABC):
    @abstractmethod
    def handle_event(self, event: Event):
        pass
