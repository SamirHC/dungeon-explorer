from app.scenes.scene import Scene
from app.events import story_event, event
from app.scenes.story.story_scene import StoryScene
from app.gui.scroll_text import ScrollText
from app.pokemon.pokemon_factory import user_pokemon_factory
from app.pokemon.portrait import PortraitEmotion


class Story4(StoryScene):
    def __init__(self):
        # Set beach waves bgm
        self.hero = user_pokemon_factory(0)
        self.sidekick = user_pokemon_factory(1)

        self.sidekick_msgs = iter(
            ScrollText(
                f"[C:YELLOW]{self.sidekick.base.name}[C:WHITE]: {msg}",
                with_sound=True,
                start_t=len(self.sidekick.base.name) + 2,
            )
            for msg in (
                "Wow! What a beautiful sight!",
                "When the weather's good, the\n"
                "[C:CYAN]Krabby[C:WHITE] come out at sundown to blow bubbles...",
                "All those bubbles, reflecting the\n"
                "setting of the sun off the waves...",
                "It's always beautiful.",
                "............",
                "This is where I always come\n" "when I'm feeling down on myself.",
                "But it makes me feel good to be\n" "here, like always.",
                "Coming here heals my spirits.",
                "Hey...[K]what's that?[K] What's going\n" "on over there?",
                "Waah![K] Someone has collapsed on\n" "the sand!",
                "What happened?![K] Are you OK?",
                "You're awake![K] Thank goodness!",
                "You wouldn't move at all. I was\n" "really scared for you!",
                "Do you have any idea how you\n" "ended up unconscious out here?",
                f"Anyway, I'm [C:YELLOW]{self.sidekick.base.name}[C:WHITE].[K]\n"
                "Happy to meet you!",
                "And who are you?",
                "I don't think I've seen you\n" "around before.",
                "What?[K] You say you're a human?",
                "You look like a totally normal\n"
                f"[C:LIME]{self.hero.base.name}[C:WHITE] to me!",
                "You're...[K]a little odd...",
                "Are you pulling some kind of\n" "trick on me?",
                "You're telling me the truth?",
                "OK, how about your name?[K]\n" "What's your name?",
                f"So you're named {self.hero.base.name}?",
                "OK.[K] Well, you don't seem to be a\n" "bad Pokemon, at least.",
                "Sorry that I doubted you.",
                "More and more bad Pokemon\n" "have been turning up lately, you see!",
                "A lot of Pokemon have gotten\n"
                "aggressive lately.[K] It's just not\n"
                "safe anymore...",
                "Yowch!",
                "Hey! Why'd you do that?!",
                "Wh-what?!",
                "Oh! That's...!",
                "Aaaah!",
                "...[K]Ohhh...",
                "Wh-what should I do?",
                "That's my personal treasure.\n" "It means everything to me.",
                "If I lose that...",
                "No! There's no time to waste!",
                "I have to get it back![K] Say, can\n" "you please help me?",
            )
        )
        self.hero_msgs = iter(
            ScrollText(msg)
            for msg in (
                "(..................)",
                "(...Ugh...)",
                "(Where...where am I...?)",
                "(I... I was unconscious?[K] What happened...?)",
                "(It's...it's true!)",
                f"(I've turned into a [C:LIME]{self.hero.base.name}[C:WHITE]!)",
                "(...But how did this happen?[K] I don't remember\n" "anything...)",
                "(My name?[K] That's right, my name is...)",
            )
        )

        self.zubat_msgs = iter(
            ScrollText(f"[C:CYAN]Zubat[C:WHITE]: {msg}", with_sound=True)
            for msg in (
                "Heh-heh-heh! Can't figure it out?",
                "We wanted to mess with you!\n" "Can't face up to us, can you?!",
                "That's yours, isn't it?",
                "Sorry, kiddo. We'll take that!",
                "See you around, chicken.[K]\n" "Heh-heh-heh",
            )
        )

        self.koffing_msgs = iter(
            ScrollText(f"[C:CYAN]Koffing[C:WHITE]: {msg}", with_sound=True)
            for msg in (
                "Well, I do beg your pardon.",
                "Whoa-ho-ho![K] Not gonna make a\n"
                "move to get that back?[K] What's the matter?[K]\n"
                "Too scared?",
                "I didn't expect that you'd be such\n" "a big coward!",
                "Come on. Let's get out of here.",
            )
        )

        super().__init__()

    def get_event_queue(self):
        return [
            story_event.SetTextboxVisibilityEvent(True),
            story_event.SetPortrait(
                self.sidekick, PortraitEmotion.INSPIRED, left=False
            ),
            story_event.MessageEvent(next(self.sidekick_msgs)),
            story_event.ProcessInputEvent(),
            story_event.SetPortrait(None, None),
            story_event.SetTextboxVisibilityEvent(False),
            event.SleepEvent(10),
            story_event.SetPortrait(self.sidekick, PortraitEmotion.NORMAL, left=False),
            story_event.SetTextboxVisibilityEvent(True),
            story_event.MessageEvent(next(self.sidekick_msgs)),
            story_event.ProcessInputEvent(),
            story_event.MessageEvent(next(self.sidekick_msgs)),
            story_event.ProcessInputEvent(),
            story_event.MessageEvent(next(self.sidekick_msgs)),
            story_event.ProcessInputEvent(),
            story_event.SetPortrait(None, None),
            story_event.SetTextboxVisibilityEvent(False),
            event.SleepEvent(10),
            story_event.SetTextboxVisibilityEvent(True),
            story_event.SetPortrait(self.sidekick, PortraitEmotion.NORMAL, left=False),
            story_event.MessageEvent(next(self.sidekick_msgs)),
            story_event.ProcessInputEvent(),
            story_event.MessageEvent(next(self.sidekick_msgs)),
            story_event.ProcessInputEvent(),
            story_event.MessageEvent(next(self.sidekick_msgs)),
            story_event.ProcessInputEvent(),
            story_event.MessageEvent(next(self.sidekick_msgs)),
            story_event.ProcessInputEvent(),
            story_event.SetPortrait(None, None),
            story_event.SetTextboxVisibilityEvent(False),
            event.SleepEvent(10),
            story_event.SetTextboxVisibilityEvent(True),
            story_event.SetPortrait(self.sidekick, PortraitEmotion.NORMAL, left=False),
            story_event.MessageEvent(next(self.sidekick_msgs)),
            story_event.ProcessInputEvent(),
            story_event.SetPortrait(None, None),
            story_event.SetTextboxVisibilityEvent(False),
            event.SleepEvent(10),
            story_event.SetTextboxVisibilityEvent(True),
            story_event.SetPortrait(
                self.sidekick, PortraitEmotion.SURPRISED, left=False
            ),
            story_event.MessageEvent(next(self.sidekick_msgs)),
            story_event.ProcessInputEvent(),
            story_event.SetPortrait(None, None),
            story_event.SetTextboxVisibilityEvent(False),
            event.SleepEvent(10),
            story_event.SetTextboxVisibilityEvent(True),
            story_event.SetPortrait(
                self.sidekick, PortraitEmotion.SURPRISED, left=False
            ),
            story_event.MessageEvent(next(self.sidekick_msgs)),
            story_event.ProcessInputEvent(),
            story_event.SetPortrait(None, None),
            story_event.SetTextboxVisibilityEvent(False),
            event.SleepEvent(10),
            story_event.SetTextboxVisibilityEvent(True),
            story_event.SetPortrait(self.hero, PortraitEmotion.PAIN),
            story_event.MessageEvent(next(self.hero_msgs)),
            story_event.ProcessInputEvent(),
            story_event.MessageEvent(next(self.hero_msgs)),
            story_event.ProcessInputEvent(),
            story_event.SetPortrait(None, None),
            story_event.SetTextboxVisibilityEvent(False),
            event.SleepEvent(10),
            story_event.SetTextboxVisibilityEvent(True),
            story_event.SetPortrait(self.sidekick, PortraitEmotion.NORMAL, left=False),
            story_event.MessageEvent(next(self.sidekick_msgs)),
            story_event.ProcessInputEvent(),
            story_event.SetPortrait(None, None),
            story_event.SetTextboxVisibilityEvent(False),
            event.SleepEvent(10),
            story_event.SetTextboxVisibilityEvent(True),
            story_event.SetPortrait(self.hero, PortraitEmotion.NORMAL),
            story_event.MessageEvent(next(self.hero_msgs)),
            story_event.ProcessInputEvent(),
            story_event.SetPortrait(None, None),
            story_event.SetTextboxVisibilityEvent(False),
            event.SleepEvent(10),
            story_event.SetTextboxVisibilityEvent(True),
            story_event.SetPortrait(self.sidekick, PortraitEmotion.NORMAL, left=False),
            story_event.MessageEvent(next(self.sidekick_msgs)),
            story_event.ProcessInputEvent(),
            story_event.MessageEvent(next(self.sidekick_msgs)),
            story_event.ProcessInputEvent(),
            story_event.SetPortrait(None, None),
            story_event.SetTextboxVisibilityEvent(False),
            event.SleepEvent(10),
            story_event.SetTextboxVisibilityEvent(True),
            story_event.SetPortrait(self.hero, PortraitEmotion.NORMAL),
            story_event.MessageEvent(next(self.hero_msgs)),
            story_event.ProcessInputEvent(),
            story_event.SetPortrait(None, None),
            story_event.SetTextboxVisibilityEvent(False),
            event.SleepEvent(10),
            story_event.SetTextboxVisibilityEvent(True),
            story_event.SetPortrait(self.sidekick, PortraitEmotion.NORMAL, left=False),
            story_event.MessageEvent(next(self.sidekick_msgs)),
            story_event.ProcessInputEvent(),
            story_event.MessageEvent(next(self.sidekick_msgs)),
            story_event.ProcessInputEvent(),
            story_event.MessageEvent(next(self.sidekick_msgs)),
            story_event.ProcessInputEvent(),
            story_event.SetPortrait(None, None),
            story_event.SetTextboxVisibilityEvent(False),
            event.SleepEvent(10),
            story_event.SetTextboxVisibilityEvent(True),
            story_event.SetPortrait(
                self.sidekick, PortraitEmotion.SURPRISED, left=False
            ),
            story_event.MessageEvent(next(self.sidekick_msgs)),
            story_event.ProcessInputEvent(),
            story_event.MessageEvent(next(self.sidekick_msgs)),
            story_event.ProcessInputEvent(),
            story_event.SetPortrait(None, None),
            story_event.SetTextboxVisibilityEvent(False),
            event.SleepEvent(10),
            story_event.SetTextboxVisibilityEvent(True),
            story_event.SetPortrait(self.hero, PortraitEmotion.SURPRISED),
            story_event.MessageEvent(next(self.hero_msgs)),
            story_event.ProcessInputEvent(),
            story_event.MessageEvent(next(self.hero_msgs)),
            story_event.ProcessInputEvent(),
            story_event.MessageEvent(next(self.hero_msgs)),
            story_event.ProcessInputEvent(),
            story_event.SetPortrait(None, None),
            story_event.SetTextboxVisibilityEvent(False),
            event.SleepEvent(10),
            story_event.SetTextboxVisibilityEvent(True),
            story_event.MessageEvent(next(self.sidekick_msgs)),
            story_event.ProcessInputEvent(),
            story_event.MessageEvent(next(self.sidekick_msgs)),
            story_event.ProcessInputEvent(),
            story_event.MessageEvent(next(self.sidekick_msgs)),
            story_event.ProcessInputEvent(),
            story_event.MessageEvent(next(self.sidekick_msgs)),
            story_event.ProcessInputEvent(),
            story_event.MessageEvent(next(self.hero_msgs)),
            story_event.ProcessInputEvent(),
            story_event.MessageEvent(next(self.sidekick_msgs)),
            story_event.ProcessInputEvent(),
            story_event.MessageEvent(next(self.sidekick_msgs)),
            story_event.ProcessInputEvent(),
            story_event.MessageEvent(next(self.sidekick_msgs)),
            story_event.ProcessInputEvent(),
            story_event.MessageEvent(next(self.sidekick_msgs)),
            story_event.ProcessInputEvent(),
            story_event.MessageEvent(next(self.sidekick_msgs)),
            story_event.ProcessInputEvent(),
            story_event.MessageEvent(next(self.sidekick_msgs)),
            story_event.ProcessInputEvent(),
            story_event.MessageEvent(next(self.koffing_msgs)),
            story_event.ProcessInputEvent(),
            story_event.MessageEvent(next(self.sidekick_msgs)),
            story_event.ProcessInputEvent(),
            story_event.MessageEvent(next(self.zubat_msgs)),
            story_event.ProcessInputEvent(),
            story_event.MessageEvent(next(self.zubat_msgs)),
            story_event.ProcessInputEvent(),
            story_event.MessageEvent(next(self.sidekick_msgs)),
            story_event.ProcessInputEvent(),
            story_event.MessageEvent(next(self.zubat_msgs)),
            story_event.ProcessInputEvent(),
            story_event.MessageEvent(next(self.sidekick_msgs)),
            story_event.ProcessInputEvent(),
            story_event.MessageEvent(next(self.zubat_msgs)),
            story_event.ProcessInputEvent(),
            story_event.MessageEvent(next(self.sidekick_msgs)),
            story_event.ProcessInputEvent(),
            story_event.MessageEvent(next(self.koffing_msgs)),
            story_event.ProcessInputEvent(),
            story_event.MessageEvent(next(self.koffing_msgs)),
            story_event.ProcessInputEvent(),
            story_event.MessageEvent(next(self.koffing_msgs)),
            story_event.ProcessInputEvent(),
            story_event.MessageEvent(next(self.zubat_msgs)),
            story_event.ProcessInputEvent(),
            story_event.MessageEvent(next(self.sidekick_msgs)),
            story_event.ProcessInputEvent(),
            story_event.MessageEvent(next(self.sidekick_msgs)),
            story_event.ProcessInputEvent(),
            story_event.MessageEvent(next(self.sidekick_msgs)),
            story_event.ProcessInputEvent(),
            story_event.MessageEvent(next(self.sidekick_msgs)),
            story_event.ProcessInputEvent(),
            story_event.MessageEvent(next(self.sidekick_msgs)),
            story_event.ProcessInputEvent(),
            story_event.MessageEvent(next(self.sidekick_msgs)),
            story_event.ProcessInputEvent(),
        ]

    def get_next_scene(self) -> Scene:
        from app.scenes.scene import Scene

        return Scene()
