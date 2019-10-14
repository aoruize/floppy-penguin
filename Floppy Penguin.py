# Floppy Penguin.py
# Matthew Ao, Lucy Zhao
# June 14, 2018
# A collision-based platform game where the player plays as a penguin trying to eat all the fish in a level.

import pygame
import sys 
pygame.init()

from random import randint
from pygame.locals import *
from FloppyPenguinSettings import *

# setting game display
gameDisplay = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Floppy Penguin")
clock = pygame.time.Clock()

# display variables
displayCounter, displayOn, fullscreen = 0, -1, False
global font
font = pygame.font.SysFont("Raleway", 36)
global fontBold
fontBold = pygame.font.SysFont("Raleway Black, bold", 48)
global fontBoldBold
fontBoldBold = pygame.font.SysFont("Raleway Black, bold", 72)

# menu variables
startPage, mainMenu,  = True, False
instructionsMenu, instructionsPageNum, instructionsNextLock, instructionsBackLock = False, 1, True, False
pauseMenu, optionsMenu = False, False
global mixerVolume
mixerVolume = 1.0

# level variables
levelMenu = False
levelNum, playLevel = 1, False
winLevel, loseLevel = False, False

# list that contains all the level lock variables
lockLevel = list([])
for i in range(0, 20):
    lockLevel.append(i)
    # level 1 starts off unlocked
    if lockLevel[i] == 1:
        lockLevel[i] = False 
    # end if
    # all other levels start off locked
    else:
        lockLevel[i] = True
    # end else
# end for

# ============== loading sounds ================
# start game sound
startSound = pygame.mixer.Sound("start.ogg")
startSound.set_volume(mixerVolume)

# background music
pygame.mixer.music.load("backgroundMusic.ogg")
pygame.mixer.music.set_volume(mixerVolume)

# fish eating sound
fishEatSound = pygame.mixer.Sound("fishEat.ogg")

# win level sound
winLevelSound = pygame.mixer.Sound("winLevel.ogg")

# wub gane sound
winGameSound = pygame.mixer.Sound("winGame.ogg")

# game over sound
gameOverSound = pygame.mixer.Sound("gameOver.ogg")

# ============== loading images ================
# title images
titleImage = pygame.image.load("titleFull.png").convert_alpha() 
titleStart = pygame.image.load("titleStart.png").convert_alpha()

# menu backgrounds
menuBackground1 = pygame.image.load("background_00.png").convert()
mainMenuBackground = pygame.image.load("background_01.png").convert()
levelMenuBackground = pygame.image.load("background_02.png").convert()

# play button penguin icons
menuPenguin1 = pygame.image.load("penguin_icon1.png").convert_alpha() 
menuPenguin2 = pygame.image.load("penguin_icon2.png").convert_alpha()

# pause menu transparent overlay
pauseScreen = pygame.image.load("opaque.png").convert_alpha() 

# level background
levelBackground = pygame.image.load("background_2.png").convert()

# win and lose displays
winDisplay = pygame.image.load("winDisplay.png").convert_alpha()
loseDisplay = pygame.image.load("loseDisplay.png").convert_alpha()

# platforms
platform1 = pygame.image.load("platform1.png").convert_alpha()
platform2 = pygame.image.load("platform2.png").convert_alpha()
platform3 = pygame.image.load("platform3.png").convert_alpha()

# fish
fishRight = pygame.image.load("fishRight0.png").convert_alpha()
fishRightRed = pygame.image.load("fishRight1.png").convert_alpha()
fishRightPurple = pygame.image.load("fishRight2.png").convert_alpha()
fishLeft = pygame.image.load("fishLeft0.png").convert_alpha()
fishLeftRed = pygame.image.load("fishLeft1.png").convert_alpha()
fishLeftPurple = pygame.image.load("fishLeft2.png").convert_alpha()

# water
water = pygame.image.load("water.png").convert_alpha()

# _______________________________________________________________
#
#                                       DEFINING CLASSES
# _______________________________________________________________

# individual platform class 
class Platform():
    def __init__(self, x, y, image):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
    # end def

    # defining collision testing 
    def test(self, player):
        if player.rect.colliderect(self.rect):
            return self
        # end if
        return None
    # end def
# end class

class Platforms():
    def __init__(self):
        # all platforms will be contained in a list
        self.container = list([])
    # end def

    # this function adds a new platform to the platforms list
    def add(self, plat):
        self.container.append(plat)
    # end def

    # this function detects collisions for every platform in the platforms list
    def testCollision(self, player):

        k = pygame.key.get_pressed()
        
        # function won't test for collision if the player isn't falling or sinking
        if not ((player.y < WATER and player.falling) or player.sinking):
            return False
        # end if
        
        # loop through every platform in the platforms list
        for plat in self.container:
            # for each platform, test whether the player is colliding with the platform; if so, the platform object will return itself, if not, the platform object will return nothing
            result = plat.test(player)
            # if platform object is returned (if player colliding with platform), player.currentPlatform is set to the returned platform object and player is set on top of platform
            if result:
                player.currentPlatform = result
                if player.underwater:
                    player.sinking = False
                # end if
                if not player.underwater:
                    player.y = result.rect.top - player.height
                    player.falling = False
                    player.fallVelocity = 0
                # end if
            # end if
        # end for
    # end def

    # drawing the platform
    def draw(self):
        display = pygame.display.get_surface()
        for plat in self.container:
            display.blit(plat.image, plat.rect.topleft)
        # end for
    # end def

    # executing the platforms class
    def execute(self, player):      
        self.draw()
        self.testCollision(player)
    # end def
# end class

