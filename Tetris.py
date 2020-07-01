from p5 import *
from array import *
import numpy
import random
import time,threading

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
trigger=1
def setup():
    global Board1,Block1
    size(width,height)
    Board1=Board(width,height)
    Block1=Stone()
    ShiftTimer()




def draw():
    background(0)
    Board1.display()
    Board1.drawblocks()
    Block1.draw()


def ShiftTimer():
    threading.Timer(0.1,shift_down).start()


def shift_down():
    try:
        Block1.position[1] += 1
    except AttributeError:
        None
    threading.Timer(0.1, ShiftTimer).start()

def key_pressed():
    if key=='UP':
        Block1.rotation()
    if key=='LEFT':
        Block1.move('Left')
    if key=='RIGHT':
        Block1.move('Right')



class Stone(object):
    def __init__(self):
        self.position=[startpointx,startpointy]
        self.Type = random.choice(Types)
        self.shape=Shapes[Types.index(self.Type)]

    def rotation(self):

        if self.Type == 'O':
            self.shape=self.shape
        else:
            for i in self.shape:
                x = i[0] * rotationmatrix[0][0] + i[1] * rotationmatrix[1][0]
                print(i[0])
                y = i[0] * rotationmatrix[0][1] + i[1] * rotationmatrix[1][1]
                i[0]=x
                i[1]=y

    def move(self,Direction):
        if Direction=='Right':
            if not (max(x[0] for x in self.shape) + int(self.position[0])) > 8:
                self.position[0]+=1
        if Direction == 'Left':
            if not (min(x[0] for x in self.shape) + int(self.position[0])) < 1:
                self.position[0]-=1

    def draw(self):
        for i in self.shape:
            fill(255)
            rect((xstart+(self.position[0]+i[0])*zellsize,ystart+(self.position[1]+i[1])*zellsize),zellsize,zellsize)

class Board(object):

    def __init__(self,width,height):
        self.occupied = np.zeros((zellsy,zellsx), dtype=int)
        self.width = width
        self.height = height

    def display(self):
        drawgrid()
    def drawblocks(self):
        for i in range(0, zellsy - 1):
            for j in range(0, zellsx - 1):
                if self.occupied[i][j] != 0:
                    print(self.occupied[i][j])
                    fill(self.occupied[i][j])
                    rect((xstart+j*zellsize,ystart+i*zellsize), zellsize, zellsize)


def drawgrid():
    line_color=255
    stroke(line_color)
    for i in range(0, zellsx+1):
        line((xstart + i * zellsize, 0), (xstart + i * zellsize, play_height))
    for j in range(0, zellsy+1):
        line((xstart,ystart+ j*zellsize), (xstart+play_width, ystart+j*zellsize))

if __name__ == '__main__':
    run(frame_rate=10)