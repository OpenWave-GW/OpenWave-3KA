# -*- coding: utf-8 -*-
"""
Program name: OpenWave-3KA

Copyright:
----------------------------------------------------------------------
OpenWave-3KA is Copyright (c) 2021 Good Will Instrument Co., Ltd All Rights Reserved.

This program is free software; you can redistribute it and/or modify it under the terms 
of the GNU Lesser General Public License as published by the Free Software Foundation; 
either version 2.1 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
See the GNU Lesser General Public License for more details.

You can receive a copy of the GNU Lesser General Public License from http://www.gnu.org/

Note:
OpenWave-3KA uses third party software which is copyrighted by its respective copyright 
holder. For details see the copyright notice of the individual package.

The Qt GUI Toolkit is Copyright (c) 2018 Qt Company Ltd.  OpenWave-3KA use Qt version 5 
library under the terms of the LGPL version 3.0.
----------------------------------------------------------------------
Description:
OpenWave-3KA is a python example program used to get waveform and image from DSO.

Environment:
  1. Python 3.9.5
  2. dso3ka_pyvisa 1.02
  3. Matplotlib 3.3.3
  4. Numpy 1.20.3
  5. PySide2 5.15.2
  6. PIL 8.2.0
  7. PyVISA 1.11.3

Version: 1.02

Modified on FEB 16 2024

Programmer: Kevin Meng, Weiche Huang
"""
import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from mpl_toolkits.axes_grid1 import host_subplot
import mpl_toolkits.axisartist as AA
from PySide2 import QtCore, QtGui, QtWidgets
import numpy as np
from PIL import Image
import os, sys, time
import dso3ka_pyvisa
import pyvisa

__version__ = "1.02" #OpenWave-3KA software version.

