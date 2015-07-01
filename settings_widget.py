#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) Grigoriy A. Armeev, 2014
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as·
# published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License v2 for more details.
import sys, os
from PyQt4 import QtGui,QtCore
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
class SettingsWidget(QtGui.QWidget):
    def __init__(self,workdir,parent=None):
        super(SettingsWidget, self).__init__(parent)
        self.parent=parent
        mainLayout = QtGui.QGridLayout(self)
        
       
        text=QtGui.QLabel(u'Φ<i>d</i>')
        tooltip=u'Quantum yield of donor, varies from 0 to 1 '
        text.setToolTip(tooltip)
        mainLayout.addWidget(text,0,0)
        self.QD=QtGui.QDoubleSpinBox(self)
        self.QD.setRange(0,1)
        self.QD.setSingleStep(0.01)
        self.QD.setValue(1)
        self.QD.valueChanged.connect(self.collectSettings)
        self.QD.setToolTip(tooltip)
        mainLayout.addWidget(self.QD,0,1)
        
        text=QtGui.QLabel(u'Φ<i>a</i>')
        tooltip=u'Quantum yield of acceptor, varies from 0 to 1 '
        text.setToolTip(tooltip)
        mainLayout.addWidget(text,0,2)
        self.QA=QtGui.QDoubleSpinBox(self)
        self.QA.setRange(0,1)
        self.QA.setSingleStep(0.01)
        self.QA.setValue(1)
        self.QA.valueChanged.connect(self.collectSettings)
        self.QA.setToolTip(tooltip)
        mainLayout.addWidget(self.QA,0,3)
        
        text=QtGui.QLabel('<i>kd</i>')
        tooltip=u'Detector efficiency at donor emission wavelength,\n varies from 0 to 1 '
        text.setToolTip(tooltip)
        mainLayout.addWidget(text)
        self.kD=QtGui.QDoubleSpinBox(self)
        self.kD.setRange(0,1)
        self.kD.setSingleStep(0.01)
        self.kD.setValue(1.00)
        self.kD.valueChanged.connect(self.collectSettings)
        self.kD.setToolTip(tooltip)
        mainLayout.addWidget(self.kD)

        text=QtGui.QLabel('<i>ka</i>')
        tooltip=u'Detector efficiency at acceptor emission wavelength,\n varies from 0 to 1 '
        text.setToolTip(tooltip)
        mainLayout.addWidget(text)
        self.kA=QtGui.QDoubleSpinBox(self)
        self.kA.setRange(0,1)
        self.kA.setSingleStep(0.01)
        self.kA.setValue(1)
        self.kA.valueChanged.connect(self.collectSettings)
        self.kA.setToolTip(tooltip)
        mainLayout.addWidget(self.kA)
        
        text=QtGui.QLabel(u'α <i>ad</i>')
        tooltip=u'Donor crosstalk coefficient (A to D), \n varies from 0 to 1'
        text.setToolTip(tooltip)        
        mainLayout.addWidget(text)
        self.aAD=QtGui.QDoubleSpinBox(self)
        self.aAD.setRange(0,1)
        self.aAD.setSingleStep(0.01)
        self.aAD.setValue(0.00)
        self.aAD.valueChanged.connect(self.collectSettings)
        self.aAD.setToolTip(tooltip)
        mainLayout.addWidget(self.aAD)
        
        text=QtGui.QLabel(u'α <i>da</i>:')
        tooltip=u'Acceptor crosstalk coefficient (D to A), \n varies from 0 to 1'
        text.setToolTip(tooltip)
        mainLayout.addWidget(text)
        self.aDA=QtGui.QDoubleSpinBox(self)
        self.aDA.setRange(0,1)
        self.aDA.setSingleStep(0.01)
        self.aDA.setValue(0.19)
        self.aDA.valueChanged.connect(self.collectSettings)
        self.aDA.setToolTip(tooltip)
        mainLayout.addWidget(self.aDA)        
                       
        
        text=QtGui.QLabel('<i>DE</i>')
        tooltip=u'Direct excitation of acceptor \n(in signal units, e.g. kHz or counts)'
        text.setToolTip(tooltip)        
        mainLayout.addWidget(text)
        self.DE=QtGui.QDoubleSpinBox(self)
        self.DE.setRange(0,1000)
        self.DE.setSingleStep(0.01)
        self.DE.setValue(0)
        self.DE.valueChanged.connect(self.collectSettings)
        self.DE.setToolTip(tooltip)        
        mainLayout.addWidget(self.DE)
        
        text=QtGui.QLabel('N bins')
        tooltip=u'Amount od bins for FRET E histogram'
        text.setToolTip(tooltip)        
        mainLayout.addWidget(text)
        self.histBins=QtGui.QDoubleSpinBox(self)
        self.histBins.setRange(0,1000)
        self.histBins.setSingleStep(1)
        self.histBins.setValue(100)
        self.histBins.valueChanged.connect(self.collectSettings)
        self.histBins.setToolTip(tooltip)        
        mainLayout.addWidget(self.histBins)
        
        
