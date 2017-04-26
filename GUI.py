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
#from scipy.signal import find_peaks_cwt
from sklearn import mixture


import matplotlib
matplotlib.use('QT4Agg')

#### Uncomment these lines if building py2exe binary with window output only
import warnings
warnings.simplefilter('ignore')

from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar
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
        
        self.fileMenu=FileSourceWidget(self)

        mainWidget.addWidget(self.fileMenu)
        tabsAndSettingsWidget=QtGui.QWidget(self)
        tabsAndSettingsLayout=QtGui.QHBoxLayout(tabsAndSettingsWidget)
        
        tabs = QtGui.QTabWidget(self)
        
        #### NOT THE BEST WAY TO IMPLEMENT THAT!
        self.lastCalcMultiple=False
        
    
        images=QtGui.QWidget(self)
        highlightColot = str('white')#tabs.palette().color(QtGui.QPalette.HighlightedText).name())
        imagesLayout=QtGui.QVBoxLayout(images)
        tabs.addTab(images,"Simple spFRET")
        
        self.figure = plt.figure(facecolor=highlightColot)
        self.canvas = FigureCanvas(self.figure)
        self.toolbar = NavigationToolbar(self.canvas, self)
        imagesLayout.addWidget(self.canvas)
        imagesLayout.addWidget(self.toolbar)
        
       
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
        
        self.logText = QtGui.QTextEdit()
        self.logText.setMaximumHeight(130)
        self.logText.setReadOnly(True)
        self.logText.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.logText.append("Welcome to Fretty 1.1! ")
        self.logger = Logger(self.logText)
        #self.errors = Logger(self.logText)
        sys.stdout = self.logger        
        
        tabs_and_logger_widget=QtGui.QWidget(self)
        tabs_and_logger_layout=QtGui.QVBoxLayout(tabs_and_logger_widget)
        tabs_and_logger_layout.addWidget(tabs)
        tabs_and_logger_layout.addWidget(self.logText)
        

        
        tabsAndSettingsLayout.addWidget(tabs_and_logger_widget)
        
        
        
        
        
        
        
        
        self.settingsWidget=SettingsWidget(self)
        self.settings=self.settingsWidget.collectSettings()
        
        tabsAndSettingsLayout.addWidget(self.settingsWidget)
        mainWidget.addWidget(tabsAndSettingsWidget)
        self.setCentralWidget(mainWidget)
        self.setWindowTitle('FRETTY')   
        
        
        self.assignConnections()
        
        
    def assignConnections(self):
        '''
        Assigning connections
        '''
        self.connect(self.fileMenu,QtCore.SIGNAL("updateFilePreview"),self.set_data)
        self.connect(self.fileMenu,QtCore.SIGNAL("updateUI"),self.repaint)
        self.connect(self.fileMenu,QtCore.SIGNAL("runCalculations"),self.plot_multiple_files)
        self.connect(self.settingsWidget,QtCore.SIGNAL("settingsUpdatedSignal"),self.apply_settings)
        
        
    def apply_settings(self,settings):
        self.settings=settings
        if self.lastCalcMultiple:
            try:
                self.plot_multiple_files()
            except IndexError:
                print "<font color=#FF0000>No files loaded.</font>"
        else:
            try:
                self.plot_single_file(self.calculate_single_file(self.data,self.settings,self.name))
            except AttributeError:
                try:
                    self.plot_multiple_files()
                except IndexError:
                    print "<font color=#FF0000>No files loaded.</font>"
    
    def set_data(self,data,name):
        self.data=data
        self.name=name
        self.plot_single_file(self.calculate_single_file(self.data,self.settings,self.name))
        self.lastCalcMultiple=False
        

       
    def plot_raw(self,data,settings,showplots=True):
        time=data.time
        cy3=data.donor
        cy5=data.acceptor
        timestep=data.timestep
        
        cy3_int=np.round(timestep*cy3*1000)
        cy5_int=np.round(timestep*cy5*1000)
        max=[cy3_int.max() if cy5_int.max()<=cy3_int.max() else cy5_int.max()][0]
        av_max=[np.average(cy3_int) if np.average(cy5_int)<=np.average(cy3_int) else np.average(cy5_int)][0]
        max=np.round(max/3)
        x=np.arange(0,max,1)
        cy3_hist=np.histogram(cy3_int,x,normed=True)[0]
        cy5_hist=np.histogram(cy5_int,x,normed=True)[0]
        x_axis=x[:-1]
        rawframe=np.vstack((x_axis,cy3_hist,cy5_hist)).T
        np.savetxt('data.txt',rawframe,header="#MHz Cy3 Cy5",fmt='%.3f',)
        m, sd1, = [5, 1]
        p = [m, sd1] # Initial guesses for leastsq
        
        plsq_cy3 = leastsq(res, p, args = (cy3_hist, x_axis))
        plsq_cy5 = leastsq(res, p, args = (cy5_hist, x_axis))

        cy3_est = norm(x_axis, plsq_cy3[0][0], plsq_cy3[0][1])
        cy5_est = norm(x_axis, plsq_cy5[0][0], plsq_cy5[0][1])

        x_axis=x_axis/(timestep*1000)
        cy3_guess=plsq_cy3[0]/(timestep*1000)
        cy5_guess=plsq_cy5[0]/(timestep*1000)
        if settings['backgrMetod']=='Auto (gauss)':
            cy3_bgrnd=cy3_guess[0]
            cy5_bgrnd=cy5_guess[0]
        elif settings['backgrMetod']=='Manual':
            cy3_bgrnd=settings['BD']
            cy5_bgrnd=settings['BA']
            
        if settings['threshMethod']=='Auto (gauss)':
            if settings['threshLogic']=='SUM':
                cy3_thld=(cy3_guess[1]+cy5_guess[1])*settings['CD']
                cy5_thld=(cy3_guess[1]+cy5_guess[1])*settings['CD']
            else:
                cy3_thld=cy3_guess[1]*settings['CD']
                cy5_thld=cy5_guess[1]*settings['CA']
                
        elif settings['threshMethod']=='Manual thresholds':
            cy3_thld=settings['TD']
            cy5_thld=settings['TA']
        elif settings['threshMethod']=='Select top events':
            cy3_thld=cy3[np.argpartition(cy3,-settings['ND'])[-settings['ND']:]].min()-cy3_bgrnd
            cy5_thld=cy5[np.argpartition(cy5,-settings['NA'])[-settings['NA']:]].min()-cy5_bgrnd
        
        #ms, cs , ws = fit_mixture(cy3.reshape(cy3.size,1),1)
        #gaus2=ws[0]*mlab.normpdf(x_axis,ms[0],cs[0])
        
        self.figure1.clf()
        if showplots:
            gs = gridspec.GridSpec(2, 2)
            ax00 = self.figure1.add_subplot(gs[0,0])
            ax00.plot(x_axis, cy3_hist,color='blue', label='Raw')
            #ax00.hist(cy3,np.arange(0,max,1/(timestep*1000)), label='Raw',normed=True)
            ax00.plot(x_axis, cy3_est,color='black', label='Fitted')
            ax00.axvline(cy3_bgrnd,color='red', label='Bkgnd',linewidth=3)
            ax00.axvline(cy3_bgrnd+cy3_thld,color='green', label='Thld',linewidth=3)
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
            ax01.axvline(cy5_bgrnd,color='red', label='Bkgnd',linewidth=3)
            ax01.axvline(cy5_bgrnd+cy5_thld,color='green', label='Thld',linewidth=3)
            ax01.legend() 
            ax01.set_title('Cy5 hist')
            ax01.set_ylabel('Amount')
            ax01.set_xlabel('Count, kHz')
            scale=[cy5_thld+1 if 10*cy5_guess[1]<=cy5_thld else 10*cy5_guess[1]][0]
            ax01.set_xlim(0,np.round(cy5_guess[0]+scale))
                    
            ax10 = self.figure1.add_subplot(gs[1,0])
            ax10.plot(time,cy3,color='blue',linestyle='None',marker=',',label='Raw')
            ax10.axhline(cy3_bgrnd,color='red', label='Bkgnd',linewidth=2)
            ax10.axhline(cy3_bgrnd+cy3_thld,color='green', label='Thld',linewidth=2)
            ax10.axhline(settings['UTD']-cy3_bgrnd,color='black', label='Up Thld',linewidth=2)
            ax10.legend()   
            ax10.set_title('Cy3 raw data')
            ax10.set_ylabel('Count, kHz')
            ax10.set_xlabel('Time, S')
            
            ax11 = self.figure1.add_subplot(gs[1,1])
            ax11.plot(time,cy5,color='blue',linestyle='None',marker=',',label='Raw')
            ax11.axhline(cy5_bgrnd,color='red', label='Bkgnd',linewidth=2)
            ax11.axhline(cy5_bgrnd+cy5_thld,color='green', label='Thld',linewidth=2)
            ax11.axhline(settings['UTA']-cy5_bgrnd,color='black', label='Up Thld',linewidth=2)
            ax11.legend()     
            ax11.set_title('Cy5 raw data')
            ax11.set_ylabel('Count, kHz')
            ax11.set_xlabel('Time, S')
            self.figure1.tight_layout()
            self.canvas1.draw()
        
        return cy3_bgrnd,cy3_thld,cy5_bgrnd,cy5_thld


    def plot_single_file(self,(result,settings,name,E)):
        self.figure.clf()
        ax = self.figure.add_subplot(111)
