import random

from app.common import utils
from app.common.direction import Direction
import app.move.move_effect_helpers as eff
from app.events import event, game_event
from app.pokemon.pokemon import Pokemon
from app.pokemon.stat import Stat
from app.pokemon.status_effect import StatusEffect
from app.pokemon.animation_id import AnimationId
from app.dungeon import target_getter
from app.move import damage_mechanics
from app.common import text
from app.dungeon.weather import Weather


# Regular Attack
def move_0(ev: game_event.BattleSystemEvent):
    def _regular_attack_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _regular_attack_effect))
    return events


# Iron Tail
def move_1(ev: game_event.BattleSystemEvent):
    def _iron_tail_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        events = eff.get_basic_attack_events(ev, defender)
        if utils.is_success(30):
            events.append(game_event.StatStageChangeEvent(defender, Stat.DEFENSE, -1))
        return events

    events = []
    events.extend(eff.get_attacker_move_animation_events(ev))
    events.extend(eff.get_events_on_all_targets(ev, _iron_tail_effect))
    return events


# Ice Ball
def move_2(ev: game_event.BattleSystemEvent):
    HIT_MULTIPLIER = 1.5

    def _ice_ball_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        damage = damage_mechanics.calculate_damage(
            ev.dungeon, ev.attacker, defender, ev.move, ev.kwargs["multiplier"]
        )
        events = eff.get_damage_events(ev, defender, damage)
        return events

    if not ev.kwargs:
        ev.kwargs["multiplier"] = 1
        ev.kwargs["iterations"] = 1

    events = []
    events += eff.get_attacker_move_animation_events(ev)
    events += eff.get_events_on_all_targets(ev, _ice_ball_effect)
    if (
        any(isinstance(e, game_event.DamageEvent) for e in events)
        and ev.kwargs["iterations"] < 5
    ):
        ev.kwargs["iterations"] += 1
        ev.kwargs["multiplier"] *= HIT_MULTIPLIER
        events.append(ev)

    return events


# Yawn
def move_3(ev: game_event.BattleSystemEvent):
    def _yawn_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        tb = (
            text.TextBuilder()
            .set_shadow(True)
            .set_color(defender.name_color)
            .write(defender.data.name)
            .set_color(text.WHITE)
        )
        if defender.status.has_status_effect(StatusEffect.YAWNING):
            tb.write(" is already yawning!")
        elif defender.status.is_asleep():
            tb.write(" is already asleep!")
        else:
            tb.write(" yawned!")
            defender.status.afflict(StatusEffect.YAWNING, ev.dungeon.turns.value + 3)

        events = []
        events.append(game_event.LogEvent(tb.build().render()))
        events.append(event.SleepEvent(20))
        return events

    events = []
    events += eff.get_attacker_move_animation_events(ev)
    events += eff.get_events_on_all_targets(ev, _yawn_effect)
    return events


# Lovely Kiss
def move_4(ev: game_event.BattleSystemEvent):
    def _lovely_kiss_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_asleep_events(ev.dungeon, defender)

    events = []
    events += eff.get_attacker_move_animation_events(ev)
    events += eff.get_events_on_all_targets(ev, _lovely_kiss_effect)
    return events


# Nightmare
def move_5(ev: game_event.BattleSystemEvent):
    def _nightmare_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        tb = (
            text.TextBuilder()
            .set_shadow(True)
            .set_color(defender.name_color)
            .write(defender.data.name)
            .set_color(text.WHITE)
        )
        if not defender.status.has_status_effect(StatusEffect.NIGHTMARE):
            # Overrides any other sleep status conditions
            defender.status.clear_affliction(StatusEffect.ASLEEP)
            defender.status.clear_affliction(StatusEffect.NAPPING)
            defender.status.clear_affliction(StatusEffect.YAWNING)
            defender.status.afflict(
                StatusEffect.NIGHTMARE, ev.dungeon.turns.value + random.randint(4, 7)
            )
            tb.write(" is caught in a nightmare!")
        else:
            tb.write(" is already having a nightmare!")

        events = []
        events.append(game_event.SetAnimationEvent(defender, AnimationId.SLEEP, True))
        events.append(game_event.LogEvent(tb.build().render()))
        events.append(event.SleepEvent(20))
        return events

    events = []
    events += eff.get_attacker_move_animation_events(ev)
    events += eff.get_events_on_all_targets(ev, _nightmare_effect)
    return events


