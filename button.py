class Button:
    def __init__(self, text, blit_pos=None, effect=None):
        self.text = text
        self.blit_pos = blit_pos
        self.effect = effect

    def draw_text(self):
        self.text_surface = self.text.render(self.text, False, self.text_color)
        return self

    def trigger(self):
        pass