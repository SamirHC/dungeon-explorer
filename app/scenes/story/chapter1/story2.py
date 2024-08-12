from app.scenes.scene import Scene
from app.scenes.story.story_scene import StoryScene


class Story2(StoryScene):
    def __init__(self):
        super().__init__()

    def get_event_queue(self):
        return []

    def get_next_scene(self) -> Scene:
        return Scene()
