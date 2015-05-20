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
from PyQt4 import QtGui, QtCore
from table_widget import TableWidget
from image_widget import ImageWidget
from file_source_widget import FileSourceWidget
from settings_widget import SettingsWidget

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
        
        self.settingsWidget=SettingsWidget(self)
        controlLayout.addWidget(self.settingsWidget)     
        self.settings=self.settingsWidget.collectSettings()

        #self.pbar = QtGui.QProgressBar(self) 
        #controlLayout.addWidget(self.pbar)    
        
        mainWidget.addWidget(controlWidget)
        self.setCentralWidget(mainWidget)
        self.setWindowTitle('FRETTY')   
        
        self.assignConnections()
        
        
    def assignConnections(self):
        '''
        Assigning connections
        '''
        self.connect(self.fileMenu,QtCore.SIGNAL("updateFilePreview"),self.set_data)
        self.connect(self.settingsWidget,QtCore.SIGNAL("settingsUpdatedSignal"),self.apply_settings)
        
    def apply_settings(self,settings):
        self.settings=settings
        self.show_graph(self.data,self.settings)
    
    def set_data(self,data):
        self.data=data
        self.show_graph(self.data,self.settings)
        
    
    def show_graph(self,data,settings):
        time=data[:,0]
        cy3=data[:,2]
        cy5=data[:,1]        
        cy5_norm=np.round(np.average(time[1:]-time[:-1])*cy5*1000)
        np.histogram(cy5_norm,np.arange(0,40,1),normed=True)[0]
        FG=cy3 - np.average(cy3) 
        FR=cy5 - np.average(cy5) - settings['DE']
        select = (FG > settings['TD']*np.std(cy3)) | (FR > settings['TD']*np.std(cy5))
        #select = (FG > settings['TD']) & (FR > settings['TA'])
        FG=FG[select]
        FR=FR[select]
        donor_cross= settings['aAD']*FG
        acceptor_cross=settings['aDA']*FR
        FG=FG-donor_cross
        FR=FR-acceptor_cross
        gamma=(float(settings['QA'])*settings['gR'])/(float(settings['QD'])*settings['gG'])
        E=FR/(FR+gamma*FG)
        result=np.histogram(E,np.arange(-0.2,1.25,0.05),normed=True)
        
#        fret = pft.FRET_data(data[:,2],data[:,1])
#        
#        threshold_donor = 7 # donor threshold
#        threshold_acceptor = 5 # acceptor threshold
#        
#        cross_DtoA = 0.20 # fractional crosstalk from donor to acceptor
#        cross_AtoD = 0.01 # fractional crosstalk from acceptor to donor
#        
#        fret.threshold_SUM(threshold_donor)
#        fret.subtract_bckd(settings['BG'],settings['BR'])
#        fret.subtract_crosstalk(settings['aDA'], settings['aAD'])
#        
        
        ax = self.figure.add_subplot(111)
        ax.hold(False)
#        result=np.histogram(fret.proximity_ratio(gamma=gamma),np.arange(0,1.05,0.05),normed=True)
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
