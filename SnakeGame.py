from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GLUT import GLUT_BITMAP_HELVETICA_18
import random
import math
import time

# Camera variables
camera_pos = (0, 600, 600)

fovY = 120  # Field of view

# Grid variables
COLS = 12
ROWS = 10
GRID_LENGTH = 150

# Game variables
Menu = True
Easy = False
Medium = False
Hard = False
gameOver = False
gamePaused = False
firstPerson = False
score = 0

# Snake variables
snakeLength = 1
snakeRadius = 30
snakeBody = []
snakeAngle = 0
snakeSpeed = 2
snakeColor = (1, 0, 0)
positionHistory = []
snakeLevelSpeed = [5, 3, 2]

# Food variables
foodList = []
bigFoodList = []
poisonFoodList = []
foodPulse = 1
foodPulseTime = 0

# Obstacle variables
obstacleList = []

# Portal variables
portalList = []
portalTimer = 0
portalSpawnInterval = 10  # Seconds

# Cheat mode variables
cheatModeActive = False
cheatModeDuration = 10  # 10 seconds
cheatModeStartTime = 0
cheatBarProgress = 0
cheatBarFull = 20  # 20 points to fill the bar

# Shell variables
shellList = []

# Brick Wall variables
WallList = []

def midPointLine(x0, y0, x1, y1):
    dx = x1 - x0
    dy = y1 - y0
    d = 2 * dy - dx
    E = 2 * dy
    NE = 2 * (dy - dx)
    x, y = x0, y0
    pixels = [(x, y)]

    while x < x1:
        if d <= 0:
            d += E
            x += 1
        else:
            d += NE
            x += 1
            y += 1
        pixels.append((x, y))
    
    return pixels

def findZone(x0, y0, x1, y1):
    dx = x1 - x0
    dy = y1 - y0
    if abs(dx) > abs(dy):
        if dx > 0:
            if dy > 0:
                return 0
            else:
                return 7
        else:
            if dy > 0:
                return 3
            else:
                return 4
    else:
        if dy > 0:
            if dx > 0:
                return 1
            else:
                return 2
        else:
            if dx > 0:
                return 6
            else:
                return 5

def convertCordinateOfZone(x0, y0, x1, y1, zone):
    if zone == 0:
        return x0, y0, x1, y1
    elif zone == 1:
        return y0, x0, y1, x1
    elif zone == 2:
        return y0, -x0, y1, -x1
    elif zone == 3:
        return -x0, y0, -x1, y1
    elif zone == 4:
        return -x0, -y0, -x1, -y1
    elif zone == 5:
        return -y0, -x0, -y1, -x1
    elif zone == 6:
        return -y0, x0, -y1, x1
    elif zone == 7:
        return x0, -y0, x1, -y1
    
def reconvertCordinateOfZone(x, y, zone):
    if zone == 0:
        return x, y
    elif zone == 1:
        return y, x
    elif zone == 2:
        return -y, x
    elif zone == 3:
        return -x, y
    elif zone == 4:
        return -x, -y
    elif zone == 5:
        return -y, -x
    elif zone == 6:
        return y, -x
    elif zone == 7:
        return x, -y

def eightWaySymmetry(x0, y0, x1, y1):
    initialZone = findZone(x0, y0, x1, y1)
    x0, y0, x1, y1 = convertCordinateOfZone(x0, y0, x1, y1, initialZone)
    pixels = midPointLine(x0, y0, x1, y1)
    newPixels = []
    for x, y in pixels:
        newPixels.append(reconvertCordinateOfZone(x, y, initialZone))
    
    return newPixels

def drawLine(x0, y0, x1, y1):
    pixels = eightWaySymmetry(x0, y0, x1, y1)
    glPointSize(1)
    for x, y in pixels:
        glBegin(GL_POINTS)
        glVertex2i(int(x), int(y))
        glEnd()

def draw_text_with_lines(x, y, text):
    char_width = 20
    char_height = 40
    spacing = 10

    for i, char in enumerate(text):
        char_x = x + i * (char_width + spacing)
        draw_character_with_lines(char_x, y, char_width, char_height, char)

