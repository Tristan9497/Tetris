from p5 import *
from threading import Thread,Event
import numpy
import random
import copy

#region Generic Definitions
height = 800
width = 1600
xstart = 600
ystart = 0
zellsy = 20
zellsx = 10
zellsize = height/zellsy
play_width = zellsize*zellsx
play_height = zellsize*zellsy
Font=None
startpointx=5
startpointy=0

Types=['I','O','S','Z','T','J','L']

#Coordinates of all Pieces relativ to center point top left corner for square piece
Shapes=[[[-2,0],[-1,0],[0,0],[1,0]],
        [[0,0],[1,0],[0,1],[1,1]],
        [[0,0],[1,0],[-1,1],[0,1]],
        [[-1,0],[0,0],[0,1],[1,1]],
        [[-1,-1],[0,-1],[1,-1],[0,0]],
        [[-1,0],[0,0],[1,0],[1,1]],
        [[-1,0],[0,0],[1,0],[-1,1]]]

rotationmatrix=[[0,-1],[1,0]]
ccrotationmatrix=[[0,1],[-1,0]]

Colors=[[0,255,255],[255,255,0],[0,255,0],[255,0,0],[128,0,128],[0,0,255],[255,165,0]]
CycleTime=0.6
#endregion

def setup():
    global Playfield, CurrentBlock, stopFlag, PieceTrigger, Score, NextShape, GameTrigger, Font, Font2, Tetris
    #standard p5 setup function
    #Trigger
    PieceTrigger = False
    GameTrigger=False

    #UI Setup
    background(0)
    size(width,height)
    Font = create_font("ARIALBD.ttf", 34)
    Font2 = create_font("ARIALBD.ttf", 72)
    text_align(align_x="CENTER", align_y="CENTER")

    # Object Generation
    Tetris=Game()
    Playfield = Board(width, height)
    CurrentBlock = Stone(random.choice(Types))
    stopFlag = Event()
    thread = MyThread(stopFlag)
    thread.start()

    # Variables
    NextShape = random.choice(Types)
    Score = 0

def draw():
    global Tetris
    #standard p5 loop function
    if GameTrigger:
        Tetris.Behaviour()
    else:
        Tetris.DisplayStartScreen()

def key_pressed(event):
    # Keyboard event handler
    global GameTrigger,Playfield,Score
    if key=='UP':
        CurrentBlock.rotation()
    if key=='LEFT':
        CurrentBlock.move('Left')
    if key=='RIGHT':
        CurrentBlock.move('Right')
    if key=='DOWN':
        CurrentBlock.move('Down')
    if key=='ENTER':
        GameTrigger=True
        Playfield=Board(width,height)
        Score=0

class MyThread(Thread):
    # Timer Thread for Downwards movement
    def __init__(self, event):
        Thread.__init__(self)
        self.stopped = event
        self.setDaemon(daemonic=True)

    def run(self):
        global NextShape, CycleTime
        while not self.stopped.wait(CycleTime):
            CycleTime-=abs(CycleTime-0.1)/1000
            if (PieceTrigger):
                Playfield.checkTopLine()
                CurrentBlock.__init__(NextShape)
                NextShape = random.choice(Types)
            else:
                CurrentBlock.move('Down')

class Game():
    def Behaviour(self):
        Playfield.drawgrid()
        Playfield.drawblocks()
        Playfield.writeScore()
        Playfield.DisplaynextBlock()
        CurrentBlock.draw()
        self.writeInfo()

    def DisplayStartScreen(self):
        background(0)
        global Score, Font
        text_font(Font)
        fill(255)
        text_align(align_x="CENTER", align_y="CENTER")
        text("To start a new game press enter", (width / 2, height / 2))
        text("To exit the game press ESC", (width / 2, height - 50))

    def writeInfo(self):
        global Font, Font2
        fill(255)
        text_font(Font2)
        text("Tetris", (300, 1 * height / 3))
        text_font(Font)
        text("Objektorientiertes Programmieren", (300, 2 * height / 3))
        text("Tristan Schwoerer", (300, (2 * height / 3)+40))
        text("F6 71336", (300, (2 * height / 3) + 80))

