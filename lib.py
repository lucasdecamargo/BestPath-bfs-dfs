import pygame as pg
from pygame import sprite

import random
from pathlib import Path
from os import listdir
from enum import Enum

from pygame.locals import(
    RLEACCEL,
    K_UP,
    K_DOWN,
    K_LEFT,
    K_RIGHT,
    K_ESCAPE,
    MOUSEBUTTONDOWN,
    MOUSEBUTTONUP,
    MOUSEMOTION,
    KEYDOWN,
    QUIT,
)

assets = Path(__file__).resolve().parent / Path("best_path_assets")

def img_load(path, width=0, height=0, scale=1):
    surf = pg.image.load(path)
    if width==0 or height==0:
        width = surf.get_width()
        height = surf.get_height()
    return pg.transform.scale(surf, (round(width*scale), round(height*scale))).convert_alpha()

def gen_grass():
    return str(assets/Path("grass/"+random.choice(listdir(assets/Path("grass")))))

class BoardPosition(sprite.Sprite):
    class Type(Enum):
        PATH = 0
        BLOCKED = 1
        AGENT = 2
        GOAL = 3

    def __init__(self, size, idx=(0,0)):
        super(BoardPosition, self).__init__()
        self.surf = img_load(gen_grass(),size,size)
        self.surf.set_colorkey((0, 0, 0), RLEACCEL)
        self.center = (round(self.surf.get_width()/2), round(self.surf.get_height()/2))
        self.rect = self.surf.get_rect()
        self.type = BoardPosition.Type.PATH
        self.reward = -1
        self.reward_last = -1
        self.idx = idx
        self.path_surf = img_load(str(assets/Path("path.png")),size,size)
        self.path_surf.set_colorkey((0, 0, 0), RLEACCEL)
        self.sol_surf = img_load(str(assets/Path("solution.png")),size,size)
        self.sol_surf.set_colorkey((0, 0, 0), RLEACCEL)
        self.grass_surf = self.surf

    def set_reward(self, val):
        self.reward_last = self.reward
        self.reward = val

    def reset_reward(self):
        self.reward = self.reward_last

    def set_pos(self, pos):
        self.rect.x = pos[0]
        self.rect.y = pos[1]
        self.center = (pos[0] + round(self.surf.get_width()/2),
            pos[1] + round(self.surf.get_height()/2))

    def set_type(self, type):
        self.type = type

    def set_reward(self, reward):
        self.reward = reward

    def update(self):
        pass

    def draw_path(self):
        self.surf = self.path_surf

    def draw_grass(self):
        self.surf = self.grass_surf

    def draw_solution(self):
        self.surf = self.sol_surf

class Board(list):
    def __init__(self, rows, cols, size=50, gap=2):
        super(Board, self).__init__()
        self.pos_x = 0
        self.pos_y = 0
        self.gap = gap
        self.size = size
        self.sgroup = sprite.Group()
        self.added = False
        for i in range(rows):
            self.append([])
            for j in range(cols):
                self[-1].append(BoardPosition(size,(i,j)))

    def set_pos(self,x,y):
        self.pos_x = x
        self.pos_y = y
    
    def draw(self):
        row_count = 0
        for row in self:
            col = 0
            for i in row:
                i.set_pos((col*(self.size+self.gap) + self.pos_x,
                    row_count*(self.size+self.gap) + self.pos_y))
                col += 1
                if not self.added:
                    self.sgroup.add(i)
                    self.added = True
            row_count += 1

    def update(self):
        self.sgroup.update()

    def blit(self, screen):
        count = 0
        for row in self:
            for i in row:
                screen.blit(i.surf, i.rect)

    def node(self, pos):
        a = pos.idx[0]
        b = pos.idx[1]
        idx = [           (a-1,b), 
               (a  ,b-1),          (a  ,b+1),
                          (a+1,b)           ]
        l = []
        for i in idx:
            if i[0] >= 0 and i[1] >= 0:
                try:
                    if self[i[0]][i[1]].type != BoardPosition.Type.BLOCKED:
                        l.append(self[i[0]][i[1]])
                except:
                    pass
        return l