# individual fish class
class Fish():
    def __init__(self, x, y, image, velocity):
        self.image = image
        self.x, self.y = x, y
        self.width, self.height = 48, 42
        if self.image in [fishRight, fishRightRed, fishRightPurple]:
            self.velocity = velocity
        # end if
        elif self.image in [fishLeft, fishLeftRed, fishLeftPurple]:
            self.velocity = -velocity
        # end elif
    # end def

    # defining collision testing 
    def test(self, player):
        # if player collides with top of platform, the current platform is returned to the Platforms testCollision function
        if player.rect.colliderect((self.x, self.y, self.width, self.height)):
            fishEatSound.set_volume(mixerVolume)
            fishEatSound.play()
            return "EAT"
        # end if
        if self.x > WIDTH and self.image in [fishRight, fishRightRed, fishRightPurple]:
            return "LOSE"
        # end if
        if self.x < 0 - self.width and self.image in [fishLeft, fishLeftRed, fishLeftPurple]:
            return "LOSE"
        # end if
        return None
    # end def
# end class

class Fishies():
    def __init__(self):
        # all platforms will be contained in a list
        self.container = list([])
        self.counter = 0
    # end def
    
    # defining adding fish to list
    def add(self, fish):
        self.container.append(fish)
        self.counter += 1
    # end def

    # defining collision testing 
    def testCollision(self, player):
        # loop through every fish in the fish container list
        for fish in self.container:
            # for each fish, test whether the player is colliding with the fish; if so, the fish object will return itself, if not, the fish object will return nothing
            result = fish.test(player)
            
            # if fish object is returned (if player colliding with fish), that fish instance will be eaten (removed from the fish list)
            if result == "EAT":
                self.container.remove(fish)
                self.counter -= 1
                if self.counter == 0:
                    return "WIN"
            if result == "LOSE":
                return "LOSE"
            # end if
        # end for
    # end def

    # drawing the fish
    def draw(self):
        display = pygame.display.get_surface()
        for fish in self.container:

            # fish constantly swims to the right
            fish.x += fish.velocity
            display.blit(fish.image, (fish.x, fish.y))

            # displaying fish count at top right corner of level
            fishDisplay = fontBold.render("FISH REMAINING   ", 0, WHITE)
            display.blit(fishDisplay, (750, 30))
            fishCountDisplay = fontBoldBold.render(str(self.counter), 0, WHITE)
            display.blit(fishCountDisplay, (1150, 10))
            levelDisplay = fontBoldBold.render(str("LEVEL " + str(levelNum)), 0, WHITE)
            display.blit(levelDisplay, (30, 20))
            # end if
        # end for
    # end def

    # executing the fish class
    def execute(self, player):
        self.testCollision(player)
        self.draw()
    # end def
# end class

