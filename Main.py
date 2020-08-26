import time

from LoadGameData import *

#######
currentDungeon = "BeachCave"


# possibleDungeonList = [Dungeon for Dungeon in DungeonSpecificPokemonDict]
# i = randint(0, len(possibleDungeonList)-1)
# currentDungeon = possibleDungeonList[i]
########


def Main(DUNGEON_NAME, currentFloor, initHP):
    # Clear:
    for sprite in all_sprites:
        all_sprites.remove(sprite)

    # Build:
    # Map
    Floor = LoadDungeonObject(DUNGEON_NAME).BuildMap()

    # User
    # possibleAllyList = [ID for ID in UserSpecificPokemonDict]
    # i = randint(0, len(possibleAllyList)-1)
    # User = LoadPokemonObject(possibleAllyList[i], "User")
    User = LoadPokemonObject("025", "User")
    User.Spawn(Floor)
    if initHP:
        User.BattleInfo.Status["HP"] = initHP
    # Enemies
    possibleEnemyList = [ID for ID in DungeonSpecificPokemonDict[DUNGEON_NAME]]
    for i in range(6):  # number of enemies spawned
        j = randint(0, len(possibleEnemyList) - 1)
        enemy = LoadPokemonObject(possibleEnemyList[j], "Enemy", DUNGEON_NAME)
        # enemy = LoadPokemonObject("025", "Enemy", DUNGEON_NAME)
        enemy.Spawn(Floor)

    # MAIN LOOP###
    running = True
    direction = None
    AttackIndex = None
    motion = False
    messageToggle = False
    menuToggle = False
    timeForOneTile = TIME_FOR_ONE_TILE
    motionTimeLeft = 0
    attackTimeLeft = 0
    turnCount = 0
    REGENRATE = 2
    t = time.time()

    while running:
        # DRAWING PHASE

        if AttackIndex is not None and motionTimeLeft == 0:  # Transformations to displace coordinates: DisplayOrigin->MapOrigin
            x = display_width / 2 - User.gridPos[0] * TILESIZE
            y = display_height / 2 - User.gridPos[1] * TILESIZE
        else:
            x = display_width / 2 - User.blitPos[0]  #
            y = display_height / 2 - User.blitPos[1]  #

        display.fill(BLACK)
        Floor.DisplayMap((x, y))  # Draws Floor first
        for sprite in all_sprites:  # Draws every sprite
            sprite.Draw(x, y)
        DrawInfo(currentFloor, User)  # Draws HP bar, User level, and floor number

        MessageLog.DrawTextBox().DrawContents()
        if messageToggle:
            MessageLog.BlitOnDisplay()  # Draws Message Log
        DungeonMenu.DrawTextBox().DrawContents()
        if menuToggle:
            DungeonMenu.BlitOnDisplay()  # Draws Menu

        # GAMEPLAY PHASE
        keys = p.key.get_pressed()  # Gets all input keys from the user

        if User.turn and not motionTimeLeft and not attackTimeLeft:  # User Attack Phase
            if AttackIndex is None:
                for key in KeyPress["Attack"]:
                    if keys[key]:
                        AttackIndex = KeyPress["Attack"][key]

            if AttackIndex != None:
                steps = User.Activate(Floor, AttackIndex)  # Activates the move specified by the user input.
                if steps:
                    stepIndex = 0  # moves can have multiple effects; sets to the 0th index effect
                    targetIndex = 0  # each effect has a designated target
                    Attacker = User
                else:
                    AttackIndex = None
                old_time = time.time()
                attackTimeLeft = timeForOneTile  # Resets timer

        #################
        if User.turn and not motionTimeLeft and not attackTimeLeft:  # User Movement Phase
            if keys[p.K_LSHIFT]:  # Speed up game.
                timeForOneTile = FASTER_TIME_FOR_ONE_TILE
            else:
                timeForOneTile = TIME_FOR_ONE_TILE  # Normal Speed

            for key in KeyPress["Direction"]:  # Detects if movement is made
                if keys[key]:
                    direction = KeyPress["Direction"][key]
            if direction:  # and sets User.direction as appropriate.
                User.direction = direction
                User.currentImg = User.imageDict["Motion"][User.direction][0]
            if direction in User.PossibleDirections(Floor):
                User.MoveOnGrid(Floor, None)  # Updates the position but NOT where the sprites are blit.
                User.turn = False
                motion = True
            direction = None
        #############
        if not User.turn and not motionTimeLeft and not attackTimeLeft:  # Enemy Attack Phase
            for Enemy in all_sprites:
                if Enemy.pokeType == "Enemy" and Enemy.turn:
                    chance = True  # Chance the enemy decides to check if an attack is suitable
                    if 1 <= Enemy.DistanceToTarget(User,
                                                   Enemy.gridPos) < 2 or chance:  # If the enemy is adjacent to the user
                        Enemy.MoveInDirectionOfMinimalDistance(User, Floor, [direction for direction in
                                                                             list(KeyPress["Direction"].values()) if
                                                                             direction != (0, 0)])  # Faces user
                        Enemy.currentImg = Enemy.imageDict["Motion"][Enemy.direction][0]

                        AttackIndex = [i for i in range(5) if
                                       Enemy.BattleInfo.MoveSet[i].PP and Enemy.FilterOutOfRangeTargets(
                                           Enemy.FindPossibleTargets(Enemy.BattleInfo.MoveSet[i].TargetType[0]),
                                           Enemy.BattleInfo.MoveSet[i].Ranges[0],
                                           Enemy.BattleInfo.MoveSet[i].CutsCorners,
                                           Floor)
                                       ]
                        if AttackIndex:
                            AttackIndex = AttackIndex[randint(0, len(AttackIndex) - 1)]
                        else:
                            AttackIndex = None
                            break
                        steps = Enemy.Activate(Floor, AttackIndex)  # Then activates a move
                        if steps:
                            stepIndex = 0
                            targetIndex = 0
                            Attacker = Enemy
                        else:
                            AttackIndex = None
                        old_time = time.time()
                        attackTimeLeft = timeForOneTile  # Resets timer
                        break
        ##############
        if not User.turn and not motionTimeLeft and not attackTimeLeft:  # Enemy Movement Phase
            for sprite in all_sprites:
                if sprite.pokeType == "Enemy":
                    Enemy = sprite
                    if Enemy.turn:
                        if not 1 <= Enemy.DistanceToTarget(User, Enemy.gridPos) < 2:
                            Enemy.MoveOnGrid(Floor, User)  # Otherwise, just move the position of the enemy
                            Enemy.turn = False
                            motion = True

        #############
        if motion:
            motion = False
            old_time = time.time()
            motionTimeLeft = timeForOneTile  # Resets timer

        ##################################### ANIMATION PHASE
        if motionTimeLeft > 0:
            t = time.time() - old_time
            old_time = time.time()
            motionTimeLeft -= t  # reduce time left by change in time.
            if motionTimeLeft <= 0:
                motionTimeLeft = 0  # Time is up.

            for sprite in all_sprites:  # All sprites are animated.
                sprite.MotionAnim(motionTimeLeft, timeForOneTile)

        elif attackTimeLeft > 0:
            t = time.time() - old_time
            old_time = time.time()
            attackTimeLeft -= t  # reduce time left by change in time.
            if attackTimeLeft <= 0:
                attackTimeLeft = 0  # Time is up.

            if steps:
                Targets = steps[stepIndex]["Targets"]
                Target = Targets[targetIndex]
                Effect = steps[stepIndex]["Effect"]
                Target.DoAnim(Effect, attackTimeLeft, timeForOneTile)
                Attacker.AttackAnim(AttackIndex, attackTimeLeft, timeForOneTile)

            if attackTimeLeft == 0 and steps:
                Attacker.currentImg = Attacker.imageDict["Motion"][Attacker.direction][0]
                if targetIndex + 1 != len(steps[stepIndex]["Targets"]):
                    targetIndex += 1
                    attackTimeLeft = timeForOneTile
                elif stepIndex + 1 != len(steps):
                    stepIndex += 1
                    targetIndex = 0
                    attackTimeLeft = timeForOneTile
                else:
                    steps = []
                    targetIndex = 0
                    stepIndex = 0
                    AttackIndex = None
                    Attacker.turn = False

        ############################################## END PHASE
        if motionTimeLeft == 0 and attackTimeLeft == 0:
            if not RemoveDead():
                return False
            elif User.gridPos == Floor.StairsCoords[1]:
                return User.BattleInfo.Status["HP"]
            elif User.gridPos in Floor.TrapCoords:
                pass

            newTurn = True
            for sprite in all_sprites:
                if sprite.turn:  # If a sprite still has their turn left
                    newTurn = False  # Then it is not a new turn.
                    break
            if newTurn:  # Once everyone has used up their turn
                turnCount += 1
                for sprite in all_sprites:
                    sprite.turn = True  # it is the next turn for everyone
                    if turnCount % REGENRATE == 0 and sprite.BattleInfo.Status["Regen"] and sprite.BattleInfo.Status[
                        "HP"] < sprite.BattleInfo.Base["HP"]:
                        User.BattleInfo.Status["HP"] += 1

        p.display.update()  # Update the screen
        clock.tick(FPS)
        ################################################# MISC PHASE
        for event in p.event.get():
            if (event.type == p.QUIT) or (
                    event.type is p.KEYDOWN and event.key == p.K_ESCAPE):  # Escape of the red cross to exit
                p.quit()
                return False
            if event.type is p.KEYDOWN:
                if event.key == p.K_F11:  # F11 to toggle fullscreen
                    if display.get_flags() & p.FULLSCREEN:
                        p.display.set_mode((display_width, display_height))
                    else:
                        p.display.set_mode((display_width, display_height), p.FULLSCREEN | p.HWSURFACE | p.DOUBLEBUF)
                elif event.key == p.K_m:
                    messageToggle = not messageToggle
                elif event.key == p.K_SPACE:
                    menuToggle = not menuToggle