def resource_path(relative_path):
    if getattr(sys, 'frozen', False): # if Bundle Resource
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class checkInterfaceWindow(QtWidgets.QWidget):
    launch_signal = QtCore.Signal(str)
    def __init__(self, device_list, message):
        global baud_rate
        super(checkInterfaceWindow, self).__init__()
        self.setWindowTitle("Select Interface")
        rm_list_num = len(device_list)
        port_list=[]
        if os.path.exists('port.config'):
            print('port.config found!')
            f = open('port.config', 'r')
            load_flag=0
            while(1):
                str = f.readline()
                if(str == ''):
                    f.close()
                    break
                elif(str[0] == '#'):
                    continue
                elif('[SOCKET]' in str):
                    port_flag=1
                    continue
                elif(port_flag==1):
                    str=str.strip('\r').strip('\n').strip(' ')
                    port_list.append(str)

        top_layout = QtWidgets.QVBoxLayout()
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)

        self.tabs = QtWidgets.QTabWidget()
        self.deviceSetLW1 = QtWidgets.QListWidget()
        if(message):
            self.messageLabel = QtWidgets.QLabel(message)
            sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
            self.messageLabel.setSizePolicy(sizePolicy)
            pe = QtGui.QPalette()
            pe.setColor(QtGui.QPalette.WindowText,QtCore.Qt.blue)
            self.messageLabel.setPalette(pe)

        # Resource filter for VISA.
        self.device1=[]
        print(device_list)
        for device in device_list:
            if('SOCKET' in device):
                self.deviceSetLW1.addItem(device)
                self.device1.append(device)
            elif('0x2184::0x006E' in device) or ('0x2184::0x006F' in device) or ('0x2184::0x0070' in device) or ('0x2184::0x0071' in device): # On Windows
                self.deviceSetLW1.addItem(device)
                self.device1.append(device)
            elif('8580::110' in device) or ('8580::111 in device') or ('8580::112' in device) or ('8580::113' in device): # On Ubuntu
                self.deviceSetLW1.addItem(device)
                self.device1.append(device)
            elif('ASRL' in device):
                self.deviceSetLW1.addItem(device)
                self.device1.append(device)
            elif('GPIB' in device):
                self.deviceSetLW1.addItem(device)
                self.device1.append(device)
                
        print('len=', len(device_list))
        self.tabs.addTab(self.deviceSetLW1, 'VISA Resource')

        # Resource filter for port.config
        self.device2=[]
        if(port_list):
            self.deviceSetLW2 = QtWidgets.QListWidget()
            for device in port_list:
                print(device)
                if(device.count('.') == 3):
                    self.deviceSetLW2.addItem(device)
                    self.device2.append(device)
            if(self.device2):
                self.tabs.addTab(self.deviceSetLW2, 'Config File')

        top_layout.addWidget(self.tabs)
        if(message):
            top_layout.addWidget(self.messageLabel)

        self.selectBtn = QtWidgets.QPushButton('Select')
        self.selectBtn.setFixedSize(80, 30)
        self.cancelBtn = QtWidgets.QPushButton('Cancel')
        self.cancelBtn.setFixedSize(80, 30)

        self.baudrate_Label = QtWidgets.QLabel("Baud rate ")
        self.baudrate_Label.setVisible(0)
        self.baudrateLineEdit= QtWidgets.QLineEdit('9600')
        self.baudrateLineEdit.setDisabled(1)
        self.baudrateLineEdit.setVisible(0)
        self.baudrateLineEdit.setFixedSize(50, 30)

        bottom_layout = QtWidgets.QHBoxLayout()
        bottom_layout.addWidget(self.baudrate_Label)
        bottom_layout.addWidget(self.baudrateLineEdit)
        bottom_layout.addStretch()
        bottom_layout.addWidget(self.selectBtn)
        bottom_layout.addWidget(self.cancelBtn)

        resourceLayout = QtWidgets.QVBoxLayout()
        resourceLayout.addLayout(top_layout)
        resourceLayout.addLayout(bottom_layout)
        
        self.setLayout(resourceLayout)
        self.resize(300, 400)

        # signal-slot
        self.selectBtn.clicked.connect(self.selectAction)
        self.cancelBtn.clicked.connect(self.cancelAction)
        self.deviceSetLW1.itemClicked.connect(self.itemClickedEvent1)
        if(port_list):
            self.deviceSetLW2.itemClicked.connect(self.itemClickedEvent2)
        self.pageIndex=0 # Default set to VISA resource.
        self.rowIndex=-1
        self.selectedInterface=''
        baud_rate=9600
        
    def itemClickedEvent1(self):
        self.pageIndex=0
        self.rowIndex=self.deviceSetLW1.currentRow()
        self.selectedInterface=self.device1[self.rowIndex]
        if('ASRL' in self.selectedInterface):
            self.baudrate_Label.setVisible(1)
            self.baudrateLineEdit.setVisible(1)
            self.baudrateLineEdit.setEnabled(1)
        else:
            self.baudrate_Label.setVisible(0)
            self.baudrateLineEdit.setVisible(0)
            self.baudrateLineEdit.setEnabled(0)

    def itemClickedEvent2(self):
        self.pageIndex=1
        self.rowIndex=self.deviceSetLW2.currentRow()
        str=self.device2[self.rowIndex].split(':')
        self.selectedInterface= 'TCPIP0::' + str[0] + '::' + str[1] + '::SOCKET'
        self.baudrate_Label.setVisible(0)
        self.baudrateLineEdit.setVisible(0)
        self.baudrateLineEdit.setEnabled(0)
        
    def cancelAction(self):
        self.launch_signal.emit('')
        self.close()

    def selectAction(self):
        baud_rate=int(self.baudrateLineEdit.text())
        self.launch_signal.emit(self.selectedInterface)
        self.close()
        
    def start_waveform_window(self, interface):
        global waveform  # Using a global now to avoid garbage collection, but other ways would be better
        waveform = Window(interface)
        waveform.show()
    

