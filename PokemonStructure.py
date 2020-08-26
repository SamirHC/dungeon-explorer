import math

from DamageChart import StageDict, DamageDict
from LoadImages import StatsAnimDict
from TextBox import *

all_sprites = p.sprite.Group()


class Pokemon(p.sprite.Sprite):  # pokeType {User, Teammate, Enemy, Other..}
    def __init__(self, imageDict, currentImg=None, turn=True, pokeType=None, gridPos=None, blitPos=None,
                 direction=(0, 1), BattleInfo=None):
        super().__init__()
        self.imageDict = imageDict
        self.currentImg = currentImg
        self.turn = turn
        self.pokeType = pokeType
        self.gridPos = gridPos
        self.blitPos = blitPos
        self.direction = direction
        self.BattleInfo = BattleInfo
        for imgType in self.imageDict:
            for direction in self.imageDict[imgType]:
                for img in self.imageDict[imgType][direction]:
                    img.set_colorkey(TRANS)

    def Spawn(self, Map):
        while True:
            valid = True
            i = randint(0, len(sum(Map.RoomCoords, [])) - 1)
            for s in all_sprites:
                if s.gridPos == sum(Map.RoomCoords, [])[i]:
                    valid = False  # If a pokemon already occupies that space
            if valid:
                break

        self.gridPos = sum(Map.RoomCoords, [])[i]
        self.blitPos = [self.gridPos[0] * TILESIZE, self.gridPos[1] * TILESIZE]
        all_sprites.add(self)

    def MoveOnGrid(self, Map, Target):
        PossibleDirectionsList = self.PossibleDirections(Map)
        self.MoveInDirectionOfMinimalDistance(Target, Map, PossibleDirectionsList)

        x = self.gridPos[0] + self.direction[0]
        y = self.gridPos[1] + self.direction[1]
        if self.direction in PossibleDirectionsList:
            self.gridPos = [x, y]

    def RemoveCornerCuttingDirections(self, possibleDirections, Map):
        x, y = self.gridPos[0], self.gridPos[1]
        for i in [(-1, 0), (0, -1), (1, 0), (0, 1)]:
            xdir, ydir = i[0], i[1]

            if Map.Floor[y + ydir][x + xdir] == " ":  # Prevents cutting corners when walls exist.
                if xdir:
                    for k in range(len(possibleDirections) - 1, -1, -1):
                        if xdir == possibleDirections[k][0]:
                            del possibleDirections[k]
                elif ydir:
                    for k in range(len(possibleDirections) - 1, -1, -1):
                        if ydir == possibleDirections[k][1]:
                            del possibleDirections[k]
        return possibleDirections

    def RemoveTileDirections(self, possibleDirections, Map, Tile):
        x, y = self.gridPos[0], self.gridPos[1]
        for i in range(len(possibleDirections) - 1, -1, -1):  # Prevents walking through non-ground tiles and through other pokemon.
            xdir, ydir = possibleDirections[i][0], possibleDirections[i][1]
            if Map.Floor[y + ydir][x + xdir] == Tile:
                del possibleDirections[i]
        return possibleDirections

    def PossibleDirections(self, Map):  # lists the possible directions the pokemon may MOVE in.
        possibleDirections = [(i, j) for i in range(-1, 2) for j in range(-1, 2)]
        if self.BattleInfo.Type1 != "Ghost" and self.BattleInfo.Type2 != "Ghost":
            possibleDirections = self.RemoveCornerCuttingDirections(possibleDirections, Map)
            possibleDirections = self.RemoveTileDirections(possibleDirections, Map, " ")
        if self.BattleInfo.Type1 != "Water" and self.BattleInfo.Type2 != "Water":
            possibleDirections = self.RemoveTileDirections(possibleDirections, Map, "F")

        for sprite in all_sprites:
            if 1 <= self.DistanceToTarget(sprite, self.gridPos) < 2:
                if self.VectorToTarget(sprite, self.gridPos) in possibleDirections:
                    possibleDirections.remove(self.VectorToTarget(sprite, self.gridPos))

        return possibleDirections  # Lists directions unoccupied and non-wall tiles(that aren't corner obstructed)

    def Draw(self, x, y):
        a = self.blitPos[0] + x
        b = self.blitPos[1] + y
        scaledShift = (POKESIZE - TILESIZE) // 2
        if self.pokeType in ["User", "Team"]:
            p.draw.ellipse(display, (255, 247, 0), (
                a + TILESIZE * 4 / 24, b + TILESIZE * 16 / 24, TILESIZE * 16 / 24, TILESIZE * 8 / 24))  # Yellow edge
            p.draw.ellipse(display, (222, 181, 0), (
                a + TILESIZE * 5 / 24, b + TILESIZE * 17 / 24, TILESIZE * 14 / 24,
                TILESIZE * 6 / 24))  # Lightbrown fade
            p.draw.ellipse(display, (165, 107, 0), (
                a + TILESIZE * 6 / 24, b + TILESIZE * 17 / 24, TILESIZE * 12 / 24, TILESIZE * 6 / 24))  # Brown ellipse
        else:
            p.draw.ellipse(display, BLACK, (
                a + TILESIZE * 4 / 24, b + TILESIZE * 16 / 24, TILESIZE * 16 / 24, TILESIZE * 8 / 24))  # BlackShadow

        display.blit(self.currentImg, (a - scaledShift,
                                       b - scaledShift))  # The pokemon image files are 200x200 px while tiles are 60x60. (200-60)/2 = 70 <- Centred when shifted by 70.

    ##############
    def VectorToTarget(self, Target, pos):
        return (Target.gridPos[0] - pos[0], Target.gridPos[1] - pos[1])

    def DistanceToTarget(self, Target, pos):
        vector = self.VectorToTarget(Target, pos)
        return (vector[0] ** 2 + vector[1] ** 2) ** (0.5)

    def CheckAggro(self, Target, Map):
        distance, vector = self.DistanceToTarget(Target, self.gridPos), self.VectorToTarget(Target, self.gridPos)
        for Room in Map.RoomCoords:
            if self.gridPos in Room and Target.gridPos in Room:  # Pokemon aggro onto the user if in the same room
                sameRoom = True
                break
            else:
                sameRoom = False

        if distance <= AGGRORANGE or sameRoom:  # Pokemon also aggro if withing a certain range AGGRORANGE
            return distance, vector, True
        else:
            return None, None, False

    def MoveInDirectionOfMinimalDistance(self, Target, Map, possibleDirections):
        if not Target:
            return
        elif Target.gridPos == (self.gridPos[0] + self.direction[0], self.gridPos[1] + self.direction[1]):
            return  # Already facing Target, no need to change direction

        distance, vector, aggro = self.CheckAggro(Target, Map)
        if aggro:
            if distance < 2:
                self.direction = vector
                return

            new_pos = self.gridPos
            new_direction = self.direction

            for direction in possibleDirections:
                surrounding_pos = (self.gridPos[0] + direction[0], self.gridPos[1] + direction[1])
                new_distance = self.DistanceToTarget(Target, surrounding_pos)

                if new_distance < distance:
                    distance = new_distance
                    new_direction = direction

            self.direction = new_direction

        else:  # Face a random, but valid direction if not aggro
            i = randint(0, len(possibleDirections) - 1)
            self.direction = possibleDirections[i]

    ################
    # ANIMATIONS
    def MotionAnim(self, motionTimeLeft, timeForOneTile):
        if self.blitPos != [self.gridPos[0] * TILESIZE, self.gridPos[1] * TILESIZE]:
            listOfImages = self.imageDict["Motion"][self.direction]
            stepSize = 1 / len(listOfImages)
            for i in range(len(listOfImages)):
                if stepSize * i <= motionTimeLeft / timeForOneTile < stepSize * (i + 1):
                    self.currentImg = self.imageDict["Motion"][self.direction][(i + 2) % len(listOfImages)]

            self.blitPos[0] = (self.gridPos[0] - (self.direction[0] * motionTimeLeft / timeForOneTile)) * TILESIZE
            self.blitPos[1] = (self.gridPos[1] - (self.direction[1] * motionTimeLeft / timeForOneTile)) * TILESIZE
            if self.blitPos[0] == self.gridPos[0] * TILESIZE and self.blitPos[1] == self.gridPos[1] * TILESIZE:
                self.currentImg = self.imageDict["Motion"][self.direction][0]

    def DoAnim(self, Effect, attackTimeLeft, timeForOneTile):
        if Effect == "Damage":
            self.HurtAnim(attackTimeLeft, timeForOneTile)
        elif Effect in ["ATK+", "ATK-", "DEF+", "DEF-", "SPATK+", "SPATK-", "SPDEF+", "SPDEF-"]:
            self.StatAnim(Effect, attackTimeLeft, timeForOneTile)
        elif Effect in []:
            self.AfflictAnim()
        else:
            pass

    def AfflictAnim(self):
        pass

    def HurtAnim(self, attackTimeLeft, timeForOneTile):
        if self.BattleInfo.Status["HP"] == 0:
            UpperBound = 1.5
        else:
            UpperBound = 0.85
        if 0.15 < attackTimeLeft / timeForOneTile <= UpperBound:
            self.currentImg = self.imageDict["Hurt"][self.direction][0]
        else:
            self.currentImg = self.imageDict["Motion"][self.direction][0]

    def AttackAnim(self, AttackIndex, attackTimeLeft, timeForOneTile):
        category = self.BattleInfo.MoveSet[AttackIndex].Category
        if category == "Physical" or category == "Special":
            pass
        elif category == "Status":
            category = "Special"
        else:
            return

        listOfImages = self.imageDict[category][self.direction]
        stepSize = 1 / len(listOfImages)
        for i in range(len(listOfImages)):
            if stepSize * i <= attackTimeLeft / timeForOneTile < stepSize * (i + 1):
                self.currentImg = self.imageDict[category][self.direction][i]

        if category == "Physical":
            self.blitPos[0] = (self.gridPos[0] + (self.direction[0]) * 2 * (
                    0.25 - (0.5 - (attackTimeLeft / timeForOneTile)) ** 2)) * TILESIZE
            self.blitPos[1] = (self.gridPos[1] + (self.direction[1]) * 2 * (
                    0.25 - (0.5 - (attackTimeLeft / timeForOneTile)) ** 2)) * TILESIZE

    def StatAnim(self, Effect, attackTimeLeft, timeForOneTile):
        stat = Effect[:-1]
        action = Effect[-1]
        listOfImages = StatsAnimDict[stat][action]
        stepSize = 1 / len(listOfImages)
        for sprite in all_sprites:
            if sprite.pokeType == "User":
                x = self.blitPos[0] + display_width / 2 - sprite.blitPos[0]
                y = self.blitPos[1] + display_height / 2 - sprite.blitPos[1]
                break
        for i in range(len(listOfImages)):
            if stepSize * i <= attackTimeLeft / timeForOneTile < stepSize * (i + 1):
                display.blit(listOfImages[i], (x, y))
                break

    ################
    def Miss(self, MoveAccuracy, Evasion):
        i = randint(0, 99)
        RawAccuracy = self.BattleInfo.Status["ACC"] / 100 * MoveAccuracy
        if round(RawAccuracy - Evasion) > i:
            return False
        else:
            return True

    def Activate(self, Map, moveIndex):
        if moveIndex == None:
            return []
        MoveUsed = self.BattleInfo.MoveSet[moveIndex]
        steps = []
        if MoveUsed.PP != 0:
            MoveUsed.PP -= 1

            msg = self.BattleInfo.Name + " used " + MoveUsed.Name
            MessageLog.Write(Text(msg).DrawText())

            for i in range(len(MoveUsed.Effects)):
                Dict = {}
                Effect = MoveUsed.Effects[i]
                Range = MoveUsed.Ranges[i]
                TargetType = MoveUsed.TargetType[i]
                Targets = self.FindPossibleTargets(TargetType)
                Targets = self.FilterOutOfRangeTargets(Targets, Range, MoveUsed.CutsCorners, Map)
                if Targets:
                    Dict["Targets"] = Targets
                    Dict["Effect"] = Effect
                    steps.append(Dict)
                    self.ActivateEffect(MoveUsed, i, Targets, Map)
                else:
                    if i == 0:
                        msg = "The move failed."
                        MessageLog.Write(Text(msg).DrawText())
                    break
        else:
            msg = "You have ran out of PP for this move."
            MessageLog.Write(Text(msg).DrawText())

        return steps

    def ActivateEffect(self, Move, Index, Targets, Map):
        Effect = Move.Effects[Index]
        if Effect == "Damage":
            for Target in Targets:

                Evasion = Target.BattleInfo.Status["EVA"]
                if Target == self:  # You cannot dodge recoil damage
                    Evasion = 0

                if self.Miss(Move.Accuracy[Index], Evasion):
                    msg = self.BattleInfo.Name + " missed."
                else:
                    Damage = self.BattleInfo.DealDamage(Move, Target, Index)
                    Target.BattleInfo.LoseHP(Damage)
                    if Target != self:
                        msg = Target.BattleInfo.Name + " took " + str(Damage) + " damage!"
                    else:
                        msg = Target.BattleInfo.Name + " took " + str(Damage) + " recoil damage!"
                MessageLog.Write(Text(msg).DrawText())
                print(self.BattleInfo.Name, self.BattleInfo.Status["HP"])
                print(Target.BattleInfo.Name, Target.BattleInfo.Status["HP"])

        elif Effect == "FixedDamage":
            for Target in Targets:
                Target.BattleInfo.LoseHP(Move.Power[Index])

        elif Effect == "Heal":
            for Target in Targets:
                Target.BattleInfo.Heal(Move.Power[Index])

        elif Effect in (
                "ATK+", "ATK-", "DEF+", "DEF-", "SPATK+", "SPATK-", "SPDEF+", "SPDEF-", "ACC+", "ACC-", "EVA+", "EVA-"):
            for Target in Targets:
                Evasion = Target.BattleInfo.Status["EVA"]
                if Target == self:  # You cannot dodge recoil damage
                    Evasion = 0
                if self.Miss(Move.Accuracy[Index], Evasion):
                    msg = self.BattleInfo.Name + " missed."
                else:
                    Target.BattleInfo.StatChange(Effect, Move.Power[Index])

        elif Effect in (
                "Poisoned", "Badly Poisoned", "Burned", "Frozen", "Paralyzed", "Sleeping", "Constricted", "Paused"):
            for Target in Targets:
                Evasion = Target.BattleInfo.Status["EVA"]
                if Target == self:  # You cannot dodge recoil damage
                    Evasion = 0
                if Index == 0:
                    if self.Miss(Move.Accuracy[Index], Evasion):
                        msg = self.BattleInfo.Name + " missed."
                    else:
                        Target.BattleInfo.Afflict(Effect, Move.Power[Index])
                        msg = Target.BattleInfo.Name + " is now " + Effect
                    MessageLog.Write(Text(msg).DrawText())

    def FindPossibleTargets(self, TargetType):
        Allies = [sprite for sprite in all_sprites if sprite.pokeType in ("User", "Team")]
        Enemies = [sprite for sprite in all_sprites if sprite.pokeType == "Enemy"]
        if self.pokeType == "Enemy":
            Allies, Enemies = Enemies, Allies

        if TargetType == "Self":
            return [self]
        elif TargetType == "All":
            return [sprite for sprite in all_sprites]
        elif TargetType == "Allies":
            return Allies
        elif TargetType == "Enemies":
            return Enemies
        elif TargetType == "Non-Self":
            return [sprite for sprite in all_sprites if sprite != self]

    def FilterOutOfRangeTargets(self, Targets, Range, CutsCorners, Map):
        if Range == "0":
            return [self]

        possibleDirections = [(i, j) for i in range(-1, 2) for j in range(-1, 2)]
        if not CutsCorners:
            possibleDirections = self.RemoveCornerCuttingDirections(possibleDirections, Map)

        if Range == "1" or Range == "2" or Range == "10":  # Front
            possibleDirections = self.RemoveTileDirections(possibleDirections, Map, " ")
            if self.direction in possibleDirections:
                for n in range(1, int(Range) + 1):
                    for Target in Targets:
                        x = self.gridPos[0] + n * self.direction[0]
                        y = self.gridPos[1] + n * self.direction[1]
                        if Map.Floor[y][x] == " ":
                            return []
                        if (Target.gridPos[0] == x) and (Target.gridPos[1] == y):
                            return [Target]

        if Range == "S" or Range == "R":  # Surrounding
            NewTargets = []
            for Target in Targets:
                for direction in possibleDirections:
                    x = self.gridPos[0] + direction[0]
                    y = self.gridPos[1] + direction[1]
                    if (Target.gridPos[0] == x) and (Target.gridPos[1] == y):
                        NewTargets.append(Target)
            if Range == "S":
                return NewTargets
            else:  # Range == "R"
                x = self.gridPos[0]
                y = self.gridPos[1]

                if Map.Floor[y][x] == "R":
                    for Room in Map.RoomCoords:
                        if [x, y] in Room:
                            possibleDirections = Room
                            break
                    for Target in Targets:
                        if Target.gridPos in possibleDirections:
                            NewTargets.append(Target)
                NewTargets = RemoveDuplicates(NewTargets)
                return NewTargets
        return []


