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

# Snake variables
snakePos = [0, 0, 0]
snakeLength = 5
snakeRadius = 30
snakeBody = []
snakeAngle = 0
snakeSpeed = 2
snakeColor = (1, 0, 0)
positionHistory = []

# Food variables
foodList = []



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

def foodSpawn(totalFood=5):
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
    global foodList, snakeBody, snakeLength, snakeSpeed, snakeRadius

    foodToRemove = []

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
    global snakePos, snakeAngle, snakeLength, snakeSpeed

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