# player class      
class Player():
    def __init__(self, velocity, maxJumpRange):    
        self.velocity, self.maxJumpRange = velocity, maxJumpRange
    # end def

    # defining player initial location 
    def setLocation(self, x, y):
        self.x, self.y = x, y
        self.width, self.height = 72, 64
        self.faceRight = True
        self.current = 0
        self.xVelocity, self.yVelocity, self.jumpVelocity = 0, 0, 0.4
        self.jumping, self.falling, self.sinking = False, True, False
        self.jumpCounter, self.fallVelocity, self.sinkVelocity = 0, 0, 0.5
        self.swimCounter, self.walkCounter = 0, 0
        self.currentPlatform = None
    # end def

    # defining player sound effects 
    def sounds(self):
        # splash sound effect
        self.splashNum = randint(1, 3)
        self.splashSound = pygame.mixer.Sound('splash' + str(self.splashNum) + '.ogg')
        self.splashSound.set_volume(mixerVolume)

        # surfacing sound effect
        self.swimNum = randint(1, 4)
        self.swimSound = pygame.mixer.Sound('swim' + str(self.swimNum) + '.ogg')
        self.swimSound.set_volume(mixerVolume/5)

        # swimming sound effect
        self.swimmingNum = randint(1, 2)
        self.swimmingSound = pygame.mixer.Sound('swimming' + str(self.swimmingNum) +'.ogg')
        self.swimmingSound.set_volume(mixerVolume)
    # end def

    # defining player controls 
    def keys(self):
        
        k = pygame.key.get_pressed()

        # setting conditions when player is underwater
        if self.y > WATER-36:
            # play splash sound effect upon falling into water at a fall velocity of > 2
            if self.falling and self.fallVelocity > 2:
                self.splashSound.play()
            # end if
            self.underwater = True
        # end if

        # setting conditions when player is not underwater
        else:
            if self.sinking:
                self.swimSound.play()
            # end if
            self.underwater = False
        # end else

        # controls when player is underwater     
        if self.underwater:

            # play swimming sounds at random intervals while completely submerged
            if self.swimCounter%(self.swimNum*self.swimmingNum*50) == 0 and self.y > WATER:
                self.swimmingSound.play()

            # setting default player sprite orientations when underwater
            if self.faceRight == True:
                self.current = 0
            # end if
            else:
                self.current = 1
            #end else

            # moving the player right, underwater
            if (k[K_d] or k[K_RIGHT]): 

                # if player was swimming left, gradually reduce leftward velocity
                if self.xVelocity < 0:
                    self.xVelocity += self.velocity
                # end if

                # accelerate player towards right
                self.xVelocity += 0.4*self.velocity
                self.faceRight = True
                if self.xVelocity > 1:
                    self.current = 2
                    # player sprite orientation faces right upon swimming with x velocity of > 1 
                # end if
            # end elif

            # moving the player left, underwater
            elif (k[K_a] or k[K_LEFT]):

                # if player was swimming right, gradually reduce rightward velocity
                if self.xVelocity > 0:
                    self.xVelocity -= self.velocity
                # end if

                # accelerate player towards left
                self.xVelocity -= 0.4*self.velocity

                # set player to not facing right
                self.faceRight = False

                # player sprite orientation faces left after swimming with x velocity of < -1
                if self.xVelocity < -1:
                    self.current = 3
                # end if
            # end elif

            # reduce right velocity to 0 upon releasing right controls
            elif self.xVelocity > 0 and not (k[K_d] or k[K_RIGHT]):
                self.xVelocity -= 2*self.velocity
            # end elif
            # reduce left velocity to 0 upon releasing left controls
            elif self.xVelocity < 0 and not (k[K_a] or k[K_LEFT]):
                self.xVelocity += 2*self.velocity
            # end elif

            # moving the player up, underwater
            if (k[K_w] or k[K_UP]): 

                # if player was swimming down, gradually reduce downward velocity
                if self.yVelocity > 0:
                    self.yVelocity -= self.velocity
                # end if

                # accelerate player upwards
                self.yVelocity -= 1.5*self.velocity

                # # player sprite orientation faces up + right upon swimming in that direction
                if self.faceRight == True and self.yVelocity <= -2: 
                    self.current = 8
                    # player sprite orientation faces further up after gaining velocity                    
                    if self.yVelocity <= -4:
                        self.current = 10
                    # end if
                # end if
                
                # player sprite orientation faces up+left upon swimming in that direction
                elif self.yVelocity <= -2:
                    self.current = 9
                    # player sprite orientation faces further up after gaining velocity
                    if self.yVelocity <= -4:
                        self.current = 11
                    # end if
                # end elif
            # end if  

            # moving the player down, underwater
            elif (k[K_s] or k[K_DOWN]):

                # if player was swimming up, gradually reduce upward velocity
                if self.yVelocity < 0:
                    self.yVelocity += self.velocity

                # accelerate player downwards
                self.yVelocity += self.velocity
                
                # player sprite orientation faces down+right upon swimming in that direction
                if self.faceRight == True:
                    self.current = 4
                    # player sprite orientation faces further down after gaining velocity
                    if self.yVelocity >= 2:
                        self.current = 6
                    # end if
                #end if

                # player sprite orientation faces down+left upon swimming in that direction   
                else:
                    self.current = 5
                    # player sprite orientation faces further down after gaining velocity
                    if self.yVelocity >= 2:
                        self.current = 7
                    #end if
                #end else
            # end elif

            # gradually reduce downward velocity to 0 after releasing down controls
            elif self.yVelocity > 0 and not (k[K_s] or k[K_DOWN]):
                self.yVelocity -= 2*self.velocity
            # end elif
            # gradually reduce upward velocity to 0 after releasing up controls
            elif self.yVelocity < 0 and not (k[K_w] or k[K_UP]):
                self.yVelocity += 2*self.velocity
            # end elif
        # end if

        # controls when player is above water
        elif not self.underwater:

            # gradually decrease x and y velocity after the player surfaces from the water
            if self.yVelocity < 0:
                self.yVelocity -= 0.1*self.yVelocity
                self.xVelocity -= 0.1*self.xVelocity
            # end if

            # moving the player right, above water
            if k[K_d] or k[K_RIGHT]:
                self.xVelocity = 1
                self.faceRight = True
                # loop walking animation
                self.walkCounter += 1
                if self.walkCounter%5 == 0:
                    self.current = 20
                if self.walkCounter%10 == 0:
                    self.current = 22
                if self.walkCounter%15 == 0:
                    self.current = 24
                if self.walkCounter%20 == 0:
                    self.current = 26
            # end if

            # moving the player left, above water
            elif k[K_a] or k[K_LEFT]:
                self.xVelocity = -1
                self.faceRight = False
                # loop walking animation
                self.walkCounter += 1
                if self.walkCounter%5 == 0:
                    self.current = 21
                if self.walkCounter%10 == 0:
                    self.current = 23
                if self.walkCounter%15 == 0:
                    self.current = 25
                if self.walkCounter%20 == 0:
                    self.current = 27
            # end elif

            else:
                self.xVelocity = 0
            # setting default player sprite orientations when above water

            if self.faceRight and not (k[K_d] or k[K_RIGHT]):
                self.current = 18
            # end if
            elif not self.faceRight and not (k[K_a] or k[K_LEFT]):
                self.current = 19
            #end else

            # player x remains unchanged otherwise
            # end else

            if (k[K_w] or k[K_UP]) and not self.jumping and not self.falling:
                self.jumping = True
            # end if
        # end elif
    # end def

    # defining player movement 
    def move(self):

        # setting movement boundaries at x = 0 and x = WIDTH
        if self.x > 0 and self.x + self.xVelocity < 0: 
            self.xVelocity = 0
        # end elif

        self.x += self.xVelocity
        self.y += self.yVelocity

        # player loses if beyond screen boundaries
        if self.y > HEIGHT or self.x > WIDTH:
            return "LOSE"
        
        # if player is underwater, player is sinking but not falling
        if self.underwater and not self.currentPlatform:
            self.sinking = True
            self.swimCounter += 1
            self.falling = False
        # end if

        # if player is above water and not on a platform, player is falling but not sinking
        elif not self.underwater and not self.currentPlatform:
            self.falling = True
            self.sinking = False
        # end if
            
        # if player is on a platform, test for when the platform is no longer colliding with player
        if self.currentPlatform:
            if not self.currentPlatform.test(self):
                # reset sinking to true if player is underwater after leaving the platform
                if self.underwater:
                    self.sinking = True
                # end if
                
                # reset falling to true if player is not underwater after leaving the platform
                elif not self.underwater:
                    self.falling = True
                # end elif
                
                # reset player's current platform to none
                self.currentPlatform = None
            # end if
        # end if
        
        # if player is sinking, add constant sink velocity to player y
        if self.sinking:
            self.fallVelocity, self.sinkVelocity = 0, 0.5
            self.y += self.sinkVelocity
        # end if
        
        # if player is jumping, accelerate jumping velocity and subtract it from player y
        if self.jumping:
            self.jumpCounter += 0.1
            self.jumpVelocity += self.jumpCounter

            # if player is surfacing from water, calculate jump velocity based on swimming y velocity
            if self.yVelocity != 0:
                self.y -= (self.maxJumpRange-self.jumpVelocity)*1.5*-self.yVelocity
                # end if

            # otherwise, if jumping on land, calculate jump velocity without swimming y velocity
            else:
                self.y -= (self.maxJumpRange-self.jumpVelocity)**4
            # end else

            # when jumping velocity hits the player's maximum jump range, stop moving up
            if self.jumpVelocity >= self.maxJumpRange:
                self.jumping = False
                self.jumpCounter, self.jumpVelocity = 0, 0.4
            # end if

            # player sprite orientations upon jumping and facing right
            if self.faceRight and self.jumpCounter > 0.2 and self.fallVelocity <= 1:
                self.current = 12
                if self.jumpCounter > 0.6 and self.fallVelocity <= 1:
                    self.current = 14
                # end if
            # end if

            # player sprite orientations upon jumping and facing left
            elif self.jumpCounter > 0.2 and self.fallVelocity <= 1:
                self.current = 13
                if self.jumpCounter > 0.6 and self.fallVelocity <= 1:
                    self.current = 15
                # end if
            # end elif
        # end if

        # if player is falling, accelerate falling velocity and add it to player y
        if self.falling:
            self.fallVelocity += 0.1         
            self.y += self.fallVelocity

            # player sprite orientation when falling and facing right
            if self.faceRight and self.fallVelocity > 1:
                self.current = 16
            # end if

            # player sprite orientation when falling and facing left
            elif self.fallVelocity > 1:
                self.current = 17
            # end elif
        # end if
    # end def

    # defining displaying the player 
    def load(self):
        self.image = pygame.image.load('penguin_' + str(self.current) + '.png').convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.topleft = (self.x, self.y)
    # end def
    
    def display(self):
        gameDisplay.blit(self.image, self.rect)
    # end def

    # executing all player components 
    def execute(self):
        self.load()
        self.display()
        self.sounds()
        self.keys()
        self.move()
    # end def
