import pygame
import math
import random

pygame.init()
WIDTH, HEIGHT = 1000, 800
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
COLOR_INACTIVE = pygame.Color('lightskyblue3')
COLOR_ACTIVE = pygame.Color('dodgerblue2')
FONT = pygame.font.Font(None, 32)

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
ORANGE = (255, 128, 0)
PURPLE = (128, 0, 255)
DARK_GREEN = (0, 128, 0)
DARK_BLUE = (0, 0, 128)

SURPRISE = (255, 153, 51)

LIGHT_GRAY = (200, 200, 200)
GRAY = (128, 128, 128)
DARK_GRAY = (50, 50, 50)

LIGHT_YELLOW = (255, 255, 153)
YELLOW = (255, 255, 0)
DARK_YELLOW = (204, 204, 0)

COLOUR = [WHITE,BLACK,RED,GREEN, BLUE, ORANGE, PURPLE, DARK_GREEN, DARK_BLUE, SURPRISE, LIGHT_GRAY, GRAY,DARK_GRAY,LIGHT_YELLOW,YELLOW,DARK_YELLOW]

CHARW, CHARH = 20, 20

CHARX = WIDTH/2-(CHARW/2)
CHARY = HEIGHT/2-(CHARH/2)

CHARCENTER = (CHARX+(CHARW/2), CHARY+(CHARH/2))

GRAVITY = 0.015

PI = math.pi

FRICTION = 0.5
DRAG = 0.001

SPEEDCAP = 1
SPEEDCAPN = SPEEDCAP * -1

AIRSC = 1.5
AIRSCN = AIRSC * -1

NUMBALLS = 300
BALLSPEED = 20

JUMPFORCE = -1
MOVEFORCE = 0.03

FRAME_RATE = 300

WHITE = (255,255,255)


class InputBox:

    def __init__(self, x, y, w, h, text=''):
        self.rect = pygame.Rect(x, y, w, h)
        self.color = COLOR_INACTIVE
        self.text = text
        self.txt_surface = FONT.render(text, True, self.color)
        self.active = False
        self.overlayText = text
        self.friction = 0.5

    def handle_event(self, event, newWalls):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # If the user clicked on the input_box rect.
            if self.rect.collidepoint(event.pos):
                # Toggle the active variable.
                self.active = not self.active
                self.text = ''
            else:
                self.active = False
            # Change the current color of the input box.
            self.color = COLOR_ACTIVE if self.active else COLOR_INACTIVE
        if event.type == pygame.KEYDOWN:
            if self.active:
                if event.key == pygame.K_RETURN:
                    if self.overlayText == "Save":
                        saveFile(self.text, newWalls)
                    else:
                        try:
                            self.friction = float(self.text)
                        except:
                            print('Not float')
                    self.text = 'Saved'
                elif event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                else:
                    self.text += event.unicode
            else:
                self.text = self.overlayText


    def update(self):
        # Resize the box if the text is too long.
        width = max(200, self.txt_surface.get_width()+10)
        self.rect.w = width
        if not self.active:
            self.text = self.overlayText
        self.txt_surface = FONT.render(self.text, True, self.color)

    def draw(self, WIN):
        # Blit the text.
        WIN.blit(self.txt_surface, (self.rect.x+5, self.rect.y+5))
        # Blit the rect.
        pygame.draw.rect(WIN, self.color, self.rect, 2)


class Character:

    def __init__(self, x, y, colour = WHITE):
        self.x = x
        self.y = y

        self.rect = pygame.Rect(CHARX, CHARY, CHARW, CHARH)

        self.touching = {'left':False, 'right':False, 'up':False, 'down':False}
        self.touchingWall = {'left':None, 'right':None, 'up':None, 'down':None}

        self.velocity = [0,0]

        self.userForce = [0,0]
        self.gravityForce = [0,0]
        self.normalForce = 0

        self.colour = colour

        self.now = 1
        self.deltaTime = 1
        self.previousTime = 1

    def draw(self):
        pygame.draw.rect(WIN, self.colour, self.rect)

    def state(self, walls, first, bigBalls = None, smallBalls = None):
        x = [-1, 1, 0, 0]

        y = [0, 0, -1, 1]

        n = 0

        tempx, tempy = self.x, self.y

        for key in self.touching:
            self.touching[key], self.touchingWall[key] = collide(self, walls, x[n], y[n])
            n += 1

        if self.touching['down'] and self.touching['left'] and self.touching['right']:
            self.y -= 1
            self.state(walls, False)

        if self.touching['down'] and self.touching['up'] and self.touching['right']:
            self.x -= 1
            self.state(walls, False)

        if self.touching['down'] and self.touching['left'] and self.touching['up']:
            self.x += 1
            self.state(walls, False)

        if first:
            x =  self.x - tempx
            y = self.y - tempy

            for i in range(len(smallBalls)):
                smallBalls[i].update(x, y, self.deltaTime)

            for i in range(len(bigBalls)):
                bigBalls[i].update(x, y, self.deltaTime)


