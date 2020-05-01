# -*- coding: utf-8 -*-
"""
Created on Thu Apr 16 11:37:10 2020

@author: hanne
"""


#======================================

def displayDebug(debugStr):

   n = len(debugStr) - 3
   print("DEBUG MSG-> " + debugStr[2: -1])


#============================

def waitForArduino():

   # wait until the Arduino sends 'Arduino Ready' - allows time for Arduino reset
   # it also ensures that any bytes left over from a previous message are discarded
   
    global endMarker
    
    msg = ""
    while msg.find("Arduino Ready") == -1:

      while ser.inWaiting() == 0:
        x = 'z'

      # then wait until an end marker is received from the Arduino to make sure it is ready to proceed
      x = "z"
      while ord(x) != endMarker: # gets the initial debugMessage
        x = ser.read()
        msg = msg + x.decode('cp437')


      displayDebug(msg)
      print()
      

#=====================================
def recvFromArduino():
    global startMarkerByte, endMarkerByte
    
    ck = bytearray()
    x = "z" #just needs to be not the start marker
    byteCount = -1 #last increment will be one too many
    #here we read in bytes, without saving, until we read a start marker 
    #may want to program in a shorter timeout, 
    msg = ""; #adding in ability to read in things that don't have start and end marker bytes. and print any messages read.
    while x != startMarkerByte:
        #look at waitforarduino code to read text messages.
        x=ser.read();
        if(x == b"\n" or x == startMarkerByte):
            #print("Nonencoded message:")
            print(msg);
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
    return msgarray
    

    
#=======================================

def decodeHighBytes(barray):
    global specialByte
    global startMarkerByte
    global endMarkerByte
    global specialMarker
    outarray = bytearray()
    n = 0
     
    while n < len(barray):
        if barray[n] == specialMarker:
            n+=1
            if barray[n] == 0:
                x = specialByte
            if barray[n] == 1:
                x = startMarkerByte
            if barray[n] == 2:
                x = endMarkerByte
        else:
            x = barray[n].to_bytes(1,'big')
        outarray += bytearray(x)
        n += 1
    #print(outarray)
    return(outarray)


#======================================

def encodeHighBytes(barray):
    global specialByte
    global startMarkerByte
    global endMarkerByte
    global specialMarker
    
    outarray = bytearray()
    
    for n in barray:
        if n >= specialMarker:
            outarray += bytearray(specialByte)
            outarray += bytearray((n-specialMarker).to_bytes(1,'big'))
        else:
            outarray += bytearray(n.to_bytes(1,'big'))
                        
    return outarray
#======================================

def sendToArduino(inputarray):
    global specialByte
    global startMarkerByte
    global endMarkerByte
    # print("inside sendToArduino")
    # print(inputarray)
    if type(inputarray) == str:
        print("sending str")
        temparray = bytearray(inputarray, 'UTF-8')
        if len(temparray) < 64:
            ser.write(startMarkerByte)
            ser.write(len(temparray).to_bytes(1,'big'))
            ser.write(temparray)
            ser.write(endMarkerByte)
        else:
            print("Message length of", end ='')
            print(len(temparray), end = '')
            print('bytes is too long. Reduce to 63 bytes.')
    elif type(inputarray) == bytearray:
        # print("sending bytearray")
        temparray = encodeHighBytes(inputarray)
        # print("temp array:")
        # print(temparray)
        # print("length")
        # print(len(temparray).to_bytes(1,'big'))
        if len(temparray) < 33:
            ser.write(startMarkerByte)
            ser.write((len(temparray)+1).to_bytes(1,'big'))
            ser.write(temparray)
            # print("sent")
            # print(temparray)
            ser.write(endMarkerByte)
        else:
            print("Message length of", end ='')
            print(len(temparray), end = '')
            print('bytes is too long. Reduce to 32 bytes.')
            
    else:
        print("Invalid input type. Must be string or bytearray.")
        
