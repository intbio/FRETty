#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) Grigoriy A. Armeev, 2015
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as·
# published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License v2 for more details.

# Cheers, Satary.
#
# This widget provides simple interface for showing pictures.
# It can be resized saving aspect ratio and it provides signals for mouse click and hover.
import sys, os
from PyQt4 import QtGui,QtCore
'''
This widget implements folders and pictures
'''
class ImageWidget(QtGui.QWidget):
    def __init__(self,parent=None):
        super(ImageWidget, self).__init__()
        
        mainLayout=QtGui.QVBoxLayout(self)
        mainLayout.setSpacing(0)
        mainLayout.setContentsMargins(0,0,0,0)       
        
        self.label=CustomLabel(self)
        mainLayout.addWidget(self.label)
        self.connect(self.label,QtCore.SIGNAL("mousePressSignal"),self.emitWigetPressedSignal)
        self.connect(self.label,QtCore.SIGNAL("mouseHoverSignal"),self.emitWigetHoveredSignal)
    
    def setImage(self,path):
        '''
        Reads image from path and sets it to wiget
        '''
        self.currentPath=self.label.path=path
        self.pixmap=QtGui.QPixmap(path)
        self.label.initsize=self.pixmap.size()
        size=self.size()#-QtCore.QSize(20,20)
        self.resizeImage(size)
        
    def emitWigetPressedSignal(self, coord, path):
        '''
        Emits signal imageWigetPressed wich provides coordinates of in pixels (as on initial picture)
        and path to that picture
        '''
        self.emit(QtCore.SIGNAL("imageWigetPressed"),coord,path)
        
    def emitWigetHoveredSignal(self, coord, path):
        '''
        Emits signal imageWigetHovered wich provides coordinates of in pixels (as on initial picture)
        and path to that picture
        '''
        self.emit(QtCore.SIGNAL("imageWigetHovered"),coord,path)
        
    def resizeEvent( self, resizeEvent):
        '''
        Overrides QWigets resizeEvent for better quality resizing of the pixmap
        
        '''
        super(ImageWidget, self).resizeEvent(resizeEvent)
        self.resizeImage(resizeEvent.size())
        
    def resizeImage(self, size):
        '''
        Resizes image keeping aspect ratio
        '''
        try:
            
            self.label.resize(size)
            pixmap=self.pixmap.scaled(size, QtCore.Qt.KeepAspectRatio)            
            self.label.setPixmap(pixmap)
            self.label.update()
            self.label.picSize=pixmap.size()
        except:
            self.label.setText('No image loaded.')
       

class CustomLabel(QtGui.QLabel):
    '''
    This class provides modified QLabel 
    which provides QSignals with coordinates in coord. system of initial image
    Provides signal for mouse hovering.
    '''
    def __init__(self, parent=None, path=None):
        super(CustomLabel, self).__init__(parent)
        self.path=path
        self.setMouseTracking(True)
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.hoverMouse)
        self.setAlignment(QtCore.Qt.AlignCenter)
        self.setSizePolicy(QtGui.QSizePolicy.Ignored,QtGui.QSizePolicy.Ignored)

    def calcCoord(self,x,y):
        lblwidth=self.size().width()
        picwidth=self.picSize.width()
        lblheight=self.size().height()
        picheight=self.picSize.height()
        initwidth=self.initsize.width()
        initheight=self.initsize.height()
        x=int((x-(lblwidth-picwidth)/2.0)*initwidth/picwidth)
        y=int((y-(lblheight-picheight)/2.0)*initheight/picheight)
        if (x>0) and (y>0) and (x < initwidth) and (y < initheight):
            return x,y
        else:
            return None

    def mousePressEvent(self, e):
        try:
            super(CustomLabel, self).mousePressEvent(e)
            coord=self.calcCoord(e.x(),e.y())
            if coord!=None:
                self.coord=coord
                self.emit(QtCore.SIGNAL("mousePressSignal"),self.coord,self.path)
        except:
            pass
        
    def mouseMoveEvent(self, e):
        try:
            super(CustomLabel, self).mouseMoveEvent(e)
            self.coord=self.calcCoord(e.x(),e.y())
            self.timer.stop()
            self.timer.start(600)
        except:
            pass
        
    def hoverMouse(self):        
        self.timer.stop()
        if self.underMouse() and (self.coord!=None):
            self.emit(QtCore.SIGNAL("mouseHoverSignal"),self.coord,self.path)