# end class

# _______________________________________________________________
#
#                                            DEFINING FUNCTIONS
# _______________________________________________________________

# button function
def button(text, x, y, w, h, colourDefault, colourHover, fontSize, locked):

    # button clicking sound effect
    buttonSound = pygame.mixer.Sound("buttonclick.ogg")
    buttonSound.set_volume(mixerVolume/3.0)

    # font sizes for normal + large text
    size1 = fontSize
    size2 = 6+fontSize
    
    # setting up fonts
    font1 = pygame.font.SysFont("Raleway Black", size1)
    font2 = pygame.font.SysFont("Raleway Black", size2)

    # polling for pygame events
    pygame.event.poll()
    (mouseX, mouseY) = pygame.mouse.get_pos()

    # if hovering over button, button text is enlarged, button text colour is set to colourDefault, and button colour changes to colourHover
    if mouseX >= x and mouseX <= x+w and mouseY >= y and mouseY <= y+h and not locked:
        pygame.draw.rect(gameDisplay, colourHover, (x, y, w, h), 0)
        textDisplay = font2.render(text, 0, colourDefault)
        gameDisplay.blit(textDisplay, (x+w/2-(len(text)*size2)/3.5, y+h/2-size2/1.8)) # blitting + centering the text

        # return 'True' if left mouse button is clicked 
        if pygame.mouse.get_pressed()[0]:
            buttonSound.play()
            pygame.time.delay(100)
            return True
        # end if
    # end if

    # if not hovering over button, button text colour is set to colourHover, and button colour is set to colourDefault
    elif not locked:
        pygame.draw.rect(gameDisplay, colourDefault, (x, y, w, h), 0)
        textDisplay = font1.render(text, 0, colourHover)
        gameDisplay.blit(textDisplay,(x+w/2-(len(text)*size1)/3.5, y+h/2-size1/1.8)) # blitting + centering the text
    # end else

    # button is disabled if locked is WHITE; the button colour is set to white
    elif locked == "WHITE":
        pygame.draw.rect(gameDisplay, WHITE, (x, y, w, h), 0)
        textDisplay = font1.render(text, 0, colourHover)
        gameDisplay.blit(textDisplay,(x+w/2-(len(text)*size1)/3.5, y+h/2-size1/1.8)) # blitting + centering the text
    # end elif
    
    # button is disabled if locked is True; the button colour is set darker and doesn't change
    else:
        pygame.draw.rect(gameDisplay, GREY, (x, y, w, h), 0)
        textDisplay = font1.render(text, 0, GREY_BLUE)
        gameDisplay.blit(textDisplay,(x+w/2-(len(text)*size1)/3.5, y+h/2-size1/1.8)) # blitting + centering the text
    # end else
# end def
    
