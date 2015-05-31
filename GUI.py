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

import sys,os,time,operator
import numpy as np
from PyQt4 import QtGui, QtCore
from table_widget import TableWidget
from image_widget import ImageWidget
from file_source_widget import FileSourceWidget
from settings_widget import SettingsWidget
from scipy.optimize import leastsq
from sklearn import mixture


import matplotlib
matplotlib.use('QT4Agg')

#### Uncomment these lines if building py2exe binary with window output only
import warnings
warnings.simplefilter('ignore')

from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QTAgg as NavigationToolbar
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.mlab as mlab


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
        highlightColot = str(tabs.palette().color(QtGui.QPalette.HighlightedText).name())
        imagesLayout=QtGui.QVBoxLayout(images)
        tabs.addTab(images,"Simple spFRET")
        
        self.figure = plt.figure(facecolor=highlightColot)
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
        self.figure1 = plt.figure(facecolor=highlightColot)
        self.canvas1 = FigureCanvas(self.figure1)
        self.toolbar1 = NavigationToolbar(self.canvas1, self)
        fastFRETLayout.addWidget(self.canvas1)
        fastFRETLayout.addWidget(self.toolbar1)
        
        results=QtGui.QWidget(self)
        resultsLayout=QtGui.QVBoxLayout(results)
        tabs.addTab(results,"Results")
        self.tableWidget=TableWidget(self)
        resultsLayout.addWidget(self.tableWidget)
        
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
        self.connect(self.fileMenu,QtCore.SIGNAL("runCalculations"),self.run_calculations)
        self.connect(self.settingsWidget,QtCore.SIGNAL("settingsUpdatedSignal"),self.apply_settings)
        
        
    def apply_settings(self,settings):
        self.settings=settings
        self.show_graph(self.data,self.settings,self.name)
    
    def set_data(self,data,name):
        self.data=data
        self.name=name
        self.show_graph(self.data,self.settings,name)
        
    def plot_raw(self,data,settings,showplots=True):
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
        cy3_thld=cy3_guess[1]*settings['TD']
        cy5_thld=cy5_guess[1]*settings['TD']
        #ms, cs , ws = fit_mixture(cy3.reshape(cy3.size,1),1)
        #gaus2=ws[0]*mlab.normpdf(x_axis,ms[0],cs[0])
        
        self.figure1.clf()
        if showplots:
            gs = gridspec.GridSpec(2, 2)
            ax00 = self.figure1.add_subplot(gs[0,0])
            ax00.plot(x_axis, cy3_hist,color='blue', label='Raw')
            #ax00.hist(cy3,np.arange(0,max,1/(timestep*1000)), label='Raw',normed=True)
            ax00.plot(x_axis, cy3_est,color='black', label='Fitted')
            ax00.axvline(cy3_guess[0],color='red', label='Bkgnd',linewidth=3)
            ax00.axvline(cy3_guess[0]+cy3_thld,color='green', label='Thld',linewidth=3)
            #ax00.plot(x_axis,gaus2, linewidth=3)
            ax00.legend()   
            ax00.set_title('Cy3 hist')
            ax00.set_ylabel('Amount')
            ax00.set_xlabel('Count, kHz')
            scale=[cy3_thld+1 if 10*cy3_guess[1]<=cy3_thld else 10*cy3_guess[1]][0]
            ax00.set_xlim(0,np.round(cy3_guess[0]+scale))

            
            ax01 = self.figure1.add_subplot(gs[0,1])
            ax01.plot(x_axis, cy5_hist,color='blue', label='Raw')
            ax01.plot(x_axis, cy5_est,color='black', label='Fitted')
            ax01.axvline(cy5_guess[0],color='red', label='Bkgnd',linewidth=3)
            ax01.axvline(cy5_guess[0]+cy5_thld,color='green', label='Thld',linewidth=3)
            ax01.legend() 
            ax01.set_title('Cy5 hist')
            ax01.set_ylabel('Amount')
            ax01.set_xlabel('Count, kHz')
            scale=[cy5_thld+1 if 10*cy5_guess[1]<=cy5_thld else 10*cy5_guess[1]][0]
            ax01.set_xlim(0,np.round(cy5_guess[0]+scale))
                    
            ax10 = self.figure1.add_subplot(gs[1,0])
            ax10.plot(time[::10],cy3[::10],color='blue',linestyle='None',marker='.',label='Raw')
            ax10.axhline(cy3_guess[0],color='red', label='Bkgnd',linewidth=3)
            ax10.axhline(cy3_guess[0]+cy3_thld,color='green', label='Thld',linewidth=3)
            ax10.legend()   
            ax10.set_title('Cy3 raw data (every 10th)')
            ax10.set_ylabel('Count, kHz')
            ax10.set_xlabel('Time, S')
            
            ax11 = self.figure1.add_subplot(gs[1,1])
            ax11.plot(time[::10],cy5[::10],color='blue',linestyle='None',marker='.',label='Raw')
            ax11.axhline(cy5_guess[0],color='red', label='Bkgnd',linewidth=3)
            ax11.axhline(cy5_guess[0]+cy5_thld,color='green', label='Thld',linewidth=3)
            ax11.legend()     
            ax11.set_title('Cy5 raw data (every 10th)')
            ax11.set_ylabel('Count, kHz')
            ax11.set_xlabel('Time, S')
            self.figure1.tight_layout()
            self.canvas1.draw()
        return cy3_guess[0],cy3_thld,cy5_guess[0],cy5_thld


    
    def show_graph(self,data,settings,name):
        cy3_bgnd,cy3_sigma,cy5_bgnd,cy5_sigma=self.plot_raw(data,settings)
        time=data[:,0]
        cy3=data[:,2]
        cy5=data[:,1]
        FG=cy3 - cy3_bgnd #np.average(cy3) 
        FR=cy5 - cy5_bgnd # np.average(cy5) - settings['DE']
        
        select = (FG > cy3_sigma) | (FR > cy5_sigma)
        #select = (FG > settings['TD']) & (FR > settings['TA'])
        FG=FG[select]
        FR=FR[select]
        donor_cross= settings['aAD']*FG
        acceptor_cross=settings['aDA']*FR
        FG=FG-donor_cross
        FR=FR-acceptor_cross
        gamma=(float(settings['QA'])*settings['gR'])/(float(settings['QD'])*settings['gG'])
        E=FR/(FR+gamma*FG)
        ms, cs , ws = fit_mixture(E.reshape(E.size,1))
        result=np.histogram(E,np.arange(-0.2,1.25,0.025),normed=True)     
        self.figure.clf()
        ax = self.figure.add_subplot(111)