class Wall:
    def __init__(self, x1, y1, x2, y2, friction=FRICTION, colour=WHITE):
        self.x1 = x1
        self.x2 = x2
        self.y1 = y1
        self.y2 = y2

        self.colour = colour

        self.friction = friction

        try:
            self.slope = (self.y2 - self.y1) / (self.x2 - self.x1)
        except:
            self.slope = math.inf

        self.angle = math.atan(self.slope)

    def draw(self, character):
        pygame.draw.line(WIN, self.colour, (CHARCENTER[0] - character.x + self.x1, CHARCENTER[1] - character.y + self.y1), (CHARCENTER[0] - character.x + self.x2, CHARCENTER[1] - character.y + self.y2), 5)

class Ball:
    def __init__(self, x, y, size, colour = WHITE):
        self.x = x
        self.y = y

        self.size = size
        self.colour = colour

        self.playerX = 0
        self.playerY = 0

    def draw(self):
        pygame.draw.circle(WIN, self.colour, (self.x, self.y), self.size)

    def update(self, xdif, ydif):
        self.x -= (xdif - self.playerX)*self.size/BALLSPEED
        self.y -= (ydif - self.playerY)*self.size/BALLSPEED

        self.playerY = ydif
        self.playerX = xdif

        if self.x > WIDTH + self.size + 1:
            self.x -= WIDTH + (self.size*2)
        if self.x < -self.size - 1:
            self.x += WIDTH + (self.size*2)

        if self.y > HEIGHT + self.size + 1:
            self.y -= HEIGHT + (self.size*2)
        if self.y < -self.size - 1:
            self.y += HEIGHT + (self.size*2)

def saveFile(name, walls):
    filehndl = open(name + '.txt', 'w')

    for i in range(len(walls)):
        filehndl.write(f'wall: {walls[i].x1} {walls[i].y1} {walls[i].x2} {walls[i].y2} {walls[i].friction} {walls[i].colour}')
        filehndl.write('\n')
   
    filehndl.close()

def update(box, box2, walls, smallBalls, bigBalls, character, newWalls):
    for i in range(len(smallBalls)):
        smallBalls[i].update(character.x, character.y)

    for i in range(len(bigBalls)):
        bigBalls[i].update(character.x, character.y)

    WIN.fill(BLACK)

    for i in range(len(walls)):
        walls[i].draw(character)

    for i in range(len(smallBalls)):
        smallBalls[i].draw()
    
    for i in range(len(newWalls)):
        newWalls[i].draw(character)


    for i in range(len(bigBalls)):
        bigBalls[i].draw()

    box.update()

    box.draw(WIN)

    box2.update()

    box2.draw(WIN)
    
    pygame.display.update()


def pressedKeys(character, kw, ks, ka, kd, speed):
    if kw:
        character.y -= speed
    if ka:
        character.x -= speed
    if ks:
        character.y += speed
    if kd:
        character.x += speed

def ui(selected, style):
    pygame.draw.rect(WIN, WHITE, (61+16, HEIGHT-62, 54, 54))

    pygame.draw.rect(WIN, GREEN, ((selected-1)*61+16, HEIGHT-62, 54, 54))

    for x in range(16):
        pygame.draw.rect(WIN, COLOUR[x], (x*61+18, HEIGHT-60, 50, 50))

    pygame.draw.rect(WIN, WHITE, (WIDTH/2-27, 8, 54, 54))
    pygame.draw.rect(WIN, BLACK, (WIDTH/2-25, 10, 50, 50))

    if style == 1:
        pygame.draw.rect(WIN, COLOUR[selected-1], (WIDTH/2-3, 11, 6, 48))
    elif style == 2:
        pygame.draw.rect(WIN, COLOUR[selected-1], (WIDTH/2-24, 31, 48, 6))
    else:
        pygame.draw.polygon(WIN, COLOUR[selected-1], [(WIDTH/2-22, 13), (WIDTH/2-19, 11), (WIDTH/2+21, 49), (WIDTH/2+19, 52)])

