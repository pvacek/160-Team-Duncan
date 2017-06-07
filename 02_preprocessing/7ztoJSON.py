# -*- coding: utf-8 -*-
"""
Created on Fri Feb 24 12:49:52 2017

@author: Patrick Vacek
"""

#Extracting 7zip files using command line

import os

#Execute 7-zip
os.chdir('C:/Program Files/7-Zip')
os.system('7zip.exe')  

os.chdir('F:/ProjectTimDuncan')
file_names=os.listdir()[0:636]

def extractJSON(file):
    os.chdir('C:/Program Files/7-Zip')
    sys_arg='7z e e:/ProjectTimDuncan/'+file+' -oe:/tempjson'
    os.system(sys_arg)
            