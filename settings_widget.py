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
class SettingsWidget(QtGui.QWidget):
    def __init__(self,workdir,parent=None):
        super(SettingsWidget, self).__init__(parent)
        self.parent=parent
        mainLayout = QtGui.QVBoxLayout(self)
        
        text=QtGui.QLabel('Q Yield A:')
        mainLayout.addWidget(text)
        self.QA=QtGui.QDoubleSpinBox(self)
        self.QA.setRange(0,1)
        self.QA.setSingleStep(0.01)
        self.QA.setValue(1)
        self.QA.valueChanged.connect(self.collectSettings)
        mainLayout.addWidget(self.QA)
        
        text=QtGui.QLabel('Q Yield D:')
        mainLayout.addWidget(text)
        self.QD=QtGui.QDoubleSpinBox(self)
        self.QD.setRange(0,1)
        self.QD.setSingleStep(0.01)
        self.QD.setValue(1)
        self.QD.valueChanged.connect(self.collectSettings)
        mainLayout.addWidget(self.QD)
        
        text=QtGui.QLabel('Sensit. A:')
        mainLayout.addWidget(text)
        self.gR=QtGui.QDoubleSpinBox(self)
        self.gR.setRange(0,1)
        self.gR.setSingleStep(0.01)
        self.gR.setValue(1)
        self.gR.valueChanged.connect(self.collectSettings)
        mainLayout.addWidget(self.gR)
        
        text=QtGui.QLabel('Sensit. A:')
        mainLayout.addWidget(text)
        self.gG=QtGui.QDoubleSpinBox(self)
        self.gG.setRange(0,1)
        self.gG.setSingleStep(0.01)
        self.gG.setValue(0.65)
        self.gG.valueChanged.connect(self.collectSettings)
        mainLayout.addWidget(self.gG)
        
        text=QtGui.QLabel('Thresh Multiply:')
        mainLayout.addWidget(text)
        self.TD=QtGui.QDoubleSpinBox(self)
        self.TD.setRange(0,1000)
        self.TD.setSingleStep(0.1)
        self.TD.setValue(9)
        self.TD.valueChanged.connect(self.collectSettings)
        mainLayout.addWidget(self.TD)
        
        
        text=QtGui.QLabel('Direct excit.:')
        mainLayout.addWidget(text)
        self.DE=QtGui.QDoubleSpinBox(self)
        self.DE.setRange(0,1)
        self.DE.setSingleStep(0.01)
        self.DE.setValue(0)
        self.DE.valueChanged.connect(self.collectSettings)
        mainLayout.addWidget(self.DE)
        
        text=QtGui.QLabel('Cross AD:')
        mainLayout.addWidget(text)
        self.aAD=QtGui.QDoubleSpinBox(self)
        self.aAD.setRange(0,1)
        self.aAD.setSingleStep(0.01)
        self.aAD.setValue(0.1)
        self.aAD.valueChanged.connect(self.collectSettings)
        mainLayout.addWidget(self.aAD)
        
        text=QtGui.QLabel('Cross DA:')
        mainLayout.addWidget(text)
        self.aDA=QtGui.QDoubleSpinBox(self)
        self.aDA.setRange(0,1)
        self.aDA.setSingleStep(0.01)
        self.aDA.setValue(0.19)
        self.aDA.valueChanged.connect(self.collectSettings)
        mainLayout.addWidget(self.aDA)

        
    def collectSettings(self):
        settings={'QA':self.QA.value(),
        'QD':self.QD.value(),
        'gR':self.gR.value(),
        'gG':self.gG.value(),
        'TD':self.TD.value(),
        'DE':self.DE.value(),
        'aAD':self.aAD.value(),
        'aDA':self.aDA.value()}
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