class Stone(object):
    def __init__(self,NextShape):
        global PieceTrigger,stopFlag
        self.position=[startpointx,startpointy]
        self.Type = NextShape
        self.shape=Shapes[Types.index(self.Type)]
        self.color=Colors[Types.index(self.Type)]
        PieceTrigger=False

    def rotation(self):
        buffershape=copy.deepcopy(self.shape)
        if self.Type == 'O':
            None
        else:
            for i in buffershape:
                x = i[0] * rotationmatrix[0][0] + i[1] * rotationmatrix[1][0]
                y = i[0] * rotationmatrix[0][1] + i[1] * rotationmatrix[1][1]
                i[0] = x
                i[1] = y

            if not Playfield.checkOccupied(buffershape,self.position):
                self.shape=buffershape

    def move(self,Direction):
        global PieceTrigger
        buffershape=copy.deepcopy(self.shape)
        bufferposition=copy.deepcopy(self.position)
        if Direction=='Right':
            #check pieces
            bufferposition[0] += 1
            if not Playfield.checkOccupied(buffershape,bufferposition):
                self.updatecoordinates(buffershape, bufferposition)


        elif Direction == 'Left':

            #check pieces
            bufferposition[0] -= 1
            if not Playfield.checkOccupied(buffershape,bufferposition):
                self.updatecoordinates(buffershape, bufferposition)


        if Direction=='Down':
            bufferposition[1] += 1
            if not Playfield.checkOccupied(buffershape,bufferposition):
                self.updatecoordinates(buffershape, bufferposition)
            else:
                Playfield.addPieceToOccupied(self)


    def draw(self):
        for i in self.shape:
            fill(self.color[0],self.color[1],self.color[2])
            rect((xstart+(self.position[0]+i[0])*zellsize,ystart+(self.position[1]+i[1])*zellsize),zellsize,zellsize)

    def updatecoordinates(self, shape, position):
        #updates block object variables
        CurrentBlock.position = position[:]
        CurrentBlock.shape = shape[:]

class Board(object):
    #This Class is meant to handle
    # * Displaying of all stationary Objects
    # * Routines to handle block behaviour when certain cases occur

    def __init__(self,width,height):
        self.occupied = np.zeros((zellsy,zellsx,3), dtype=int)
        self.width = width
        self.height = height

    #Routines
    def checkOccupied(self, shape, position):
        Adder = 0
        xmin = min(a[0] for a in shape) + position[0]
        xmax = max(a[0] for a in shape) + position[0]
        ymax = max(b[1] for b in shape) + position[1]
        # check boarders

        if (xmin in range(0, zellsx)) and (xmax in range(0, zellsx)) and (ymax in range(0, zellsy)):
            # check Fields
            for x in shape:
                Adder += sum(self.occupied[x[1] + position[1], x[0] + position[0]])
            if Adder > 0:
                return True
            else:
                return False
        else:
            return True

    def addPieceToOccupied(self, Block):
        global PieceTrigger
        for i in Block.shape:
            self.occupied[(Block.position[1] + i[1]), (Block.position[0] + i[0])] = copy.deepcopy(Block.color)
        PieceTrigger = True
        self.FindLine()

    def FindLine(self):
        global Score
        Counter=0
        Line=0
        for i in range(zellsy-1,-1,-1):
            for j in range(0,zellsx):
                if sum(self.occupied[i,j])>0:
                    Counter+=1
            if Counter==10:
                self.removeLine(i)
                return

    def removeLine(self, Line):
        global Score
        for k in range(Line, 0, -1):
            self.occupied[k]=self.occupied[k - 1]
        Score+=100
        #start FindLine again to rmeove potential remaining Lines
        self.FindLine()

    def checkTopLine(self):
        global GameTrigger
        sum=0
        for i in self.occupied[0]:
            sum += numpy.sum(i)
        print(sum)
        if sum>0:
            GameTrigger=False

    #Display
    def drawgrid(self):
        background(0)
        line_color = 255
        stroke(line_color)
        for i in range(0, zellsx + 1):
            line((xstart + i * zellsize, 0), (xstart + i * zellsize, play_height))
        for j in range(0, zellsy + 1):
            line((xstart, ystart + j * zellsize), (xstart + play_width, ystart + j * zellsize))

    def drawblocks(self):
        for i in range(0, zellsy):
            for j in range(0, zellsx):
                    fill(self.occupied[i,j,0],self.occupied[i,j,1],self.occupied[i,j,2])
                    rect((xstart+j*zellsize,ystart+i*zellsize), zellsize, zellsize)

    def writeScore(self):
        global Score, Font
        text_font(Font)
        fill(255)

        text("Current Score:" + str(Score), (1300, 2*height/3))
        text("Next Piece", (1300, (1 * height / 3)-100))

    def DisplaynextBlock(self):
        global NextShape
        Testshape=copy.deepcopy(Shapes[Types.index(NextShape)])
        NewColor=copy.deepcopy(Colors[Types.index(NextShape)])
        for i in Testshape:
            fill(NewColor[0],NewColor[1],NewColor[2])
            rect((1300+(i[0])*zellsize,1*height/3+(i[1])*zellsize),zellsize,zellsize)


if __name__ == '__main__':
    run()