def draw_character_with_lines(x, y, width, height, char):
    if char == "M":
        drawLine(x, y, x, y + height)  # Left vertical line
        drawLine(x, y + height, x + width / 2, y)  # Diagonal to middle
        drawLine(x + width / 2, y, x + width, y + height)  # Diagonal to top right
        drawLine(x + width, y + height, x + width, y)  # Right vertical line
    elif char == "A":
        drawLine(x, y, x + width / 2, y + height)  # Left diagonal
        drawLine(x + width / 2, y + height, x + width, y)  # Right diagonal
        drawLine(x + width / 4, y + height / 2, x + 3 * width / 4, y + height / 2)  # Horizontal bar
    elif char == "I":
        drawLine(x + width / 2, y, x + width / 2, y + height)  # Vertical line
    elif char == "N":
        drawLine(x, y, x, y + height)  # Left vertical line
        drawLine(x, y + height, x + width, y)  # Diagonal
        drawLine(x + width, y, x + width, y + height)  # Right vertical line
    elif char == "U":
        drawLine(x, y + height, x, y)  # Left vertical line
        drawLine(x, y, x + width, y)  # Bottom horizontal line
        drawLine(x + width, y, x + width, y + height)  # Right vertical line
    elif char == "S":
        drawLine(x + width, y + height, x, y + height)  # Top horizontal line
        drawLine(x, y + height, x, y + height / 2)  # Left vertical (top half)
        drawLine(x, y + height / 2, x + width, y + height / 2)  # Middle horizontal line
        drawLine(x + width, y + height / 2, x + width, y)  # Right vertical (bottom half)
        drawLine(x + width, y, x, y)  # Bottom horizontal line
    elif char == "Y":
        drawLine(x, y + height, x + width / 2, y + height / 2)  # Left diagonal
        drawLine(x + width / 2, y + height / 2, x + width, y + height)  # Right diagonal
        drawLine(x + width / 2, y + height / 2, x + width / 2, y)  # Vertical line (bottom half)
    elif char == "D":
        drawLine(x, y, x, y + height)  # Left vertical line
        drawLine(x, y + height, x + width / 2, y + height)  # Top horizontal line
        drawLine(x + width / 2, y + height, x + width, y + height / 2)  # Top-right diagonal
        drawLine(x + width, y + height / 2, x + width / 2, y)  # Bottom-right diagonal
        drawLine(x + width / 2, y, x, y)  # Bottom horizontal line
    elif char == "R":
        drawLine(x, y, x, y + height)  # Left vertical line
        drawLine(x, y + height, x + width / 2, y + height)  # Top horizontal line
        drawLine(x + width / 2, y + height, x + width, y + height / 2)  # Top-right diagonal
        drawLine(x + width, y + height / 2, x + width / 2, y + height / 2)  # Middle horizontal line
        drawLine(x, y + height / 2, x + width / 2, y + height / 2)  # Connect to left
        drawLine(x + width / 2, y + height / 2, x + width, y)  # Diagonal leg
    elif char == " ":
        pass  # Space, no lines drawn
    elif char == ".":
        drawLine(x + width / 2, y, x + width / 2, y)  # Single point for a dot
    elif char == "1":
        drawLine(x + width / 2, y, x + width / 2, y + height)  # Vertical line
    elif char == "2":
        drawLine(x, y + height, x + width, y + height)  # Top horizontal line
        drawLine(x + width, y + height, x + width, y + height / 2)  # Right vertical line
        drawLine(x + width, y + height / 2, x, y)  # Diagonal to bottom left
        drawLine(x, y, x + width, y)  # Bottom horizontal line
    elif char == "3":
        drawLine(x, y + height, x + width, y + height)  # Top horizontal line
        drawLine(x + width, y + height, x + width, y)  # Right vertical line
        drawLine(x, y + height / 2, x + width, y + height / 2)  # Middle horizontal line
        drawLine(x, y, x + width, y)  # Bottom horizontal line
    elif char == "E":
        drawLine(x, y, x, y + height)  # Left vertical line
        drawLine(x, y + height, x + width, y + height)  # Top horizontal line
        drawLine(x, y + height / 2, x + width / 2, y + height / 2)  # Middle horizontal line
        drawLine(x, y, x + width, y)  # Bottom horizontal line
    elif char == "H":
        drawLine(x, y, x, y + height)  # Left vertical line
        drawLine(x + width, y, x + width, y + height)  # Right vertical line
        drawLine(x, y + height / 2, x + width, y + height / 2)  # Middle horizontal line
    elif char == "G":
        drawLine(x + width, y + height, x, y + height)  # Top horizontal line
        drawLine(x, y + height, x, y)  # Left vertical line
        drawLine(x, y, x + width, y)  # Bottom horizontal line
        drawLine(x + width, y, x + width, y + height / 2)  # Right vertical (bottom half)
        drawLine(x + width, y + height / 2, x + width / 2, y + height / 2)  # Middle horizontal line
    elif char == "O":
        drawLine(x, y, x, y + height)  # Left vertical line
        drawLine(x, y + height, x + width, y + height)  # Top horizontal line
        drawLine(x + width, y + height, x + width, y)  # Right vertical line
        drawLine(x + width, y, x, y)  # Bottom horizontal line
    elif char == "V":
        drawLine(x, y + height, x + width / 2, y)  # Left diagonal
        drawLine(x + width / 2, y, x + width, y + height)  # Right diagonal
    elif char == "4":
        drawLine(x, y + height, x, y + height / 2)  # Left vertical line
        drawLine(x, y + height / 2, x + width, y + height / 2)  # Middle horizontal line
        drawLine(x + width, y, x + width, y + height)  # Right vertical line
    elif char == "5":
        drawLine(x + width, y + height, x, y + height)  # Top horizontal line
        drawLine(x, y + height, x, y + height / 2)  # Left vertical (top half)
        drawLine(x, y + height / 2, x + width, y + height / 2)  # Middle horizontal line
        drawLine(x + width, y + height / 2, x + width, y)  # Right vertical (bottom half)
        drawLine(x + width, y, x, y)  # Bottom horizontal line
    elif char == "6":
        drawLine(x + width, y + height, x, y + height)  # Top horizontal line
        drawLine(x, y + height, x, y)  # Left vertical line
        drawLine(x, y, x + width, y)  # Bottom horizontal line
        drawLine(x + width, y, x + width, y + height / 2)  # Right vertical (bottom half)
        drawLine(x + width, y + height / 2, x, y + height / 2)  # Middle horizontal line
    elif char == "7":
        drawLine(x, y + height, x + width, y + height)  # Top horizontal line
        drawLine(x + width, y + height, x, y)  # Diagonal line
    elif char == "8":
        drawLine(x, y + height, x + width, y + height)  # Top horizontal line
        drawLine(x, y + height, x, y)  # Left vertical line
        drawLine(x, y, x + width, y)  # Bottom horizontal line
        drawLine(x + width, y, x + width, y + height)  # Right vertical line
        drawLine(x, y + height / 2, x + width, y + height / 2)  # Middle horizontal line
    elif char == "9":
        drawLine(x, y + height, x + width, y + height)  # Top horizontal line
        drawLine(x, y + height, x, y + height / 2)  # Left vertical (top half)
        drawLine(x, y + height / 2, x + width, y + height / 2)  # Middle horizontal line
        drawLine(x + width, y + height / 2, x + width, y)  # Right vertical line
        drawLine(x + width, y, x, y)  # Bottom horizontal line
    elif char == "0":
        drawLine(x, y, x, y + height)  # Left vertical line
        drawLine(x, y + height, x + width, y + height)  # Top horizontal line
        drawLine(x + width, y + height, x + width, y)  # Right vertical line
        drawLine(x + width, y, x, y)  # Bottom horizontal line
    elif char == "C":
        drawLine(x + width, y + height, x, y + height)  # Top horizontal line
        drawLine(x, y + height, x, y)  # Left vertical line
        drawLine(x, y, x + width, y)  # Bottom horizontal line
    elif char == "P":
        drawLine(x, y, x, y + height)  # Left vertical line
        drawLine(x, y + height, x + width, y + height)  # Top horizontal line
        drawLine(x + width, y + height, x + width, y + height / 2)  # Right vertical (top half)
        drawLine(x + width, y + height / 2, x, y + height / 2)  # Middle horizontal line
    elif char == "T":
        drawLine(x, y + height, x + width, y + height)  # Top horizontal line
        drawLine(x + width / 2, y, x + width / 2, y + height)  # Vertical line

def mainMenu():
    # Set up a 2D orthographic projection for the menu
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, 1000, 0, 800)  # Set the 2D coordinate system
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()

    # Draw the background
    glColor3f(0.2, 0.2, 0.2)
    glBegin(GL_QUADS)
    glVertex2f(0, 0)
    glVertex2f(1000, 0)
    glVertex2f(1000, 800)
    glVertex2f(0, 800)
    glEnd()

    # Draw the title "Main Menu" using lines
    glColor3f(1, 1, 1)  # Set line color to white
    draw_text_with_lines(400, 600, "MAIN MENU")

    # Draw the menu options using lines
    draw_text_with_lines(410, 500, "1. EASY")
    draw_text_with_lines(410, 450, "2. MEDIUM")
    draw_text_with_lines(410, 400, "3. HARD")

    # Restore the previous projection and modelview matrices
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

def GameOverScreen():
    # Set up a 2D orthographic projection for the game over screen
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, 1000, 0, 800)  # Set the 2D coordinate system
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()

    # Draw the background
    glColor3f(0.2, 0.2, 0.2)
    glBegin(GL_QUADS)
    glVertex2f(0, 0)
    glVertex2f(1000, 0)
    glVertex2f(1000, 800)
    glVertex2f(0, 800)
    glEnd()

    # Draw the title "Game Over" using lines
    glColor3f(1, 1, 1)  # Set line color to white
    draw_text_with_lines(400, 600, "GAME OVER")

    # Draw the score using lines
    draw_text_with_lines(410, 500, f"SCORE: {score}")

    draw_text_with_lines(300, 350, "PRESS R TO RESTART")

    draw_text_with_lines(300, 250, "PRESS M TO MAIN MENU")

    # Restore the previous projection and modelview matrices
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

def draw_text(x, y, text, font=GLUT_BITMAP_HELVETICA_18):
    glColor3f(1,1,1)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    
    gluOrtho2D(0, 1000, 0, 800)

    
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    
    glRasterPos2f(x, y)
    for ch in text:
        glutBitmapCharacter(font, ord(ch))
    
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

def levelEasy():
    tile_size = GRID_LENGTH
    rows = ROWS
    cols = COLS

    glPushMatrix()
    glTranslatef(-cols * tile_size / 2, -rows * tile_size / 2, 0)

    for i in range(rows):
        for j in range(cols):
            # Alternate colors
            if (i + j) % 2 == 0:
                glColor3f(0.5, 0.5, 0.5)
            else:
                glColor3f(1, 1, 1)

            # Draw a tile
            glBegin(GL_QUADS)
            glVertex3f(j * tile_size, i * tile_size, 0)
            glVertex3f((j + 1) * tile_size, i * tile_size, 0)
            glVertex3f((j + 1) * tile_size, (i + 1) * tile_size, 0)
            glVertex3f(j * tile_size, (i + 1) * tile_size, 0)
            glEnd()

    glPopMatrix()

def levelMedium():
    tile_size = GRID_LENGTH
    rows = ROWS
    cols = COLS

    glPushMatrix()
    glTranslatef(-cols * tile_size / 2, -rows * tile_size / 2, 0)

    for i in range(rows):
        for j in range(cols):
            # Alternate colors
            if (i + j) % 2 == 0:
                glColor3f(0.3, 0.3, 0.6)  # Darker blue-gray
            else:
                glColor3f(0.7, 0.7, 0.9)  # Lighter blue-gray

            # Draw a tile
            glBegin(GL_QUADS)
            glVertex3f(j * tile_size, i * tile_size, 0)
            glVertex3f((j + 1) * tile_size, i * tile_size, 0)
            glVertex3f((j + 1) * tile_size, (i + 1) * tile_size, 0)
            glVertex3f(j * tile_size, (i + 1) * tile_size, 0)
            glEnd()

    glPopMatrix()

