# -*- coding: utf-8 -*-
"""
Created on Wed Apr 29 14:01:54 2020

@author: hanne
"""


import sys
from PySide2.QtWidgets import QApplication, QMainWindow
from PySide2.QtCore import QFile, Signal, QThread
from ui_mainwindow import Ui_MainWindow
import serial

from ArduinoCommWithIndividualCommands import *

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        
        self.ui.ConnectButton.clicked.connect(self.openCommPort)
        self.reader = comRead()
        self.reader.outputTxt.connect(self.updateTextBrowser)
        self.ui.DisconnectButton.clicked.connect(self.closeCommPort)
        self.ui.ConnectedRadioButton.clicked.connect(self.keepCommChecked)
        
    def keepCommChecked(self):
        global serial_open
        if serial_open == True:
            self.ui.ConnectedRadioButton.setChecked(True)
        elif serial_open == False:
            self.ui.ConnectedRadioButton.setChecked(False)
    
    def testPushButton(self):
        testarray = bytearray('apple', 'UTF-8')
        ser.write(startMarkerByte)
        ser.write(len(testarray).to_bytes(1,'big'))
        ser.write(testarray)
        ser.write(endMarkerByte)
    
    def updateTextBrowser(self, msg):
        self.ui.CommQTextBrowser.append(str(msg))
        print("msg start 1")
        print(msg)
        print("msg stop 1")
        
    def closeEvent(self, event):
        global ser
        global serial_open
        print("closing app")
        if serial_open == True:
            try:
                ser.close()
                print("port closed")
            except(serial.SerialException):
                if serial_open == False:
                    print("port already closed")
                else:
                    print("?? Weird serial stuff ??")
            
    def openCommPort(self):
        global serial_open
        global baudrate
        global ser
        if serial_open == False:
            self.terminalPrint("Opening " + self.ui.COM_Input.text() + "...")
            try:
                ser = serial.Serial(self.ui.COM_Input.text(), baudrate, timeout = 1)
                #print(self.ui.COM_Input.text() + " opened successfully.")
                serial_open = True
                self.ui.ConnectedRadioButton.setChecked(True)
                self.terminalPrint(self.ui.COM_Input.text() + " opened successfully.")
            except:
                self.terminalPrint("Unsuccesful at opening" + self.ui.COM_Input.text())
        else:
            self.terminalPrint("Serial port already open...")
    
    def closeCommPort(self):
        global serial_open
        global baudrate
        global ser
        if serial_open == True:
            try:
                ser.close()
                serial_open = False
                self.ui.ConnectedRadioButton.setChecked(False)
                self.terminalPrint("Serial port closed.")
            except:
                self.terminalPrint("Issue closing port.")
    
    def terminalPrint(self,text):
        self.ui.CommQTextBrowser.append(text)
        
        
class comRead(QThread):
    outputTxt = Signal(bytearray)
    
    def __init__(self):
        QThread.__init__(self)
        
    def run(self):
        while True:
            self.outputTxt.emit(readMessageThread())
            time.sleep(0.1)
            self.outputTxt.emit("test")



if __name__ == "__main__":
    #temporary
    serial_open = False
    baudrate = 115200;
    
    
    app = QApplication.instance()
    if app is None:
        # Create the Qt Application if it doesn't exist
        app = QApplication(sys.argv)
        
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
    