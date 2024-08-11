import pygame

from app.common import constants
from app.common import settings
from app.common.action import Action
from app.common.inputstream import InputStream
from app.events import story_event, event
from app.model.animation import Animation
from app.scenes.scene import Scene
from app.gui.frame import Frame
from app.gui.text import ScrollText


class StoryScene(Scene):
    def __init__(self):
        super().__init__(30, 30)
        
        # Logic
        self.is_textbox_visible = False
        self.scroll_text: ScrollText = None
        self.event_index = 0
        self.event_queue: list[story_event.StoryEvent] = self.get_event_queue()
        self.camera = pygame.Rect(0, 0, constants.DISPLAY_WIDTH, constants.DISPLAY_HEIGHT)
        
        self.bg = constants.BLANK_ANIMATION  # Drawn first
        self.fg = constants.BLANK_ANIMATION  # Drawn after sprites, before textbox
        self.filter = constants.BLANK_ANIMATION  #Drawn after everything (usually has alpha)
        
        # Scene Assets:
        # - Textbox
        self.textbox_frame = Frame((30, 7), 255)
        self.textbox_rect = pygame.Rect(self.textbox_frame.get_rect(topleft=(8, 128)))
        
        # - Text
        self.text_pos = pygame.Vector2(8, 128) + (12, 10)
        
    #######################
    # Define in child class
    def get_next_scene(self) -> Scene:
        return Scene()
    
    def get_event_queue(self):
        return []
    #######################
    
    @property
    def current_event(self):
        return self.event_queue[self.event_index]
    
    def process_input(self, input_stream: InputStream):
        if self.in_transition:
            return
        if self.event_index == len(self.event_queue):
            self.next_scene = self.get_next_scene()
            return
        
        kb = input_stream.keyboard
        if type(self.current_event) is story_event.ProcessInputEvent:
            if kb.is_down(settings.get_key(Action.INTERACT)):
                self.current_event.handled = True
                if self.event_index == len(self.event_queue) - 1:
                    self.next_scene = self.get_next_scene()
        elif self.scroll_text is not None and self.scroll_text.is_paused:
            if kb.is_down(settings.get_key(Action.INTERACT)):
                self.scroll_text.unpause()
    
    def update(self):
        super().update()
        self.bg.update()
        self.fg.update()
        self.filter.update()
        if self.event_index == len(self.event_queue):
            return
        # Handle events
        ev = self.current_event
        match type(ev):
            case event.SleepEvent: self.handle_sleep_event(ev)
            case story_event.TextboxMessageEvent: self.handle_textbox_message_event(ev)
            case story_event.ScreenFlashEvent: self.handle_screen_flash_event(ev)
            case story_event.SetTextboxVisibilityEvent: self.handle_set_textbox_visibility_event(ev)
            case story_event.ProcessInputEvent: self.handle_process_input_event(ev)
            case story_event.SetBackgroundEvent: self.handle_process_set_background_event(ev)
            case story_event.PanCameraEvent: self.handle_pan_camera_event(ev)
            case story_event.FadeOutEvent: self.handle_fade_out_event(ev)
            case story_event.FadeInEvent: self.handle_fade_in_event(ev)
            case story_event.SetCameraPositionEvent: self.handle_set_camera_position_event(ev)
            case story_event.SfxEvent: self.handle_sfx_event(ev)
            case _: print(f"{ev}: Handler not implemented")
    
    def render(self) -> pygame.Surface:
        surface = pygame.Surface(self.bg.render().get_size())
        surface.blit(self.bg.render(), (0, 0))
        surface.blit(self.fg.render(), (0, 0))
            
        surface = surface.subsurface(self.camera)
        
        if self.is_textbox_visible:
            surface.blit(self.textbox_frame, self.textbox_rect)
            if self.scroll_text is not None:
                surface.blit(self.scroll_text.render(), self.text_pos)
        
        surface.blit(self.filter.render(), (0, 0))
        return surface
    
    def handle_sleep_event(self, ev: event.SleepEvent):
        if ev.time > 0:
            ev.time -= 1
        else:
            self.event_index += 1
    
    def handle_textbox_message_event(self, ev: story_event.TextboxMessageEvent):
        if self.scroll_text is None and not ev.scroll_text.is_done:
            self.scroll_text = ev.scroll_text
        elif self.scroll_text is not None and not ev.scroll_text.is_done:
            self.scroll_text.update()
        elif ev.scroll_text.is_done:
            self.event_index += 1
    
    def handle_screen_flash_event(self, ev: story_event.ScreenFlashEvent):
        if ev.is_done:
            if ev.restore:
                self.filter = constants.BLANK_ANIMATION
            self.event_index += 1
            return
        
        ev.t += 1
        surface = pygame.Surface(constants.DISPLAY_SIZE)
        surface.fill(constants.WHITE)
        surface.set_alpha(ev.alpha)
        self.filter = Animation.constant(surface)
    
    def handle_set_textbox_visibility_event(self, ev: story_event.SetTextboxVisibilityEvent):
        self.is_textbox_visible = ev.is_visible
        self.event_index += 1
    
    def handle_process_input_event(self, ev: story_event.ProcessInputEvent):
        if ev.handled:
            self.scroll_text = None
            self.event_index += 1
    
    def handle_process_set_background_event(self, ev: story_event.SetBackgroundEvent):
        self.bg = ev.bg
        self.event_index += 1
    
    def handle_pan_camera_event(self, ev: story_event.PanCameraEvent):
        if ev.is_done:
            self.event_index += 1
            self.camera.topleft = ev.dest
            return
        
        self.camera.topleft = ev.start + (ev.dest - ev.start) * ev.t / ev.duration
        ev.t += 1

    def handle_fade_out_event(self, ev: story_event.FadeOutEvent):
        if ev.is_done:
            self.event_index += 1
            return
        self.alpha = ev.alpha
        ev.t += 1
    
    def handle_fade_in_event(self, ev: story_event.FadeInEvent):
        if ev.is_done:
            self.event_index += 1
            return
        self.alpha = ev.alpha
        ev.t += 1
    
    def handle_set_camera_position_event(self, ev: story_event.SetCameraPositionEvent):
        self.camera.topleft = ev.position
        self.event_index += 1
    
    def handle_sfx_event(self, ev: story_event.SfxEvent):
        ev.sfx.play(ev.loops)
        self.event_index += 1
    