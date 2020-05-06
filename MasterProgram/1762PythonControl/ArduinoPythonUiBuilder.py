# -*- coding: utf-8 -*-
"""
Created on Wed Apr 29 14:01:54 2020

@author: hanne
"""


import sys
from PySide2.QtWidgets import QApplication, QMainWindow
from PySide2.QtCore import QFile, Signal, QThread
from PySide2 import QtGui
from ui_mainwindow import Ui_MainWindow
import serial
import queue
import time


from ArduinoCommWithIndividualCommands import *

class MainWindow(QMainWindow):
    varNum = 19 #number of variables just below (including mode)
    ##########################################################
    #!!!!!These need to match pythonArduinoComm.cpp!!!!!!!!!!
    mode = 0
    flash = 17;
    interval = 18;
    numSteps = 1;
    runsPerStep = 2;
    sweepUpperBound = 3;
    sweepLowerBound = 4;
    sweepCenterFrequency = 5;
    sweepRate = 6;
    sweepSpan = 7;
    sweepRateStart = 8;
    sweepRateStop = 9;
    frequency = 10;
    outputStateSF = 11;
    pulseTime = 12;
    freqStart = 13;
    freqStop = 14;
    pulseTimeStart = 15;
    pulseTimeStop = 16;
    ###########################################################
    ##########Mode Numeric Lables##########
    mode_SingleFrequency = 4;
    mode_SweepScan = 3;
    mode_Spectroscopy = 5 ;
    mode_RabiScan = 6;
    mode_Test1 = 1;
    mode_Test2 = 2;
    
    #modeList = [["Single Frequency", mode_SingleFrequency],["Spectroscopy", mode_Spectroscopy],["Rabi Scan", mode_RabiScan],["Frequency Sweep Scan", mode_SweepScan]]
    #####commands#######
    modechange = 1;
    varchange = 2;
    ########InitialValues#####################################
    #mode selection
    modeInit = 1;
    
    #for testing communicaiton
    flashInit = 0;
    intervalInit = 0;
    
    #common paramters for all scans
    numStepsInit = 10;
    runsPerStepInit = 10;
    
    #frequency sweep parameters
    sweepUpperBoundInit = 41000000;
    sweepLowerboundInit = 39000000;
    sweepCenterFrequencyInit = 40000000;
    sweepRateInit = 100000000;
    sweepSpanInit = 1000000;
    #frequency sweep scan specific paramters
    sweepRateStartInit = 100000000;
    sweepRateStopInit = 1000000000;        
    
    #single frequency mode
    frequencyInit = 40000000;
    outputStateSFInit = 0;
   
    #single frequency spectroscopy paramters
    pulseTimeInit = 1000; #microseconds of delay
    freqStartInit = 39000000;
    freqStopInit = 41000000;
    
    #Rabi Flopping Paramters
    pulseTimeStartInit = 10; #microseconds of delay
    pulseTimeStopInit = 100; #microseconds of delay
    
    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.COM_Input.setText('/dev/tty.usbmodem14101')
        # self.fromArduinoQueue = queue.Queue()
        

        
        self.variableArray = self.InitialVariableArrayConstructor()
        self.UpdateVarLCDs()
        
        self.ui.UploadButton.clicked.connect(self.updateArduino)
        self.ui.ConnectButton.clicked.connect(self.openCommPort)
        
        self.ui.OutputFreqUnitComboBox.currentTextChanged.connect(lambda: self.UpdateSingleLCD(self.ui.OutputFreqUnitComboBox,self.ui.OutputFreqQLCD,self.variableArray[self.frequency]))
        self.ui.FreqStartUnitComboBox.currentTextChanged.connect(lambda: self.UpdateSingleLCD(self.ui.FreqStartUnitComboBox,self.ui.FreqStartQLCD,self.variableArray[self.freqStart]))
        self.ui.FreqStopUnitComboBox.currentTextChanged.connect(lambda: self.UpdateSingleLCD(self.ui.FreqStopUnitComboBox,self.ui.FreqStopQLCD,self.variableArray[self.freqStop]))
        self.ui.SweepUpperBoundUnitComboBox.currentTextChanged.connect(lambda: self.UpdateSingleLCD(self.ui.SweepUpperBoundUnitComboBox,self.ui.SweepUpperBoundQLCD,self.variableArray[self.sweepUpperBound]))
        self.ui.SweepLowerBoundUnitComboBox.currentTextChanged.connect(lambda: self.UpdateSingleLCD(self.ui.SweepLowerBoundUnitComboBox,self.ui.SweepLowerBoundQLCD,self.variableArray[self.sweepLowerBound]))
        self.ui.SweepCenterFreqUnitComboBox.currentTextChanged.connect(lambda: self.UpdateSingleLCD(self.ui.SweepCenterFreqUnitComboBox,self.ui.SweepCenterFreqQLCD,self.variableArray[self.sweepCenterFrequency]))
        self.ui.SweepSpanUnitComboBox.currentTextChanged.connect(lambda: self.UpdateSingleLCD(self.ui.SweepSpanUnitComboBox,self.ui.SweepSpanQLCD,self.variableArray[self.sweepSpan]))
        
        
        self.reader = comRead()
        self.reader.outputTxt.connect(self.updateTextBrowser)
        #self.reader.encodedMsg.connect(self.putMsgInFromArduinoQueue)
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
        if type(msg)==bytearray:
            tempmsg = msg[1:].decode()
            print("bytearray")
            self.ui.CommQTextBrowser.append(tempmsg)
        elif type(msg)==str:    
            self.ui.CommQTextBrowser.append(str(msg))
        # print("msg start 1")
        # print(msg)
        # print("msg stop 1")
        
    def closeEvent(self, event):
        global ser
        global serial_open
        print("closing app...")
        if self.reader.keepgoing == True:
            self.reader.stop()
        if serial_open == True:
            try:
                ser.close()
                print("port closed")
            except(serial.SerialException):
                if serial_open == False:
                    print("port already closed")
                else:
                    print("?? Weird serial stuff ??")
        print("app closed.")
            
    def openCommPort(self):
        global serial_open
        global baudrate
        global ser
        global ArduinoRdy
        if serial_open == False:
            self.updateTextBrowser("Opening " + self.ui.COM_Input.text() + "...")
            try:
                ser = serial.Serial(self.ui.COM_Input.text(), baudrate, timeout = 0.1)
                #print(self.ui.COM_Input.text() + " opened successfully.")
                serial_open = True
                self.reader.start()
                self.ui.ConnectedRadioButton.setChecked(True)
                self.updateTextBrowser(self.ui.COM_Input.text() + " opened successfully." +"\n Uploading initial variables...")
                try:
                    while ArduinoRdy == False:
                        time.sleep(0.2)
                        print("Arduino Not Ready")
                    self.InitialUpload()
                    self.updateTextBrowser("sucessfully uploaded initial variables.")
                except:
                    self.updateTextBrowser("unsucessful at uploading initial variables")
                
            except:
                self.updateTextBrowser("Unsuccesful at opening" + self.ui.COM_Input.text())
        else:
            self.updateTextBrowser("Serial port already open...")
    
    def closeCommPort(self):
        global serial_open
        global baudrate
        global ser
        global ArduinoRdy
        if serial_open == True:
            try:
                serial_open = False
                time.sleep(0.1)
                ser.close()
                self.ui.ConnectedRadioButton.setChecked(False)
                ArduinoRdy = False
                self.updateTextBrowser("Serial port closed.")
            except:
                self.updateTextBrowser("Issue closing port.")
    
    # def terminalPrint(self,text):
    #     self.ui.CommQTextBrowser.append(text)
    
    def InitialVariableArrayConstructor(self):
        #this function just initilizes the variable array to whatever they are set to. Will want to upload initial values to arduino probs
        varArray = [0]*self.varNum;
        #initial mode will be zero for now so no need to define
        varArray[self.flash] = self.flashInit
        varArray[self.interval] = self.intervalInit
        varArray[self.numSteps] = self.numStepsInit
        varArray[self.runsPerStep] = self.runsPerStepInit
        varArray[self.sweepUpperBound] = self.sweepUpperBoundInit
        varArray[self.sweepLowerBound] = self.sweepLowerboundInit
        varArray[self.sweepCenterFrequency] = self.sweepCenterFrequencyInit
        varArray[self.sweepRate] = self.sweepRateInit
        varArray[self.sweepSpan] = self.sweepSpanInit
        varArray[self.sweepRateStart] = self.sweepRateStartInit
        varArray[self.sweepRateStop] = self.sweepRateStopInit
        varArray[self.frequency] = self.frequencyInit
        varArray[self.outputStateSF] = self.outputStateSFInit
        varArray[self.pulseTime] = self.pulseTimeInit
        varArray[self.freqStart] = self.freqStartInit
        varArray[self.freqStop] = self.freqStopInit
        varArray[self.pulseTimeStart] = self.pulseTimeStartInit
        varArray[self.pulseTimeStop] = self.pulseTimeStopInit
        varArray[self.mode] = self.modeInit
        
        #set initial line edits to avoid empty error until I put in some safety code
        self.ui.OutputFreqQLineEdit.setText(str(MakeHumanReadable(varArray[self.frequency],self.ui.OutputFreqUnitComboBox.currentText())))
        self.ui.FreqStartQLineEdit.setText(str(MakeHumanReadable(varArray[self.freqStart],self.ui.FreqStartUnitComboBox.currentText())))
        self.ui.FreqStopQLineEdit.setText(str(MakeHumanReadable(varArray[self.freqStop],self.ui.FreqStopUnitComboBox.currentText())))
        self.ui.PulseTimeQLineEdit.setText(str(varArray[self.pulseTime]))
        self.ui.PulseTimeStartQLineEdit.setText(str(varArray[self.pulseTimeStart]))
        self.ui.PulseTimeStopQLineEdit.setText(str(varArray[self.pulseTimeStop]))
        self.ui.NumStepsQLineEdit.setText(str(varArray[self.numSteps]))
        self.ui.RunsPerStepQLineEdit.setText(str(varArray[self.runsPerStep]))
        self.ui.SweepUpperBoundQLineEdit.setText(str(MakeHumanReadable(varArray[self.sweepUpperBound],self.ui.SweepUpperBoundUnitComboBox.currentText())))
        self.ui.SweepLowerBoundQLineEdit.setText(str(MakeHumanReadable(varArray[self.sweepLowerBound],self.ui.SweepLowerBoundUnitComboBox.currentText())))
        self.ui.SweepCenterFreqQLineEdit.setText(str(MakeHumanReadable(varArray[self.sweepCenterFrequency],self.ui.SweepCenterFreqUnitComboBox.currentText())))
        self.ui.SweepRateQLineEdit.setText(str(varArray[self.sweepRate]))
        self.ui.SweepSpanQLineEdit.setText(str(MakeHumanReadable(varArray[self.sweepSpan],self.ui.SweepSpanUnitComboBox.currentText())))
        self.ui.SweepRateStartQLineEdit.setText(str(varArray[self.sweepRateStart]))
        self.ui.SweepRateStopQLineEdit.setText(str(varArray[self.sweepRateStop]))
        #print(varArray)
        return varArray
    

    def UpdateSingleLCD(self, comboBox, targetLCD, varArrayValue):
        targetLCD.display(MakeHumanReadable(varArrayValue,comboBox.currentText()))

        
    
    def UpdateVarLCDs(self):
        #print("updating LCD")
        # self.ui.OutputFreqQLCD.display(self.variableArray[self.frequency])
        # self.ui.FreqStartQLCD.display(self.variableArray[self.freqStart])
        # self.ui.FreqStopQLCD.display(self.variableArray[self.freqStop])
        # self.ui.PulseTimeQLCD.display(self.variableArray[self.pulseTime])
        # self.ui.PulseTimeStartQLCD.display(self.variableArray[self.pulseTimeStart])
        # self.ui.PulseTimeStopQLCD.display(self.variableArray[self.pulseTimeStop])
        # self.ui.NumStepsQLCD.display(self.variableArray[self.numSteps])
        # self.ui.RunsPerStepQLCD.display(self.variableArray[self.runsPerStep])
        # self.ui.SweepUpperBoundQLCD.display(self.variableArray[self.sweepUpperBound])
        # self.ui.SweepLowerBoundQLCD.display(self.variableArray[self.sweepLowerBound])
        # self.ui.SweepCenterFreqQLCD.display(self.variableArray[self.sweepCenterFrequency])
        # self.ui.SweepRateQLCD.display(self.variableArray[self.sweepRate])
        # self.ui.SweepSpanQLCD.display(self.variableArray[self.sweepSpan])
        # self.ui.SweepRateStartQLCD.display(self.variableArray[self.sweepRateStart])
        self.ui.OutputFreqQLCD.display(MakeHumanReadable(self.variableArray[self.frequency],self.ui.OutputFreqUnitComboBox.currentText()))
        self.ui.FreqStartQLCD.display(MakeHumanReadable(self.variableArray[self.freqStart],self.ui.FreqStartUnitComboBox.currentText()))
        self.ui.FreqStopQLCD.display(MakeHumanReadable(self.variableArray[self.freqStop],self.ui.FreqStopUnitComboBox.currentText()))
        self.ui.PulseTimeQLCD.display(self.variableArray[self.pulseTime])
        self.ui.PulseTimeStartQLCD.display(self.variableArray[self.pulseTimeStart])
        self.ui.PulseTimeStopQLCD.display(self.variableArray[self.pulseTimeStop])
        self.ui.NumStepsQLCD.display(self.variableArray[self.numSteps])
        self.ui.RunsPerStepQLCD.display(self.variableArray[self.runsPerStep])
        self.ui.SweepUpperBoundQLCD.display(MakeHumanReadable(self.variableArray[self.sweepUpperBound],self.ui.SweepUpperBoundUnitComboBox.currentText()))
        self.ui.SweepLowerBoundQLCD.display(MakeHumanReadable(self.variableArray[self.sweepLowerBound],self.ui.SweepLowerBoundUnitComboBox.currentText()))
        self.ui.SweepCenterFreqQLCD.display(MakeHumanReadable(self.variableArray[self.sweepCenterFrequency],self.ui.SweepCenterFreqUnitComboBox.currentText()))
        self.ui.SweepRateQLCD.display(self.variableArray[self.sweepRate])
        self.ui.SweepSpanQLCD.display(MakeHumanReadable(self.variableArray[self.sweepSpan],self.ui.SweepSpanUnitComboBox.currentText()))
        self.ui.SweepRateStartQLCD.display(self.variableArray[self.sweepRateStart])
        self.ui.SweepRateStopQLCD.display(self.variableArray[self.sweepRateStop])
        
    def modeSelectResult(self):
        if(self.ui.ModeSelectDropDown.currentText() == "Single Frequency"):
            self.updateTextBrowser("Single Frequency mode selected.")
            return self.mode_SingleFrequency
        
        elif(self.ui.ModeSelectDropDown.currentText() == "Spectroscopy"):
            self.updateTextBrowser("Spectroscopy mode seleceted.")
            return self.mode_Spectroscopy
        
        elif(self.ui.ModeSelectDropDown.currentText() == "Rabi Scan"):
            self.updateTextBrowser("Rabi scan mode selected.")
            return self.mode_RabiScan
        
        elif(self.ui.ModeSelectDropDown.currentText() == "Frequency Sweep Scan"):
            self.updateTextBrowser("Frequency sweep scan mode selected.")
            return self.mode_SweepScan
        
        else:
            self.updateTextBrowser("Mode selection not found.. make sure code includes any new drop down selections added..")
            self.updateTextBrowser("Will keep current mode.")
            return self.variableArray[self.mode]
    
    def HumanVarInputConvert(self, valueTxt, unitTxt = "Hz"):
        #default value is "Hz" i.e. a multiplier of 1.
        temp = valueTxt.split(".")
        if len(temp) > 2:
            self.updateTextBrowser("Too many decimals, ignoring everything after 2nd decimal.")
        if unitTxt == "MHz":
            unit = 1000000
        elif unitTxt == "kHz":
            unit = 1000
        elif unitTxt == "Hz":
            unit = 1
        
        #calculate number in front of decimal
        b4dec = int(temp[0]) * unit
        
        #calculate number after decimal
        afterdec=0
        #min function here protects against a super long number after the dec
        if len(temp)>1:
            for i in range(0, min(len(temp[1]),10)):
                multiplier = int(unit/(10**(i+1))) #int here ensures that the value added will be zero if it is less than 1. 
                afterdec += int(temp[1][i])*multiplier
        
        totVal = b4dec + afterdec
        
        return totVal
    
    def updateVarTempArray(self, currentArray):
        #takes each of the input QlineEdits and puts into temp array
        #need to put in mode stuff
        try:
            tempArray = [0]*self.varNum
            #print(self.ui.ModeSelectDropDown.currentText())
            newMode = self.modeSelectResult()
            tempArray[self.mode] = newMode
            tempArray[self.frequency] = self.HumanVarInputConvert(self.ui.OutputFreqQLineEdit.text(),self.ui.OutputFreqUnitComboBox.currentText())#int(self.ui.OutputFreqQLineEdit.text())
            tempArray[self.freqStart] = self.HumanVarInputConvert(self.ui.FreqStartQLineEdit.text(),self.ui.FreqStartUnitComboBox.currentText())
            tempArray[self.freqStop] = self.HumanVarInputConvert(self.ui.FreqStopQLineEdit.text(),self.ui.FreqStopUnitComboBox.currentText())
            tempArray[self.pulseTime] = self.HumanVarInputConvert(self.ui.PulseTimeQLineEdit.text())
            tempArray[self.pulseTimeStart] = self.HumanVarInputConvert(self.ui.PulseTimeStartQLineEdit.text())
            tempArray[self.pulseTimeStop] = self.HumanVarInputConvert(self.ui.PulseTimeStopQLineEdit.text())
            tempArray[self.numSteps] = self.HumanVarInputConvert(self.ui.NumStepsQLineEdit.text())
            tempArray[self.runsPerStep] = self.HumanVarInputConvert(self.ui.RunsPerStepQLineEdit.text())
            tempArray[self.sweepUpperBound] = self.HumanVarInputConvert(self.ui.SweepUpperBoundQLineEdit.text(),self.ui.SweepUpperBoundUnitComboBox.currentText())
            tempArray[self.sweepLowerBound] = self.HumanVarInputConvert(self.ui.SweepLowerBoundQLineEdit.text(),self.ui.SweepLowerBoundUnitComboBox.currentText())
            tempArray[self.sweepCenterFrequency] = self.HumanVarInputConvert(self.ui.SweepCenterFreqQLineEdit.text(),self.ui.SweepCenterFreqUnitComboBox.currentText())
            tempArray[self.sweepRate] = self.HumanVarInputConvert(self.ui.SweepRateQLineEdit.text())
            tempArray[self.sweepSpan] = self.HumanVarInputConvert(self.ui.SweepSpanQLineEdit.text(),self.ui.SweepSpanUnitComboBox.currentText())
            tempArray[self.sweepRateStart] = self.HumanVarInputConvert(self.ui.SweepRateStartQLineEdit.text())
            tempArray[self.sweepRateStop] = self.HumanVarInputConvert(self.ui.SweepRateStopQLineEdit.text())
            tempArray[self.outputStateSF] = int(self.ui.OutputONCheckbox.isChecked()) #just for now need to put a button in.
            tempArray[self.interval] = int(110)
        except ValueError:
            #if someone put in a bad value it will just return the current array. This will make it so it does nothing later.
            self.updateTextBrowser("Looks like you put in a string instead of a number")
            return currentArray
        
        
        return tempArray
    
    # def putMsgInFromArduinoQueue(self, msg):
    #     print("putting" + str(msg) + "into queue")
    #     self.fromArduinoQueue.put(msg)
    
    def updateArduino(self):
        global serial_open
        global ser
        global ArduinoQueue
        if serial_open == True:
            tempArray = self.updateVarTempArray(self.variableArray)
            for i in range(self.varNum):
                #check if variable has been changed
                responseRcvd = False
                if tempArray[i] != self.variableArray[i]:
                    print("i = " + str(i))
                    #if mode change do this - need to write code
                    if i == self.mode:
                        #need to send command byte for mode change, and mode to change to
                        print("uploading mode change")
                        msgArray = bytearray(self.modechange.to_bytes(1,'big')) + bytearray(tempArray[i].to_bytes(1,'big'))
                        sent = sendToArduino2(msgArray,ser)
                        if sent == False:
                             self.updateTextBrowser("issue updating variable, see python terminal")
                             return
                        #wait for reply from arduino before continuing
                        #responseRcvd = False
                        while responseRcvd == False:
                            #check if queue has an item in it
                            if ArduinoQueue.empty() == False:
                                #read msg from queue
                                msgFromArduino = ArduinoQueue.get()
                                #print(msgFromArduino)
                                #compare to msg sent
                                if(msgFromArduino[1:] == msgArray):
                                    responseRcvd = True
                                    #update current value to match uploaded value
                                    self.variableArray[i]=tempArray[i]
                                    print("response recieved")
                    #only other option is a variable change:
                    else:
                        #need to send command byte for variable change, index of variable to change, and new value
                        try:
                            msgArray = bytearray(self.varchange.to_bytes(1,'big')) + bytearray(i.to_bytes(1,'big')) + bytearray(tempArray[i].to_bytes(4,'big'))
                        except OverflowError:
                            print("value too big to send to arduino")
                            self.updateTextBrowser("value too big to send to arduino")
                            return
                        print("uploading var change")
                        sent = sendToArduino2(msgArray,ser)
                        if sent == False:
                             self.updateTextBrowser("issue updating variable, see python terminal")
                             return
                        #wait for reply from arduino before continuing
                        #responseRcvd = False
                        while responseRcvd == False:
                            #check if queue has an item in it
                            if ArduinoQueue.empty() == False:
                                #read msg from queue
                                msgFromArduino = ArduinoQueue.get()
                                #print(msgFromArduino)
                                #compare to msg sent
                                if(msgFromArduino[1:] == msgArray):
                                    responseRcvd = True
                                    #update current value to match uploaded value
                                    self.variableArray[i]=tempArray[i]
                                    print("response recieved")
                                    
                            else:
                                print("no message")
                                time.sleep(.1)
            self.UpdateVarLCDs()
                                    #may need to add a timeout feature in this in the future to try to resend the data. or we get stuck here forever!
                                    #need to test what is there for now though.
                                
    def InitialUpload(self):
        global serial_open
        global ser
        global ArduinoQueue
        if serial_open == True:
            tempArray = self.variableArray
            for i in range(self.varNum):
                #check if variable has been changed
                responseRcvd = False
                #print("i = " + str(i))
                #if mode change do this - need to write code
                if i == self.mode:
                    #need to send command byte for mode change, and mode to change to
                    #print("uploading mode change")
                    msgArray = bytearray(self.modechange.to_bytes(1,'big')) + bytearray(tempArray[i].to_bytes(1,'big'))
                    sent = sendToArduino2(msgArray,ser)
                    if sent == False:
                         self.updateTextBrowser("issue updating variable, see python terminal")
                         return
                    #wait for reply from arduino before continuing
                    #responseRcvd = False
                    while responseRcvd == False:
                        #check if queue has an item in it
                        if ArduinoQueue.empty() == False:
                            #read msg from queue
                            msgFromArduino = ArduinoQueue.get()
                            #print(msgFromArduino)
                            #compare to msg sent
                            if(msgFromArduino[1:] == msgArray):
                                responseRcvd = True
                                #update current value to match uploaded value
                                self.variableArray[i]=tempArray[i]
                                #print("response recieved")
                #only other option is a variable change:
                else:
                    #need to send command byte for variable change, index of variable to change, and new value
                    try:
                        msgArray = bytearray(self.varchange.to_bytes(1,'big')) + bytearray(i.to_bytes(1,'big')) + bytearray(tempArray[i].to_bytes(4,'big'))
                    except OverflowError:
                        print("value too big to send to arduino")
                        self.updateTextBrowser("value too big to send to arduino")
                        return
                    #print("uploading var change")
                    sent = sendToArduino2(msgArray,ser)
                    if sent == False:
                         self.updateTextBrowser("issue updating variable, see python terminal")
                         return
                    #wait for reply from arduino before continuing
                    #responseRcvd = False
                    while responseRcvd == False:
                        #check if queue has an item in it
                        if ArduinoQueue.empty() == False:
                            #read msg from queue
                            msgFromArduino = ArduinoQueue.get()
                            #print(msgFromArduino)
                            #compare to msg sent
                            if(msgFromArduino[1:] == msgArray):
                                responseRcvd = True
                                #update current value to match uploaded value
                                self.variableArray[i]=tempArray[i]
                                #print("response recieved")
                                
                        else:
                            #print("no message")
                            time.sleep(.1)
                                #may need to add a timeout feature in this in the future to try to resend the data. or we get stuck here forever!
                                #need to test what is there for now though.
        self.UpdateVarLCDs()
                
                
            
    
        
        