def levelHard():
    tile_size = GRID_LENGTH
    rows = ROWS
    cols = COLS

    glPushMatrix()
    glTranslatef(-cols * tile_size / 2, -rows * tile_size / 2, 0)

    for i in range(rows):
        for j in range(cols):
            # Alternate colors
            if (i + j) % 2 == 0:
                glColor3f(0.5, 0.2, 0.2)  # Dark red
            else:
                glColor3f(0.8, 0.5, 0.5)  # Light red

            # Draw a tile
            glBegin(GL_QUADS)
            glVertex3f(j * tile_size, i * tile_size, 0)
            glVertex3f((j + 1) * tile_size, i * tile_size, 0)
            glVertex3f((j + 1) * tile_size, (i + 1) * tile_size, 0)
            glVertex3f(j * tile_size, (i + 1) * tile_size, 0)
            glEnd()

    glPopMatrix()

def drawSnake():
    global snakeBody, cheatModeActive
    
    glPushMatrix()

    for i, segment in enumerate(snakeBody):
        glPushMatrix()

        if cheatModeActive:
            # Rainbow effect for cheat mode
            pulse = (time.time() * 3) % 1.0
            if i == 0:
                glColor3f(1.0, pulse, pulse)  # Head color
            else:
                color_offset = (i * 0.1) % 1.0
                r = 0.5 + 0.5 * math.sin(math.pi * 2 * (pulse + color_offset))
                g = 0.5 + 0.5 * math.sin(math.pi * 2 * (pulse + color_offset + 0.33))
                b = 0.5 + 0.5 * math.sin(math.pi * 2 * (pulse + color_offset + 0.66))
                glColor3f(r, g, b)
        else:
            # Normal colors
            if i == 0:
                glColor3f(0.6, 0, 0)  # Red head
            else:
                glColor3f(snakeColor[0], snakeColor[1], snakeColor[2])
                
        glTranslatef(segment[0], segment[1], segment[2])
        gluSphere(gluNewQuadric(), snakeRadius, 10, 10)

        glPopMatrix()

    glPopMatrix()

def drawSnakeBody():
    global snakeBody, snakeLength

    for i in range(snakeLength):
        if i == 0:
            snakeBody.append([0, 0, 0])
        else:
            newSnakeBodyY = i * snakeRadius * 2
            snakeBody.append([snakeBody[i - 1][0], newSnakeBodyY, snakeBody[i - 1][2]])