def addFish(level):
    if level == 1:
        FISH.add(Fish(100, 500, fishRight, 1))
        FISH.add(Fish(70, 400, fishRight, 1))
        FISH.add(Fish(120, 600, fishRight, 1))
    # end if
    elif level == 2:
        FISH.add(Fish(100, 500, fishRight, 2))
        FISH.add(Fish(800, 600, fishRight, 1))
    # end elif
    elif level == 3:
        FISH.add(Fish(100, 500, fishRight, 2))
        FISH.add(Fish(70, 300, fishRight, 3))
        FISH.add(Fish(400, 600, fishRight, 1))
        FISH.add(Fish(700, 500, fishRight, 1.5))
        FISH.add(Fish(500, 300, fishRight, 1))
        FISH.add(Fish(800, 600, fishRight, 1))
    # end elif
    elif level == 4:
        FISH.add(Fish(100, 500, fishRight, 2))
        FISH.add(Fish(70, 300, fishRight, 3))
        FISH.add(Fish(400, 600, fishRight, 1))
        FISH.add(Fish(700, 500, fishRight, 1.5))
        FISH.add(Fish(500, 300, fishRight, 1))
        FISH.add(Fish(800, 600, fishLeft, 1))
    elif level == 5:
        FISH.add(Fish(-100, 500, fishRight, 2))
        FISH.add(Fish(-800, 300, fishRightRed, 5))
    elif level == 6:
        FISH.add(Fish(-100, 500, fishRight, 2))
        FISH.add(Fish(-70, 300, fishRight, 3))
        FISH.add(Fish(-400, 600, fishRight, 1))
        FISH.add(Fish(-5000, 400, fishRightRed, 5))
        FISH.add(Fish(1700, 500, fishLeft, 1.5))
        FISH.add(Fish(2000, 200, fishLeft, 1))
        FISH.add(Fish(1800, 600, fishLeftRed, 5))
    elif level == 7:
        FISH.add(Fish(-2000, 500, fishRightRed, 8))
        FISH.add(Fish(1500, 600, fishLeft, 1))
        FISH.add(Fish(2120, 650, fishLeft, 1))
        FISH.add(Fish(1820, 250, fishLeft, 1))
        FISH.add(Fish(-7000, 300, fishRightRed, 9))
        FISH.add(Fish(-4000, 200, fishRightRed, 8))
        FISH.add(Fish(-700, 200, fishRightRed, 7))
        FISH.add(Fish(-5000, 200, fishRightRed, 8))
        FISH.add(Fish(-9000, 600, fishRightRed, 10))
    elif level == 8:
        FISH.add(Fish(1100, 200, fishLeft, 1))
        FISH.add(Fish(7000, 300, fishLeftRed, 5))
        FISH.add(Fish(1400, 600, fishLeft, 1))
        FISH.add(Fish(1700, 500, fishLeft, 1.5))
        FISH.add(Fish(1500, 300, fishLeft, 1))
        FISH.add(Fish(1800, 650, fishLeft, 1))
        FISH.add(Fish(-2000, 500, fishRight, 2))
        FISH.add(Fish(-15000, randint(130, 670), fishRightPurple, 9))
        FISH.add(Fish(-4000, 600, fishRightRed, 4))
        FISH.add(Fish(-900, 670, fishRightRed, 7))
        FISH.add(Fish(-600, 300, fishRightRed, 7))
        FISH.add(Fish(-700, 500, fishRightRed, 7))
        FISH.add(Fish(-1500, 300, fishRight, 1.5))
        FISH.add(Fish(-900, 600, fishRight, 2))
    elif level == 9:
        FISH.add(Fish(100, randint(130, 670), fishRightPurple, 2))
        FISH.add(Fish(70, randint(130, 670), fishRightPurple, 2))
        FISH.add(Fish(400, randint(130, 670), fishRightPurple, 1))
        FISH.add(Fish(700, randint(130, 670), fishRightPurple, 1.5))
        FISH.add(Fish(500, randint(130, 670), fishRightPurple, 1))
        FISH.add(Fish(300, randint(130, 670), fishRightPurple, 1))
        FISH.add(Fish(-30, randint(130, 670), fishRightPurple, 2))
        FISH.add(Fish(-300, randint(130, 670), fishRightPurple, 1))
        FISH.add(Fish(-700, randint(130, 670), fishRightPurple, 1.5))
        FISH.add(Fish(-500, randint(130, 670), fishRightPurple, 1))
        FISH.add(Fish(-800, randint(130, 670), fishRightPurple, 1))
        FISH.add(Fish(-1000, randint(130, 670), fishRightPurple, 2))
        FISH.add(Fish(-1400, randint(130, 670), fishRightPurple, 2))
        FISH.add(Fish(-1500, randint(130, 670), fishRightPurple, 1.5))
        FISH.add(Fish(-1550, randint(130, 670), fishRightPurple, 2))
        FISH.add(Fish(-1600, randint(130, 670), fishRightPurple, 2))
    elif level == 10:
        FISH.add(Fish(-1700, 320, fishRight, 1))
        FISH.add(Fish(1900, 600, fishLeft, 1))
        FISH.add(Fish(2200, 400, fishLeft, 1))
        FISH.add(Fish(-1700, 500, fishRightRed, 7))
        FISH.add(Fish(1900, 200, fishLeftRed, 7))
        FISH.add(Fish(-3200, 300, fishRightRed, 7))
        FISH.add(Fish(-1800, randint(400, 670), fishRightPurple, 2))
        FISH.add(Fish(-2800, randint(400, 670), fishRightPurple, 2))
        FISH.add(Fish(-3800, randint(400, 670), fishRightPurple, 2))
        FISH.add(Fish(-4800, randint(300, 670), fishRightPurple, 2))
        FISH.add(Fish(-5800, randint(300, 670), fishRightPurple, 2))
        FISH.add(Fish(2800, randint(300, 670), fishLeftPurple, 2))
        FISH.add(Fish(3800, randint(200, 670), fishLeftPurple, 2))
        FISH.add(Fish(4800, randint(200, 670), fishLeftPurple, 2))
        FISH.add(Fish(5800, randint(200, 670), fishLeftPurple, 2))
        FISH.add(Fish(6800, randint(130, 670), fishLeftPurple, 2))
        FISH.add(Fish(-1800, randint(400, 670), fishRightPurple, 2))
        FISH.add(Fish(-2800, randint(400, 670), fishRightPurple, 2))
        FISH.add(Fish(-3800, randint(400, 670), fishRightPurple, 2))
        FISH.add(Fish(-4800, randint(300, 670), fishRightPurple, 2))
        FISH.add(Fish(-5800, randint(300, 670), fishRightPurple, 2))
        FISH.add(Fish(2800, randint(300, 670), fishLeftPurple, 2))
        FISH.add(Fish(3800, randint(200, 670), fishLeftPurple, 2))
        FISH.add(Fish(4800, randint(200, 670), fishLeftPurple, 2))
        FISH.add(Fish(5800, randint(200, 670), fishLeftPurple, 2))
        FISH.add(Fish(6800, randint(130, 670), fishLeftPurple, 2))
        FISH.add(Fish(-25000, 300, fishRightRed, 7))
        FISH.add(Fish(-25400, 400, fishRightRed, 7))
        FISH.add(Fish(-25800, 500, fishRightRed, 7))
        FISH.add(Fish(-26200, 600, fishRightRed, 7))
        FISH.add(Fish(-26600, 650, fishRightRed, 7))
        FISH.add(Fish(-27000, 550, fishRightRed, 7))
        FISH.add(Fish(-27400, 400, fishRightRed, 7))
        FISH.add(Fish(-27800, 300, fishRightRed, 7))
        FISH.add(Fish(-28200, 200, fishRightRed, 7))
        FISH.add(Fish(-28600, 180, fishRightRed, 7))
        FISH.add(Fish(-29000, 250, fishRightRed, 7))
        FISH.add(Fish(-29400, 300, fishRightRed, 7))
        FISH.add(Fish(-29800, 400, fishRightRed, 7))
        FISH.add(Fish(-30200, 500, fishRightRed, 7))
        FISH.add(Fish(-30600, 650, fishRightRed, 7))
