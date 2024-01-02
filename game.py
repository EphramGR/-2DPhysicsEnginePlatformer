import math
import pygame
import time
import random

WIDTH, HEIGHT = 1000, 800

WIN = pygame.display.set_mode((WIDTH, HEIGHT))

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

CHARW, CHARH = 20, 20

CHARX = WIDTH/2-(CHARW/2)
CHARY = HEIGHT/2-(CHARH/2)

CHARCENTER = (CHARX+(CHARW/2), CHARY+(CHARH/2))

pygame.init()
font = pygame.font.SysFont('arial', 20)

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
clock = pygame.time.Clock()

TESTFILE = 'test.txt'
#TESTFILE = 'ice.txt'
#TESTFILE = 'fall.txt'
#TESTFILE = 'play.txt'
#TESTFILE = 'benchmark.txt'

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
			print('boosting up')
			self.state(walls, False)


		if self.touching['down'] and self.touching['up'] and self.touching['right']:
			self.x -= 1
			print('boosting left')
			self.state(walls, False)

		if self.touching['down'] and self.touching['left'] and self.touching['up']:
			self.x += 1
			print('boosting right')
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

	def draw(self):
		pygame.draw.circle(WIN, self.colour, (self.x, self.y), self.size)

	def update(self, xdif, ydif, deltaTime):
		self.x -= xdif*self.size/BALLSPEED #* deltaTime
		self.y -= ydif*self.size/BALLSPEED #* deltaTime

		if self.x > WIDTH + self.size + 1:
			self.x -= WIDTH + (self.size*2)
		if self.x < -self.size - 1:
			self.x += WIDTH + (self.size*2)

		if self.y > HEIGHT + self.size + 1:
			self.y -= HEIGHT + (self.size*2)
		if self.y < -self.size - 1:
			self.y += HEIGHT + (self.size*2)


def collide(character, walls, x, y):
	rect = pygame.Rect(CHARX + x, CHARY + y, CHARW, CHARH)

	for i in range(len(walls)):
		if rect.clipline((CHARCENTER[0] - character.x + walls[i].x1, CHARCENTER[1] - character.y + walls[i].y1), (CHARCENTER[0] - character.x + walls[i].x2, CHARCENTER[1] - character.y + walls[i].y2)):
			return True, walls[i]

	return False, None

def update(character, walls, smallBalls, bigBalls):
	WIN.fill(BLACK)

	for i in range(len(smallBalls)):
		smallBalls[i].draw()
	
	for i in range(len(walls)):
		walls[i].draw(character)

	character.state(walls, True, bigBalls, smallBalls)
	
	#character.gravity()
	drag, friction, yfriction = move(character, walls, smallBalls, bigBalls)

	character.draw()

	for i in range(len(bigBalls)):
		bigBalls[i].draw()

	printStats(character, walls, drag, friction, yfriction)
	
	pygame.display.update()

def pressedKeys(character, walls, kw, ks, ka, kd):
	if kw:
		if character.touching['down']:
			character.userForce[1] = JUMPFORCE
		else:
			character.userForce[1] = 0
	else:
		character.userForce[1] = 0
	#if ks:
		#t, _ = collide(character, walls, 0, 1)
		#if not t:
			#character.y += 1

	if ka and kd:
		character.userForce[0] = 0
	else:
		if ka:
			if not character.touching['left']:
				character.userForce[0] = -MOVEFORCE

		elif kd:
			if not character.touching['right']:
				character.userForce[0] = MOVEFORCE
		else:
			character.userForce[0] = 0


def move(character, walls, smallBalls, bigBalls):
	drag, friction, yfriction = forceUpdate(character, walls)
	character.x += character.velocity[0] #* character.deltaTime
	character.y += character.velocity[1] #* character.deltaTime

	for i in range(len(smallBalls)):
		smallBalls[i].update(character.velocity[0], character.velocity[1], character.deltaTime)

	for i in range(len(bigBalls)):
		bigBalls[i].update(character.velocity[0], character.velocity[1], character.deltaTime)

	return drag, friction, yfriction