class Window(QtWidgets.QMainWindow):
    def __init__(self, interface_name):
        global dso
        global baud_rate
        super(Window, self).__init__()
        self._main = QtWidgets.QWidget()
        self.setCentralWidget(self._main)

        #Connecting to a DSO.
        if(interface_name):
            try:
                inst = rm.open_resource(interface_name)
                if('ASRL' in interface_name):
                    inst.baud_rate = baud_rate
                    inst.timeout = 10000
                elif('SOCKET' in interface_name):
                    inst.read_termination = '\n'
                    inst.timeout = 5000
                elif('0x2184::0x006E' in interface_name) or ('0x2184::0x006F' in interface_name) or ('0x2184::0x0070' in interface_name) or ('0x2184::0x0071' in interface_name) or ('0x2184::0x0085' in interface_name) or ('0x2184::0x0086' in interface_name):
                    inst.timeout = 5000
            except Exception as e:
                inst=None
                print(e)
        else:
            inst=None
        dso=dso3ka_pyvisa.Dso(inst)

        self.setWindowTitle('OpenWave-3KA V%s @ %s'%(__version__, interface_name))
        filename = resource_path(os.path.join("res","openwave.ico"))
        self.setWindowIcon(QtGui.QIcon(filename))
        self.setWindowIcon(QtGui.QIcon(filename))
        
        #Waveform area.
        self.figure = plt.figure()
        self.figure.set_facecolor('white')

        self.canvas = FigureCanvas(self.figure)
        self.canvas.setMinimumSize(800,  400)
        
        self.toolbar = NavigationToolbar(self.canvas, self)
        self.toolbar.hide()

        #Zoom In/out and Capture Buttons
        self.zoomBtn = QtWidgets.QPushButton('Zoom')
        self.zoomBtn.setFixedSize(100, 30)
        self.zoomBtn.clicked.connect(self.toolbar.zoom)

        self.panBtn = QtWidgets.QPushButton('Pan')
        self.panBtn.setFixedSize(100, 30)
        self.panBtn.clicked.connect(self.toolbar.pan)

        self.homeBtn = QtWidgets.QPushButton('Home')
        self.homeBtn.setFixedSize(100, 30)
        self.homeBtn.clicked.connect(self.toolbar.home)

        self.captureBtn = QtWidgets.QPushButton('Capture')
        self.captureBtn.setFixedSize(100, 50)
        self.captureBtn.clicked.connect(self.manualCapture)
        if(dso.connection_status==0):
            self.captureBtn.setEnabled(False)
            
        self.continuousBtn = QtWidgets.QRadioButton('Continuous')
        self.continuousBtn.setEnabled(True)
        self.continuousBtn.clicked.connect(self.setContinuous)

        #Continuous capture selection
        self.captureLayout = QtWidgets.QHBoxLayout()
        self.captureLayout.addWidget(self.captureBtn)
        self.captureLayout.addWidget(self.continuousBtn)

        #Type: Raw Data/Image
        self.typeBtn = QtWidgets.QPushButton('Raw Data')
        self.typeBtn.setToolTip("Switch to get raw data or image from DSO.")
        self.typeBtn.setFixedSize(120, 50)
        self.typeFlag=True #Initial state -> Get raw data
        self.typeBtn.setCheckable(True)
        self.typeBtn.setChecked(True)
        self.typeBtn.clicked.connect(self.typeAction)
        
        #Channel Selection.
        self.ch1checkBox = QtWidgets.QCheckBox('CH1')
        self.ch1checkBox.setFixedSize(60, 30)
        self.ch1checkBox.setChecked(True)
        self.ch2checkBox = QtWidgets.QCheckBox('CH2')
        self.ch2checkBox.setFixedSize(60, 30)
        if(dso.chnum==4):
            self.ch3checkBox = QtWidgets.QCheckBox('CH3')
            self.ch3checkBox.setFixedSize(60, 30)
            self.ch4checkBox = QtWidgets.QCheckBox('CH4')
            self.ch4checkBox.setFixedSize(60, 30)
        
        #Set channel selection layout.
        self.selectLayout = QtWidgets.QHBoxLayout()
        self.selectLayout.addWidget(self.ch1checkBox)
        self.selectLayout.addWidget(self.ch2checkBox)
        if(dso.chnum==4):
            self.selectLayout2 = QtWidgets.QHBoxLayout()
            self.selectLayout2.addWidget(self.ch3checkBox)
            self.selectLayout2.addWidget(self.ch4checkBox)

        self.typeLayout = QtWidgets.QHBoxLayout()
        self.typeLayout.addWidget(self.typeBtn)
        self.typeLayout.addLayout(self.selectLayout)
        if(dso.chnum==4):
            self.typeLayout.addLayout(self.selectLayout2)

        self.zoominoutLayout = QtWidgets.QHBoxLayout()
        self.zoominoutLayout.addWidget(self.zoomBtn)
        self.zoominoutLayout.addWidget(self.panBtn)
        self.zoominoutLayout.addWidget(self.homeBtn)

        #Save/Load/Quit button
        self.saveBtn = QtWidgets.QPushButton('Save')
        self.saveBtn.setFixedSize(100, 50)
        self.saveMenu = QtWidgets.QMenu(self)
        self.csvAction = self.saveMenu.addAction("&As CSV File")
        self.pictAction = self.saveMenu.addAction("&As PNG File")
        self.saveBtn.setMenu(self.saveMenu)
        self.saveBtn.setToolTip("Save waveform to CSV file or PNG file.")
        self.connect(self.csvAction, QtCore.SIGNAL("triggered()"), self.saveCsvAction)
        self.connect(self.pictAction, QtCore.SIGNAL("triggered()"), self.savePngAction)

        self.loadBtn = QtWidgets.QPushButton('Load')
        self.loadBtn.setToolTip("Load CHx's raw data from file(*.CSV, *.LSF).")
        self.loadBtn.setFixedSize(100, 50)
        self.loadBtn.clicked.connect(self.loadAction)

        self.quitBtn = QtWidgets.QPushButton('Quit')
        self.quitBtn.setFixedSize(100, 50)
        self.quitBtn.clicked.connect(self.quitAction)

        # set the layout
        self.waveLayout = QtWidgets.QHBoxLayout()
        self.waveLayout.addWidget(self.canvas)
        
        self.wave_box=QtWidgets.QVBoxLayout()
        self.wave_box.addLayout(self.waveLayout)
        
        self.wavectrlLayout = QtWidgets.QHBoxLayout()
        self.wavectrlLayout.addStretch(1)
        self.wavectrlLayout.addLayout(self.zoominoutLayout)
        self.wavectrlLayout.addStretch(1)
        self.wavectrlLayout.addLayout(self.captureLayout)
        self.wavectrlLayout.addStretch(1)
        
        self.saveloadLayout = QtWidgets.QHBoxLayout()
        self.saveloadLayout.addWidget(self.saveBtn)
        self.saveloadLayout.addWidget(self.loadBtn)
        self.saveloadLayout.addWidget(self.quitBtn)
        
        self.ctrl_box=QtWidgets.QHBoxLayout()
        self.ctrl_box.addLayout(self.typeLayout)
        self.ctrl_box.addLayout(self.saveloadLayout)
        
        main_box=QtWidgets.QVBoxLayout(self._main)
        main_box.addLayout(self.wave_box)         #Waveform area.
        main_box.addLayout(self.wavectrlLayout)   #Zoom In/Out...
        main_box.addLayout(self.ctrl_box)         #Save/Load/Quit
        self.setLayout(main_box)
        
        self.captured_flag=0
        self.timer=QtCore.QTimer()
        self.timer.timeout.connect(self.timerCapture)

    def typeAction(self):
        if(self.typeFlag==True):
            self.typeFlag=False
            self.typeBtn.setText("Image")
            self.csvAction.setEnabled(False)
        else:
            self.typeFlag=True
            self.typeBtn.setText("Raw Data")
            self.csvAction.setEnabled(True)
        self.typeBtn.setChecked(self.typeFlag)
        self.ch1checkBox.setEnabled(self.typeFlag)
        self.ch2checkBox.setEnabled(self.typeFlag)
        if(dso.chnum==4):
            self.ch3checkBox.setEnabled(self.typeFlag)
            self.ch4checkBox.setEnabled(self.typeFlag)

    def saveCsvAction(self):
        if(self.typeFlag==True): #Save raw data to csv file.
            file_name=QtWidgets.QFileDialog.getSaveFileName(self, "Save as", 'DS0001', "Fast CSV File(*.CSV)")[0]
            num=len(dso.ch_list)
            #print('num=%d'%num)
            if(num==0):
                print('There is no waveform data!')
                return
            for ch in range(num):
                if(dso.info[ch]==[]):
                    print('Failed to save data, raw data information is required!')
                    return
            print('---', len(dso.info[0]), dso.info[0])
            f = open(file_name, 'wb')
            item=len(dso.info[0])
            #Write file header.
            str='%s,\r\n' % dso.info[0][0]
            print(str)
            f.write(str.encode('utf-8'))
            for x in range(1,  item-1):
                str=''
                for ch in range(num):
                    if(dso.info[ch][x][0:4] == 'Mode'):
                        str+='Mode,Fast,'
                    else:
                        str+=('%s,' % dso.info[ch][x])
                str+='\r\n'
                f.write(str.encode())
            str=''
            if(num==1):
                str+=('%s,' % dso.info[0][item-1])
            else:
                for ch in range(num):
                    str+=('%s,,' % dso.info[ch][item-1])
            str+='\r\n'
            f.write(str.encode())
            #Write raw data.
            item=len(dso.iWave[0])
            #print item
            tenth=int(item/10)
            n_tenth=tenth-1
            percent=10
            for x in range(item):
                str=''
                if(num==1):
                    str+=('%s,' % dso.iWave[0][x])
                else:
                    for ch in range(num):
                        str+=('%s, ,' % dso.iWave[ch][x])
                str+='\r\n'
                f.write(str.encode())
                if(x==n_tenth):
                    n_tenth+=tenth
                    print('%3d %% Saved\r'%percent, end='')
                    percent+=10
            f.close()

    def savePngAction(self):
        #Save figure to png file.
        file_name=QtWidgets.QFileDialog.getSaveFileName(self, "Save as", 'DS0001', "PNG File(*.png)")[0]
        if(file_name==''):
            return
        if(self.typeFlag==True): #Save raw data waveform as png file.
            self.figure.savefig(file_name)
        else:  #Save figure to png file.
            if(dso.osname=='pi'): #For raspberry pi only.
                img=dso.im.transpose(Image.FLIP_TOP_BOTTOM)
                img.save(file_name)
            else:
                dso.im.save(file_name)
        print('Saved image to %s.'%file_name)

    def loadAction(self):
        dso.ch_list=[]
        full_path_name=QtWidgets.QFileDialog.getOpenFileName(self,self.tr("Open File"),".","CSV/LSF files (*.CSV *.LSF);;All files (*.*)")  
        sFileName=full_path_name[0]
        print(sFileName)
        if(len(sFileName)<=0):
            return
        if os.path.exists(sFileName):
            print('Reading file...')
            count=dso.readRawDataFile(sFileName)
            #Draw waveform.
            if(count>0):
                total_chnum=len(dso.ch_list)
                if(total_chnum==0):
                    return
                self.drawWaveform(0)
        else:
            print('File not found!')

    def quitAction(self):
        if(dso.connection_status==1):
            dso.closeIO()
        self.close()
    
    def timerCapture(self):
        self.captureAction()
        if(self.continuousBtn.isChecked()==True):
            self.timer.start(10)  #Automatic capturing. 
        
    def manualCapture(self):
        if(self.continuousBtn.isChecked()==True):
            if(self.captured_flag ==0):
                self.captured_flag = 1   #Continuous capture started.
                self.captureBtn.setText("Click to Stop")
                self.loadBtn.setEnabled(False)
                self.timer.start()
            else:
                self.captured_flag = 0   #Continuous capture stopped.
                self.captureBtn.setText("Capture")
                self.loadBtn.setEnabled(True)
                self.timer.stop()
        self.captureAction()
    
    def captureAction(self):
        dso.iWave=[[], [], [], []]
        dso.ch_list=[]
        if(self.typeFlag==True): #Get raw data.
            draw_flag=False
            #Turn on the selected channels.
            if((self.ch1checkBox.isChecked()==True) and (dso.isChannelOn(1)==False)):
                dso.write(":CHAN1:DISP ON")           #Set CH1 on.
            if((self.ch2checkBox.isChecked()==True) and (dso.isChannelOn(2)==False)):
                dso.write(":CHAN2:DISP ON")           #Set CH2 on.
            if(dso.chnum==4):
                if((self.ch3checkBox.isChecked()==True) and (dso.isChannelOn(3)==False)):
                    dso.write(":CHAN3:DISP ON")       #Set CH3 on.
                if((self.ch4checkBox.isChecked()==True) and (dso.isChannelOn(4)==False)):
                    dso.write(":CHAN4:DISP ON")       #Set CH4 on.
            #Get all the selected channel's raw datas.
            if(self.ch1checkBox.isChecked()==True):
                dso.getRawData(True, 1)              #Read CH1's raw data from DSO (including header).
            if(self.ch2checkBox.isChecked()==True):
                dso.getRawData(True, 2)              #Read CH2's raw data from DSO (including header).
            if(dso.chnum==4):
                if(self.ch3checkBox.isChecked()==True):
                    dso.getRawData(True, 3)          #Read CH3's raw data from DSO (including header).
                if(self.ch4checkBox.isChecked()==True):
                    dso.getRawData(True, 4)          #Read CH4's raw data from DSO (including header).
            #Draw waveform.
            total_chnum=len(dso.ch_list)
            if(total_chnum==0):
                return
            if(self.drawWaveform(1)==-1):
                time.sleep(5)
                self.drawWaveform(0)
        else: #Get image.
            img_type=1   #1 for RLE format, 0 for PNG format.
            if(img_type):
                dso.write(':DISP:OUTP?')                 #Send command to get image from DSO.
            else:
                dso.write(':DISP:PNGOutput?')            #Send command to get image from DSO.
            dso.getBlockData(None)
            dso.ImageDecode(img_type)
            self.showImage()
            self.canvas.draw()
            print('Image is ready!')

    def setContinuous(self):
        if(self.continuousBtn.isChecked()==False):
            self.captured_flag = 0   #Continuous capture stopped.
            self.timer.stop()
            self.loadBtn.setEnabled(True)
            self.captureBtn.setText("Capture")

    def showImage(self):
        #Turn the ticks off and show image.
        plt.clf()
        ax = plt.gca()
        ax.xaxis.set_visible(False)
        ax.yaxis.set_visible(False)
        plt.imshow(dso.im)
        plt.tight_layout()

    def drawWaveform(self, mode):
        total_chnum=len(dso.ch_list)
        num=dso.points_num
        ch_colortable=['#C0B020',  '#0060FF',  '#FF0080',  '#00FF60']
        ch=int(dso.ch_list[0][2])-1 #Get the channel of first waveform.
        plt.cla()
        plt.clf()
        #Due to the memory limitation of matplotlib, we must reduce the sample points.
        if(num==10000000):
            if(total_chnum>2):
