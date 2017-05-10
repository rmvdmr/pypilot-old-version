#!/usr/bin/env python
#
#   Copyright (C) 2016 Sean D'Epagnier
#
# This Program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public
# License as published by the Free Software Foundation; either
# version 3 of the License, or (at your option) any later version.  

import math, json, Image, numpy

from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GL import *

import objview
from pypilot import quaternion

class BoatPlot():
    def __init__(self):
        self.Q = [-0.32060682, -0.32075041, 0.73081691, -0.51013437]
        self.Scale = 3
        self.compasstex = 0
        self.objinit = False
        self.texture_compass = True

    def display(self, fusionQPose):
        #fusionQPose = [1, 0, 0, 0]
        if not self.objinit:
            objview.init('sailboat.obj')
            self.objinit = True

        glClearColor(0, .2, .7, 0)
        glClearDepth(100)
        
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        glPushMatrix()

        def glRotateQ(q):
            try:
                glRotatef(quaternion.angle(q)*180/math.pi, q[1], q[2], q[3])
            except:
                pass

        dist = 16
        glTranslatef(0, 0, -dist)
        glScalef(self.Scale, self.Scale, self.Scale)
        glRotateQ(self.Q)

        glPushMatrix()
        #q = quaternion.multiply(fusionQPose, quaternion.angvec2quat(-math.pi/2, [1, 0, 0]))
        q = fusionQPose
        glRotateQ(q)
        glTranslatef(0, 0, -.7)
        objview.draw()
        glPopMatrix()

        if self.texture_compass:
            self.draw_texture_compass()
        else:
            self.draw_vector_compass()
        glPopMatrix()

    def draw_vector_compass(self):

        s = 1

        #glTranslatef(0, -2*s, 0)
        
        def draw_string(str, pos):
            viewport = glGetIntegerv(GL_VIEWPORT)
            proj = glGetDoublev(GL_PROJECTION_MATRIX)
            model = glGetDoublev(GL_MODELVIEW_MATRIX)
            winpos = gluProject(pos[0], pos[1], pos[2], model, proj, viewport)
            glPushMatrix()
            glLoadIdentity()
            glMatrixMode(GL_PROJECTION)
            glPushMatrix()
            glLoadIdentity()
            glRasterPos2d(2*winpos[0]/viewport[2]-1, 2*winpos[1]/viewport[3]-1)
            for c in str:
                glutBitmapCharacter(GLUT_BITMAP_9_BY_15, ctypes.c_int(ord(c)))

            glPopMatrix()
            glMatrixMode(GL_MODELVIEW)
            glPopMatrix()

        draw_string('N', [s, 0, 0])
        draw_string('S', [-s, 0, 0])
        draw_string('E', [0, s, 0])
        draw_string('W', [0, -s, 0])

        glBegin(GL_LINES)
        f = .9*s
        glVertex2f(-f, 0), glVertex2f(f, 0)
        glVertex2f(0, -f), glVertex2f(0, f)
        glEnd()

    def draw_texture_compass(self):
        if self.compasstex == 0:
            self.compasstex = glGenTextures(1)
            img = Image.open('compass.png')

            data = numpy.array(list(img.getdata()), numpy.int8)
            glBindTexture(GL_TEXTURE_2D, self.compasstex)

            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

            glPixelStorei(GL_UNPACK_ALIGNMENT, 1)
#            glTexImage2D( GL_TEXTURE_2D, 0, GL_RGBA,
#                          img.size[0], img.size[1], 0, GL_RGBA, GL_UNSIGNED_BYTE, data )
            gluBuild2DMipmaps(GL_TEXTURE_2D, GL_RGBA,
                              img.size[0], img.size[1], GL_RGBA, GL_UNSIGNED_BYTE, data)
        
        glEnable(GL_TEXTURE_2D)
        glEnable(GL_BLEND)
        glBlendFunc( GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA );

        glBindTexture(GL_TEXTURE_2D, self.compasstex)
        glBegin(GL_QUADS)
        glTexCoord2f(0, 0),        glVertex3f(-1, -1, 0)
        glTexCoord2f(1, 0),        glVertex3f(1, -1, 0)
        glTexCoord2f(1, 1),        glVertex3f(1, 1, 0)
        glTexCoord2f(0, 1),        glVertex3f(-1, 1, 0)
        glEnd()
        glDisable(GL_BLEND)
        glDisable(GL_TEXTURE_2D)

    def reshape(self, width, height):
        glViewport(0, 0, width, height)

        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        ar = 0.5 * width / height
        glFrustum(-ar, ar, -0.5, 0.5, 2.0, 300.0)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

if __name__ == '__main__':
    plot = BoatPlot()

    def display():
        plot.display([1, 0, 0, 0])
        glutSwapBuffers()

    last = False
    def mouse(button, state, x, y):
        if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
            global last
            last = x, y
                
    def motion(x, y):
        global last
        dx, dy = x - last[0], y - last[1]
        q = quaternion.angvec2quat((dx**2 + dy**2)**.4/180*math.pi, [dy, dx, 0])
        plot.Q = quaternion.multiply(q, plot.Q)
        last = x, y
        glutPostRedisplay()

    def keyboard(key, x, y):
        exit(0)

    glutInit(sys.argv)
    glutInitWindowPosition(0, 0)
    glutInitWindowSize(600, 500)
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutCreateWindow(sys.argv[0])

#    glutIdleFunc(idle)
    glutReshapeFunc( plot.reshape )
    glutDisplayFunc( display )

    glutKeyboardFunc( keyboard )
    glutMouseFunc( mouse )
    glutMotionFunc( motion )
    
    glutMainLoop()