def prefillPositionHistory():
    global positionHistory, snakeBody, snakeLength, snakeSpeed, snakeRadius

    # Insert initial snake positions into history, spaced correctly
    for i in range((snakeLength + 1) * (snakeRadius * 2) // snakeSpeed):
        positionHistory.append(snakeBody[0][:])

def snakeForwardMovement():
    global snakeAngle, snakeLength, snakeSpeed, snakeBody, positionHistory, cheatModeActive, score, Easy, Medium, Hard

    if Easy:
        speedReduction = snakeLevelSpeed[0]
    elif Medium:
        speedReduction = snakeLevelSpeed[1]
    elif Hard:
        speedReduction = snakeLevelSpeed[2]
    else:
        speedReduction = 1

    # Calculate speed based on score (increase by 1 for every 30 points)
    calculatedSpeed = snakeSpeed + (score // 30)

    # Boundaries
    min_x = -COLS * GRID_LENGTH / 2 + 50
    max_x = COLS * GRID_LENGTH / 2 - 50
    min_y = -ROWS * GRID_LENGTH / 2 + 50
    max_y = ROWS * GRID_LENGTH / 2 - 50

    # Calculate current speed (doubled in cheat mode)
    current_speed = calculatedSpeed * 2 if cheatModeActive else calculatedSpeed

    # Move the head
    snakeBody[0][0] -= current_speed * math.sin(math.radians(-snakeAngle)) / speedReduction
    snakeBody[0][1] -= current_speed * math.cos(math.radians(snakeAngle)) / speedReduction

    if snakeBody[0][0] < min_x:
        snakeBody[0][0] = min_x
    if snakeBody[0][0] > max_x:
        snakeBody[0][0] = max_x
    if snakeBody[0][1] < min_y:
        snakeBody[0][1] = min_y
    if snakeBody[0][1] > max_y:
        snakeBody[0][1] = max_y

    # Record the current head position
    positionHistory.insert(0, snakeBody[0][:])

    # Keep the path history from growing too large
    max_history_length = (snakeLength + 1) * (snakeRadius * 2) // int(calculatedSpeed)
    if len(positionHistory) > max_history_length:
        positionHistory.pop()

    # Move body segments along the path history
    for i in range(1, len(snakeBody)):
        index = i * (snakeRadius * 2) // int(calculatedSpeed)
        if index < len(positionHistory):
            snakeBody[i][0] = positionHistory[index][0]
            snakeBody[i][1] = positionHistory[index][1]
            snakeBody[i][2] = positionHistory[index][2]

def drawFood(x, y, z):
    glPushMatrix()
    
    # Food Orange Sphere
    glColor3f(1, 0.6, 0)

    glTranslatef(x, y, z + 35)
    gluSphere(gluNewQuadric(), 30, 10, 10)

    glPopMatrix()

def foodSpawn(totalFood=1):
    global foodList, bigFoodList, score

    # Boundaries
    min_x = -COLS * GRID_LENGTH / 2 + 50
    max_x = COLS * GRID_LENGTH / 2 - 50
    min_y = -ROWS * GRID_LENGTH / 2 + 50
    max_y = ROWS * GRID_LENGTH / 2 - 50

    # Randomly generate food positions
    for i in range(totalFood):
        x = random.randint(int(min_x), int(max_x))
        y = random.randint(int(min_y), int(max_y))
        z = 0
        
        # Ensure food don't spawn on the snake or other game objects
        valid_position = False
        while not valid_position:
            valid_position = True
            
            # Check if it's too close to the snake
            for segment in snakeBody:
                segment_x, segment_y, segment_z = segment
                if math.sqrt((x - segment_x) ** 2 + (y - segment_y) ** 2) < 60:
                    valid_position = False
                    break
            
            # Check if it's too close to other game objects
            for food in foodList + bigFoodList + poisonFoodList:
                # Handle different structures of foodList and poisonFoodList
                if len(food) == 4:  # This is a poison food with spawn time
                    food_x, food_y, food_z, _ = food
                else:
                    food_x, food_y, food_z = food
                    
                if math.sqrt((x - food_x) ** 2 + (y - food_y) ** 2) < 80:
                    valid_position = False
                    break
                    
            # Check if it's too close to other obstacles
            for obstacle in obstacleList:
                obs_x, obs_y, obs_z = obstacle
                if math.sqrt((x - obs_x) ** 2 + (y - obs_y) ** 2) < 80:
                    valid_position = False
                    break
            
            # Check if it's too close to portals
            for portal in portalList:
                portal_x, portal_y, portal_z = portal
                if math.sqrt((x - portal_x) ** 2 + (y - portal_y) ** 2) < 80:
                    valid_position = False
                    break
            
            # Check if it's too close to shells
            for shell in shellList:
                shell_x, shell_y, shell_z = shell
                if math.sqrt((x - shell_x) ** 2 + (y - shell_y) ** 2) < 80:
                    valid_position = False
                    break
            
            # Check if it's too close to walls
            for wall in WallList:
                wall_x, wall_y, wall_z, width, height = wall
                if (wall_x - width / 2 <= x <= wall_x + width / 2) and (wall_y - height / 2 <= y <= wall_y + height / 2):
                    valid_position = False
                    break
            
            if not valid_position:
                x = random.randint(int(min_x), int(max_x))
                y = random.randint(int(min_y), int(max_y))

        foodList.append((x, y, z))


def foodSpawnBig():
    global bigFoodList

    # Boundaries
    min_x = -COLS * GRID_LENGTH / 2 + 50
    max_x = COLS * GRID_LENGTH / 2 - 50
    min_y = -ROWS * GRID_LENGTH / 2 + 50
    max_y = ROWS * GRID_LENGTH / 2 - 50

    # Randomly generate big food position
    x = random.randint(int(min_x), int(max_x))
    y = random.randint(int(min_y), int(max_y))
    z = 0

    # Ensure Big food don't spawn on the snake or other game objects
    valid_position = False
    while not valid_position:
        valid_position = True
            
        # Check if it's too close to the snake
        for segment in snakeBody:
            segment_x, segment_y, segment_z = segment
            if math.sqrt((x - segment_x) ** 2 + (y - segment_y) ** 2) < 60:
                valid_position = False
                break
            
        # Check if it's too close to other game objects
        for food in foodList + bigFoodList + poisonFoodList:
            # Handle different structures of foodList and poisonFoodList
            if len(food) == 4:  # This is a poison food with spawn time
                food_x, food_y, food_z, _ = food
            else:
                food_x, food_y, food_z = food
                    
            if math.sqrt((x - food_x) ** 2 + (y - food_y) ** 2) < 80:
                valid_position = False
                break
                    
        # Check if it's too close to other obstacles
        for obstacle in obstacleList:
            obs_x, obs_y, obs_z = obstacle
            if math.sqrt((x - obs_x) ** 2 + (y - obs_y) ** 2) < 80:
                valid_position = False
                break
            
        # Check if it's too close to portals
        for portal in portalList:
            portal_x, portal_y, portal_z = portal
            if math.sqrt((x - portal_x) ** 2 + (y - portal_y) ** 2) < 80:
                valid_position = False
                break
        
        # Check if it's too close to shells
        for shell in shellList:
            shell_x, shell_y, shell_z = shell
            if math.sqrt((x - shell_x) ** 2 + (y - shell_y) ** 2) < 80:
                valid_position = False
                break
        
        # Check if it's too close to walls
        for wall in WallList:
            wall_x, wall_y, wall_z, width, height = wall
            if (wall_x - width / 2 <= x <= wall_x + width / 2) and (wall_y - height / 2 <= y <= wall_y + height / 2):
                valid_position = False
                break
            
        if not valid_position:
            x = random.randint(int(min_x), int(max_x))
            y = random.randint(int(min_y), int(max_y))

    bigFoodList.append((x, y, z))

def foodSpawnPoison():
    global poisonFoodList

    # Boundaries
    min_x = -COLS * GRID_LENGTH / 2 + 50
    max_x = COLS * GRID_LENGTH / 2 - 50
    min_y = -ROWS * GRID_LENGTH / 2 + 50
    max_y = ROWS * GRID_LENGTH / 2 - 50

    # Randomly generate poison food position
    x = random.randint(int(min_x), int(max_x))
    y = random.randint(int(min_y), int(max_y))
    z = 0

    # Ensure Big food don't spawn on the snake or other game objects
    valid_position = False
    while not valid_position:
        valid_position = True
            
        # Check if it's too close to the snake
        for segment in snakeBody:
            segment_x, segment_y, segment_z = segment
            if math.sqrt((x - segment_x) ** 2 + (y - segment_y) ** 2) < 60:
                valid_position = False
                break
            
        # Check if it's too close to other game objects
        for food in foodList + bigFoodList + poisonFoodList:
            # Handle different structures of foodList and poisonFoodList
            if len(food) == 4:  # This is a poison food with spawn time
                food_x, food_y, food_z, _ = food
            else:
                food_x, food_y, food_z = food
                    
            if math.sqrt((x - food_x) ** 2 + (y - food_y) ** 2) < 80:
                valid_position = False
                break
                    
        # Check if it's too close to other obstacles
        for obstacle in obstacleList:
            obs_x, obs_y, obs_z = obstacle
            if math.sqrt((x - obs_x) ** 2 + (y - obs_y) ** 2) < 80:
                valid_position = False
                break
            
        # Check if it's too close to portals
        for portal in portalList:
            portal_x, portal_y, portal_z = portal
            if math.sqrt((x - portal_x) ** 2 + (y - portal_y) ** 2) < 80:
                valid_position = False
                break
        
        # Check if it's too close to shells
        for shell in shellList:
            shell_x, shell_y, shell_z = shell
            if math.sqrt((x - shell_x) ** 2 + (y - shell_y) ** 2) < 80:
                valid_position = False
                break
        
        # Check if it's too close to walls
        for wall in WallList:
            wall_x, wall_y, wall_z, width, height = wall
            if (wall_x - width / 2 <= x <= wall_x + width / 2) and (wall_y - height / 2 <= y <= wall_y + height / 2):
                valid_position = False
                break
            
        if not valid_position:
            x = random.randint(int(min_x), int(max_x))
            y = random.randint(int(min_y), int(max_y))

    # Append poison food with its spawn time
    poisonFoodList.append((x, y, z, time.time()))  # Add current time as spawn time

def updatePoisonFoodLifetime():
    global poisonFoodList

    current_time = time.time()
    poisonFoodList = [
        (x, y, z, spawn_time)
        for x, y, z, spawn_time in poisonFoodList
        if current_time - spawn_time < 10  # Keep only poison food younger than 10 seconds
    ]


def Collision():
    global foodList, snakeBody, snakeLength, score, gameOver, portalList, cheatBarProgress, cheatModeActive

    # Regular food collision
    for food in foodList[:]:  # Create a copy of the list to avoid modification during iteration
        food_x, food_y, food_z = food
        head_x, head_y, head_z = snakeBody[0]

        if math.sqrt((food_x - head_x) ** 2 + (food_y - head_y) ** 2) < 50:
            # Remove the food from the list
            foodList.remove(food)

            # Increase the snake length
            snakeLength += 1

            # Add a new segment to the snake body
            new_segment = [food_x, food_y, food_z]
            snakeBody.append(new_segment)

            # Spawn new food
            foodSpawn(1)

            # Increase the score (10 points in cheat mode, 1 point normally)
            if cheatModeActive:
                score += 10
            else:
                score += 1
                # Update cheat bar progress
                cheatBarProgress += 1
                if cheatBarProgress > cheatBarFull:
                    cheatBarProgress = cheatBarFull

            # Spawn big food if the score is a multiple of 5
            if score % 5 == 0 and not bigFoodList:
                foodSpawnBig()

            # Spawn poison food randomly
            if random.random() < 0.5:
                foodSpawnPoison()
    
    # Big food collision 
    for bigFood in bigFoodList[:]:  # Create a copy of the list
        bigFood_x, bigFood_y, bigFood_z = bigFood
        head_x, head_y, head_z = snakeBody[0]

        if math.sqrt((bigFood_x - head_x) ** 2 + (bigFood_y - head_y) ** 2) < 50:
            # Remove the big food from the list
            bigFoodList.remove(bigFood)

            # Increase the score
            if cheatModeActive:
                score += 50  # More points in cheat mode
            else:
                score += 5
                cheatBarProgress += 5
                if cheatBarProgress > cheatBarFull:
                    cheatBarProgress = cheatBarFull

            # Increase the snake length
            snakeLength += 1
    
    # Poison food collision 
    for poisonFood in poisonFoodList[:]:  # Create a copy of the list
        poisonFood_x, poisonFood_y, poisonFood_z, _ = poisonFood
        head_x, head_y, head_z = snakeBody[0]

        if math.sqrt((poisonFood_x - head_x) ** 2 + (poisonFood_y - head_y) ** 2) < 50:
            # Remove the poison food from the list
            poisonFoodList.remove(poisonFood)

            # Decrease the score only if not in cheat mode
            if not cheatModeActive:
                score -= 1
                cheatBarProgress -= 1
                if cheatBarProgress < 0:
                    cheatBarProgress = 0

                if snakeLength < 0:
                    gameOver = True
                    Easy = False
                    Medium = False
                    Hard = False
                    glutPostRedisplay()
                    return

                # Decrease the snake length
                if snakeLength > 1:
                    snakeLength -= 1
                    snakeBody.pop()
    
    # Obstacle collision
    for obstacle in obstacleList:
        obstacle_x, obstacle_y, obstacle_z = obstacle
        head_x, head_y, head_z = snakeBody[0]

        if math.sqrt((obstacle_x - head_x) ** 2 + (obstacle_y - head_y) ** 2) < 50:
            # Game over only if not in cheat mode
            if not cheatModeActive:
                gameOver = True
                Easy = False
                Medium = False
                Hard = False
                glutPostRedisplay()
                return
    
    # Wall collision
    for wall in WallList:
        wall_x, wall_y, wall_z, width, height = wall
        head_x, head_y, head_z = snakeBody[0]

        if (wall_x - width / 2 < head_x < wall_x + width / 2) and (wall_y - height / 2 < head_y < wall_y + height / 2):
            # Game over only if not in cheat mode
            if not cheatModeActive:
                gameOver = True
                Easy = False
                Medium = False
                Hard = False
                glutPostRedisplay()
                return
    
    # Portal collision
    if len(portalList) >= 2:
        portal1 = portalList[0]
        portal2 = portalList[1]
        
        portal1_x, portal1_y, portal1_z = portal1
        portal2_x, portal2_y, portal2_z = portal2
        head_x, head_y, head_z = snakeBody[0]
        
        # Check if snake enters portal 1
        if math.sqrt((portal1_x - head_x) ** 2 + (portal1_y - head_y) ** 2) < 50:
            # Teleport to portal 2
            snakeBody[0][0] = portal2_x
            snakeBody[0][1] = portal2_y
            
            # Update position history to avoid weird body movement
            positionHistory[0] = [portal2_x, portal2_y, portal2_z]
            
            # Remove portals after use
            portalList = []
        
        # Check if snake enters portal 2
        elif math.sqrt((portal2_x - head_x) ** 2 + (portal2_y - head_y) ** 2) < 50:
            # Teleport to portal 1
            snakeBody[0][0] = portal1_x
            snakeBody[0][1] = portal1_y
            
            # Update position history
            positionHistory[0] = [portal1_x, portal1_y, portal1_z]
            
            # Remove portals after use
            portalList = []
    
    # Shell collision
    for shell in shellList:
        shell_x, shell_y, shell_z = shell
        head_x, head_y, head_z = snakeBody[0]

        if math.sqrt((shell_x - head_x) ** 2 + (shell_y - head_y) ** 2) < 50:
            # Reduce snake length
            if snakeLength > 5:
                snakeLength -= 5
                for _ in range(5):
                    snakeBody.pop()
                    
                # Remove the shell
                shellList.remove(shell)

def foodPulseWave():
    global foodPulseTime, foodPulse
    
    foodPulseTime += 0.02
    foodPulse = 1 + 0.3 * math.sin(foodPulseTime)

def drawBigFood(x, y, z):
    glPushMatrix()
    
    # Food Blue Sphere
    glColor3f(0, 0, 1)

    glTranslatef(x, y, z + 35)
    glScale(foodPulse, foodPulse, foodPulse)
    gluSphere(gluNewQuadric(), 60, 10, 10)

    glPopMatrix()

def drawPoisonFood(x, y, z):
    glPushMatrix()
    
    # Food Green Sphere
    glColor3f(0, 0.7, 0)

    glTranslatef(x, y, z + 35)
    glScale(foodPulse, foodPulse, foodPulse)
    gluSphere(gluNewQuadric(), 40, 10, 10)

    glPopMatrix()

def drawObstacle(x, y, z):
    glPushMatrix()
    
    # Obstacle (black cube)
    glColor3f(0, 0, 0)
    glTranslatef(x, y, z + 35)
    
    # Draw a cube
    glBegin(GL_QUADS)
    # Front face
    glVertex3f(-30, -30, -30)
    glVertex3f(30, -30, -30)
    glVertex3f(30, 30, -30)
    glVertex3f(-30, 30, -30)
    
    # Back face
    glVertex3f(-30, -30, 30)
    glVertex3f(30, -30, 30)
    glVertex3f(30, 30, 30)
    glVertex3f(-30, 30, 30)
    
    # Left face
    glVertex3f(-30, -30, -30)
    glVertex3f(-30, 30, -30)
    glVertex3f(-30, 30, 30)
    glVertex3f(-30, -30, 30)
    
    # Right face
    glVertex3f(30, -30, -30)
    glVertex3f(30, 30, -30)
    glVertex3f(30, 30, 30)
    glVertex3f(30, -30, 30)
    
    # Top face
    glVertex3f(-30, 30, -30)
    glVertex3f(30, 30, -30)
    glVertex3f(30, 30, 30)
    glVertex3f(-30, 30, 30)
    
    # Bottom face
    glVertex3f(-30, -30, -30)
    glVertex3f(30, -30, -30)
    glVertex3f(30, -30, 30)
    glVertex3f(-30, -30, 30)
    glEnd()
    
    glPopMatrix()

def drawPortal(x, y, z):
    glPushMatrix()
    
    # Portal (purple square)
    glColor3f(0.5, 0, 0.8)
    glTranslatef(x, y, z + 15)
    
    # Create a square
    glBegin(GL_QUADS)
    glVertex3f(-40, -40, 0)
    glVertex3f(40, -40, 0)
    glVertex3f(40, 40, 0)
    glVertex3f(-40, 40, 0)
    glEnd()
    
    # Add inner square for portal effect
    glColor3f(0.7, 0.3, 1.0)
    glBegin(GL_QUADS)
    glVertex3f(-20, -20, 1)
    glVertex3f(20, -20, 1)
    glVertex3f(20, 20, 1)
    glVertex3f(-20, 20, 1)
    glEnd()

    glPopMatrix()

def drawShell(x, y, z):
    glPushMatrix()
    
    # Portal (purple circle)
    glColor3f(0.8, 0.2, 0.2)
    glTranslatef(x, y, z + 15)
    
    # Create a circle
    num_segments = 100
    radius = 60
    glBegin(GL_TRIANGLE_FAN)
    for i in range(num_segments + 1):
        theta = 2.0 * math.pi * float(i) / float(num_segments)
        dx = radius * math.cos(theta)
        dy = radius * math.sin(theta)
        glVertex3f(dx, dy, 0)
    glEnd()
    
    # Add inner circle for portal effect
    glColor3f(0.9, 0.4, 0.4)
    radius_inner = 30
    glBegin(GL_TRIANGLE_FAN)
    for i in range(num_segments + 1):
        theta = 2.0 * math.pi * float(i) / float(num_segments)
        dx = radius_inner * math.cos(theta)
        dy = radius_inner * math.sin(theta)
        glVertex3f(dx, dy, 1)
    glEnd()

    glPopMatrix()

def shellSpawn():
    global shellList

    # Boundaries
    min_x = -COLS * GRID_LENGTH / 2 + 50
    max_x = COLS * GRID_LENGTH / 2 - 50
    min_y = -ROWS * GRID_LENGTH / 2 + 50
    max_y = ROWS * GRID_LENGTH / 2 - 50
    
    x = random.randint(int(min_x), int(max_x))
    y = random.randint(int(min_y), int(max_y))
    z = 0
    
    # Ensure shells don't spawn on the snake or other game objects
    valid_position = False
    while not valid_position:
        valid_position = True
        
        # Check if it's too close to the snake
        for segment in snakeBody:
            segment_x, segment_y, segment_z = segment
            if math.sqrt((x - segment_x) ** 2 + (y - segment_y) ** 2) < 60:
                valid_position = False
                break
        
        # Check if it's too close to foods
        for food in foodList + bigFoodList + poisonFoodList:
            if len(food) == 4:
                food_x, food_y, food_z, _ = food
            else:
                food_x, food_y, food_z = food
                
            if math.sqrt((x - food_x) ** 2 + (y - food_y) ** 2) < 80:
                valid_position = False
                break
                
        # Check if it's too close to other obstacles
        for obstacle in obstacleList:
            obs_x, obs_y, obs_z = obstacle
            if math.sqrt((x - obs_x) ** 2 + (y - obs_y) ** 2) < 80:
                valid_position = False
                break
        
        # Check if it's too close to portals
        for portal in portalList:
            portal_x, portal_y, portal_z = portal
            if math.sqrt((x - portal_x) ** 2 + (y - portal_y) ** 2) < 80:
                valid_position = False
                break
        
        # Check if it's too close to walls
        for wall in WallList:
            wall_x, wall_y, wall_z, width, height = wall
            if (wall_x - width / 2 <= x <= wall_x + width / 2) and (wall_y - height / 2 <= y <= wall_y + height / 2):
                valid_position = False
                break

        if not valid_position:
            x = random.randint(int(min_x), int(max_x))
            y = random.randint(int(min_y), int(max_y))
    
    shellList.append((x, y, z))

def obstacleSpawn():
    global obstacleList

    # Boundaries
    min_x = -COLS * GRID_LENGTH / 2 + 50
    max_x = COLS * GRID_LENGTH / 2 - 50
    min_y = -ROWS * GRID_LENGTH / 2 + 50
    max_y = ROWS * GRID_LENGTH / 2 - 50
    
    x = random.randint(int(min_x), int(max_x))
    y = random.randint(int(min_y), int(max_y))
    z = 0
    
    # Ensure obstacles don't spawn on the snake or other game objects
    valid_position = False
    while not valid_position:
        valid_position = True
        
        # Check if it's too close to the snake
        for segment in snakeBody:
            segment_x, segment_y, segment_z = segment
            if math.sqrt((x - segment_x) ** 2 + (y - segment_y) ** 2) < 60:
                valid_position = False
                break
        
        # Check if it's too close to other game objects
        for food in foodList + bigFoodList + poisonFoodList:
            # Handle different structures of foodList and poisonFoodList
            if len(food) == 4:  # This is a poison food with spawn time
                food_x, food_y, food_z, _ = food
            else:
                food_x, food_y, food_z = food
                
            if math.sqrt((x - food_x) ** 2 + (y - food_y) ** 2) < 80:
                valid_position = False
                break
                
        # Check if it's too close to other obstacles
        for obstacle in obstacleList:
            obs_x, obs_y, obs_z = obstacle
            if math.sqrt((x - obs_x) ** 2 + (y - obs_y) ** 2) < 80:
                valid_position = False
                break
        
        # Check if it's too close to portals
        for portal in portalList:
            portal_x, portal_y, portal_z = portal
            if math.sqrt((x - portal_x) ** 2 + (y - portal_y) ** 2) < 80:
                valid_position = False
                break

        # Check if it's too close to shells
        for shell in shellList:
            shell_x, shell_y, shell_z = shell
            if math.sqrt((x - shell_x) ** 2 + (y - shell_y) ** 2) < 80:
                valid_position = False
                break
        
        # Check if it's too close to walls
        for wall in WallList:
            wall_x, wall_y, wall_z, width, height = wall
            if (wall_x - width / 2 <= x <= wall_x + width / 2) and (wall_y - height / 2 <= y <= wall_y + height / 2):
                valid_position = False
                break
        
        if not valid_position:
            x = random.randint(int(min_x), int(max_x))
            y = random.randint(int(min_y), int(max_y))
    
    obstacleList.append((x, y, z))

def portalSpawn():
    global portalList
    
    # We need pairs of portals
    portalList = []
    
    # Boundaries
    min_x = -COLS * GRID_LENGTH / 2 + 50
    max_x = COLS * GRID_LENGTH / 2 - 50
    min_y = -ROWS * GRID_LENGTH / 2 + 50
    max_y = ROWS * GRID_LENGTH / 2 - 50
    
    # First portal
    x1 = random.randint(int(min_x), int(max_x))
    y1 = random.randint(int(min_y), int(max_y))
    z1 = 0
    
    valid_position = False
    while not valid_position:
        valid_position = True
        
        # Check if it's too close to the snake
        for segment in snakeBody:
            segment_x, segment_y, segment_z = segment
            if math.sqrt((x1 - segment_x) ** 2 + (y1 - segment_y) ** 2) < 60:
                valid_position = False
                break
        
        # Check if it's too close to other game objects (similar to obstacleSpawn)
        for food in foodList + bigFoodList + poisonFoodList:
            if len(food) == 4:  # This is a poison food with spawn time
                food_x, food_y, food_z, _ = food
            else:
                food_x, food_y, food_z = food
                
            if math.sqrt((x1 - food_x) ** 2 + (y1 - food_y) ** 2) < 80:
                valid_position = False
                break
        
        # Check if it's too close to obstacles
        for obstacle in obstacleList:
            obs_x, obs_y, obs_z = obstacle
            if math.sqrt((x1 - obs_x) ** 2 + (y1 - obs_y) ** 2) < 80:
                valid_position = False
                break
        
        # Check if it's too close to shells
        for shell in shellList:
            shell_x, shell_y, shell_z = shell
            if math.sqrt((x1 - shell_x) ** 2 + (y1 - shell_y) ** 2) < 80:
                valid_position = False
                break
        
        # Check if it's too close to walls
        for wall in WallList:
            wall_x, wall_y, wall_z, width, height = wall
            if (wall_x - width / 2 <= x1 <= wall_x + width / 2) and (wall_y - height / 2 <= y1 <= wall_y + height / 2):
                valid_position = False
                break
        
        if not valid_position:
            x1 = random.randint(int(min_x), int(max_x))
            y1 = random.randint(int(min_y), int(max_y))
    
    # Second portal
    x2 = random.randint(int(min_x), int(max_x))
    y2 = random.randint(int(min_y), int(max_y))
    z2 = 0
    
    valid_position = False
    while not valid_position:
        valid_position = True
        
        # Check if it's too close to the snake
        for segment in snakeBody:
            segment_x, segment_y, segment_z = segment
            if math.sqrt((x2 - segment_x) ** 2 + (y2 - segment_y) ** 2) < 60:
                valid_position = False
                break
        
        # Check if it's too close to other game objects
        for food in foodList + bigFoodList + poisonFoodList:
            if len(food) == 4:  # This is a poison food with spawn time
                food_x, food_y, food_z, _ = food
            else:
                food_x, food_y, food_z = food
                
            if math.sqrt((x2 - food_x) ** 2 + (y2 - food_y) ** 2) < 80:
                valid_position = False
                break
        
        # Check if it's too close to obstacles
        for obstacle in obstacleList:
            obs_x, obs_y, obs_z = obstacle
            if math.sqrt((x2 - obs_x) ** 2 + (y2 - obs_y) ** 2) < 80:
                valid_position = False
                break
        
        # Check if it's too close to first portal
        if math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2) < 200:  # Minimum distance between portals
            valid_position = False
        
        # Check if it's too close to shells
        for shell in shellList:
            shell_x, shell_y, shell_z = shell
            if math.sqrt((x2 - shell_x) ** 2 + (y2- shell_y) ** 2) < 80:
                valid_position = False
                break
        
        # Check if it's too close to walls
        for wall in WallList:
            wall_x, wall_y, wall_z, width, height = wall
            if (wall_x - width / 2 <= x2 <= wall_x + width / 2) and (wall_y - height / 2 <= y2 <= wall_y + height / 2):
                valid_position = False
                break
        
        if not valid_position:
            x2 = random.randint(int(min_x), int(max_x))
            y2 = random.randint(int(min_y), int(max_y))
    
    portalList.append((x1, y1, z1))
    portalList.append((x2, y2, z2))

def drawWall(x, y, z, width, height):
    glPushMatrix()
    
    # Wall
    glColor3f(0.5, 0.7, 0.2)
    glTranslatef(x, y, z + 35)
    glScalef(width / 60, height / 60, 0.2)  # Reduce the z-axis scaling to make the wall thinner

    # Draw a cube
    glBegin(GL_QUADS)
    # Front face
    glVertex3f(-30, -30, -30)
    glVertex3f(30, -30, -30)
    glVertex3f(30, 30, -30)
    glVertex3f(-30, 30, -30)
    
    # Back face
    glVertex3f(-30, -30, 30)
    glVertex3f(30, -30, 30)
    glVertex3f(30, 30, 30)
    glVertex3f(-30, 30, 30)
    
    # Left face
    glVertex3f(-30, -30, -30)
    glVertex3f(-30, 30, -30)
    glVertex3f(-30, 30, 30)
    glVertex3f(-30, -30, 30)
    
    # Right face
    glVertex3f(30, -30, -30)
    glVertex3f(30, 30, -30)
    glVertex3f(30, 30, 30)
    glVertex3f(30, -30, 30)
    
    # Top face
    glVertex3f(-30, 30, -30)
    glVertex3f(30, 30, -30)
    glVertex3f(30, 30, 30)
    glVertex3f(-30, 30, 30)
    
    # Bottom face
    glVertex3f(-30, -30, -30)
    glVertex3f(30, -30, -30)
    glVertex3f(30, -30, 30)
    glVertex3f(-30, -30, 30)
    glEnd()
    
    glPopMatrix()

def spawnWallEasy():
    global WallList

    # Clear any existing walls
    WallList = []

    # Boundaries
    min_x = -COLS * GRID_LENGTH / 2
    max_x = COLS * GRID_LENGTH / 2
    min_y = -ROWS * GRID_LENGTH / 2
    max_y = ROWS * GRID_LENGTH / 2
    z = 0  # Fixed z-coordinate for the walls

    segment_length = GRID_LENGTH  # Length of each wall segment
    gap_size = GRID_LENGTH * 2  # Size of the gap in the middle

    # Top wall (two segments with a gap in the middle)
    for x in range(int(min_x), int(max_x), segment_length):
        if x + segment_length / 2 < (min_x + max_x) / 2 - gap_size / 2 or x + segment_length / 2 > (min_x + max_x) / 2 + gap_size / 2:
            WallList.append((x + segment_length / 2, max_y, z, segment_length, GRID_LENGTH))

    # Bottom wall (two segments with a gap in the middle)
    for x in range(int(min_x), int(max_x), segment_length):
        if x + segment_length / 2 < (min_x + max_x) / 2 - gap_size / 2 or x + segment_length / 2 > (min_x + max_x) / 2 + gap_size / 2:
            WallList.append((x + segment_length / 2, min_y, z, segment_length, GRID_LENGTH))

    # Left wall (two segments with a gap in the middle)
    for y in range(int(min_y), int(max_y), segment_length):
        if y + segment_length / 2 < (min_y + max_y) / 2 - gap_size / 2 or y + segment_length / 2 > (min_y + max_y) / 2 + gap_size / 2:
            WallList.append((min_x, y + segment_length / 2, z, GRID_LENGTH, segment_length))

    # Right wall (two segments with a gap in the middle)
    for y in range(int(min_y), int(max_y), segment_length):
        if y + segment_length / 2 < (min_y + max_y) / 2 - gap_size / 2 or y + segment_length / 2 > (min_y + max_y) / 2 + gap_size / 2:
            WallList.append((max_x, y + segment_length / 2, z, GRID_LENGTH, segment_length))

def spawnWallMedium():
    global WallList

    # Clear any existing walls
    WallList = []

    # Boundaries
    min_x = -COLS * GRID_LENGTH / 2
    max_x = COLS * GRID_LENGTH / 2
    min_y = -ROWS * GRID_LENGTH / 2
    max_y = ROWS * GRID_LENGTH / 2
    z = 0  # Fixed z-coordinate for the walls

    segment_length = GRID_LENGTH  # Length of each wall segment
    gap_size = GRID_LENGTH * 2  # Size of the gap in the middle

    # Outer walls (with gaps in the middle)
    for x in range(int(min_x), int(max_x), segment_length):
        if x + segment_length / 2 < (min_x + max_x) / 2 - gap_size / 2 or x + segment_length / 2 > (min_x + max_x) / 2 + gap_size / 2:
            WallList.append((x + segment_length / 2, max_y, z, segment_length, GRID_LENGTH))  # Top wall
            WallList.append((x + segment_length / 2, min_y, z, segment_length, GRID_LENGTH))  # Bottom wall

    for y in range(int(min_y), int(max_y), segment_length):
        if y + segment_length / 2 < (min_y + max_y) / 2 - gap_size / 2 or y + segment_length / 2 > (min_y + max_y) / 2 + gap_size / 2:
            WallList.append((min_x, y + segment_length / 2, z, GRID_LENGTH, segment_length))  # Left wall
            WallList.append((max_x, y + segment_length / 2, z, GRID_LENGTH, segment_length))  # Right wall

    # Inner horizontal walls (smaller total size)
    for x in range(int(min_x) + GRID_LENGTH * 2, int(max_x) - GRID_LENGTH * 2, segment_length):
        WallList.append((x + segment_length / 2, (min_y + max_y) / 4, z, segment_length, GRID_LENGTH * 0.5))  # Top inner wall
        WallList.append((x + segment_length / 2, (3 * (min_y + max_y)) / 4, z, segment_length, GRID_LENGTH * 0.5))  # Bottom inner wall

    # Inner vertical walls (smaller total size)
    for y in range(int(min_y) + GRID_LENGTH * 2, int(max_y) - GRID_LENGTH * 2, segment_length):
        WallList.append(((min_x + max_x) / 4, y + segment_length / 2, z, GRID_LENGTH * 0.5, segment_length))  # Left inner wall
        WallList.append(((3 * (min_x + max_x)) / 4, y + segment_length / 2, z, GRID_LENGTH * 0.5, segment_length))  # Right inner wall

def spawnWallHard():
    global WallList

    # Clear any existing walls
    WallList = []

    # Boundaries
    min_x = -COLS * GRID_LENGTH / 2
    max_x = COLS * GRID_LENGTH / 2
    min_y = -ROWS * GRID_LENGTH / 2
    max_y = ROWS * GRID_LENGTH / 2
    z = 0  # Fixed z-coordinate for the walls

    segment_length = GRID_LENGTH  # Length of each wall segment
    gap_size = GRID_LENGTH * 2  # Size of the gap in the middle

    # Outer walls (no gaps)
    for x in range(int(min_x), int(max_x), segment_length):
        WallList.append((x + segment_length / 2, max_y, z, segment_length, GRID_LENGTH))  # Top wall
        WallList.append((x + segment_length / 2, min_y, z, segment_length, GRID_LENGTH))  # Bottom wall

    for y in range(int(min_y), int(max_y), segment_length):
        WallList.append((min_x, y + segment_length / 2, z, GRID_LENGTH, segment_length))  # Left wall
        WallList.append((max_x, y + segment_length / 2, z, GRID_LENGTH, segment_length))  # Right wall

    # Inner horizontal walls (smaller total size)
    for x in range(int(min_x) + GRID_LENGTH * 2, int(max_x) - GRID_LENGTH * 2, segment_length):
        WallList.append((x + segment_length / 2, (min_y + max_y) / 4, z, segment_length, GRID_LENGTH * 0.5))  # Top inner wall
        WallList.append((x + segment_length / 2, (3 * (min_y + max_y)) / 4, z, segment_length, GRID_LENGTH * 0.5))  # Bottom inner wall

    # Inner vertical walls (smaller total size)
    for y in range(int(min_y) + GRID_LENGTH * 2, int(max_y) - GRID_LENGTH * 2, segment_length):
        WallList.append(((min_x + max_x) / 4, y + segment_length / 2, z, GRID_LENGTH * 0.5, segment_length))  # Left inner wall
        WallList.append(((3 * (min_x + max_x)) / 4, y + segment_length / 2, z, GRID_LENGTH * 0.5, segment_length))  # Right inner wall

    # Diagonal walls (for added complexity)
    for i in range(1, 4):
        # Top-left to bottom-right
        WallList.append((min_x + i * GRID_LENGTH, min_y + i * GRID_LENGTH, z, GRID_LENGTH, GRID_LENGTH))  # Bottom-left to top-right
        WallList.append((max_x - i * GRID_LENGTH, min_y + i * GRID_LENGTH, z, GRID_LENGTH, GRID_LENGTH))  # Bottom-right to top-left

        # Bottom-left to top-right
        WallList.append((min_x + i * GRID_LENGTH, max_y - i * GRID_LENGTH, z, GRID_LENGTH, GRID_LENGTH))  # Top-left to bottom-right
        WallList.append((max_x - i * GRID_LENGTH, max_y - i * GRID_LENGTH, z, GRID_LENGTH, GRID_LENGTH))  # Top-right to bottom-left


def drawCheatBar():
    global cheatBarProgress, cheatBarFull, cheatModeActive, cheatModeStartTime, cheatModeDuration
    
    # Draw the cheat bar background
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, 1000, 0, 800)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    
    # Draw background bar
    glColor3f(0.3, 0.3, 0.3)
    glBegin(GL_QUADS)
    glVertex2f(10, 730)
    glVertex2f(210, 730)
    glVertex2f(210, 750)
    glVertex2f(10, 750)
    glEnd()
    
    # Calculate progress
    progress_width = 0
    
    # Draw progress bar
    if cheatModeActive:
        # Show time remaining during cheat mode
        remaining_time = max(0, cheatModeDuration - (time.time() - cheatModeStartTime))
        progress_width = (remaining_time / cheatModeDuration) * 200
        glColor3f(1.0, 0.0, 1.0)  # Purple for active cheat mode
    else:
        progress_width = (cheatBarProgress / cheatBarFull) * 200
        if cheatBarProgress >= cheatBarFull:
            glColor3f(0.0, 1.0, 0.0)  # Green when full
        else:
            glColor3f(1.0, 0.5, 0.0)  # Orange when filling
    
    glBegin(GL_QUADS)
    glVertex2f(10, 730)
    glVertex2f(10 + progress_width, 730)
    glVertex2f(10 + progress_width, 750)
    glVertex2f(10, 750)
    glEnd()
    
    # Draw text
    if cheatModeActive:
        remaining_time = max(0, cheatModeDuration - (time.time() - cheatModeStartTime))
        draw_text(220, 733, f"CHEAT MODE ACTIVE: {remaining_time:.1f}s")
    elif cheatBarProgress >= cheatBarFull:
        draw_text(220, 733, "CHEAT MODE READY - PRESS C")
    else:
        draw_text(220, 733, f"CHEAT MODE: {int(cheatBarProgress)}/{cheatBarFull}")
    
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