#        result=np.histogram(fret.proximity_ratio(gamma=gamma),np.arange(0,1.05,0.05),normed=True)
        axis=result[1][:-1]+(result[1][1]-result[1][0])/2.0
        ax.plot(axis,result[0],linewidth=3, label='Eff')

        if (settings['nGausFit']!=0):
            ms, cs , ws = fit_mixture(E.reshape(E.size,1),settings['nGausFit'])
            
            gaus=np.zeros((settings['nGausFit'],axis.size))
            for i in range(settings['nGausFit']):
                gaus[i]=ws[i]*mlab.normpdf(axis,ms[i],cs[i])
                ax.plot(axis,gaus[i], linewidth=2,
                    label='Fit ' + str(i) +', Pos '+str(np.round(ms[i],2))+', '+str(np.round(ws[i]*100,2))+'%')
            ax.plot(axis,gaus.sum(0), linewidth=2,linestyle='--')

        ax.set_title(os.path.basename(name))
        ax.set_ylabel('Amount, %')
        ax.set_xlabel('FRET Eff')
        box = ax.get_position()
        ax.set_position([box.x0, box.y0 + box.height * 0.1,
                 box.width, box.height * 0.9])
        #ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.1),ncol=5)
        if (settings['nGausFit']==0):
            table=np.vstack((axis,np.round(result[0],4))).transpose()
            self.tableWidget.buildFromList(np.vstack((['FRET eff.','Amount'],table)),False)
        else:
            table=np.vstack((axis,np.round(result[0],4),gaus,gaus.sum(0))).transpose()
            header= ['FRET eff.','Amount']
            [header.append('Fitted ' + str(i)) for i in range(1,settings['nGausFit']+1)]
            header.append('Fitted Sum')
            self.tableWidget.buildFromList(np.vstack((header,table)),False)
            self.tableWidget.addFromList(np.array([[' ']]))
            gausses= np.array([np.array(ms),np.array(cs).flatten(),np.array(ws)]).T
            gausses[:,2]*=100
            gausses=np.hstack(( np.transpose([np.arange(1,gausses.shape[0]+1)]),gausses ))

            self.tableWidget.addFromList(np.vstack( ([['#','Position','Sigma','Area, %']],gausses) ).T)
            

        self.tableWidget.addFromList(np.array([[' ']]))   
        self.tableWidget.addFromList(np.hstack(([['Settings'],['']],np.array([settings.keys(),[str(qstring) for qstring in settings.values()]]))))
        #print np.array([settings.keys(),[str(qstring) for qstring in settings.values()]])
        self.canvas.draw()

    def plot_multiple_files(self):
        if len(self.fileMenu.getSelectedPaths()) != 0:
            if len(self.fileMenu.getSelectedPaths()) == 1:
                self.lastCalcMultiple=False
                self.data=self.fileMenu.getSelectedData()[0]
                self.name=self.fileMenu.getSelectedPaths()[0]
                self.plot_single_file(self.calculate_single_file(self.data,self.settings,self.name))
            else:
                self.lastCalcMultiple=True
                self.figure.clf()
                ax = self.figure.add_subplot(111)
        #        result=np.histogram(fret.proximity_ratio(gamma=gamma),np.arange(0,1.05,0.05),normed=True)

                paths=self.fileMenu.getSelectedPaths()
                datas=self.fileMenu.getSelectedData()
                names=[os.path.basename(name) for name in paths]
                result,settings,name,E=self.calculate_single_file(datas[0],self.settings,paths[0],plotRaw=False)
                axis=result[1][:-1]+(result[1][1]-result[1][0])/2.0
                ax.plot(axis,result[0],linewidth=3, label=names[0])
                table=np.vstack((axis,np.round(result[0],4)))
                for i in xrange(1,len(paths)):
                    result,settings,name,E=self.calculate_single_file(datas[i],self.settings,paths[i],plotRaw=False)
                    axis=result[1][:-1]+(result[1][1]-result[1][0])/2.0
                    ax.plot(axis,result[0],linewidth=3, label=names[i])
                    table=np.vstack((table,np.round(result[0],4)))


                ax.set_title('Superimposer plots')
                ax.set_ylabel('Amount, %')
                ax.set_xlabel('FRET Eff')
                box = ax.get_position()
                ax.set_position([box.x0, box.y0 + box.height * 0.1,
                         box.width, box.height * 0.9])
                ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.1),ncol=3)
                self.tableWidget.buildFromList(np.vstack((np.hstack((['FRET eff.'],names)),table.transpose())),False)
                self.tableWidget.addFromList(np.array([[' ']]))   
                self.tableWidget.addFromList(np.hstack(([['Settings'],['']],np.array([settings.keys(),[str(qstring) for qstring in settings.values()]]))))
                #print np.array([settings.keys(),[str(qstring) for qstring in settings.values()]])
                self.canvas.draw()
                self.canvas.draw()
        else:
            print "<font color=#FF0000>No files loaded.</font>"

    def calculate_single_file(self,data,settings,name,plotRaw=True):
        
        donor_bgnd,donor_thld,acceptor_bgnd,acceptor_thld=self.plot_raw(data,settings,showplots=plotRaw)
        time=data.time
        DonorFlux=data.donor #np.average(cy3)
        AcceptorFlux=data.acceptor # np.average(cy5) - settings['DE']



        if settings['threshLogic']=='AND':
            select = (DonorFlux >= donor_thld) & (AcceptorFlux >= acceptor_thld)
        elif settings['threshLogic']=='OR':
            select = (DonorFlux >= donor_thld) | (AcceptorFlux >= acceptor_thld)
        elif settings['threshLogic']=='SUM':
            select = ((DonorFlux + AcceptorFlux) > donor_thld)
            
        
        
        mask = (DonorFlux < settings['UTD']) & (AcceptorFlux < settings['UTA']) & select
        #select = find_peaks_cwt(DonorFlux,np.arange(1,4)) and find_peaks_cwt(AcceptorFlux,np.arange(1,4))
        
       
        #filterring complexes
        complex_filter=mask
        pos,length=count_adjacent_true(complex_filter>0)
        ident=(40-len(os.path.basename(name)))/2
        print "<pre>%s %s %s</pre>" %("-"*ident, os.path.basename(name),"-"*ident)
        print "Amount of events before filtering is %d"%pos.size
        
        stops=pos+length
        pauses=pos[1:]-stops[:-1]
        
        agg_search_max_length=settings['AggSearchMaxLength']
        print "Amount of aggregates is %d"%(length > agg_search_max_length).sum()
        
        lengthsmMask=length > agg_search_max_length
        pos=pos[lengthsmMask]
        length=length[lengthsmMask]
        for burstpos,purstlength in zip(pos,length):
            complex_filter[burstpos:burstpos+purstlength]=0
        
        mask=complex_filter.astype(bool)
        print "Amount of events after filtering is %d"%count_adjacent_true(mask)[0].size
                
        #select = (DonorFlux > settings['TD']) & (AcceptorFlux > settings['TA'])
        DonorFlux=DonorFlux[mask] - donor_bgnd
        AcceptorFlux=AcceptorFlux[mask] - acceptor_bgnd
        
        
        print "Amount of bins after filtering is %d"%AcceptorFlux.size
        
        donor_cross= settings['aDA']*DonorFlux
        acceptor_cross=settings['aAD']*AcceptorFlux
        DonorFlux=DonorFlux-acceptor_cross
        AcceptorFlux=AcceptorFlux-donor_cross
        gamma=(float(settings['QA'])*settings['kA'])/(float(settings['QD'])*settings['kD'])
        E=AcceptorFlux/(AcceptorFlux+gamma*DonorFlux)
        #print 'saving '+  name[:-4]+'_Eff.txt'
        #np.savetxt(name[:-4]+'_Eff.txt',E,fmt='%.6f')
        
        
        result=np.histogram(E,np.linspace(-0.2, 1.2, num=settings['histBins']),normed=True)
        return result,settings,name,E


        
    def update_table(self,dictionary):
        self.tableWidget.buildFromDict(dictionary)
        
    def updateProgressBar(self,value):
        self.pbar.setValue(value)