def sendToArduino2(inputarray,ser):
    global specialByte
    global startMarkerByte
    global endMarkerByte
    sent = False
    # print("inside sendToArduino")
    # print(inputarray)
    if type(inputarray) == str:
        print("sending str")
        temparray = bytearray(inputarray, 'UTF-8')
        if len(temparray) < 64:
            ser.write(startMarkerByte)
            ser.write(len(temparray).to_bytes(1,'big'))
            ser.write(temparray)
            ser.write(endMarkerByte)
            sent = True
            return sent
        else:
            print("Message length of", end ='')
            print(len(temparray), end = '')
            print('bytes is too long. Reduce to 63 bytes.')
            sent = False
            return sent
    elif type(inputarray) == bytearray:
        # print("sending bytearray")
        temparray = encodeHighBytes(inputarray)
        # print("temp array:")
        # print(temparray)
        # print("length")
        # print(len(temparray).to_bytes(1,'big'))
        if len(temparray) < 33:
            ser.write(startMarkerByte)
            ser.write((len(temparray)+1).to_bytes(1,'big'))
            ser.write(temparray)
            # print("sent")
            # print(temparray)
            ser.write(endMarkerByte)
            sent = True
            return sent
        else:
            print("Message length of", end ='')
            print(len(temparray), end = '')
            print('bytes is too long. Reduce to 32 bytes.')
            sent = False
            return sent
            
    else:
        print("Invalid input type. Must be string or bytearray.")
        sent = False
        return sent

#======================================
#"enter commmand: 1 for mode change, 2 for variable change. \n"
def getAndSendTestMessage():

    ##########################################################
    #!!!!!These need to match pythonArduinoComm.cpp!!!!!!!!!!
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
    message = bytearray();
    command = int(input("enter 1 to change mode, 2 to change variables:"));
    if command == 1:
        mode = int(input("enter mode to switch to: \n"));
        message = bytearray(command.to_bytes(1,'big')) + bytearray(mode.to_bytes(1,'big'));
    elif command == 2:
        print("Variable Addresses:");
        print("---------Variables for Testing----------");
        print("flash - ", flash);
        print("interval - ", interval);
        print("----------------------------------------");
        print("");
        print("-------------Globaly useful variables--------------");
        print("num steps - ", numSteps);
        print("runs per step - ", runsPerStep);
        print("-------------------------------------------------");
        print("");
        print("--------------Frequency Sweep Variables------------");
        print("sweep upper bound - ", sweepUpperBound);
        print("sweep lower bound - ", sweepLowerBound);
        print("sweep center frequency - ", sweepCenterFrequency);
        print("sweep rate (non-scan mode) - ", sweepRate);
        print("sweep span - ", sweepSpan);
        print("--------------Frequency Sweep Scan Variables-------");
        print("sweep rate scan start - ", sweepRateStart);
        print("sweep rate scan stop - ", sweepRateStop);
        print("----------------------------------------------------");
        print("");
        print("--------------------Single Frequency Mode-----------------");
        print("AOM frequency, Single frequency mode- ", frequency);
        print("AOM output state - ", outputStateSF);
        print("-----------------------------------------------------------");
        print("");
        print("-------------------Spectroscopy Mode---------------------");
        print("Spectroscopy pulse time - ", pulseTime);
        print("Spectroscopy start frequency - ", freqStart);
        print("Spectroscopy stop frequency - ", freqStop);
        print("-----------------------------------------------------------");
        print("");
        print("-------------------Rabi Flopping Mode----------------------");
        print("Rabi flop initial pulse time - ", pulseTimeStart);
        print("Rabi flop final pulse time - ", pulseTimeStop);
        print("-------------------------------------------------------------");
        
        
        varToChange = int(input("enter the variable you wish to change."));
        print("input recieved")
        print(varToChange)
        if varToChange == flash:
            newVarValue = int(input("enter 0 for no flash, 1 for flashing: "));
        elif varToChange == interval:
            newVarValue = int(input("enter flash rate in units of 10s of ms: "));
        elif varToChange == numSteps:
            newVarValue = int(input("enter number of steps: "));
        elif varToChange == runsPerStep:
            newVarValue = int(input("enter number of runs per step:"));
        elif varToChange == sweepUpperBound:
            newVarValue = int(input("enter absolute upper bound of sweep: "));
        elif varToChange == sweepLowerBound:
            newVarValue = int(input("enter absolute lower bound of sweep: "));
        elif varToChange == sweepCenterFrequency:
            newVarValue = int(input("enter sweep center frequency: "));
        elif varToChange == sweepRate:
            newVarValue = int(input("enter sweep rate: "));
        elif varToChange == sweepSpan:
            newVarValue = int(input("enter sweep span: "));
        elif varToChange == sweepRateStart:
            newVarValue = int(input("enter starting sweep rate: "));
        elif varToChange == sweepRateStop:
            newVarValue = int(input("enter ending sweep rate: "));
        elif varToChange == frequency:
            newVarValue = int(input("enter AOM frequency: "));
        elif varToChange == outputStateSF:
            onoff = int(input("enter 0 for AOM on or 1 for AOM off (single freq mode only): "));
            if (onoff > 0):
                newVarValue = 1;
            else:
                newVarValue = 0;
        elif varToChange == pulseTime:
            newVarValue = int(input("enter 1762 pulse duration: "));
        elif varToChange == freqStart:
            newVarValue = int(input("enter spectroscopy starting frequency: "));
        elif varToChange == freqStop:
            newVarValue = int(input("enter spectroscopy ending frequency: "));
        elif varToChange == pulseTimeStart:
            newVarValue = int(input("enter rabi flopping starting pulse duration: "));
        elif varToChange == pulseTimeStop:
            newVarValue = int(input("enter rabi flopping ending pulse duration: "));
        else:
            print("invalid value.")
            varToChange = 0;#0 should do nothing to the adrunio program.. default assignment.
            newVarValue = 0;
            
        message = bytearray(command.to_bytes(1,'big')) + bytearray(varToChange.to_bytes(1,'big')) + bytearray(newVarValue.to_bytes(4,'big'));
    print("")
    print("Sending the following message:")
    print(message);      
    sendToArduino(message);