#                down_sample_factor=4
                down_sample_factor=1
            elif(total_chnum==2):
#                down_sample_factor=4
                down_sample_factor=1
            else:
                down_sample_factor=1
            num=num/down_sample_factor
        elif(num==20000000):
            if(total_chnum > 1):
                down_sample_factor=4
            else:
                down_sample_factor=2
            num=num/down_sample_factor
        elif(num==100000000):
            if(total_chnum>2):
                down_sample_factor=40
            elif(total_chnum==2):
                down_sample_factor=20
            else:
                down_sample_factor=10
            num=num/down_sample_factor
        elif(num==200000000):
            if(total_chnum>2):
                down_sample_factor=80
            elif(total_chnum==2):
                down_sample_factor=40
            else:
                down_sample_factor=20
            num=num/down_sample_factor
        else:
            down_sample_factor=1
        dt=dso.dt[0] #Get dt from the first opened channel.
        t_start=dso.hpos[0]-num*dt/2
        t_end  =dso.hpos[0]+num*dt/2
        t = np.arange(t_start, t_end, dt)
        #print t_start, t_end, dt, len(t)
        if((len(t)-num)==1): #Avoid floating point rounding error.
            t=t[:-1]
        wave_type='-' #Set waveform type to vector.
        #Draw waveforms.
        ax=[[], [], [], []]
        p=[]
        for ch in range(total_chnum):
            if(ch==0):
                ax[ch]=host_subplot(111, axes_class=AA.Axes)
                ax[ch].set_xlabel("Time (sec)")
            else:
                ax[ch]=ax[0].twinx()
            print("%s Units: %s" %(dso.ch_list[ch],  dso.vunit[ch]))
            ax[ch].set_ylabel("%s Units: %s" %(dso.ch_list[ch],  dso.vunit[ch]))
            ch_color=ch_colortable[int(dso.ch_list[ch][2])-1]
            if(ch>=1):
                new_fixed_axis = ax[ch].get_grid_helper().new_fixed_axis
                ax[ch].axis["right"] = new_fixed_axis(loc="right", axes=ax[ch], offset=(60*(ch-1), 0))
            ax[ch].set_xlim(t_start, t_end)
            ax[ch].set_ylim(-4*dso.vdiv[ch]-dso.vpos[ch], 4*dso.vdiv[ch]-dso.vpos[ch]) #Setup vertical display range.
            fwave=dso.convertWaveform(ch, down_sample_factor)
            #print('Length=%d'%(len(fwave)))
            if(ch==0):
                try:
                    p=ax[ch].plot(t, fwave, color=ch_color, ls=wave_type, label = dso.ch_list[ch])
                except Exception as e:
                    print('e:', e)
                    if(mode==1):
                        #print sys.exc_info()[0]
                        time.sleep(5)
                        print('Trying to plot again!',)
                    return -1
            else:
                try:
                    p+=ax[ch].plot(t, fwave, color=ch_color, ls=wave_type, label = dso.ch_list[ch])
                except Exception as e:
                    print('e:', e)
                    if(mode==1):
                        #print sys.exc_info()[0]
                        time.sleep(5)
                        print('Trying to plot again!',)
                    return -1
        if(total_chnum>1):
            labs = [l.get_label() for l in p]
            plt.legend(p, labs,   loc='upper right')
        plt.tight_layout() 
        self.canvas.draw()
        del ax, t, p
        return 0

if __name__ == '__main__':
    file_name = resource_path(os.path.join("res","license.txt"))
    with open(file_name, 'r', encoding='utf-8') as license_file:
        license_str=license_file.read()
    print(license_str)
    print('-----------------------------------------------------------------------------');
    print('OpenWave-3KA V%s\n'% __version__)

    try:
        rm = pyvisa.ResourceManager()
        resource_list = rm.list_resources('?*')
        message=''
    except Exception as e:
        resource_list=()
        message="Warning! Please find NI-VISA from National Instruments's website and manually install it before running this program."

    app = QtWidgets.QApplication(sys.argv)

    window = checkInterfaceWindow(resource_list, message)

    window.resize(300, 400)
    window.launch_signal.connect(window.start_waveform_window)
    window.show()

    sys.exit(app.exec_())
