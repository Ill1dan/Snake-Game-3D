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
snakeLength = 2
snakeAngle = 0
snakeSpeed = 2
snakeColor = (1, 0, 0)


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

    # Snake Position
    glTranslatef(snakePos[0], snakePos[1], snakePos[2])
    glRotatef(snakeAngle, 0, 0, 1)

    for i in range(snakeLength):
        if i == 0:
            glColor3f(0.6, 0, 0)
        else:
            glColor3f(snakeColor[0], snakeColor[1], snakeColor[2])
        glTranslatef(0, i * 50, 0)
        gluSphere(gluNewQuadric(), 30, 10, 10)

    glPopMatrix()

def snakeForwardMovement():
    global snakePos, snakeAngle, snakeLength, snakeSpeed

    # Boundaries
    min_x = -COLS * GRID_LENGTH / 2 + 50
    max_x = COLS * GRID_LENGTH / 2 - 50
    min_y = -ROWS * GRID_LENGTH / 2 + 50
    max_y = ROWS * GRID_LENGTH / 2 - 50

    # Snake Movement
    snakePos[0] -= snakeSpeed * math.sin(math.radians(-snakeAngle))
    snakePos[1] -= snakeSpeed * math.cos(math.radians(snakeAngle))

    if snakePos[0] < min_x:
        snakePos[0] = min_x
    if snakePos[0] > max_x:
        snakePos[0] = max_x
    if snakePos[1] < min_y:
        snakePos[1] = min_y
    if snakePos[1] > max_y:
        snakePos[1] = max_y


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
    global gameOver, firstPerson

    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
        pass
    
    if button == GLUT_RIGHT_BUTTON and state == GLUT_DOWN:
        pass

def keyboardListener(key, x, y):
    global snakePos, snakeAngle, snakeLength, snakeSpeed

    # Move forward (W key)
    if key == b'w':
        pass

    # Move backward (S key)
    if key == b's':
        pass

    # Rotate gun left (A key)
    if key == b'a':
        snakeAngle += 90
        if snakeAngle > 360:
            snakeAngle -= 360

    # Rotate gun right (D key)
    if key == b'd':
        snakeAngle -= 90
        if snakeAngle < 0:
            snakeAngle += 360

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

    glutPostRedisplay()


def showScreen():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    glViewport(0, 0, 1000, 800)

    setupCamera()
    levelEasy()
    drawSnake()

    glutSwapBuffers()


def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(1000, 800)
    glutInitWindowPosition(0, 0)
    wind = glutCreateWindow(b"Snake Game Project")

    glutDisplayFunc(showScreen)
    glutKeyboardFunc(keyboardListener)
    glutSpecialFunc(specialKeyListener)
    # glutMouseFunc(mouseListener)
    glutIdleFunc(idle)

    glutMainLoop()

if __name__ == "__main__":
    main()