##################################################################

def DrawInfo(currentFloor, User):
    # FloorNo
    CoolFont("Floor " + str(currentFloor), RED, (0, 0))
    # Level
    CoolFont("Level " + str(User.BattleInfo.LVL), RED, (display_width * (0.1), 0))
    # HP
    BaseHP = User.BattleInfo.Base["HP"]
    CurrentHP = User.BattleInfo.Status["HP"]
    CoolFont("HP " + str(CurrentHP) + " of " + str(BaseHP), RED, (display_width * (0.2), 0))
    # HP BAR
    BARHEIGHT = display_height * 0.03
    BARPOS = (display_width * (0.4), 0)
    WIDTHSCALE = 1.5

    p.draw.rect(display, RED, (BARPOS[0], BARPOS[1], BaseHP * WIDTHSCALE, BARHEIGHT))
    if CurrentHP > 0:
        p.draw.rect(display, GREEN, (BARPOS[0], BARPOS[1], CurrentHP * WIDTHSCALE, BARHEIGHT))
    p.draw.rect(display, BLACK, (BARPOS[0], BARPOS[1], BaseHP * WIDTHSCALE, 2))
    p.draw.rect(display, BLACK, (BARPOS[0], BARPOS[1] + BARHEIGHT - 2, BaseHP * WIDTHSCALE, 2))
    p.draw.rect(display, WHITE, (BARPOS[0], BARPOS[1], BaseHP * WIDTHSCALE, 1))
    p.draw.rect(display, WHITE, (BARPOS[0], BARPOS[1] + BARHEIGHT - 2, BaseHP * WIDTHSCALE, 1))


def RemoveDead():
    for sprite in all_sprites:
        if sprite.BattleInfo.Status["HP"] == 0:
            # print(sprite.BattleInfo.Name,"fainted!")
            msg = sprite.BattleInfo.Name + " fainted!"
            MessageLog.Write(Text(msg).DrawText())
            all_sprites.remove(sprite)
    if "User" not in [sprite.pokeType for sprite in all_sprites]:
        return False
    else:
        return True


#######################################################################
# DUNGEON MAIN LOOP
initHP = 0
for x in range(1, 100):
    initHP = Main(currentDungeon, x, initHP)
    if not initHP:
        break
    if x == 10:
        print("YOU WIN!")

p.display.update()  # Update the screen
clock.tick(FPS)