#=====================================
def readMessageThread():
    global msgPresent;
    while True:
        if ser.in_waiting > 0:    
            msgarray = recvFromArduino()
            print("recieved coded message: ")
            print(msgarray)
            msgPresent = True;
            return msgarray





#=====================================
import serial
import time
import sys
import threading

startMarker = 254;
endMarker = 255;
specialMarker = 253;
specialByte = specialMarker.to_bytes(1,'big')
startMarkerByte = startMarker.to_bytes(1,'big')
endMarkerByte = endMarker.to_bytes(1,'big')
baudrate = 115200;
COMPORT = 'COM3';
    
# ser = serial.Serial(COMPORT, baudrate,  timeout = 1)

if __name__ == "__main__":
    COMPORT = 'COM3';
    
    ser = serial.Serial(COMPORT, baudrate,  timeout = 1)
    
    
    startMarker = 254;
    endMarker = 255;
    specialMarker = 253;
    specialByte = specialMarker.to_bytes(1,'big')
    startMarkerByte = startMarker.to_bytes(1,'big')
    endMarkerByte = endMarker.to_bytes(1,'big')
    
    
    waitForArduino()
    #time.sleep(1)
    
    
    try:
        msgPresent = False;
        msgreadthread = threading.Thread(target = readMessageThread);
        msgreadthread.start();
        getAndSendTestMessage();
        while True:
            # msgPresent = False
            # if ser.in_waiting > 0:    
            #     msgarray = recvFromArduino()
            #     print("recieved message: ")
            #     print(msgarray)
            #     msgPresent = True;
            try:
                # time.sleep(0.0001);
                if msgPresent == True:
                    msgPresent = False;
                    getAndSendTestMessage();
                    print("hit ctr-c to send a message")
            except KeyboardInterrupt:
                print("keyboard interrupt")
                # if msgPresent == True:
                #     msgPresent = False;
                #     getAndSendTestMessage();
                #     print("hit ctr-c to send a message")
                
    except KeyboardInterrupt:
        ser.close()
        print("keyboard interrupt")
                
    except:
        ser.close()
        print("exiting")
    
    ser.close()
    sys.exit()