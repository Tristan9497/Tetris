from p5 import *
from array import *
import numpy
import random
import time
import threading
from threading import Thread,Event

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


def setup():
    global Board1, CurrentBlock, stopFlag, PieceTrigger, Score, NextShape, GameTrigger, Font, Font2

    #Trigger
    PieceTrigger = False
    GameTrigger=False

    #UI Setup
    background(0)
    size(width,height)
    Font = create_font("ARIALBD.ttf", 34)
    Font2 = create_font("ARIALBD.ttf", 72)
    text_align(align_x="CENTER", align_y="CENTER")

    #Object Generation
    Board1=Board(width,height)
    CurrentBlock=Stone(random.choice(Types))
    stopFlag = Event()
    thread=MyThread(stopFlag)
    thread.start()

    #Variables
    NextShape = random.choice(Types)
    Score=0

def draw():
    #Main Loop
    if GameTrigger:
        GameBehaviour()
    else:
        Board1.DisplayStartScreen()

def GameBehaviour():
    Board1.drawgrid()
    Board1.drawblocks()
    Board1.removeLine()
    CurrentBlock.draw()
    Board1.writeScore()
    Board1.writeInfo()
    Board1.DisplaynextBlock()

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
                Board1.checkTopLine()
                CurrentBlock.__init__(NextShape)
                NextShape = random.choice(Types)
            else:
                CurrentBlock.move('Down')

def key_pressed(event):
    # Keyboard events
    global GameTrigger,Board1,Score
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
        Board1=Board(width,height)
        Score=0

class Stone(object):
    def __init__(self,NextShape):
        global PieceTrigger,stopFlag
        self.position=[startpointx,startpointy]
        self.Type = NextShape
        self.shape=Shapes[Types.index(self.Type)]
        self.color=Colors[Types.index(self.Type)]
        PieceTrigger=False

    def rotation(self):
        buffershape=self.shape
        if self.Type == 'O':
            None
        else:
            for i in buffershape:
                x = i[0] * rotationmatrix[0][0] + i[1] * rotationmatrix[1][0]
                y = i[0] * rotationmatrix[0][1] + i[1] * rotationmatrix[1][1]
                i[0] = x
                i[1] = y

            if not checkOccupied(buffershape,self.position):
                self.shape=buffershape
            else:
                for i in buffershape:
                    x = i[0] * ccrotationmatrix[0][0] + i[1] * ccrotationmatrix[1][0]
                    y = i[0] * ccrotationmatrix[0][1] + i[1] * ccrotationmatrix[1][1]
                    i[0] = x
                    i[1] = y

    def move(self,Direction):
        global PieceTrigger
        buffershape=self.shape
        bufferposition=self.position
        if Direction=='Right':
            #check pieces
            bufferposition[0] += 1
            if not checkOccupied(buffershape, bufferposition):
                self.updatecoordinates(buffershape, bufferposition)
            else:
                bufferposition[0] -= 1

        elif Direction == 'Left':
            #check pieces
            bufferposition[0] -= 1
            if not checkOccupied(buffershape, bufferposition):
                self.updatecoordinates(buffershape, bufferposition)
            else:
                bufferposition[0] += 1

        if Direction=='Down':
            bufferposition[1] += 1
            if not checkOccupied(buffershape, bufferposition):
                self.updatecoordinates(buffershape, bufferposition)
            else:
                bufferposition[1] -= 1
                Board1.addPieceToOccupied(self)

    def draw(self):
        for i in self.shape:
            fill(self.color[0],self.color[1],self.color[2])
            rect((xstart+(self.position[0]+i[0])*zellsize,ystart+(self.position[1]+i[1])*zellsize),zellsize,zellsize)

    def updatecoordinates(self, shape, position):
        #updates block object variables
        CurrentBlock.position = position
        CurrentBlock.shape = shape

def checkOccupied(shape,position):
    Adder=0
    xmin = min(a[0] for a in shape) + position[0]
    xmax = max(a[0] for a in shape) + position[0]
    ymax = max(b[1] for b in shape) + position[1]
    #check boarders
    if (xmin in range(0,zellsx)) and (xmax in range(0,zellsx)) and (ymax in range(0,zellsy)):
        #check Fields
        for x in shape:
            Adder+= sum(Board1.occupied[x[1] + position[1], x[0] + position[0]])
        if Adder>0:
            return True
        else:
            return False
    else:
        return True

class Board(object):
    #This Class is meant to handle
    # Displaying of all stationary Objects
    # Detection for placed blocks
    def __init__(self,width,height):
        self.occupied = np.zeros((zellsy,zellsx,3), dtype=int)
        self.width = width
        self.height = height

    def addPieceToOccupied(self, Block):
        global PieceTrigger
        for i in Block.shape:
            for j in range(0, len(Block.color)):
                self.occupied[(Block.position[1] + i[1]), (Block.position[0] + i[0]), (j)] = Block.color[j]
        PieceTrigger = True

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

    def removeLine(self):
        global Score
        Counter=0
        for i in range(zellsy-1,-1,-1):
            for j in range(0,zellsx):
                if sum(self.occupied[i,j])>0:
                    Counter+=1
            if Counter==10:
                for k in range(i, 0, -1):
                    self.occupied[k]=self.occupied[k - 1]
                self.occupied[0] = numpy.zeros((zellsx, 3), dtype=int)
                Score+=10
            Counter=0

    def checkTopLine(self):
        global GameTrigger
        sum=0
        for i in self.occupied[0]:
            sum += numpy.sum(i)
        print(sum)
        if sum>0:
            GameTrigger=False

    #Display
    def writeScore(self):
        global Score, Font
        text_font(Font)
        fill(255)

        text("Current Score:" + str(Score), (1300, 2*height/3))
        text("Next Piece", (1300, (1 * height / 3)-100))

    def writeInfo(self):
        global Font, Font2
        text_font(Font2)
        text("Tetris", (300, 1 * height / 3))
        text_font(Font)
        text("Objektorientiertes Programmieren", (300, 2 * height / 3))
        text("Tristan Schwörer", (300, (2 * height / 3)+40))
        text("F6 71336", (300, (2 * height / 3) + 80))

    def DisplaynextBlock(self):
        global NextShape
        shape=Shapes[Types.index(NextShape)]
        NewColor=Colors[Types.index(NextShape)]
        for i in shape:
            fill(NewColor[0],NewColor[1],NewColor[2])
            rect((1300+(i[0])*zellsize,1*height/3+(i[1])*zellsize),zellsize,zellsize)

    def DisplayStartScreen(self):
        background(0)
        global Score, Font
        text_font(Font)
        fill(255)
        text_align(align_x="CENTER", align_y="CENTER")
        text("To start a new game press enter", (width / 2, height / 2))
        text("To exit the game press ESC", (width / 2, height - 50))

if __name__ == '__main__':
    run()
