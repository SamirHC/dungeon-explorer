from app.scenes.scene import Scene
from app.scenes.story.story_scene import StoryScene
from app.events import story_event, event


class Story2(StoryScene):
    def __init__(self):
        super().__init__()
        
    def get_event_queue(self):
        return [
            
        ]

    def get_next_scene(self) -> Scene:
        from app.scenes.story.chapter1.story1 import Story1
        return Scene()