class comRead(QThread):
    global startMarkerByte, endMarkerByte, serial_open, ser, ArduinoQueue
    
    global ArduinoRdy
    
    outputTxt = Signal(str)
    
    encodedMsg = Signal(bytearray)
    
    
    def __init__(self):
        QThread.__init__(self)
        self.keepgoing = False
        
    def run(self):
        global ArduinoRdy
        self.keepgoing = True
        while self.keepgoing == True:
            # self.outputTxt.emit(readMessageThread())
            # time.sleep(0.1)
            # self.outputTxt.emit("test")
            if serial_open:
                if ser.in_waiting > 0:
                    ck = bytearray()
                    x = "z" #just needs to be not the start marker
                    byteCount = -1 #last increment will be one too many
                    #here we read in bytes, without saving, until we read a start marker 
                    #may want to program in a shorter timeout, 
                    msg = ""; #adding in ability to read in things that don't have start and end marker bytes. and print any messages read.
                    while x != startMarkerByte:
                        if (serial_open == False or self.keepgoing == False):
                            return
                        #look at waitforarduino code to read text messages.
                        x=ser.read();
                        if(x == b"\n" or x == startMarkerByte):
                            if (msg == "" or msg == " "):
                                pass
                            else:
                                #print("Nonencoded message:")
                                #print(msg);
                                self.outputTxt.emit(msg)
                                msg = "";
                        msg = msg + x.decode('cp437');
                        
                    x = ser.read()
                    #once a start marker is read in, we keep reading in bytes and adding to
                    #the temporary list ck
                    while x != endMarkerByte:
                        ck += bytearray(x)
                        x = ser.read()
                        byteCount += 1
        
                    #ck += bytearray(x)
                    msgarray = decodeHighBytes(ck)
                    #print(msgarray)
                    cmnd = msgarray[1]
                    #print("cmnd is: " + str(cmnd))
                    if (cmnd == 1 or cmnd == 2):
                        #print("is a command")
                        #self.encodedMsg.emit(msgarray)
                        ArduinoQueue.put(msgarray)
                    else:
                        if (ArduinoRdy == False):
                            if msgarray[1:].decode()=="Arduino Ready":
                                ArduinoRdy = True
                                print("Arduino Ready message recieved")
                        #print("not a command")
                        self.outputTxt.emit(str(msgarray))
                #This statement keeps this thread from eating up CPU when there is no message to be read.
                else:
                    if ArduinoRdy == True:
                        #print("in slow sleep")
                        time.sleep(0.1)
                    else:
                        #print("in fast sleep")
                        time.sleep(0.1)
            
            elif serial_open == False:
                self.keepgoing = False
            

                

    def stop(self):
        self.keepgoing = False
    
def MakeHumanReadable(val, unitSelect = "Hz"):
    if unitSelect == "Hz":
        outputVal = val
        return outputVal
    if unitSelect == "kHz":
        outputVal = val/1000
        return outputVal
    if unitSelect == "MHz":
        outputVal = val/1000000
        return outputVal

ArduinoQueue=queue.Queue()

if __name__ == "__main__":
    #temporary
    baudrate = 115200;
    serial_open = False
    ArduinoRdy = False
    app = QApplication.instance()
    if app is None:
        # Create the Qt Application if it doesn't exist
        app = QApplication(sys.argv)
    app.setWindowIcon(QtGui.QIcon('ion.jpg'))
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
    