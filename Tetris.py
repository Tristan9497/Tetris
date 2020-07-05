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

Colors=[[0,255,255],[255,255,0],[0,255,0],[255,0,0],[128,0,128],[0,0,255],[255,165,0]]

def setup():
    global Board1, CurrentBlock, stopFlag, PieceTrigger
    PieceTrigger = False
    size(width,height)
    Board1=Board(width,height)
    CurrentBlock=Stone()

    stopFlag = Event()
    thread=MyThread(stopFlag)
    thread.start()

def draw():
    background(0)
    Board1.display()
    Board1.drawblocks()
    CurrentBlock.draw()


#Timer Thread for Downwards movement
class MyThread(Thread):
    def __init__(self, event):
        Thread.__init__(self)
        self.stopped = event
        self.setDaemon(daemonic=True)

    def run(self):
        while not self.stopped.wait(0.5):
            if (PieceTrigger):
                CurrentBlock.__init__()
            else:
                CurrentBlock.move('Down')

#Keyboard events
def key_pressed(event):
    if key=='UP':
        CurrentBlock.rotation()
    if key=='LEFT':
        CurrentBlock.move('Left')
    if key=='RIGHT':
        CurrentBlock.move('Right')
    if key=='DOWN':
        CurrentBlock.move('Down')

class Stone(object):
    def __init__(self):
        global PieceTrigger,stopFlag
        self.position=[startpointx,startpointy]
        self.Type = random.choice(Types)
        self.shape=Shapes[Types.index(self.Type)]
        self.color=Colors[Types.index(self.Type)]
        PieceTrigger=False


    def rotation(self):
        buffershape=self.shape
        if self.Type == 'O':
            self.shape=self.shape
        else:
            for i in buffershape:
                x = i[0] * rotationmatrix[0][0] + i[1] * rotationmatrix[1][0]
                y = i[0] * rotationmatrix[0][1] + i[1] * rotationmatrix[1][1]
                i[0] = x
                i[1] = y
            if not checkOccupied(buffershape,self.position):
                self.shape=buffershape



    def move(self,Direction):
        global PieceTrigger
        buffershape=self.shape
        bufferposition=self.position
        if Direction=='Right':
            #check pieces
            bufferposition[0] += 1
            if not checkOccupied(buffershape, bufferposition):
                # add currentpiece to occupied and spawn new piece
                updatecoordinates(buffershape, bufferposition)
            else:
                bufferposition[0] -= 1
                updatecoordinates(self.shape, self.position)

        elif Direction == 'Left':
            #check pieces
            bufferposition[0] -= 1
            if not checkOccupied(buffershape, bufferposition):
                # add currentpiece to occupied and spawn new piece
                updatecoordinates(buffershape, bufferposition)
            else:
                bufferposition[0] += 1
                updatecoordinates(self.shape, self.position)

        if Direction=='Down':
            bufferposition[1] += 1
            if not checkOccupied(buffershape, bufferposition):
                # add currentpiece to occupied and spawn new piece
                updatecoordinates(buffershape, bufferposition)
            else:
                bufferposition[1] -= 1
                addPieceToOccupied(self)
                # Set new Position


    def draw(self):
        for i in self.shape:
            fill(self.color[0],self.color[1],self.color[2])
            rect((xstart+(self.position[0]+i[0])*zellsize,ystart+(self.position[1]+i[1])*zellsize),zellsize,zellsize)


def updatecoordinates(shape, position):
    CurrentBlock.position = position
    CurrentBlock.shape = shape

def addPieceToOccupied(Block):
    global PieceTrigger
    for i in Block.shape:
        for j in range(0, len(Block.color)):
            Board1.occupied[(Block.position[1] + i[1]), (Block.position[0] + i[0]), (j)] = Block.color[j]
    PieceTrigger = True

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

    def __init__(self,width,height):
        self.occupied = np.zeros((zellsy,zellsx,3), dtype=int)
        self.width = width
        self.height = height

    def display(self):
        drawgrid()

    def drawblocks(self):
        for i in range(0, zellsy):
            for j in range(0, zellsx):
                    fill(self.occupied[i,j,0],self.occupied[i,j,1],self.occupied[i,j,2])
                    rect((xstart+j*zellsize,ystart+i*zellsize), zellsize, zellsize)


def drawgrid():
    line_color=255
    stroke(line_color)
    for i in range(0, zellsx+1):
        line((xstart + i * zellsize, 0), (xstart + i * zellsize, play_height))
    for j in range(0, zellsy+1):
        line((xstart,ystart+ j*zellsize), (xstart+play_width, ystart+j*zellsize))

if __name__ == '__main__':
    run(frame_rate=30)