###################### BACKGROUND METHODS ############################   
        
        text=QtGui.QLabel('Background substraction:')
        mainLayout.addWidget(text,6,0,1,2)
        self.BackGrSubMethod=QtGui.QComboBox(self)
        self.BackGrSubMethod.addItem('Auto (gauss)')
        self.BackGrSubMethod.addItem('Manual')
        self.BackGrSubMethod.setCurrentIndex(0)        
        self.BackGrSubMethod.currentIndexChanged.connect(self.collectSettings)
        mainLayout.addWidget(self.BackGrSubMethod,6,2,1,2)
        
        self.BDtext=QtGui.QLabel('Bd:')
        mainLayout.addWidget(self.BDtext,7,0,1,1)
        self.BD=QtGui.QDoubleSpinBox(self)
        self.BD.setRange(0,1000)
        self.BD.setSingleStep(0.1)
        self.BD.setValue(9)
        self.BD.valueChanged.connect(self.collectSettings)
        mainLayout.addWidget(self.BD,7,1,1,1)
        
        self.BAtext=QtGui.QLabel('Ba:')
        mainLayout.addWidget(self.BAtext,7,2,1,1)
        self.BA=QtGui.QDoubleSpinBox(self)
        self.BA.setRange(0,1000)
        self.BA.setSingleStep(0.1)
        self.BA.setValue(9)
        self.BA.valueChanged.connect(self.collectSettings)
        mainLayout.addWidget(self.BA,7,3,1,1)     
        