class DragSprite(sprite.Sprite):
    group = sprite.Group()

    def __init__(self, path, width=0, height=0, scale=1):
        super(DragSprite, self).__init__()
        self.surf = img_load(path,width,height,scale)
        self.surf.set_colorkey((0, 0, 0), RLEACCEL)
        self.rect = self.surf.get_rect()
        self.center = (round(self.surf.get_width()/2), round(self.surf.get_height()/2))
        self.dragging = False
        self.off_x = 0
        self.off_y = 0
        self.board = None
        self.pos = None
        DragSprite.group.add(self)

    def set_board(self, board):
        self.board = board

    @staticmethod
    def set_board_all(board):
        for i in DragSprite.group:
            i.set_board(board)

    def match(self):
        if self.board is not None:
            for row in self.board:
                for i in row:
                    if i.rect.collidepoint(self.center) and i.type == BoardPosition.Type.PATH:
                        self.set_center(i.center)
                        self.pos = i
                        return i
        self.pos = None
        return None
    
    def set_pos(self,pos):
        self.rect.x = pos[0]
        self.rect.y = pos[1]
        self.center = (pos[0] + round(self.surf.get_width()/2),
            pos[1] + round(self.surf.get_height()/2))

    def set_center(self,pos):
        self.rect.x = pos[0] - round(self.surf.get_width()/2)
        self.rect.y = pos[1] - round(self.surf.get_height()/2)

    def mouse_signal(self, event):
        pass

    @staticmethod
    def blit(screen):
        for i in DragSprite.group:
            screen.blit(i.surf, i.rect)
    
    @staticmethod
    def loop(event):
        for i in reversed(DragSprite.group.sprites()):
            if event.type == MOUSEBUTTONDOWN:
                if event.button == 1:
                    if i.rect.collidepoint(event.pos):
                        i.dragging = True
                        x,y = event.pos
                        i.off_x = i.rect.x - x
                        i.off_y = i.rect.y - y
                        i.mouse_signal(MOUSEBUTTONDOWN)
                        return

            elif event.type == MOUSEBUTTONUP:
                if event.button == 1 and i.dragging:
                    i.dragging = False
                    i.match()
                    i.mouse_signal(MOUSEBUTTONUP)
                    return

            elif event.type == MOUSEMOTION:
                if i.dragging:
                    x,y = event.pos
                    i.set_pos((x + i.off_x, y + i.off_y))
                    i.mouse_signal(MOUSEMOTION)
                    return


class Agent(DragSprite):
    def __init__(self, size=0):
        super(Agent, self).__init__(str(assets/Path("playerBlue01.png")),size,size)

    def match(self):
        pos = self.pos
        DragSprite.match(self)
        if self.pos is not None:
            self.pos.set_type(BoardPosition.Type.AGENT)
            self.pos.set_reward(0)
        if pos is not None:
            pos.set_type(BoardPosition.Type.PATH)
            pos.reset_reward() 

    def mouse_signal(self, event):
        return
        if event == MOUSEBUTTONUP:
            nodes = self.board.node(self.pos)
            for n in nodes:
                print(n.idx)
            print("-----")


class Goal(DragSprite):
    def __init__(self, size=0):
        super(Goal, self).__init__(str(assets/Path("goalWhite01.png")),size,size)
        self.reward = 1

    def match(self):
        pos = self.pos
        DragSprite.match(self)
        if self.pos is not None:
            self.pos.set_type(BoardPosition.Type.GOAL)
            self.pos.set_reward(self.reward)
        if pos is not None:
            pos.set_type(BoardPosition.Type.PATH)
            pos.reset_reward() 

class Wall(DragSprite):
    def __init__(self,size=0):
        super(Wall, self).__init__(str(assets/Path("wall.png")),size,size)
        
    def match(self):
        pos = self.pos
        DragSprite.match(self)
        if self.pos is not None:
            self.pos.set_type(BoardPosition.Type.BLOCKED)
        else:
            self.kill()
        if pos is not None:
            pos.set_type(BoardPosition.Type.PATH)
    

class WallFactory(Wall):
    group = sprite.Group()

    def __init__(self,size=0):
        super(WallFactory, self).__init__(size)
        self.size = size
        
    def mouse_signal(self, event):
        if event == MOUSEBUTTONDOWN:
            new_wall = Wall(self.size)
            new_wall.set_pos((self.rect.x,self.rect.y))
            new_wall.board = self.board
            new_wall.dragging = True
            new_wall.off_x = self.off_x
            new_wall.off_y = self.off_y
            self.dragging = False


class Button(sprite.Sprite):
    group = sprite.Group()

    def __init__(self, surf):
        super(Button,self).__init__()
        self.surf = surf
        self.rect = surf.get_rect()
        Button.group.add(self)

    def mouse_signal(self, event):
        pass

    def set_center(self,pos):
        self.rect.x = pos[0] - round(self.surf.get_width()/2)
        self.rect.y = pos[1] - round(self.surf.get_height()/2)

    @staticmethod
    def loop(event):
        for i in reversed(Button.group.sprites()):
            if event.type == MOUSEBUTTONDOWN:
                if event.button == 1:
                    if i.rect.collidepoint(event.pos):
                        i.mouse_signal(i,MOUSEBUTTONDOWN)
                        return

            elif event.type == MOUSEBUTTONUP:
                if event.button == 1:
                    i.mouse_signal(i,MOUSEBUTTONUP)

    @staticmethod
    def blit(screen):
        for i in Button.group:
            screen.blit(i.surf, i.rect)
