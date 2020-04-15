# -*- coding: utf-8 -*-
"""
Created on Fri Apr 10 16:10:15 2020

@author: John Hannegan
Based on code by 
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
    byteCount = -1 #last increment will be one to many
    #here we read in bytes, without saving, until we read a start marker 
    #may want to program in a shorter timeout, 
    while x != startMarkerByte:
        x=ser.read()
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
        if len(temparray) < 64:
            ser.write(startMarkerByte)
            ser.write((len(temparray)+1).to_bytes(1,'big'))
            ser.write(temparray)
            # print("sent")
            # print(temparray)
            ser.write(endMarkerByte)
        else:
            print("Message length of", end ='')
            print(len(temparray), end = '')
            print('bytes is too long. Reduce to 63 bytes.')
            
    else:
        print("Invalid input type. Must be string or bytearray.")

#======================================
      
import serial
import time
import sys

baudrate = 9600;
COMPORT = 'COM3';

ser = serial.Serial(COMPORT, baudrate,  timeout = 1)


startMarker = 254;
endMarker = 255;
specialMarker = 253;
specialByte = specialMarker.to_bytes(1,'big')
startMarkerByte = startMarker.to_bytes(1,'big')
endMarkerByte = endMarker.to_bytes(1,'big')

# message = "Put your message here."
# messageByteArray = bytearray(message, 'UTF-8')
# messageByteArray2 = bytearray('I am a string with this character:', 'UTF-8')
# messageByteArray2 += bytearray((255).to_bytes(1,'big'))


waitForArduino()
#time.sleep(1)
# ser.write(startMarkerByte)
# ser.write((len(messageByteArray)).to_bytes(1,'big'))
# ser.write(messageByteArray)
# ser.write(endMarkerByte)

# ser.write(startMarkerByte)
# ser.write((len(messageByteArray2)).to_bytes(1,'big'))
# ser.write(messageByteArray2)
# ser.write(endMarkerByte)
#sendToArduino(messageByteArray2)
# messageByteArray3 = bytearray((1).to_bytes(1,'big')) + bytearray((0).to_bytes(1,'big')) + bytearray((5).to_bytes(1,'big'))
# print(messageByteArray3)
# sendToArduino(messageByteArray3)

try:
    # mode = int(input("mode:"));
    # # print(mode)
    # # print(type(mode))
    # messageByteArray3 = bytearray((mode).to_bytes(1,'big')) + bytearray((3).to_bytes(1,'big')) + bytearray((5).to_bytes(1,'big'))
    # print(messageByteArray3)
    # #time.sleep(1)
    # sendToArduino(messageByteArray3)
    mode = int(input("enter mode number:"));
    print("\n")
    flash = int(input("LEDMode: enter 0 for static, 1 for flashing."))
    print("\n")
    flashrate = int(input("Enter flash rate in units of 10s of ms:"))
    print("\n")
    message = bytearray(mode.to_bytes(1,'big')) + bytearray(flash.to_bytes(1,'big')) + bytearray(flashrate.to_bytes(1,'big'))
    print(message)
    sendToArduino(message)
    while True:
        msgPresent = False
        if ser.in_waiting > 0:    
            msgarray = recvFromArduino()
            print("recieved message: ")
            print(msgarray)
            msgPresent = True
        if msgPresent == True:
            # for i in msgarray:
            #     print(chr(i))
            msgPresent = False
            mode = int(input("enter mode number:"));
            print("\n")
            flash = int(input("LEDMode: enter 0 for static, 1 for flashing."))
            print("\n")
            flashrate = int(input("Enter flash rate in units of 10s of ms:"))
            print("\n")
            message = bytearray((mode).to_bytes(1,'big')) + bytearray((flash).to_bytes(1,'big')) + bytearray((flashrate).to_bytes(1,'big'))
            print(message)
            sendToArduino(message)
            
except:
    ser.close()
    print("exiting")

ser.close()
sys.exit()