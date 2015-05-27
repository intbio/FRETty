#!/usr/bin/env python
# -*- coding: utf-8 -*-

#    This file is a part of Fretty project
#    Copyright (C) 2015  Grigory A. Armeev
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License version 2 as·
#    published by the Free Software Foundation.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License v2 for more details.
#
#    You should have received a copy of the GNU General Public License along
#    with this program; if not, write to the Free Software Foundation, Inc.,
#    51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

from distutils.core import setup
import py2exe, sys, os

#import skimage
import matplotlib
import PyQt4

sys.argv.append('py2exe')
sys.path.append('..')

rootdir = os.path.dirname(os.getcwd())
script = os.path.join(rootdir, 'GUI.py')
#icon = os.path.join(rootdir, 'misc', 'darfi.ico')

#Mydata_files = [('images', ['D:\Users\Vanya\Python_win32\Ksenia\gui\smile_icon_2.jpg'])]

qt_if_dlls_path = os.path.join(os.path.dirname(PyQt4.__file__), u'plugins', u'imageformats')
qt_if_dlls = [os.path.join(qt_if_dlls_path, dll) for dll in os.listdir(qt_if_dlls_path)]

#orb_descriptor = os.path.join(skimage.data_dir, 'orb_descriptor_positions.txt')
mydata_files = [
            ('imageformats', \
              qt_if_dlls
              ),\
#              (os.path.join('skimage', 'data'), [\
#              orb_descriptor,
#              ])\
#             ,('misc', [icon,])
#              ('mpl_data',[matplotlib.get_data_path()])\
              ]
              
mydata_files += matplotlib.get_py2exe_datafiles()

setup(
#    options = {'py2exe': {'bundle_files': 1}},
#    windows=[{'script':script, "icon_resources":[(1, icon)]}],
    windows=[{'script':script}],
    data_files = mydata_files,
    options={"py2exe":{"includes":[\
            "sip",\
#            "pic_an",\
            "scipy.special._ufuncs_cxx",\
#            "skimage.filters.rank.core_cy",\
            "scipy.sparse.csgraph._validation",\
#            "skimage._shared.geometry",\
#            "skimage",\
            "sklearn.utils.lgamma",\
            "sklearn.utils.weight_vector",\
            "sklearn.neighbors.typedefs",\
            "sklearn.utils.sparsetools._graph_validation",\
#            "PIL.TiffImagePlugin"
            ],
            'excludes': ['_gtkagg', 'tkagg','wxagg']}},
#
# Uncomment the next line if you want to see console output:           
#    console = [{'script': script}],
# If console output is off warnings should be supressed in simple_gui.py
#
    zipfile = None,
)

raw_input()
