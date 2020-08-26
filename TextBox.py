from ImportsAndConstants import *

class TextBox:
    def __init__(self, x, y, w, h, borderColors, MAXLINES, Contents=None, textBoxSurface=None, pointingAt=None):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.borderColors = borderColors
        self.MAXLINES = MAXLINES
        self.Contents = Contents
        self.textBoxSurface = textBoxSurface
        self.pointingAt = pointingAt

    def DrawTextBox(self):
        wDim = self.w*display_width
        hDim = self.h*display_height#creates semi-transparent black surface
        self.textBoxSurface = p.Surface((wDim, hDim))
        self.textBoxSurface.set_alpha(180)
        self.textBoxSurface.fill(BLACK)
        #borders
        borderThickness = 3
        p.draw.rect(self.textBoxSurface, self.borderColors[0], (0, 0, wDim, borderThickness))#Top
        p.draw.rect(self.textBoxSurface, self.borderColors[0], (0, hDim-borderThickness, wDim, borderThickness))#Bottom
        p.draw.rect(self.textBoxSurface, self.borderColors[0], (0, 0, borderThickness, hDim))#Left
        p.draw.rect(self.textBoxSurface, self.borderColors[0], (wDim-borderThickness, 0, borderThickness, hDim-borderThickness))#Right

        return self
        
    def DrawContents(self):
        xGap = 5
        yGap = 5
        spacing = 36
        i = 0
        while len(self.Contents)>self.MAXLINES:
            del self.Contents[0]
        for i in range(len(self.Contents)):
            xPos = xGap
            yPos = yGap+spacing*i
            img = self.Contents[::-1][i].textSurface
            self.textBoxSurface.blit(img, (xPos, yPos))

    def BlitOnDisplay(self):
        xPos = self.x*display_width
        yPos = self.y*display_height
        display.blit(self.textBoxSurface, (xPos, yPos))

    def Write(self,textObj):
        self.Contents.append(textObj)
            
class Button:
    def __init__(self, text, blitPos=None, Effect=None, textColor=WHITE, textSurface=None):
        self.text = text
        self.blitPos = blitPos
        self.Effect = Effect
        self.textColor = textColor
        self.textSurface = textSurface

    def DrawText(self):
        self.textSurface = FONT.render(self.text, False, self.textColor)
        return self

    def Trigger(self):
        pass

class Text:
    def __init__(self, text, textColor=WHITE, textSurface=None):
        self.text = text
        self.textColor = textColor
        self.textSurface = textSurface

    def DrawText(self):
        self.textSurface = FONT.render(self.text, False, self.textColor)
        return self


MessageLog = TextBox(0.0275, 0.7, 0.95, 0.275, [BORDERBLUE1,BORDERBLUE2], 5, [])
DungeonMenu = TextBox(0.0275,0.05, 0.4, 0.625, [BORDERBLUE1,BORDERBLUE2], 9, [Button("Exit").DrawText(),Button("Options").DrawText(),Button("Team").DrawText(),Button("Inventory").DrawText(),Button("Moves").DrawText()])