def specialKeyListener(key, x, y):
    global camera_pos
    x, y, z = camera_pos

    if key == GLUT_KEY_UP:
        y -= 10
        z -= 10

    if key == GLUT_KEY_DOWN:
        y += 10
        z += 10

    if key == GLUT_KEY_LEFT:
        x -= 10

    if key == GLUT_KEY_RIGHT:
        x += 10

    camera_pos = (x, y, z)

def mouseListener(button, state, x, y):
    global firstPerson

    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
        pass
        
    if button == GLUT_RIGHT_BUTTON and state == GLUT_DOWN:
        firstPerson = not firstPerson

def keyboardListener(key, x, y):
    global Menu, Easy, Medium, Hard, snakeAngle, gameOver, gamePaused
    global cheatModeActive, cheatModeStartTime, cheatBarProgress

    # Move to main menu (M key)
    if key == b'm':
        Menu = True
        Easy = False
        Medium = False
        Hard = False
        resetGame()

    # Pause game (P key)
    if key == b'p':
        gamePaused = not gamePaused
        return

    # Restart game if it's over
    if gameOver and key == b'r':
        resetGame()
        return

    # Activate cheat mode
    if key == b'c' and cheatBarProgress >= cheatBarFull and not cheatModeActive:
        cheatModeActive = True
        cheatModeStartTime = time.time()
        cheatBarProgress = 0

    # Move forward (W key)
    if key == b'w':
        if snakeAngle != 180:
            snakeAngle = 0

    # Move backward (S key)
    if key == b's':
        if snakeAngle != 0:
            snakeAngle = 180

    # Rotate gun left (A key)
    if key == b'a':
        if snakeAngle != 270:
            snakeAngle = 90

    # Rotate gun right (D key)
    if key == b'd':
        if snakeAngle != 90:
            snakeAngle = 270
    
    if key == b'1' and Menu:
        Menu = False
        Easy = True
        Medium = False
        Hard = False
        resetGame()
    
    if key == b'2'and Menu:
        Menu = False
        Easy = False
        Medium = True
        Hard = False
        resetGame()
    
    if key == b'3'and Menu:
        Menu = False
        Easy = False
        Medium = False
        Hard = True
        resetGame()

