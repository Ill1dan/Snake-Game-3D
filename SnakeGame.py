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
        # Move forward (W key)
        if key == b'w':
            pass

        # Move backward (S key)
        if key == b's':
            pass

        # Rotate gun left (A key)
        if key == b'a':
            pass

        # Rotate gun right (D key)
        if key == b'd':
            pass

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

    glutPostRedisplay()


def showScreen():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    glViewport(0, 0, 1000, 800)

    setupCamera()

    glutSwapBuffers()


def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(1000, 800)
    glutInitWindowPosition(0, 0)
    wind = glutCreateWindow(b"Snake Game Project")

    glutDisplayFunc(showScreen)
    # glutKeyboardFunc(keyboardListener)
    # glutSpecialFunc(specialKeyListener)
    # glutMouseFunc(mouseListener)
    glutIdleFunc(idle)

    glutMainLoop()

if __name__ == "__main__":
    main()