# Morning Sun
def move_6(ev: game_event.BattleSystemEvent):
    def _morning_sun_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        SWITCHER = {
            Weather.CLEAR: 50,
            Weather.CLOUDY: 30,
            Weather.FOG: 10,
            Weather.HAIL: 10,
            Weather.RAINY: 10,
            Weather.SANDSTORM: 20,
            Weather.SNOW: 1,
            Weather.SUNNY: 80,
        }
        heal_amount = SWITCHER.get(ev.dungeon.floor.status.weather, 0)
        return [game_event.HealEvent(defender, heal_amount)]

    events = []
    events += eff.get_attacker_move_animation_events(ev)
    events += eff.get_events_on_all_targets(ev, _morning_sun_effect)
    return events


# Vital Throw
def move_7(ev: game_event.BattleSystemEvent):
    def _vital_throw_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        tb = (
            text.TextBuilder()
            .set_shadow(True)
            .set_color(defender.name_color)
            .write(defender.data.name)
            .set_color(text.WHITE)
        )
        if defender.status.has_status_effect(StatusEffect.VITAL_THROW):
            tb.write(" is already ready with its\nVital Throw!")
        else:
            tb.write(" readied its Vital Throw!")
            defender.status.afflict(
                StatusEffect.VITAL_THROW, ev.dungeon.turns.value + 18
            )

        events = []
        events.append(game_event.LogEvent(tb.build().render()))
        events.append(event.SleepEvent(20))
        return events

    events = []
    events += eff.get_attacker_move_animation_events(ev)
    events += eff.get_events_on_all_targets(ev, _vital_throw_effect)
    return events


# Dig
def move_8(ev: game_event.BattleSystemEvent):
    def _dig_effect(ev: game_event.BattleSystemEvent):
        tb = text.TextBuilder().set_shadow(True)
        if ev.dungeon.tileset.underwater:
            tb.set_color(text.WHITE).write(" It can only be used on the ground!")
        else:
            (
                tb.set_shadow(True)
                .set_color(ev.attacker.name_color)
                .write(ev.attacker.data.name)
                .set_color(text.WHITE)
                .write(" burrowed underground!")
            )
            ev.attacker.status.afflict(StatusEffect.DIGGING, ev.dungeon.turns.value + 1)

        events = []
        events.append(game_event.LogEvent(tb.build().render()))
        events.append(event.SleepEvent(20))
        return events

    events = []
    events += eff.get_attacker_move_animation_events(ev)
    events += _dig_effect(ev)
    return events


# Thrash
def move_9(ev: game_event.BattleSystemEvent):
    def _thrash_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return eff.get_basic_attack_events(ev, defender)

    if not ev.kwargs:
        ev.kwargs["direction"] = ev.attacker.direction
        ev.kwargs["iterations"] = 0

    events = []
    if ev.kwargs["iterations"] < 3:
        ev.kwargs["iterations"] += 1
        ev.attacker.direction = random.choice(list(Direction))
        events += eff.get_attacker_move_animation_events(ev)
        events += eff.get_events_on_all_targets(ev, _thrash_effect)
        events.append(ev)
    else:
        ev.attacker.direction = ev.kwargs["direction"]
        events.append(event.SleepEvent(20))

    return events


# Sweet Scent
def move_10(ev: game_event.BattleSystemEvent):
    def _sweet_scent_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return [game_event.StatStageChangeEvent(defender, Stat.EVASION, -1)]

    events = []
    events += eff.get_attacker_move_animation_events(ev)
    events += eff.get_events_on_all_targets(ev, _sweet_scent_effect)
    return events


# Charm
def move_11(ev: game_event.BattleSystemEvent):
    def _charm_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        return [game_event.StatDivideEvent(defender, Stat.ATTACK, 1)]

    events = []
    events += eff.get_attacker_move_animation_events(ev)
    events += eff.get_events_on_all_targets(ev, _charm_effect)
    return events


# Rain Dance
def move_12(ev: game_event.BattleSystemEvent):
    events = []
    events += eff.get_attacker_move_animation_events(ev)
    events.append(game_event.SetWeatherEvent(Weather.RAINY))
    return events


# Confuse Ray
def move_13(ev: game_event.BattleSystemEvent):
    def _confuse_ray_effect(ev: game_event.BattleSystemEvent, defender: Pokemon):
        defender.status.afflict(StatusEffect.CONFUSED, ev.dungeon.turns.value + random.randint(7, 12))
        return eff.get_confusion_events(defender)
    events = []
    events += eff.get_attacker_move_animation_events(ev)
    events += eff.get_events_on_all_targets(ev, _confuse_ray_effect)
    return events
