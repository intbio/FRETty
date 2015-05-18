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
import sys, os
from PyQt4 import QtGui,QtCore
import numpy as np

class FileSourceWidget(QtGui.QWidget):
    '''
    Provides Widget for opening multiple files
    '''
    def __init__(self,workdir,parent=None):
        super(FileSourceWidget, self).__init__(parent)
        self.parent=parent
        self.filters="Image Files (*.txt)"
        self.fileList=QtCore.QStringList()
        self.fileWidgetList=[]

        self.foldersScrollArea = QtGui.QScrollArea(self)
        self.foldersScrollArea.setWidgetResizable(True)

        self.foldersScrollAreaWidget = QtGui.QWidget()
        self.foldersScrollAreaWidget.setGeometry(QtCore.QRect(0, 0, 380, 280))
        self.folderLayout = QtGui.QGridLayout(self.foldersScrollAreaWidget)
        self.folderLayout.setAlignment(QtCore.Qt.AlignTop)
        self.foldersScrollArea.setWidget(self.foldersScrollAreaWidget)
        
        openFiles = QtGui.QPushButton("Add Files")
        openFiles.clicked.connect(self.addFiles)
        
        removeFiles = QtGui.QPushButton("Remove selected")
        removeFiles.clicked.connect(self.removeSelected)
        

        self.mainLayout = QtGui.QVBoxLayout(self)
        self.mainLayout.addWidget(openFiles)
        self.mainLayout.addWidget(removeFiles)
        self.mainLayout.addWidget(self.foldersScrollArea)
        self.setMaximumWidth(300)
        self.setGeometry(300, 200, 200, 400)
        self.checkAllBox = QtGui.QCheckBox('Check/Uncheck All', self)
        self.checkAllBox.setChecked(True)
        self.checkAllBox.stateChanged.connect(lambda:
                (self.checkAll() if self.checkAllBox.isChecked()
                else self.unCheckAll()))
        self.folderLayout.addWidget(self.checkAllBox)

  
    def addFiles(self):        
        qstringlist=QtGui.QFileDialog.getOpenFileNames(self,'Open Image',filter=self.filters)
        if qstringlist.isEmpty:
            for i in range(len(qstringlist)):
                self.fileList.append(qstringlist[i])
            self.fileList.removeDuplicates()
            self.fileList.sort()
            self.rebuildFileWidgetList() 
    
    def rebuildFileWidgetList(self):
        [self.fileWidgetList[i].setParent(None) for i in reversed(range(len(self.fileWidgetList)))]
        self.fileWidgetList= [fileIconWidget(unicode(self.fileList[i])) for i in range(len(self.fileList))]
        [self.folderLayout.addWidget(self.fileWidgetList[i]) for i in range(len(self.fileWidgetList))]
        for i in range(len(self.fileWidgetList)):
            self.connect(self.fileWidgetList[i],QtCore.SIGNAL("updateFilePreview"),self.sendUpdateSignal)
    
    def removeSelected(self):
        for i in reversed(range(len(self.fileWidgetList))):
            if self.fileWidgetList[i].checkState.isChecked():
                self.fileList.removeAt(i)
                self.fileWidgetList[i].setParent(None) 

                
    def getSelectedPaths(self):
        paths=[]
        for i in range(len(self.fileWidgetList)):
            if self.fileWidgetList[i].checkState.isChecked():
                paths.append(self.fileWidgetList[i].path)
        return paths
        
        
    def checkAll(self):
        [self.fileWidgetList[i].checkState.setChecked(True) for i in range(len(self.fileWidgetList))]
        
        
    def unCheckAll(self):
        [self.fileWidgetList[i].checkState.setChecked(False) for i in range(len(self.fileWidgetList))]
        
    def sendUpdateSignal(self,data):
        '''
        Wiget emits this signal, when file is clicked
        '''
        self.emit(QtCore.SIGNAL("updateFilePreview"),data)
        

class fileIconWidget(QtGui.QWidget):

    def __init__(self,path):
        super(fileIconWidget, self).__init__()
        self.path=path
        self.data=open_lsm_txt(path)
        
        self.Layout = QtGui.QGridLayout(self)
        self.Layout.setSpacing(0)
        self.Layout.setContentsMargins(0,0,0,0)
        self.Layout.setAlignment(QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        
        self.checkState = QtGui.QCheckBox(self)
        self.checkState.setTristate(False)
        self.checkState.setChecked(True)
        
        self.r_button = QtGui.QPushButton(os.path.basename(self.path))
        self.r_button.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.r_button.setStyleSheet("text-align: left;padding: 3px")    
        self.r_button.clicked.connect(self.sendUpdateSignal)
        self.Layout.addWidget(self.checkState,0,0)
        self.Layout.addWidget(self.r_button,0,1)
    
    def sendUpdateSignal(self):
        self.emit(QtCore.SIGNAL("updateFilePreview"),self.data)


def main():
    
    app = QtGui.QApplication(sys.argv)
    workDir=unicode(QtCore.QDir.currentPath())
    ex = FileSourceWidget(workDir)
    ex.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()    


def readlines_reverse(filename):
    with open(filename) as qfile:
        qfile.seek(0, os.SEEK_END)
        position = qfile.tell()
        line = ''
        while position >= 0:
            qfile.seek(position)
            next_char = qfile.read(1)
            if next_char == "\n":
                yield line[::-1]
                line = ''
            else:
                line += next_char
            position -= 1
        yield line[::-1]
        
def open_lsm_txt(path):
    j=0
    for line in readlines_reverse(path):
        if (line!=''):
            if len(line.split()) == 4:
                break
        j+=1
    data=np.genfromtxt(path,skip_header=2,skip_footer=j,usecols=(0,1,3))
    return data