def resetGame():
    global snakeBody, snakeLength, positionHistory, snakeAngle, score, snakeSpeed
    global foodList, bigFoodList, poisonFoodList, obstacleList, portalList, gameOver
    global cheatModeActive, cheatBarProgress
    
    # Reset snake
    snakeBody = []
    snakeLength = 1
    positionHistory = []
    snakeAngle = 0
    
    # Reset game objects
    foodList = []
    bigFoodList = []
    poisonFoodList = []
    obstacleList = []
    portalList = []
    
    # Reset game state
    score = 0
    gameOver = False
    
    # Reset cheat mode
    cheatModeActive = False
    cheatBarProgress = 0
    
    # Reset snake speed
    snakeSpeed = 2
    
    # Initialize snake
    drawSnakeBody()
    prefillPositionHistory()
    
    # Spawn initial food
    foodSpawn(1)

def setupCamera():
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(fovY, 1.25, 0.1, 1500)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    if firstPerson:
        head_x, head_y, head_z = snakeBody[0]

        # Position the camera slightly behind and above the snake's head
        eyeX = head_x
        eyeY = head_y
        eyeZ = head_z + 100

        # Adjust the center position based on the snake's angle
        centerX = head_x - math.sin(math.radians(-snakeAngle)) * 50
        centerY = head_y - math.cos(math.radians(-snakeAngle)) * 50
        centerZ = head_z

        gluLookAt(eyeX, eyeY, eyeZ,
                centerX, centerY, centerZ,
                0, 0, 1)
    else:
        x, y, z = camera_pos

        cameraAngle = math.radians(x)

        x = y * math.sin(cameraAngle)
        y = y * math.cos(cameraAngle)
            
        gluLookAt(x, y, z,
                0, 0, 0,
                0, 0, 1)