"""
14	Hail
15	Aromatherapy
16	Bubble
17	Encore
18	Cut
19	Rage
20	Super Fang
21	Pain Split
22	Torment
23	String Shot
24	Swagger
25	Snore
26	Heal Bell
27	Screech
28	Rock Throw
29	Rock Smash
30	Rock Slide
31	Weather Ball
32	Whirlpool
33	Fake Tears
34	Sing
35	Spite
36	Air Cutter
37	SmokeScreen
38	Pursuit
39	DoubleSlap
40	Mirror Move
41	Overheat
42	Aurora Beam
43	Memento
44	Octazooka
45	Flatter
46	Astonish
47	Will-O-Wisp
48	Return
49	Grudge
50	Strength
51	Counter
52	Flame Wheel
53	Flamethrower
54	Odor Sleuth
55	Sharpen
56	Double Team
57	Gust
58	Harden
59	Disable
60	Razor Wind
61	Bide
62	Crunch
63	Bite
64	Thunder
65	ThunderPunch
66	Endeavor
67	Facade
68	Karate Chop
69	Clamp
70	Withdraw
71	Constrict
72	Brick Break
73	Rock Tomb
74	Focus Energy
75	Focus Punch
76	Giga Drain
77	Reversal
78	SmellingSalt
79	Spore
80	Leech Life
81	Slash
82	Silver Wind
83	Metal Sound
84	GrassWhistle
85	Tickle
86	Spider Web
87	Crabhammer
88	Haze
89	Mean Look
90	Cross Chop
91	Outrage
92	Low Kick
93	AncientPower
94	Synthesis
95	Agility
96	Rapid Spin
97	Icy Wind
98	Mind Reader
99	Cosmic Power
100	Sky Attack
101	Powder Snow
102	Follow Me
103	Meteor Mash
104	Endure
105	Rollout
106	Scary Face
107	Psybeam
108	Psywave
109	Psychic
110	Psycho Boost
111	Hypnosis
112	Uproar
113	Water Spout
114	Signal Beam
115	Psych Up
116	Submission
117	Recover
118	Earthquake
119	Nature Power
120	Lick
121	Flail
122	Tail Whip
123	Selfdestruct
124	Stun Spore
125	Bind
126	Shadow Punch
127	Shadow Ball
128	Charge
129	Thunderbolt
130	Mist
131	Fissure
132	ExtremeSpeed
133	Extrasensory
134	Safeguard
135	Absorb
136	Sky Uppercut
137	Skill Swap
138	Sketch
139	Headbutt
140	Double-Edge
141	Sandstorm
142	Sand-Attack
143	Sand Tomb
144	Spark
145	Swift
146	Kinesis
147	Smog
148	Growth
149	Sacred Fire
150	Sheer Cold
151	SolarBeam
152	SonicBoom
153	Fly
154	Tackle
155	Explosion
156	Dive
157	Fire Blast
158	Waterfall
159	Muddy Water
160	Stockpile
161	Slam
162	Twister
163	Bullet Seed
164	Twineedle
165	Softboiled
166	Egg Bomb
167	Faint Attack
168	Barrage
169	Minimize
170	Seismic Toss
171	Supersonic
172	Taunt
173	Moonlight
174	Peck
175	Arm Thrust
176	Horn Attack
177	Horn Drill
178	Wing Attack
179	Aerial Ace
180	Icicle Spear
181	Swords Dance
182	Vine Whip
183	Conversion
184	Conversion 2
185	Helping Hand
186	Iron Defense
187	Teleport
188	ThunderShock
189	Shock Wave
190	Quick Attack
191	Sweet Kiss
192	Thunder Wave
193	Zap Cannon
194	Block
195	Howl
196	Poison Gas
197	Toxic
198	Poison Fang
199	PoisonPowder
200	Poison Sting
201	Spike Cannon
202	Acid Armor
203	Take Down
204	Jump Kick
205	Bounce
206	Hi Jump Kick
207	Tri Attack
208	Dragon Claw
209	Trick
210	Triple Kick
211	Drill Peck
212	Mud Sport
213	Mud-Slap
214	Thief
215	Amnesia
216	Night Shade
217	Growl
218	Slack Off
219	Surf
220	Role Play
221	Needle Arm
222	Double Kick
223	Sunny Day
224	Leer
225	Wish
226	Fake Out
227	Sleep Talk
228	Pay Day
229	Assist
230	Heat Wave
231	Sleep Powder
232	Rest
233	Ingrain
234	Confusion
235	Body Slam
236	Swallow
237	Curse
238	Frenzy Plant
239	Hydro Cannon
240	Hydro Pump
241	Hyper Voice
242	Hyper Beam
243	Superpower
244	Steel Wing
245	Spit Up
246	DynamicPunch
247	Guillotine
248	ViceGrip
249	Knock Off
250	Pound
251	Razor Leaf
252	Baton Pass
253	Petal Dance
254	Splash
255	BubbleBeam
256	Doom Desire
257	Belly Drum
258	Barrier
259	Light Screen
260	Scratch
261	Hyper Fang
262	Ember
263	Secret Power
264	Dizzy Punch
265	Bulk Up
266	Imprison
267	FeatherDance
268	Whirlwind
269	Beat Up
270	Blizzard
271	Stomp
272	Blast Burn
273	Flash
274	Teeter Dance
275	Crush Claw
276	Blaze Kick
277	Present
278	Eruption
279	Sludge
280	Sludge Bomb
281	Glare
282	Transform
283	Poison Tail
284	Roar
285	Bone Rush
286	Camouflage
287	Covet
288	Tail Glow
289	Bone Club
290	Bonemerang
291	Fire Spin
292	Fire Punch
293	Perish Song
294	Wrap
295	Spikes
296	Magnitude
297	Magical Leaf
298	Magic Coat
299	Mud Shot
300	Mach Punch
301	Protect
302	Defense Curl
303	Rolling Kick
304	Substitute
305	Detect
306	Pin Missile
307	Water Sport
308	Water Gun
309	Mist Ball
310	Water Pulse
311	Fury Attack
312	Fury Swipes
313	Destiny Bond
314	False Swipe
315	Foresight
316	Mirror Coat
317	Future Sight
318	Milk Drink
319	Calm Mind
320	Mega Drain
321	Mega Kick
322	Mega Punch
323	Megahorn
324	Hidden Power
325	Metal Claw
326	Attract
327	Mimic
328	Frustration
329	Leech Seed
330	Metronome
331	Dream Eater
332	Acid
333	Meditate
334	Snatch
335	Luster Purge
336	Leaf Blade
337	Recycle
338	Reflect
339	Refresh
340	Revenge
341	Dragon Rage
342	DragonBreath
343	Dragon Dance
344	Ice Punch
345	Ice Beam
346	Fury Cutter
347	Comet Punch
348	Skull Bash
349	Lock-On
350	Rock Blast
351	Cotton Spore
352	Struggle
353	Aeroblast
354	Volt Tackle
355	regular attack
360	Wide Slash
394	Vacuum-Cut
430	Hammer Arm
431	Iron Head
432	Aqua Jet
433	Aqua Tail
434	Aqua Ring
435	Spacial Rend
436	Dark Pulse
437	Ominous Wind
438	Gastro Acid
439	Healing Wish
440	Close Combat
441	Wood Hammer
442	Air Slash
443	Energy Ball
444	Tailwind
445	Punishment
446	Chatter
447	Lucky Chant
448	Guard Swap
449	Heal Order
450	Heal Block
451	Shadow Sneak
452	Thunder Fang
453	Rock Wrecker
454	Focus Blast
455	Giga Impact
456	Defog
457	Trump Card
458	Grass Knot
459	Cross Poison
460	Attack Order
461	Ice Fang
462	Ice Shard
463	Psycho Cut
464	Psycho Shift
465	Me First
466	Embargo
467	$$$ (Judgment)
468	Seed Flare
469	Brine
470	X-Scissor
471	Natural Gift
472	Payback
473	Zen Headbutt
474	Wring Out
475	Gyro Ball
476	Shadow Claw
477	Shadow Force
478	Gravity
479	Vacuum Wave
480	Stealth Rock
481	Stone Edge
482	Switcheroo
483	Dark Void
484	Earth Power
485	Gunk Shot
486	Seed Bomb
487	Double Hit
488	Assurance
489	Charge Beam
490	Pluck
491	Night Slash
492	Acupressure
493	Magnet Rise
494	Roar of Time
495	Poison Jab
496	Toxic Spikes
497	Last Resort
498	Dragon Rush
499	Trick Room
500	Drain Punch
501	Mud Bomb
502	U-turn
503	Fling
504	Worry Seed
505	Crush Grip
506	Heart Swap
507	Force Palm
508	Aura Sphere
509	Roost
510	Bullet Punch
511	Power Whip
512	Power Gem
513	Power Swap
514	Power Trick
515	Sucker Punch
516	Feint
517	Flare Blitz
518	Brave Bird
519	Lava Plume
520	Defend Order
521	Discharge
522	Fire Fang
523	Magnet Bomb
524	Magma Storm
525	Copycat
526	Lunar Dance
527	Mirror Shot
528	Miracle Eye
529	Bug Bite
530	Bug Buzz
531	Wake-Up Slap
532	Metal Burst
533	Head Smash
534	Captivate
535	Avalanche
536	Flash Cannon
537	Leaf Storm
538	Draco Meteor
539	Dragon Pulse
540	Rock Polish
541	Rock Climb
542	Nasty Plot
"""


dispatcher = {i: globals().get(f"move_{i}", move_0) for i in range(321)}


def get_events_from_move(ev: game_event.BattleSystemEvent):
    return dispatcher.get(ev.move.move_id, dispatcher[0])(ev)
