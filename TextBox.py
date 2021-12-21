from constants import *

class TextBox:
    def __init__(self, x, y, w, h, border_colors, max_lines, contents=None, text_box_surface=None, pointing_at=None):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.border_colors = border_colors
        self.max_lines = max_lines
        self.contents = contents
        self.text_box_surface = text_box_surface
        self.pointing_at = pointing_at

    def draw_text_box(self):
        width = self.w * display_width
        height = self.h * display_height  # creates semi-transparent black surface
        self.text_box_surface = p.Surface((width, height))
        self.text_box_surface.set_alpha(180)
        self.text_box_surface.fill(BLACK)
        #borders
        border_thickness = 3
        p.draw.rect(self.text_box_surface, self.border_colors[0], (0, 0, width, border_thickness))  # Top
        p.draw.rect(self.text_box_surface, self.border_colors[0], (0, height-border_thickness, width, border_thickness))  # Bottom
        p.draw.rect(self.text_box_surface, self.border_colors[0], (0, 0, border_thickness, height))  # Left
        p.draw.rect(self.text_box_surface, self.border_colors[0], (width-border_thickness, 0, border_thickness, height-border_thickness))  # Right

        return self
        
    def draw_contents(self):
        x_gap = 5
        y_gap = 5
        spacing = 36
        i = 0
        while len(self.contents)>self.max_lines:
            del self.contents[0]
        for i in range(len(self.contents)):
            x_pos = x_gap
            y_pos = y_gap + spacing * i
            image = self.contents[::-1][i].text_surface
            self.text_box_surface.blit(image, (x_pos, y_pos))

    def blit_on_display(self):
        x_pos = self.x * display_width
        y_pos = self.y * display_height
        display.blit(self.text_box_surface, (x_pos, y_pos))

    def write(self, text):
        self.contents.append(text)
            
class Button:
    def __init__(self, text, blit_pos=None, effect=None, text_color=WHITE, text_surface=None):
        self.text = text
        self.blit_pos = blit_pos
        self.effect = effect
        self.text_color = text_color
        self.text_surface = text_surface

    def draw_text(self):
        self.text_surface = FONT.render(self.text, False, self.text_color)
        return self

    def trigger(self):
        pass

class Text:
    def __init__(self, text, text_color=WHITE, text_surface=None):
        self.text = text
        self.text_color = text_color
        self.text_surface = text_surface

    def draw_text(self):
        self.text_surface = FONT.render(self.text, False, self.text_color)
        return self


message_log = TextBox(0.0275, 0.7, 0.95, 0.275, [BORDER_BLUE_1,BORDER_BLUE_2], 5, [])
dungeon_menu = TextBox(0.0275,0.05, 0.4, 0.625, [BORDER_BLUE_1,BORDER_BLUE_2], 9, [Button("Exit").draw_text(),Button("Options").draw_text(),Button("Team").draw_text(),Button("Inventory").draw_text(),Button("Moves").draw_text()])




