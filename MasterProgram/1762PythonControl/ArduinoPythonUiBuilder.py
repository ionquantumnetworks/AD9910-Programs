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
import queue


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
        
        # self.fromArduinoQueue = queue.Queue()
        
        self.variableArray = self.InitialVariableArrayConstructor()
        self.UpdateVarLCDs()
        
        self.ui.UploadButton.clicked.connect(self.updateArduino)
        self.ui.ConnectButton.clicked.connect(self.openCommPort)
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
            self.ui.CommQTextBrowser.append(tempmsg)
        elif type(msg)==str:    
            self.ui.CommQTextBrowser.append(str(msg))
        # print("msg start 1")
        # print(msg)
        # print("msg stop 1")
        
    def closeEvent(self, event):
        global ser
        global serial_open
        print("closing app")
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
            
    def openCommPort(self):
        global serial_open
        global baudrate
        global ser
        if serial_open == False:
            self.updateTextBrowser("Opening " + self.ui.COM_Input.text() + "...")
            try:
                ser = serial.Serial(self.ui.COM_Input.text(), baudrate, timeout = 0.1)
                #print(self.ui.COM_Input.text() + " opened successfully.")
                serial_open = True
                self.reader.start()
                self.ui.ConnectedRadioButton.setChecked(True)
                self.updateTextBrowser(self.ui.COM_Input.text() + " opened successfully.")
            except:
                self.updateTextBrowser("Unsuccesful at opening" + self.ui.COM_Input.text())
        else:
            self.updateTextBrowser("Serial port already open...")
    
    def closeCommPort(self):
        global serial_open
        global baudrate
        global ser
        if serial_open == True:
            try:
                serial_open = False
                time.sleep(0.1)
                ser.close()
                self.ui.ConnectedRadioButton.setChecked(False)
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
        
        #set initial line edits to avoid empty error until I put in some safety code
        self.ui.OutputFreqQLineEdit.setText(str(varArray[self.frequency]))
        self.ui.FreqStartQLineEdit.setText(str(varArray[self.freqStart]))
        self.ui.FreqStopQLineEdit.setText(str(varArray[self.freqStop]))
        self.ui.PulseTimeQLineEdit.setText(str(varArray[self.pulseTime]))
        self.ui.PulseTimeStartQLineEdit.setText(str(varArray[self.pulseTimeStart]))
        self.ui.PulseTimeStopQLineEdit.setText(str(varArray[self.pulseTimeStop]))
        self.ui.NumStepsQLineEdit.setText(str(varArray[self.numSteps]))
        self.ui.RunsPerStepQLineEdit.setText(str(varArray[self.runsPerStep]))
        self.ui.SweepUpperBoundQLineEdit.setText(str(varArray[self.sweepUpperBound]))
        self.ui.SweepLowerBoundQLineEdit.setText(str(varArray[self.sweepLowerBound]))
        self.ui.SweepCenterFreqQLineEdit.setText(str(varArray[self.sweepCenterFrequency]))
        self.ui.SweepRateQLineEdit.setText(str(varArray[self.sweepRate]))
        self.ui.SweepSpanQLineEdit.setText(str(varArray[self.sweepSpan]))
        self.ui.SweepRateStartQLineEdit.setText(str(varArray[self.sweepRateStart]))
        self.ui.SweepRateStopQLineEdit.setText(str(varArray[self.sweepRateStop]))
        #print(varArray)
        return varArray
                 
    def UpdateVarLCDs(self):
        #print("updating LCD")
        self.ui.OutputFreqQLCD.display(self.variableArray[self.frequency])
        self.ui.FreqStartQLCD.display(self.variableArray[self.freqStart])
        self.ui.FreqStopQLCD.display(self.variableArray[self.freqStop])
        self.ui.PulseTimeQLCD.display(self.variableArray[self.pulseTime])
        self.ui.PulseTimeStartQLCD.display(self.variableArray[self.pulseTimeStart])
        self.ui.PulseTimeStopQLCD.display(self.variableArray[self.pulseTimeStop])
        self.ui.NumStepsQLCD.display(self.variableArray[self.numSteps])
        self.ui.RunsPerStepQLCD.display(self.variableArray[self.runsPerStep])
        self.ui.SweepUpperBoundQLCD.display(self.variableArray[self.sweepUpperBound])
        self.ui.SweepLowerBoundQLCD.display(self.variableArray[self.sweepLowerBound])
        self.ui.SweepCenterFreqQLCD.display(self.variableArray[self.sweepCenterFrequency])
        self.ui.SweepRateQLCD.display(self.variableArray[self.sweepRate])
        self.ui.SweepSpanQLCD.display(self.variableArray[self.sweepSpan])
        self.ui.SweepRateStartQLCD.display(self.variableArray[self.sweepRateStart])
        self.ui.SweepRateStopQLCD.display(self.variableArray[self.sweepRateStop])
        
    def updateVarTempArray(self, currentArray):
        #takes eahc of the input QlineEdits and puts into temp array
        #need to put in mode stuff
        try:
            tempArray = [0]*self.varNum
            tempArray[self.mode] = 2
            tempArray[self.frequency] = int(self.ui.OutputFreqQLineEdit.text())
            tempArray[self.freqStart] = int(self.ui.FreqStartQLineEdit.text())
            tempArray[self.freqStop] = int(self.ui.FreqStopQLineEdit.text())
            tempArray[self.pulseTime] = int(self.ui.PulseTimeQLineEdit.text())
            tempArray[self.pulseTimeStart] = int(self.ui.PulseTimeStartQLineEdit.text())
            tempArray[self.pulseTimeStop] = int(self.ui.PulseTimeStopQLineEdit.text())
            tempArray[self.numSteps] = int(self.ui.NumStepsQLineEdit.text())
            tempArray[self.runsPerStep] = int(self.ui.RunsPerStepQLineEdit.text())
            tempArray[self.sweepUpperBound] = int(self.ui.SweepUpperBoundQLineEdit.text())
            tempArray[self.sweepLowerBound] = int(self.ui.SweepLowerBoundQLineEdit.text())
            tempArray[self.sweepCenterFrequency] = int(self.ui.SweepCenterFreqQLineEdit.text())
            tempArray[self.sweepRate] = int(self.ui.SweepRateQLineEdit.text())
            tempArray[self.sweepSpan] = int(self.ui.SweepSpanQLineEdit.text())
            tempArray[self.sweepRateStart] = int(self.ui.SweepRateStartQLineEdit.text())
            tempArray[self.sweepRateStop] = int(self.ui.SweepRateStopQLineEdit.text())
            tempArray[self.outputStateSF] = int(False) #just for now need to put a button in.
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
                                    #may need to add a timeout feature in this in the future to try to resend the data. or we get stuck here forever!
                                    #need to test what is there for now though.
                                
                    
                
                
            