# end def

def level(level):
    penguin.setLocation(penguinStartX, penguinStartY)
    FISH.counter = 0
    del FISH.container[:]
    addFish(level)
# end def

# _______________________________________________________________
#
#                               INSTANTIATING CLASSES + FUNCTIONS
# _______________________________________________________________

# instantiate player class
penguin = Player(0.02, 2.0)
penguinStartX, penguinStartY = 150, 50
penguin.setLocation(penguinStartX, penguinStartY)
penguin.load()

# instantiate platform classes
PLATFORMS = Platforms()
PLATFORMS.add(Platform(0, 128, platform1))
PLATFORMS.add(Platform(10, 500, platform3))
PLATFORMS.add(Platform(150, 480, platform2))
PLATFORMS.add(Platform(300, 560, platform2))
PLATFORMS.add(Platform(600, 420, platform3))
PLATFORMS.add(Platform(880, 400, platform3))
PLATFORMS.add(Platform(800, 520, platform3))
PLATFORMS.add(Platform(1020, 600, platform2))

# instantiate fish class
FISH = Fishies()

# _______________________________________________________________
#
#                                                       MAIN PROGRAM
# _______________________________________________________________

running = True
while running:
    # clear loop events and set loop speed to FPS
    pygame.event.clear()
    clock.tick(FPS)

    global keys
    keys = pygame.key.get_pressed()
    pygame.event.poll()
    (mouseX, mouseY) = pygame.mouse.get_pos()

    # ===== start page =====
    if startPage:

        # display background and title
        gameDisplay.blit(menuBackground1, (0, 0))
        gameDisplay.blit(titleImage, (100, 200))

        # flashing message: "press ENTER to start"
        displayCounter += 1
        if displayCounter%40 == 0:
            displayOn = -displayOn
        # end if
        if displayOn > 0:
            gameDisplay.blit(titleStart, (100, 400))
        # end if, end flashing message

        # proceed to main menu if enter is pressed
        if keys[K_RETURN]:
            startSound.play()
            startPage, mainMenu = False, True
            displayCounter = 0
            pygame.time.delay(200)
            pygame.mixer.music.play(-1)
        # end if
    # end if
        
    # ===== main menu =====
    if mainMenu:
        # displaying background and title
        gameDisplay.blit(mainMenuBackground, (0, 0))

        # play button
        playGame = button("PLAY", 80, 100, 500, 200, WHITE, GREY_BLUE, 50, False)

        # if hovering over play button, penguin image changes
        if mouseX >= 80 and mouseX <= 580 and mouseY >= 100 and mouseY <= 300:
            gameDisplay.blit(menuPenguin1, (110, 130))
        # end if
        else:
            gameDisplay.blit(menuPenguin2, (110, 130))
        # end else
        if playGame:
            mainMenu, levelMenu = False, True
        # end if
        
        # instructions button
        instructions = button("HOW TO PLAY", 80, 330, 400, 150, WHITE, LIGHT_BLUE, 36, False)
        if instructions:
            mainMenu, instructionsMenu = False, True
        # end if

        # options button
        options = button("OPTIONS", 80, 510, 400, 150, WHITE, LIGHT_BLUE, 36, False)
        if options:
            mainMenu, optionsMenu = False, True
        # end if

        # instructions button
        quitGame = button("QUIT", 1020, 80, 175, 100, WHITE, GREY_BLUE, 32, False)
        if quitGame:
            running = False
        # end if
    # end if

    # ===== options menu =====
    if optionsMenu:
        # displaying background and title
        gameDisplay.blit(menuBackground1, (0, 0))
        
        # volume display button
        volumeDisplay = button(str("VOLUME: " + str(10*mixerVolume)), 100, 300, 400, 150, WHITE, GREY_BLUE, 36, "WHITE")

        if mixerVolume > 0.9:
            volumeUpLock = True
            mixerVolume = 1
        # end if
        else:
            volumeUpLock = False
        # end else

        if mixerVolume < 0.1:
            volumeDownLock = True
            mixerVolume = 0
        # end if
        else:
            volumeDownLock = False
        # end else
        
        # volume up button
        volumeUp = button("+", 600, 300, 150, 150, WHITE, LIGHT_BLUE, 36, volumeUpLock)
        if volumeUp:
            mixerVolume += 0.1
            pygame.mixer.music.set_volume(mixerVolume/5.0)
        # end if
        
        # volume down button
        volumeDown = button("-", 780, 300, 150, 150, WHITE, LIGHT_BLUE, 36, volumeDownLock)
        if volumeDown and mixerVolume > 0.1:
            mixerVolume -= 0.1
            pygame.mixer.music.set_volume(mixerVolume/5.0)
        # end if
        
        # menu button
        mainMenu = button("BACK", 60, 60, 175, 100, WHITE, GREY_BLUE, 36, False)
        if mainMenu:
            optionsMenu, mainMenu = False, True
        # end if
    # end if

    # ===== instructions menu =====
    if instructionsMenu:
        
        # displaying current instructions page
        instructionsPage = pygame.image.load("instructions" + str(instructionsPageNum) + ".png").convert() # menu pages
        gameDisplay.blit(instructionsPage, (0, 0))
        gameDisplay.blit(water, (0, 3.5*WATER))

        if instructionsPageNum < 8: # button disappears once user reaches last page
            instructionsNextLock = False
        # end if
        else:
            instructionsNextLock = True
        # end else
        if instructionsPageNum > 1: # button disappears once user reaches last page
            instructionsBackLock = False
        # end if
        else:
            instructionsBackLock = True
        # end else
        
        # next page button
        nextPage = button(">", CENTREX, 565, 75, 100, WHITE, GREY_BLUE, 36, instructionsNextLock)
        if nextPage:
            instructionsPageNum += 1
        # end if

        # previous page button
        lastPage = button("<", CENTREX - 100, 565, 75, 100, WHITE, GREY_BLUE, 36, instructionsBackLock)
        if lastPage:
            instructionsPageNum -= 1
        # end if

        # menu button
        mainMenu = button("BACK", 60, 60, 175, 100, WHITE, GREY_BLUE, 36, False)
        if mainMenu:
            instructionsMenu, mainMenu = False, True
        # end if
    # end if
        
    # reset instructions page to 1 if not on instructions page
    else:
        instructionsPageNum = 1
    # end else

    # ===== pause menu =====
    if pauseMenu:
        
        displayCounter += 1

        # only runs on the first instance of the game loop
        if displayCounter < 2:
            gameDisplay.blit(pauseScreen, (0, 0)) # display pause screen overlay
        # end if
            
        # resume button
        resumeButton = button("RESUME", 440, 100, 400, 140, WHITE, GREY_BLUE, 36, False)
        if resumeButton:
            playLevel, pauseMenu = True, False # if clicked, resume the game
            displayCounter = 0
        # end if

        # restart button
        restartButton = button("RESTART", 440, 290, 400, 140, WHITE, LIGHT_BLUE, 36, False)
        if restartButton:
            playLevel, pauseMenu = False, False 
            level(levelNum)
            playLevel = True
            displayCounter = 0
        # end if
            
        # menu button
        mainMenu = button("MAIN MENU", 440, 480, 400, 140, WHITE, LIGHT_BLUE, 36, False)
        if mainMenu:
            pauseMenu, playLevel, mainMenu = False, False, True
            displayCounter = 0
        # end if
    # end if

    # ===== win level  menu =====
    if winLevel:
        
        displayCounter += 1
        # only runs on the first instance of the game loop
        if displayCounter < 2:
            pygame.mixer.music.set_volume(mixerVolume/5) # lower background music volume
            winLevelSound.set_volume(mixerVolume)
            winLevelSound.play() # play win level sound effect
            gameDisplay.blit(pauseScreen, (0, 0)) # display pause screen overlay
        # end if

        # plays the win game sound effect if on the last level
        if displayCounter == 100 and levelNum == 10:
            winGameSound.set_volume(mixerVolume)
            winGameSound.play() # play win level sound effect
        # end elif

        # does not play the win game sound effect otherwise
        elif displayCounter == 100:
            pygame.mixer.music.set_volume(mixerVolume)
        # end if

        # disable restart / main menu buttons when victory music is playing after last level
        if displayCounter < 620 and levelNum == 10:
            restartButtonLock = True
            mainMenuLock = True
        # end if
        
        else:
            restartButtonLock = False
            mainMenuLock = False
        # end else
        
        # unlock next level
        if levelNum != 10:
            lockLevel[levelNum+1] = False 
            nextLevelButton = button("NEXT LEVEL", 440, 100, 400, 140, WHITE, GREY_BLUE, 36, False)
            if nextLevelButton:
                playLevel, winLevel = True, False # if clicked, resume the game
                levelNum += 1
                level(levelNum)
                displayCounter = 0
            # end if
        # end if

        else:
            gameDisplay.blit(winDisplay, (300, 120)) # display "YOU WON!"
        
        # restart button
        restartButton = button("RESTART", 440, 290, 400, 140, WHITE, LIGHT_BLUE, 36, restartButtonLock)
        if restartButton:
            playLevel, winLevel = False, False 
            level(levelNum)
            playLevel = True
            displayCounter = 0
            pygame.mixer.music.set_volume(mixerVolume)
        # end if
            
        # menu button
        mainMenu = button("MAIN MENU", 440, 480, 400, 140, WHITE, LIGHT_BLUE, 36, mainMenuLock)
        if mainMenu:
            winLevel, playLevel, mainMenu = False, False, True
            displayCounter = 0
            pygame.mixer.music.set_volume(mixerVolume)
        # end if
    # end if

    # ===== lose level menu =====
    if loseLevel:        
        displayCounter += 1

        # only runs on the first instance of the game loop
        if displayCounter < 2:
            pygame.mixer.music.set_volume(mixerVolume/5) # lower background music volume
            gameOverSound.set_volume(mixerVolume)
            gameOverSound.play() # plays the game over sound
            gameDisplay.blit(pauseScreen, (0, 0)) # display pause screen overlay
            gameDisplay.blit(loseDisplay, (300, 120)) # display "YOU LOST!"
        # end if

        if displayCounter == 100:
            pygame.mixer.music.set_volume(mixerVolume)
        # end if
        
        # restart button
        restartButton = button("TRY AGAIN", 440, 290, 400, 140, WHITE, GREY_BLUE, 36, False)
        if restartButton:
            playLevel, loseLevel = False, False 
            level(levelNum)
            playLevel = True
            displayCounter = 0
        # end if
            
        # menu button
        mainMenu = button("MAIN MENU", 440, 480, 400, 140, WHITE, LIGHT_BLUE, 36, False)
        if mainMenu:
            loseLevel, playLevel, mainMenu = False, False, True
            displayCounter = 0
        # end if
    # end if

    # ===== levels menu =====
    if levelMenu:
        
        # displaying background
        gameDisplay.blit(levelMenuBackground, (0, 0))
        
        # level 1 button
        levelOne = button("1", 100, 250, 140, 140, WHITE, GREY_BLUE, 36, lockLevel[1])
        if levelOne:
            levelMenu, playLevel, levelNum = False, True, 1 # if clicked, set level to 1, then play the level
            level(levelNum)
        # end if

        # level 2 button
        levelTwo = button("2", 300, 250, 140, 140, WHITE, GREY_BLUE, 36, lockLevel[2])
        if levelTwo:
            levelMenu, playLevel, levelNum = False, True, 2 # if clicked, set level to 2, then play the level
            level(levelNum)
        # end if

        # level 3 button
        levelThree = button("3", 500, 250, 140, 140, WHITE, GREY_BLUE, 36, lockLevel[3])
        if levelThree:
            levelMenu, playLevel, levelNum = False, True, 3 # if clicked, set level to 3, then play the level
            level(levelNum)
        # end if

        # level 4 button
        levelFour = button("4", 700, 250, 140, 140, WHITE, GREY_BLUE, 36, lockLevel[4])
        if levelFour:
            levelMenu, playLevel, levelNum = False, True, 4 # if clicked, set level to 4, then play the level
            level(levelNum)
        # end if

        # level 5 button
        levelFive = button("5", 900, 250, 140, 140, WHITE, GREY_BLUE, 36, lockLevel[5])
        if levelFive:
            levelMenu, playLevel, levelNum = False, True, 5 # if clicked, set level to 5, then play the level
            level(levelNum)
        # end if

        # level 6 button
        levelSix = button("6", 100, 450, 140, 140, WHITE, GREY_BLUE, 36, lockLevel[6])
        if levelSix:
            levelMenu, playLevel, levelNum = False, True, 6 # if clicked, set level to 6, then play the level
            level(levelNum)
        # end if

        # level 7 button
        levelSeven = button("7", 300, 450, 140, 140, WHITE, GREY_BLUE, 36, lockLevel[7])
        if levelSeven:
            levelMenu, playLevel, levelNum = False, True, 7 # if clicked, set level to 7, then play the level
            level(levelNum)
        # end if

        # level 8 button
        levelEight = button("8", 500, 450, 140, 140, WHITE, GREY_BLUE, 36, lockLevel[8])
        if levelEight:
            levelMenu, playLevel, levelNum = False, True, 8 # if clicked, set level to 8, then play the level
            level(levelNum)
        # end if

        # level 9 button
        levelNine = button("9", 700, 450, 140, 140, WHITE, GREY_BLUE, 36, lockLevel[9])
        if levelNine:
            levelMenu, playLevel, levelNum = False, True, 9 # if clicked, set level to 9, then play the level
            level(levelNum)
        # end if

        # level 10 button
        levelTen = button("10", 900, 450, 140, 140, WHITE, GREY_BLUE, 36, lockLevel[10])
        if levelTen:
            levelMenu, playLevel, levelNum = False, True, 10 # if clicked, set level to 10, then play the level
            level(levelNum)
        # end if
            
        # menu button
        mainMenu = button("BACK", 60, 60, 175, 100, WHITE, GREY_BLUE, 36, False)
        if mainMenu:
            levelMenu, mainMenu = False, True
        # end if
    # end if

    # ____________________________________
    #
    # playing a level
    # ____________________________________
    
    if playLevel:
        pygame.mixer.music.set_volume(mixerVolume) # reset background music volume
        gameDisplay.blit(levelBackground, (0, 0)) # displaying level background
        PLATFORMS.execute(penguin) # executing the platforms class
        FISH.execute(penguin) # executing the fish class
        penguin.execute() # executing the player class
        gameDisplay.blit(water, (0, WATER)) # displaying water overtop everything

        # if all fish are eaten, the level is won
        if FISH.testCollision(penguin) == "WIN":
            playLevel, winLevel = False, True 
        # end if
        # if one of the fish swims away, the level is lost
        if FISH.testCollision(penguin) == "LOSE":
            playLevel, loseLevel = False, True
        # end if
        # if the penguin swims beyond WIDTH or HEIGHT, the level is lost
        if penguin.move() == "LOSE":
            playLevel, loseLevel = False, True
        # end if

        if keys[K_ESCAPE]:
            playLevel, pauseMenu = False, True # if the user presses esc., the game is paused
        # end if
    # end if

        
    # ____________________________________
    #
    # background game functions
    # ____________________________________

    # ===== toggle fullscreen OFF =====
    if keys[K_TAB] and fullscreen:
        pygame.display.quit() # close current game display
        pygame.display.init() 
        gameDisplay = pygame.display.set_mode((WIDTH, HEIGHT)) # reset game window
        fullscreen = False
        displayCounter = 0
    # end if

    # ===== toggle fullscreen ON =====
    elif keys[K_TAB] and not fullscreen:
        pygame.display.quit() # close current game display
        pygame.display.init()
        gameDisplay = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN) # reset game window as fullscreen
        fullscreen = True
        displayCounter = 0
    # end elif

    # ===== update game display =====
    pygame.display.update()
#end while loop

pygame.quit()
quit()
sys.exit()
