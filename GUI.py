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
from scipy.optimize import leastsq

from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QTAgg as NavigationToolbar
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec


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
        tabs.addTab(fastFRET,"Raw data")
        self.figure1 = plt.figure()
        self.canvas1 = FigureCanvas(self.figure1)
        self.toolbar1 = NavigationToolbar(self.canvas1, self)
        fastFRETLayout.addWidget(self.canvas1)
        fastFRETLayout.addWidget(self.toolbar1)
        
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
        
    def plot_raw(self,data,settings):
        time=data[:,0]
        cy3=data[:,2]
        cy5=data[:,1]
        timestep=np.average(time[1:]-time[:-1])
        cy3_int=np.round(timestep*cy3*1000)
        cy5_int=np.round(timestep*cy5*1000)
        max=[cy3_int.max() if cy5_int.max()<=cy3_int.max() else cy5_int.max()][0]
        av_max=[np.average(cy3_int) if np.average(cy5_int)<=np.average(cy3_int) else np.average(cy5_int)][0]
        max=np.round(max/3)
        x=np.arange(0,max,1)
        cy3_hist=np.histogram(cy3_int,x,normed=True)[0]
        cy5_hist=np.histogram(cy5_int,x,normed=True)[0]
        x_axis=x[:-1]
        m, sd1, = [5, 1]
        p = [m, sd1] # Initial guesses for leastsq
        plsq_cy3 = leastsq(res, p, args = (cy3_hist, x_axis))
        plsq_cy5 = leastsq(res, p, args = (cy5_hist, x_axis))

        cy3_est = norm(x_axis, plsq_cy3[0][0], plsq_cy3[0][1])
        cy5_est = norm(x_axis, plsq_cy5[0][0], plsq_cy5[0][1])

        x_axis=x_axis/(timestep*1000)
        cy3_guess=plsq_cy3[0]/(timestep*1000)
        cy5_guess=plsq_cy5[0]/(timestep*1000)
        
        self.figure1.clf()
        gs = gridspec.GridSpec(2, 2)
        ax00 = self.figure1.add_subplot(gs[0,0])
        ax00.plot(x_axis, cy3_hist,color='blue', label='Raw')
        ax00.plot(x_axis, cy3_est,color='black', label='Fitted')
        ax00.axvline(cy3_guess[0],color='red', label='Bkgnd')
        ax00.axvline(cy3_guess[0]+3*cy3_guess[1],color='green', label='Thld')
        ax00.legend()   
        ax00.set_title('Cy3 hist')
        ax00.set_ylabel('Amount')
        ax00.set_xlabel('Count, kHz')
        ax00.set_xlim(0,np.round(cy3_guess[0]+10*cy3_guess[1]))

        
        ax01 = self.figure1.add_subplot(gs[0,1])
        ax01.plot(x_axis, cy5_hist,color='blue', label='Raw')
        ax01.plot(x_axis, cy5_est,color='black', label='Fitted')
        ax01.axvline(cy5_guess[0],color='red', label='Bkgnd')
        ax01.axvline(cy5_guess[0]+3*cy3_guess[1],color='green', label='Thld')
        ax01.legend() 
        ax01.set_title('Cy5 hist')
        ax01.set_ylabel('Amount')
        ax01.set_xlabel('Count, kHz')
        ax01.set_xlim(0,np.round(cy5_guess[0]+10*cy5_guess[1]))
                
        ax10 = self.figure1.add_subplot(gs[1,0])
        ax10.plot(time[::10],cy3[::10],color='blue',linestyle='None',marker='.',label='Raw')
        ax10.axhline(cy3_guess[0],color='red', label='Bkgnd')
        ax10.axhline(cy3_guess[0]+3*cy3_guess[1],color='green', label='Thld')
        ax10.legend()   
        ax10.set_title('Cy3 raw data (every 10th)')
        ax10.set_ylabel('Count, kHz')
        ax10.set_xlabel('Time, S')
        
        ax11 = self.figure1.add_subplot(gs[1,1])
        ax11.plot(time[::10],cy5[::10],color='blue',linestyle='None',marker='.',label='Raw')
        ax11.axhline(cy5_guess[0],color='red', label='Bkgnd')
        ax11.axhline(cy5_guess[0]+3*cy5_guess[1],color='green', label='Thld')
        ax11.legend()     
        ax11.set_title('Cy5 raw data (every 10th)')
        ax11.set_ylabel('Count, kHz')
        ax11.set_xlabel('Time, S')
        self.figure1.tight_layout()
        self.canvas1.draw()
        return cy3_guess[0],cy3_guess[1],cy5_guess[0],cy5_guess[1]


    
    def show_graph(self,data,settings):
        cy3_bgnd,cy3_sigma,cy5_bgnd,cy5_sigma=self.plot_raw(data,settings)
        time=data[:,0]
        cy3=data[:,2]
        cy5=data[:,1]
        FG=cy3 - cy3_bgnd #np.average(cy3) 
        FR=cy5 - cy5_bgnd # np.average(cy5) - settings['DE']
        select = (FG > settings['TD']*cy3_sigma) | (FR > settings['TD']*cy5_sigma)
        #select = (FG > settings['TD']) & (FR > settings['TA'])
        FG=FG[select]
        FR=FR[select]
        donor_cross= settings['aAD']*FG
        acceptor_cross=settings['aDA']*FR
        FG=FG-donor_cross
        FR=FR-acceptor_cross
        gamma=(float(settings['QA'])*settings['gR'])/(float(settings['QD'])*settings['gG'])
        E=FR/(FR+gamma*FG)
        result=np.histogram(E,np.arange(-0.2,1.25,0.05),normed=False)
        
       
        
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

def norm(x, mean, sd):
  norm = []
  for i in range(x.size):
    norm += [1.0/(sd*np.sqrt(2*np.pi))*np.exp(-(x[i] - mean)**2/(2*sd**2))]
  return np.array(norm)

def res(p, y, x):
  m,  sd1  = p
  m1 = m
  
  y_fit = norm(x, m1, sd1)
  err = y - y_fit
  return err      
        
def main():
    
    app = QtGui.QApplication(sys.argv)
    ex = MainWindow()
    ex.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()    
