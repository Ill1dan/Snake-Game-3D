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
mainMenu = True
Easy = False
Medium = False
Hard = False
gameOver = False
gamePaused = False

# Snake variables
snakePos = [0, 0, 0]
snakeLength = 1
snakeRadius = 30
snakeBody = []
snakeAngle = 0
snakeSpeed = 2
snakeColor = (1, 0, 0)
positionHistory = []

# Food variables
foodList = []

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
        drawLine(x + width / 2, y + height / 2, x, y + height / 2)  # Connect to left
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

def drawSnake():
    glPushMatrix()

    for i, segment in enumerate(snakeBody):
        glPushMatrix()

        if i == 0:
            glColor3f(0.6, 0, 0)
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
    global snakePos, snakeAngle, snakeLength, snakeSpeed, snakeBody, positionHistory

    # Boundaries
    min_x = -COLS * GRID_LENGTH / 2 + 50
    max_x = COLS * GRID_LENGTH / 2 - 50
    min_y = -ROWS * GRID_LENGTH / 2 + 50
    max_y = ROWS * GRID_LENGTH / 2 - 50

    # Move the head
    snakeBody[0][0] -= snakeSpeed * math.sin(math.radians(-snakeAngle))
    snakeBody[0][1] -= snakeSpeed * math.cos(math.radians(snakeAngle))

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
    max_history_length = (snakeLength + 1) * (snakeRadius * 2) // snakeSpeed
    if len(positionHistory) > max_history_length:
        positionHistory.pop()

    # Move body segments along the path history
    for i in range(1, len(snakeBody)):
        index = i * (snakeRadius * 2) // snakeSpeed
        if index < len(positionHistory):
            snakeBody[i][0] = positionHistory[index][0]
            snakeBody[i][1] = positionHistory[index][1]
            snakeBody[i][2] = positionHistory[index][2]

def drawFood(x, y, z):
    glPushMatrix()
    
    # Food Orange Sphere
    glColor3f(1, 0.6, 0)

    glTranslatef(x, y, z + 35)
    # glScale(enemyPulse, enemyPulse, enemyPulse)
    gluSphere(gluNewQuadric(), 30, 10, 10)

    glPopMatrix()

def foodSpawn(totalFood=1):
    global foodList

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

        for segment in snakeBody:
            segment_x, segment_y, segment_z = segment

            while (x >= segment_x - 30 and x <= segment_x + 30) and (y >= segment_y - 30 and y <= segment_y + 30):
                x = random.randint(int(min_x), int(max_x))
                y = random.randint(int(min_y), int(max_y))

        foodList.append((x, y, z))

def foodCollision():
    global foodList, snakeBody, snakeLength

    for food in foodList:
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
    global snakeAngle, snakeLength, snakeSpeed, snakeBody

    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
        pass
        
    if button == GLUT_RIGHT_BUTTON and state == GLUT_DOWN:
        pass

def keyboardListener(key, x, y):
    global mainMenu, Easy, Medium, Hard, snakeAngle

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
    
    if key == b'1':
        mainMenu = False
        Easy = True
        Medium = False
        Hard = False
    
    if key == b'2':
        mainMenu = False
        Easy = False
        Medium = True
        Hard = False
    
    if key == b'3':
        mainMenu = False
        Easy = False
        Medium = False
        Hard = True

def setupCamera():
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(fovY, 1.25, 0.1, 1500)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    x, y, z = camera_pos

    cameraAngle = math.radians(x)

    x = y * math.sin(cameraAngle)
    y = y * math.cos(cameraAngle)
        
    gluLookAt(x, y, z,
            0, 0, 0,
            0, 0, 1)


def idle():
    global snakePos, snakeAngle, snakeLength, snakeSpeed

    # Snake Movement
    snakeForwardMovement()

    foodCollision()

    glutPostRedisplay()


def showScreen():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    glViewport(0, 0, 1000, 800)
    setupCamera()

    if mainMenu:
        mainMenu()
    elif Easy:
        levelEasy()
        drawSnake()
        # Draw the food
        for food in foodList:
            drawFood(food[0], food[1], food[2])

    glutSwapBuffers()


def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(1000, 800)
    glutInitWindowPosition(0, 0)
    wind = glutCreateWindow(b"Snake Game Project")
    drawSnakeBody()
    prefillPositionHistory()
    foodSpawn()
    glutDisplayFunc(showScreen)
    glutKeyboardFunc(keyboardListener)
    glutSpecialFunc(specialKeyListener)
    glutMouseFunc(mouseListener)
    glutIdleFunc(idle)

    glutMainLoop()

if __name__ == "__main__":
    main()