###################################################################################################
class Move:
    def __init__(self, Name, Power, Accuracy, Critical, PP, Type, Category, CutsCorners, TargetType, Ranges, Effects):
        # Single
        self.Name = Name
        self.Power = Power
        self.Accuracy = Accuracy
        self.Critical = Critical
        self.PP = PP
        self.Type = Type
        self.Category = Category  # ["ATK","SPATK"]
        self.CutsCorners = CutsCorners  # 1/0 [True/False]
        # Multi
        self.TargetType = TargetType  # ["Self","Allies","Enemies","All"]
        self.Ranges = Ranges
        self.Effects = Effects  # ["Damage","Heal","ATK+","DEF+","SPATK+","SPDEF+","ATK-","DEF-","SPATK-","SPDEF-"...]

    def EmptyPP(self):
        self.PP = 0


class PokemonBattleInfo:
    def __init__(self, ID, Name, LVL, XP, Type1, Type2, Base, Status, MoveSet):
        self.ID = ID
        self.Name = Name
        self.LVL = LVL
        self.XP = XP
        self.Type1 = Type1
        self.Type2 = Type2
        self.Base = Base
        self.Status = Status
        self.MoveSet = MoveSet

    def LoseHP(self, Amount):
        self.Status["HP"] -= Amount
        if self.Status["HP"] < 0:
            self.Status["HP"] = 0

    def DealDamage(self, Move, Target, Index):
        # Step 0 - Determine Stats
        if Move.Category == "Physical":
            A = self.Base["ATK"] * StageDict[self.Status["ATK"]]
            D = Target.BattleInfo.Base["DEF"] * StageDict[Target.BattleInfo.Status["DEF"]]
        elif Move.Category == "Special":
            A = self.Base["SPATK"] * StageDict[self.Status["SPATK"]]
            D = Target.BattleInfo.Base["SPDEF"] * StageDict[Target.BattleInfo.Status["SPDEF"]]
        else:
            return 0
        L = self.LVL
        P = Move.Power[Index]
        if Target.pokeType in ["User", "Team"]:
            Y = 340 / 256
        else:
            Y = 1
        logInput = ((A - D) / 8 + L + 50) * 10
        if logInput < 1:
            logInput = 1
        elif logInput > 4095:
            logInput = 4095
        CriticalChance = randint(0, 99)

        # Step 1 - Stat Modification
        # Step 2 - Raw Damage Calculation
        Damage = ((A + P) * (39168 / 65536) - (D / 2) + 50 * math.log(logInput) - 311) / Y
        # Step 3 - Final Damage Modifications
        if Damage < 1:
            Damage = 1
        elif Damage > 999:
            Damage = 999

        Damage *= DamageDict[Move.Type][Target.BattleInfo.Type1] * DamageDict[Move.Type][
            Target.BattleInfo.Type2]  # Apply type advantage multiplier
        if Move.Critical > CriticalChance:
            Damage *= 1.5
        # Step 4 - Final Calculations
        Damage *= (randint(0, 16383) + 57344) / 65536  # Random pertebation
        Damage = round(Damage)

        return Damage

    def StatChange(self, Effect, Power):
        if Effect[-1] == "+":
            Effect = Effect[:-1]
            self.Status[Effect] += Power
            if self.Status[Effect] > 20:
                self.Status[Effect] = 20

        elif Effect[-1] == "-":
            Effect = Effect[:-1]
            self.Status[Effect] -= Power
            if self.Status[Effect] < 0:
                self.Status[Effect] = 0

    def Afflict(self, Effect, Power):

        if not self.Status[Effect]:
            self.Status[Effect] = Power
        else:
            print(self.Name, "is already", Effect)

    def Heal(self, Power):
        self.Status["HP"] += Power
