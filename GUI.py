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

import sys,os,time
import numpy as np
from pyfret import pyFRET as pft
from PyQt4 import QtGui, QtCore
from table_widget import TableWidget
from image_widget import ImageWidget
from file_source_widget import FileSourceWidget

from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QTAgg as NavigationToolbar
import matplotlib.pyplot as plt


try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s
    
class MainWindow(QtGui.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.initUI()
        self.show()
    
    def initUI(self):
        '''
        Setting up Interface
        '''
        mainWidget = QtGui.QSplitter(QtCore.Qt.Horizontal)
        mainWidget.setSizes([1,3])
        
        self.fileMenu=FileSourceWidget(self)

        mainWidget.addWidget(self.fileMenu)
        

        tabs = QtGui.QTabWidget(self)
    
        images=QtGui.QWidget(self)
        imagesLayout=QtGui.QVBoxLayout(images)
        tabs.addTab(images,"Simple spFRET")
        
        self.figure = plt.figure()
        self.canvas = FigureCanvas(self.figure)
        self.toolbar = NavigationToolbar(self.canvas, self)
        imagesLayout.addWidget(self.canvas)
        imagesLayout.addWidget(self.toolbar)
        #self.preview=ImageWidget(self)  
        #imagesLayout.addWidget(self.preview)
        
        #self.result=ImageWidget(self)  
        #imagesLayout.addWidget(self.result)
        
       
        fastFRET=QtGui.QWidget(self)
        fastFRETLayout=QtGui.QVBoxLayout(fastFRET)
        tabs.addTab(fastFRET,"Fast spFRET")
        mainWidget.addWidget(tabs)
        
        controlWidget=QtGui.QWidget(self)
        controlLayout=QtGui.QVBoxLayout(controlWidget)
        controlLayout.setAlignment(QtCore.Qt.AlignTop)
        
        #self.runButton=QtGui.QPushButton('Run calc')
        #controlLayout.addWidget(self.runButton)     
        
        #self.pbar = QtGui.QProgressBar(self) 
        #controlLayout.addWidget(self.pbar)    
        
        mainWidget.addWidget(controlWidget)
        self.setCentralWidget(mainWidget)
        self.setWindowTitle('-PASTENAME-GUI')   
        
        self.assignConnections()
        
        
    def assignConnections(self):
        '''
        Assigning connections
        '''
        self.connect(self.fileMenu,QtCore.SIGNAL("updateFilePreview"),self.preview_file)
        
        #self.connect(self.preview,QtCore.SIGNAL("imageWigetPressed"),self.previewClicked)
        #self.connect(self.preview,QtCore.SIGNAL("imageWigetHovered"),self.previewHovered)
        
        #self.connect(self.result,QtCore.SIGNAL("imageWigetPressed"),self.resultClicked)
        #self.connect(self.result,QtCore.SIGNAL("imageWigetHovered"),self.resultHovered)
        
        #self.runButton.clicked.connect(self.run_calculations)
    
    def previewClicked(self, coord, path):
        print "preview Clicked",coord, path
    
    def previewHovered(self, coord, path):
        print "preview Hovered",coord, path
         
    def resultClicked(self, coord, path):
        print "result Clicked",coord, path
         
    def resultHovered(self, coord, path):
        print "result Hovered",coord, path 
        
    def preview_file(self,data):
        lol = pft.FRET_data(data[:,2],data[:,1])
        lol.subtract_bckd(2.0,1.0)
        threshold_donor = 7 # donor threshold
        threshold_acceptor = 5 # acceptor threshold
        lol.threshold_SUM(threshold_donor)
        cross_DtoA = 0.20 # fractional crosstalk from donor to acceptor
        cross_AtoD = 0.01 # fractional crosstalk from acceptor to donor
        lol.subtract_crosstalk(cross_DtoA, cross_AtoD)
        
        ax = self.figure.add_subplot(111)
        ax.hold(False)
        result=np.histogram(lol.proximity_ratio(gamma=0.95),np.arange(0,1.05,0.05),normed=True)
        ax.plot(result[1][:-1]+(result[1][1]-result[1][0])/2.0,result[0])
        self.canvas.draw()

    
    def run_calculations(self):
        '''
        Running calculation in separate thread
        '''
        #Setting up thread and worker
        self.workThread = QtCore.QThread()
        self.worker = Calculator(self.fileMenu.getSelectedPaths())
        self.worker.moveToThread(self.workThread)
        #connect signal for thread finish
        self.worker.finished.connect(self.workThread.quit)
        #connect signal for table update
        self.worker.signal_update_table.connect(self.update_table)
        #connect signal for status update 
        self.worker.signal_update_pbar.connect(self.updateProgressBar)
        #connect signal of started thread for running calculations
        self.workThread.started.connect(self.worker.run)
        #Run Forest! Run!
        self.workThread.start()
        
    def update_table(self,dictionary):
        self.tableWidget.buildFromDict(dictionary)
        
    def updateProgressBar(self,value):
        self.pbar.setValue(value)
        
class Calculator(QtCore.QObject): 
    signal_update_table = QtCore.pyqtSignal(dict) 
    signal_update_pbar = QtCore.pyqtSignal(int) 
    finished = QtCore.pyqtSignal()   
     
    def __init__(self,listOfPaths):
        QtCore.QObject.__init__(self)
        self.paths=listOfPaths
    
    def run(self):
        print 'started'
        status=0
        for path in self.paths:
            time.sleep(3)
            status+=1
            self.signal_update_pbar.emit(status*100/len(self.paths))
        
        dictionary={'result':{'Value':str(status)}}
        self.signal_update_table.emit(dictionary)
        self.finished.emit()
        
        
def main():
    
    app = QtGui.QApplication(sys.argv)
    ex = MainWindow()
    ex.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()    