def main():
    clock = pygame.time.Clock()
    input_box1 = InputBox(0, 0, 100, 32, text = 'Save')
    input_box2 = InputBox(WIDTH-200, 0, 100, 32, text = 'Friction (base 0.5)')

    character = Character(0,0)

    walls = []

    wall = Wall(-10000,0,10000,0, colour = LIGHT_GRAY)
    walls.append(wall)

    wall = Wall(0,-10000,0,10000, colour = LIGHT_GRAY)
    walls.append(wall)

    smallBalls = []

    bigBalls = []

    newWalls = []

    kw, ks, ka, kd, kz, kctrl = False, False, False, False, False, False

    selected = 1
    style = 1

    for i in range(NUMBALLS):
        size = random.uniform(2,6)
        c = round(382.5-63.75*size)

        c2 = round(282.5-13.75*size)

        ball = Ball(random.randint(0, WIDTH), random.randint(0, HEIGHT), size*1.5, colour = (c,c/2,c2))

        if size < 4.5:
            smallBalls.append(ball)
        else:
            bigBalls.append(ball)

    firstPoint = True

    speed = 5

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit()
            input_box1.handle_event(event, newWalls)
            input_box2.handle_event(event, None)

            friction = input_box2.friction

            if event.type == pygame.MOUSEBUTTONDOWN and not input_box1.active and not input_box2.active and event.button == 1:
                if firstPoint:
                    p1 = event.pos
                    p1 = p1[0] - CHARCENTER[0] + character.x,  p1[1] - CHARCENTER[1] + character.y
                    firstPoint = False
                else:
                    if style == 3:
                        newWalls.append(Wall(p1[0],  p1[1], event.pos[0] - CHARCENTER[0] + character.x, event.pos[1] - CHARCENTER[1] + character.y, colour = COLOUR[selected-1], friction = friction))
                    elif style == 1:
                        newWalls.append(Wall(p1[0],  p1[1], p1[0], event.pos[1] - CHARCENTER[1] + character.y, colour = COLOUR[selected-1], friction = friction))
                    else:
                        newWalls.append(Wall(p1[0],  p1[1], event.pos[0] - CHARCENTER[0] + character.x, p1[1], colour = COLOUR[selected-1], friction = friction))
                    firstPoint = True

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_w:
                    kw = True

                if event.key == pygame.K_s:
                    ks = True

                if event.key == pygame.K_a:
                    ka = True

                if event.key == pygame.K_d:
                    kd = True

                if event.key == pygame.K_r:
                    character.x, character.y = 0, 0

                if event.key == pygame.K_1 and selected != 1:
                    selected = 1
                elif event.key == pygame.K_1:
                    selected = 11
                if event.key == pygame.K_2 and selected != 2:
                    selected = 2
                elif event.key == pygame.K_2:
                    selected = 12
                if event.key == pygame.K_3 and selected != 3:
                    selected = 3
                elif event.key == pygame.K_3:
                    selected = 13
                if event.key == pygame.K_4 and selected != 4:
                    selected = 4
                elif event.key == pygame.K_4:
                    selected = 14
                if event.key == pygame.K_5 and selected != 5:
                    selected = 5
                elif event.key == pygame.K_5:
                    selected = 15
                if event.key == pygame.K_6 and selected != 6:
                    selected = 6
                elif event.key == pygame.K_6:
                    selected = 16
                if event.key == pygame.K_7:
                    selected = 7
                if event.key == pygame.K_8:
                    selected = 8
                if event.key == pygame.K_9:
                    selected = 9
                if event.key == pygame.K_0:
                    selected = 10
                if event.key == pygame.K_BACKQUOTE:
                    style += 1
                    if style == 4:
                        style = 1
                if event.key == pygame.K_EQUALS:
                    speed += 1
                if event.key == pygame.K_MINUS:
                    speed -= 1
                if event.key == pygame.K_LCTRL:
                    kctrl = True
                if event.key == pygame.K_z:
                    kz = True

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_w:
                    kw = False

                if event.key == pygame.K_s:
                    ks = False

                if event.key == pygame.K_a:
                    ka = False

                if event.key == pygame.K_d:
                    kd = False
                if event.key == pygame.K_LCTRL:
                    kctrl = False
                if event.key == pygame.K_z:
                    kz = False

        
        pressedKeys(character, kw, ks, ka, kd, speed)

        if kz and kctrl:
            try:
                newWalls.pop()
            except:
                pass
            kz = False

        update(input_box1, input_box2, walls, smallBalls, bigBalls, character, newWalls)

        if not firstPoint:
            if style == 3:
                blank = Wall(p1[0],  p1[1], pygame.mouse.get_pos()[0] - CHARCENTER[0] + character.x, pygame.mouse.get_pos()[1] - CHARCENTER[1] + character.y, colour = COLOUR[selected-1])
            elif style == 1:
                blank = Wall(p1[0],  p1[1], p1[0], pygame.mouse.get_pos()[1] - CHARCENTER[1] + character.y, colour = COLOUR[selected-1])
            else:
                blank = Wall(p1[0],  p1[1], pygame.mouse.get_pos()[0] - CHARCENTER[0] + character.x, p1[1], colour = COLOUR[selected-1])

            blank.draw(character)

        ui(selected, style)

        pygame.display.flip()
        clock.tick(30)


main()