def forceUpdate(character, walls):
	yfriction = 0
	if character.touching['down']:
		#if line is horizontal
		if abs(character.touchingWall['down'].angle) < 0.00001 or abs(character.touchingWall['down'].angle - PI) < 0.00001:
			character.velocity[1] = 0
			character.gravityForce = [0,0]
			#normalForce = 

		else:
			character.gravityForce[1] = math.sin(character.touchingWall['down'].angle) * GRAVITY
			character.gravityForce[0] = math.cos(character.touchingWall['down'].angle) * GRAVITY

			if character.touchingWall['down'].slope < 0:
				character.gravityForce[1] *= -1
				character.gravityForce[0] *= -1

			yfriction = character.touchingWall['down'].friction * GRAVITY

			if character.gravityForce[0] < 0.002 and character.gravityForce[0] > 0:
				character.gravityForce[1] = 0
				character.gravityForce[0] = 0

		frictionForce = character.touchingWall['down'].friction * GRAVITY
		dragForce = 0

		test = character.velocity[0] 

		test += character.userForce[0] + character.gravityForce[0]

		if character.velocity[0] < SPEEDCAP and character.velocity[0] > SPEEDCAPN:
			if test > SPEEDCAP:
				character.velocity[0] = SPEEDCAP
			elif test < SPEEDCAPN:
				character.velocity[0] = SPEEDCAPN
			else:
				character.velocity[0] = test
	else:
		character.gravityForce = [0, GRAVITY]
		frictionForce = 0
		dragForce = DRAG * math.sqrt(character.velocity[0]**2 + character.velocity[1]**2)

		character.velocity[0] += character.userForce[0] + character.gravityForce[0]###

	if character.velocity[0] > 0:
		character.velocity[0] -= frictionForce + dragForce
		if character.velocity[0] < 0:
			character.velocity[0] = 0

	elif character.velocity[0] < 0:
		character.velocity[0] += frictionForce + dragForce
		if character.velocity[0] > 0:
			character.velocity[0] = 0

	if character.velocity[0] > AIRSC:
		character.velocity[0] = AIRSC
	elif character.velocity[0] < AIRSCN:
		character.velocity[0] = AIRSCN

	character.velocity[1] += character.userForce[1] + character.gravityForce[1] - yfriction

	if character.touching['right'] and character.velocity[0] >= 0:
		if character.touchingWall['right'].slope == math.inf or (abs(character.touchingWall['right'].angle) < 0.00001 or abs(character.touchingWall['right'].angle - PI) < 0.00001):
			character.velocity[0] = 0
		else:
			character.velocity[0] += character.userForce[0] * math.cos(character.touchingWall['right'].angle)
			character.velocity[1] += character.userForce[0] * math.sin(character.touchingWall['right'].angle)

	if character.touching['left'] and character.velocity[0] < 0:
		if character.touchingWall['left'].slope == math.inf or (abs(character.touchingWall['left'].angle) < 0.00001 or abs(character.touchingWall['left'].angle - PI) < 0.00001):
			character.velocity[0] = 0
		else:
			character.velocity[0] += character.userForce[0] * abs(math.cos(character.touchingWall['left'].angle))
			character.velocity[1] += character.userForce[0] * abs(math.sin(character.touchingWall['left'].angle))


	if character.touching['up']:
		if character.velocity[1] < 0:
			character.velocity[1] = 0
	elif character.velocity[1] < -2:
		character.velocity[1] = -2

	return dragForce, frictionForce, yfriction

def printStats(character, walls, drag, friction, yfriction):
	arr = []

	arr.append('velocity: ' + str(character.velocity))

	arr.append('userForce: ' + str(character.userForce))

	arr.append('gravity: ' + str(character.gravityForce))

	arr.append('normalForce: ' + str(character.normalForce))

	arr.append('Drag: ' + str(drag))

	arr.append('friction: ' + str(friction))

	arr.append('yfriction: ' + str(yfriction))

	arr.append('coords:' + str(round(character.x)) + ', ' + str(round(character.y)))

	arr.append('FPS:' + str(round(clock.get_fps(),2)))

	arr.append('Delta Time: ' + str(round(character.deltaTime, 5)))


	for key in character.touching:
		arr.append(key + ': '+ str(character.touching[key]))

	for x in range(len(arr)):
		text = font.render(arr[x], True, WHITE)

		textRect = text.get_rect()
		textRect.topleft = (5, x*20)
		WIN.blit(text, textRect)

def load(file):
	walls = []

	filehndl = open(file, 'r')
	filetxt = filehndl.read()

	string = filetxt.split('\n')

	for x in range(len(string)):
		if string[x][0:5] == 'wall:':
			temp = string[x].split(' ')
			temp[6] = temp[6].replace('(', '').replace(',','')
			temp[7] = temp[7].replace(',','')
			temp[8] = temp[8].replace(')', '')
			c = (float(temp[6]), float(temp[7]), float(temp[8]))
			walls.append(Wall(float(temp[1]), float(temp[2]), float(temp[3]), float(temp[4]), friction = float(temp[5]), colour = c))

	return walls

def main():
	character = Character(0,0, colour = SURPRISE)#random.randint(1, 1000), random.randint(1, 1000))

	walls = load(TESTFILE)

	smallBalls = []

	bigBalls = []

	for i in range(NUMBALLS):
		size = random.uniform(2,6)
		c = round(382.5-63.75*size)

		c2 = round(282.5-13.75*size)

		ball = Ball(random.randint(0, WIDTH), random.randint(0, HEIGHT), size*1.5, colour = (c,c/2,c2))

		if size < 4.5:
			smallBalls.append(ball)
		else:
			bigBalls.append(ball)

	'''for i in range(3):
		wall = Wall(random.randint(1, 500), random.randint(1, 500), random.randint(500, 1000), random.randint(500, 1000))
		walls.append(wall)

	for i in range(3):
		wall = Wall(random.randint(500, 1000), random.randint(500, 1000), random.randint(1, 500), random.randint(1, 500))
		walls.append(wall)'''


	kw, ks, ka, kd = False, False, False, False

	while True:
		character.now = time.time()
		character.deltaTime = character.now - character.previousTime
		character.previousTime = character.now

		update(character, walls, smallBalls, bigBalls)


		pressedKeys(character, walls, kw, ks, ka, kd)

		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				exit()

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

			if event.type == pygame.KEYUP:
				if event.key == pygame.K_w:
					kw = False

				if event.key == pygame.K_s:
					ks = False

				if event.key == pygame.K_a:
					ka = False

				if event.key == pygame.K_d:
					kd = False

		clock.tick(FRAME_RATE)

main()