#        result=np.histogram(fret.proximity_ratio(gamma=gamma),np.arange(0,1.05,0.05),normed=True)
        axis=result[1][:-1]+(result[1][1]-result[1][0])/2.0
        ax.plot(axis,result[0],linewidth=3, label='Eff')
        gaus1=ws[0]*mlab.normpdf(axis,ms[0],cs[0])
        gaus2=ws[1]*mlab.normpdf(axis,ms[1],cs[1])
        ax.plot(axis,gaus1, linewidth=2,
            label='Fit 1, Pos '+str(np.round(ms[0],2))+', '+str(np.round(ws[0]*100,2))+'%')
        ax.plot(axis,gaus2, linewidth=2,
            label='Fit 2, Pos '+str(np.round(ms[1],2))+', '+str(np.round(ws[1]*100,2))+'%')
        ax.plot(axis,gaus1+gaus2, linewidth=2,linestyle='--')
        ax.set_title(os.path.basename(name))
        ax.set_ylabel('Amount, %')
        ax.set_xlabel('FRET Eff')
        box = ax.get_position()
        ax.set_position([box.x0, box.y0 + box.height * 0.1,
                 box.width, box.height * 0.9])
        ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.1),ncol=5)
        table=np.vstack((axis,np.round(result[0],4),np.round(gaus1,4),np.round(gaus2,4))).transpose()
        self.tableWidget.buildFromList(np.vstack((['FRET eff.','Amount','Fitted 1', 'Fitted 2'],table)),False)
        
        self.canvas.draw()
        

    
    def run_calculations(self):
        '''
        Running calculation in separate thread
        '''
        total_FG=np.array([])
        total_FR=np.array([])
        for data in self.fileMenu.getSelectedData():
            cy3_bgnd,cy3_sigma,cy5_bgnd,cy5_sigma=self.plot_raw(data,self.settings,showplots=False)
            time=data[:,0]
            cy3=data[:,2]
            cy5=data[:,1]
            FG=cy3 - cy3_bgnd #np.average(cy3) 
            FR=cy5 - cy5_bgnd # np.average(cy5) - settings['DE']
            select = (FG > cy3_sigma) | (FR > cy5_sigma)
            total_FG=np.append(total_FG,FG[select])
            total_FR=np.append(total_FR,FR[select])
        settings=self.settings
        FG=total_FG
        FR=total_FR
        donor_cross= settings['aAD']*FG
        acceptor_cross=settings['aDA']*FR
        FG=FG-donor_cross
        FR=FR-acceptor_cross
        gamma=(float(settings['QA'])*settings['gR'])/(float(settings['QD'])*settings['gG'])
        E=FR/(FR+gamma*FG)
        ms, cs , ws = fit_mixture(E.reshape(E.size,1))
        result=np.histogram(E,np.arange(-0.2,1.25,0.025),normed=True)     
        self.figure.clf()
        ax = self.figure.add_subplot(111)
        axis=result[1][:-1]+(result[1][1]-result[1][0])/2.0
        ax.plot(axis,result[0],linewidth=3, label='Eff')
        gaus1=ws[0]*mlab.normpdf(axis,ms[0],cs[0])
        gaus2=ws[1]*mlab.normpdf(axis,ms[1],cs[1])
        ax.plot(axis,gaus1, linewidth=2,
            label='Fit 1, Pos '+str(np.round(ms[0],2))+', '+str(np.round(ws[0]*100,2))+'%')
        ax.plot(axis,gaus2, linewidth=2,
            label='Fit 2, Pos '+str(np.round(ms[1],2))+', '+str(np.round(ws[1]*100,2))+'%')
        ax.plot(axis,gaus1+gaus2, linewidth=2,linestyle='--')
        ax.set_title('Built from selected')
        ax.set_ylabel('Amount, %')
        ax.set_xlabel('FRET Eff')
        box = ax.get_position()
        ax.set_position([box.x0, box.y0 + box.height * 0.1,
                 box.width, box.height * 0.9])
        ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.1),ncol=5)

        self.canvas.draw()
        
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

def fit_mixture(data, ncomp=2, doplot=False):
    clf = mixture.GMM(n_components=ncomp)#,covariance_type='full')
    clf.fit(data)
    ml = clf.means_    
    cl = clf.covars_
    wl = clf.weights_
    ms = [m[0] for m in ml]
    cs = [np.sqrt(c) for c in cl]
    ws = [w for w in wl]
    #s=sorted(zip(ml,cs,ws))
    #ml=[e[0] for e in s]
    #cs=[e[1] for e in s]
    #ws=[e[2] for e in s]
    return ms, cs, ws

if __name__ == '__main__':
    main()    
