import scene

class SceneManager:
    def __init__(self):
        self.scenes: list[scene.Scene] = []

    def add(self, s: scene.Scene):
        self.scenes.append(s)

    def pop(self) -> scene.Scene:
        if self.scenes:
            return self.scenes.pop()

    def current_scene(self) -> scene.Scene:
        if self.scenes:
            return self.scenes[-1]