###################### THRESHOLD METHODS ############################   
        
        text=QtGui.QLabel('Thresholding method:')
        mainLayout.addWidget(text,8,0,1,2)
        self.ThresholdMethod=QtGui.QComboBox(self)
        self.ThresholdMethod.addItem('Auto (gauss)')
        self.ThresholdMethod.addItem('Manual thresholds')
        self.ThresholdMethod.addItem('Select top events')
        #self.ThresholdMethod.model().item(2).setEnabled(False)
        self.ThresholdMethod.setCurrentIndex(0)        
        self.ThresholdMethod.currentIndexChanged.connect(self.collectSettings)
        mainLayout.addWidget(self.ThresholdMethod,8,2,1,2)

        text=QtGui.QLabel('Thresholding logic:')
        mainLayout.addWidget(text,9,0,1,2)
        self.ThresholdLogic=QtGui.QComboBox(self)
        self.ThresholdLogic.addItem('OR')
        self.ThresholdLogic.addItem('AND')
        self.ThresholdLogic.addItem('SUM')
        self.ThresholdLogic.setCurrentIndex(0)        
        self.ThresholdLogic.currentIndexChanged.connect(self.collectSettings)
        mainLayout.addWidget(self.ThresholdLogic,9,2,1,2)               


        self.CDtext=QtGui.QLabel('Coef. D:')
        mainLayout.addWidget(self.CDtext,10,0,1,1)
        self.CD=QtGui.QDoubleSpinBox(self)
        self.CD.setRange(0,1000)
        self.CD.setSingleStep(0.1)
        self.CD.setValue(9)
        self.CD.valueChanged.connect(self.collectSettings)
        mainLayout.addWidget(self.CD,10,1,1,1)
        
        self.CAtext=QtGui.QLabel('Coef. A:')
        mainLayout.addWidget(self.CAtext,10,2,1,1)
        self.CA=QtGui.QDoubleSpinBox(self)
        self.CA.setRange(0,1000)
        self.CA.setSingleStep(0.1)
        self.CA.setValue(9)
        self.CA.valueChanged.connect(self.collectSettings)
        mainLayout.addWidget(self.CA,10,3,1,1)
        
        self.TDtext=QtGui.QLabel('Thresh. D:')
        mainLayout.addWidget(self.TDtext,11,0,1,1)
        self.TD=QtGui.QDoubleSpinBox(self)
        self.TD.setRange(0,1000)
        self.TD.setSingleStep(0.1)
        self.TD.setValue(9)
        self.TD.valueChanged.connect(self.collectSettings)
        mainLayout.addWidget(self.TD,11,1,1,1)
        
        self.TAtext=QtGui.QLabel('Thresh. A:')
        mainLayout.addWidget(self.TAtext,11,2,1,1)
        self.TA=QtGui.QDoubleSpinBox(self)
        self.TA.setRange(0,1000)
        self.TA.setSingleStep(0.1)
        self.TA.setValue(9)
        self.TA.valueChanged.connect(self.collectSettings)
        mainLayout.addWidget(self.TA,11,3,1,1)       
        
        
        self.NDtext=QtGui.QLabel('Nd:')
        mainLayout.addWidget(self.NDtext,12,0,1,1)
        self.ND=QtGui.QDoubleSpinBox(self)
        self.ND.setRange(0,100000)
        self.ND.setSingleStep(0.1)
        self.ND.setValue(5000)
        self.ND.valueChanged.connect(self.collectSettings)
        mainLayout.addWidget(self.ND,12,1,1,1)
        
        self.NAtext=QtGui.QLabel('Na:')
        mainLayout.addWidget(self.NAtext,12,2,1,1)
        self.NA=QtGui.QDoubleSpinBox(self)
        self.NA.setRange(0,100000)
        self.NA.setSingleStep(0.1)
        self.NA.setValue(5000)
        self.NA.valueChanged.connect(self.collectSettings)
        mainLayout.addWidget(self.NA,12,3,1,1)        

###################### FITTING METHODS ############################   

        text=QtGui.QLabel('Gauss fitting:')
        mainLayout.addWidget(text,13,0,1,2)
        self.gausFitting=QtGui.QComboBox(self)
        self.gausFitting.addItem('None')
        self.gausFitting.addItem('1')
        self.gausFitting.addItem('2')
        self.gausFitting.addItem('3')
        self.gausFitting.addItem('4')
        self.gausFitting.addItem('5')
        self.gausFitting.setCurrentIndex(0)        
        self.gausFitting.currentIndexChanged.connect(self.collectSettings)
        mainLayout.addWidget(self.gausFitting,13,2,1,2) 
        