class Logger(object):
    def __init__(self, output):
        self.output = output

    def write(self, string):
        if not (string == "\n" ):
            trstring = QtGui.QApplication.translate("MainWindow", string.rstrip(), None, QtGui.QApplication.UnicodeUTF8)
            self.output.append(trstring)
        
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

def count_adjacent_true(arr):
    assert len(arr.shape) == 1
    assert arr.dtype == np.bool
    if arr.size == 0:
        return np.empty(0, dtype=int), np.empty(0, dtype=int)
    sw = np.insert(arr[1:] ^ arr[:-1], [0, arr.shape[0]-1], values=True)
    swi = np.arange(sw.shape[0])[sw]
    offset = 0 if arr[0] else 1
    lengths = swi[offset+1::2] - swi[offset:-1:2]
    return swi[offset:-1:2], lengths

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
    clf = mixture.GMM(n_components=ncomp,thresh=0.001)#,covariance_type='full')
    clf.fit(data)
    ml = clf.means_    
    cl = clf.covars_
    wl = clf.weights_
    ms = [m[0] for m in ml]
    cs = [np.sqrt(c) for c in cl]
    ws = [w for w in wl]
    
    gausses= np.array([np.array(ms),np.array(cs).flatten(),np.array(ws)]).T
    gausses.sort(axis=0)
    return gausses.T[0], gausses.T[1], gausses.T[2]

if __name__ == '__main__':
    main()    