# class comQueueAdd(QThread):
    
#     def __init__(self, value, target):
#         QTread.__init__(self)
#         self.value = value
#         self.target = target
#         self.responseRcvd = False
        
#     def run(self):
#         while responseRcvd == False:
            
#     @QtCore.Slot(object)
#     def putMsgInFromArduinoQueue(self,target,value):
#         print("putting" + str(value) + "into queue")
#         self.target.put(value)
    
        
        
class comRead(QThread):
    global startMarkerByte, endMarkerByte, serial_open, ser, ArduinoQueue
    
    outputTxt = Signal(str)
    
    encodedMsg = Signal(bytearray)
    
    
    def __init__(self):
        QThread.__init__(self)
        self.keepgoing = False
        
    def run(self):
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
                            #print("Nonencoded message:")
                            print(msg);
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
                    print(msgarray)
                    cmnd = msgarray[1]
                    print("cmnd is: " + str(cmnd))
                    if (cmnd == 1 or cmnd == 2):
                        print("is a command")
                        self.encodedMsg.emit(msgarray)
                        ArduinoQueue.put(msgarray)
                    else:
                        print("not a command")
                        self.outputTxt.emit(str(msgarray))
                        
            time.sleep(0.1)

    def stop(self):
        self.keepgoing = False
    


# class VariableRegisterArray():
#     global startMarkerByte, endMarkerByte, serial_open, ser
    
    
#     def __init__():
#         #mode selection
#         self.mode = 1;
        
#         #for testing communicaiton
#         self.flash = 0;
#         self.interval = 1;
        
#         #common paramters for all scans
#         self.numSteps = 10;
#         self.runsPerStep = 10;
        
#         #frequency sweep parameters
#         self.sweepUpperBound = 41000000;
#         self.sweepLowerbound = 39000000;
#         self.sweepCenterFrequency = 40000000;
#         self.sweepRate = 100000000;
#         self.sweepSpan = 1000000;
#         #frequency sweep scan specific paramters
#         self.sweepRateStart = 100000000;
#         self.sweepRateStop = 1000000000;        
        
#         #single frequency mode
#         self.frequency = 40000000;
#         self.outputStateSF = False;
       
#         #single frequency spectroscopy paramters
#         self.pulseTime = 1000; #microseconds of delay
#         self.freqStart = 39000000;
#         self.freqStop = 41000000;
        
#         #Rabi Flopping Paramters
#         self.pulseTimeStart = 10; #microseconds of delay
#         self.pulseTimeStop = 100; #microseconds of delay

ArduinoQueue=queue.Queue()

if __name__ == "__main__":
    #temporary
    baudrate = 115200;
    serial_open = False
    
    app = QApplication.instance()
    if app is None:
        # Create the Qt Application if it doesn't exist
        app = QApplication(sys.argv)
        
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
    