###################### FORMULAS ############################  

        windowColor = str(self.palette().color(QtGui.QPalette.Window).name())    
        self.figure = plt.figure(facecolor=windowColor)
        self.canvas = FigureCanvas(self.figure)
        mainLayout.addWidget(self.canvas,14,0,1,4)
        mainLayout.setAlignment(QtCore.Qt.AlignTop)
        self.drawFormulas()
        
    def drawFormulas(self):
        self.figure.clf()
        self.figure.suptitle(r"$E=\frac{F_a}{F_a+\gamma_d F_d}$" "\n"
                            r"$F_d=I_d - B_d -\alpha_{ad}(I_a-B_a)$" "\n"
                            r"$F_a=I_a - B_a -\alpha_{da}(I_d-B_d)-DE_a$" "\n" 
                            r"$\gamma_d=\frac{\Phi_a k_d}{\Phi_d k_a}= " + 
                            str(round((self.QA.value()*self.kD.value())/(self.QD.value()*self.kA.value()),4))+ "$\n"
                            r"$I - intensity, B - background$" "\n"
                            r"$\alpha - crosstalk, \gamma - instr.coef.$" ,
                      x=0.0, y=0.5, 
                      fontsize=18,
                      horizontalalignment='left',
                      verticalalignment='center')
        self.canvas.setMaximumWidth(278)
        self.canvas.setMaximumHeight(190)
        self.canvas.setSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Minimum)        
        self.canvas.draw()

    def changeHideStatus(self):
        self.hideAll()
        if self.BackGrSubMethod.currentText()=='Manual':
            self.BAtext.show()
            self.BA.show()
            self.BDtext.show()        
            self.BD.show()
            
        if (self.ThresholdLogic.currentText()=='OR') | (self.ThresholdLogic.currentText()=='AND'):
            self.ThresholdMethod.model().item(2).setEnabled(True)
            self.ThresholdLogic.model().item(2).setEnabled(True)
            if self.ThresholdMethod.currentText()=='Auto (gauss)':
                self.CD.show()
                self.CDtext.show()       
                self.CA.show()
                self.CAtext.show()       
            elif self.ThresholdMethod.currentText()=='Manual thresholds':
                self.TD.show()
                self.TDtext.show()
                self.TA.show()
                self.TAtext.show()  
            elif self.ThresholdMethod.currentText()=='Select top events':
                self.ThresholdLogic.model().item(2).setEnabled(False)
                self.ND.show()
                self.NDtext.show()
                self.NA.show()
                self.NAtext.show()   
        else:            
            self.ThresholdMethod.model().item(2).setEnabled(False)
            if self.ThresholdMethod.currentText()=='Select top events':
                self.ThresholdMethod.setCurrentIndex(0)
            elif self.ThresholdMethod.currentText()=='Auto (gauss)':
                self.CD.show()
                self.CDtext.show()       
            elif self.ThresholdMethod.currentText()=='Manual thresholds':
                self.TD.show()
                self.TDtext.show()
            
    def hideAll(self):
        self.BAtext.hide()
        self.BA.hide()
        self.BDtext.hide()        
        self.BD.hide()
        self.CD.hide()
        self.CDtext.hide()       
        self.CA.hide()
        self.CAtext.hide()      
        self.TD.hide()
        self.TDtext.hide()        
        self.TA.hide()
        self.TAtext.hide()        
        self.ND.hide()
        self.NDtext.hide()        
        self.NA.hide()
        self.NAtext.hide()
        
    def collectSettings(self):
        self.changeHideStatus()
        self.drawFormulas()
        settings={'QD':self.QD.value(),
        'QA':self.QA.value(),
        'kD':self.kD.value(),
        'kA':self.kA.value(),
        'BD':self.BD.value(),
        'BA':self.BA.value(),
        'CD':self.CD.value(),
        'CA':self.CA.value(),
        'TD':self.TD.value(),
        'TA':self.TA.value(),
        'ND':self.ND.value(),
        'NA':self.NA.value(),
        'DE':self.DE.value(),
        'aAD':self.aAD.value(),
        'aDA':self.aDA.value(),
        'histBins':self.histBins.value(),
        'threshMethod':self.ThresholdMethod.currentText(),
        'threshLogic':self.ThresholdLogic.currentText(),
        'backgrMetod':self.BackGrSubMethod.currentText(),
        'nGausFit':self.gausFitting.currentIndex()}
        self.emit(QtCore.SIGNAL("settingsUpdatedSignal"),settings)
        return settings

def main():    
    app = QtGui.QApplication(sys.argv)
    workDir=unicode(QtCore.QDir.currentPath())
    ex = SettingsWidget(workDir)
    ex.show()
    sys.exit(app.exec_())
    
if __name__ == '__main__':
    main()    
