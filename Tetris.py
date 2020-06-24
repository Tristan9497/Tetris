from p5 import *
import numpy
height=800
width=1600
xstart=600
ystart=0
zellsy = 20
zellsx = 10
zellsize=height/zellsy
play_width=zellsize*zellsx
play_height=zellsize*zellsy

Types=['I','O','S','Z','T','J','L']
Shapes=[['0000',
         '0000',
         'XXXX',
         '0000'],
        ['0000',
         '0XX0',
         '0XX0',
         '0000'],
        ['0XX',
         'XX0',
         '000'],
        ['XX0',
         '0XX',
         '000'],
        ['0X0',
         'XXX',
         '000'],
        ['X00',
         'XXX',
         '000'],
        ['00X',
         'XXX',
         '000']]


def setup():
    global Board1

    size(width,height)

    Board1=Board(width,height)

def draw():
    background(0)
    Board1.display()

class Stone(object):
    def __init__(self,Type):
        self.Type=Type
        self.shape=Shapes[Types.index(Type)]
    def rotation(self):
        self.shape=rotateblock(self)


def rotateblock(Block):
    if Block.Type=='O':
        return Block.shape
    elif Block.Type=='I':
        if Block.shape[0][2]=='X':
            Block.shape=['0000',
                         '0000',
                         'XXXX',
                         '0000']
        elif Block.shape[2][0]=='X':
            Block.shape=['00X0',
                         '00X0',
                         '00X0',
                         '00X0']
    else:
        #TODO
        return 3





class Board(object):
    def __init__(self,width,height):
        self.width=width
        self.height=height

    def display(self):
        drawgrid()

def drawgrid():
    line_color=255
    stroke(line_color)
    for i in range(0, zellsx+1):
        line((xstart + i * zellsize, 0), (xstart + i * zellsize, play_height))
    for j in range(0, zellsy+1):
        line((xstart,ystart+ j*zellsize), (xstart+play_width, ystart+j*zellsize))

if __name__ == '__main__':
    run()