def idle():
    global snakeAngle, snakeLength, snakeSpeed, portalTimer
    global cheatModeActive, cheatModeStartTime, cheatModeDuration

    if not gamePaused and not gameOver:
        # Update cheat mode timer
        if cheatModeActive:
            current_time = time.time()
            if current_time - cheatModeStartTime >= cheatModeDuration:
                cheatModeActive = False

        # Snake Movement
        snakeForwardMovement()

        # Food Pulse Wave
        foodPulseWave()

        # Food Collision and Spawn
        Collision()

        # Update poison food lifetime
        updatePoisonFoodLifetime()

        # Spawn obstacles randomly (about every 40 seconds)
        if random.random() < 0.0003:
            obstacleSpawn()
        
        # Spawn portals randomly (about every 30 seconds)
        current_time = time.time()
        if len(portalList) == 0 and current_time - portalTimer > portalSpawnInterval:
            portalSpawn()
            portalTimer = current_time
        
        # Spawn shell every 30 points
        if score % 30 == 0 and score > 0 and len(shellList) == 0:
            shellSpawn()

    glutPostRedisplay()

def showScreen():
    global snakeBody, wallList

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    glViewport(0, 0, 1000, 800)
    setupCamera()

    if gameOver:
        GameOverScreen()
        glutSwapBuffers()
        return
    elif Menu:
        mainMenu()
        foodSpawn()
    elif Easy:
        levelEasy()
        spawnWallEasy()
        
    elif Medium:
        levelMedium()
        spawnWallMedium()

        snakeX, snakeY, snakeZ = snakeBody[0]
        if snakeX == 0 and snakeY == 0:
            snakeBody[0] = [-250, -250, 0]

    elif Hard:
        levelHard()
        spawnWallHard()

        snakeX, snakeY, snakeZ = snakeBody[0]
        if snakeX == 0 and snakeY == 0:
            snakeBody[0] = [200, 400, 0]
    
    if Easy or Medium or Hard:
        # Draw the snake
        drawSnake()

        # Draw the food
        for food in foodList:
            drawFood(food[0], food[1], food[2])
        
        for bigFood in bigFoodList:
            drawBigFood(bigFood[0], bigFood[1], bigFood[2])
        
        for poisonFood in poisonFoodList:
            poisonFood_x, poisonFood_y, poisonFood_z, _ = poisonFood
            drawPoisonFood(poisonFood_x, poisonFood_y, poisonFood_z)
        
        # Draw the Brick Wall
        for wall in WallList:
            drawWall(wall[0], wall[1], wall[2], wall[3], wall[4])

        # Draw shells
        for shell in shellList:
            drawShell(shell[0], shell[1], shell[2])
        
        # Draw obstacles
        for obstacle in obstacleList:
            drawObstacle(obstacle[0], obstacle[1], obstacle[2])
        
        # Draw portals
        for portal in portalList:
            drawPortal(portal[0], portal[1], portal[2])

        draw_text(10, 770, f"Game Score: {score}")
        draw_text(200, 770, f"Speed: {snakeSpeed + (score // 30) * 1:.1f}")

        # Draw cheat mode bar
        drawCheatBar()

    glutSwapBuffers()


def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(1000, 800)
    glutInitWindowPosition(0, 0)
    wind = glutCreateWindow(b"Snake Game Project")
    drawSnakeBody()
    prefillPositionHistory()
    glutDisplayFunc(showScreen)
    glutKeyboardFunc(keyboardListener)
    glutSpecialFunc(specialKeyListener)
    glutMouseFunc(mouseListener)
    glutIdleFunc(idle)

    glutMainLoop()

if __name__ == "__main__":
    main()
