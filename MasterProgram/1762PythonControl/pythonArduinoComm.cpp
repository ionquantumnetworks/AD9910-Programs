#include <SPI.h>
#include <stdint.h>
#include <hardwareSerial.h>
#include "pythonArduinoComm.h"

const int startMarker = 254;
const int endMarker = 255;
const int specialByte = 253;
const int maxMessage = 64;

uint8_t bytesRecvd = 0;
uint8_t dataSentNum = 0; //The transmitted value of the number of bytes in the data package - this will be given by the second byte recieved
uint8_t dataRecvCount = 0;

uint8_t dataRecvd[maxMessage];
uint8_t dataSend[maxMessage];
uint8_t tempBuffer[maxMessage];

uint8_t dataSendCount = 0; //Number of 'real' bytes to be sent to the PC
uint8_t dataTotalSend = 0; // the number of bytes to send to PC taking into account encoded bytes

uint8_t command = 0;
uint8_t mode = 0;
uint8_t variableToChange = 0;
unsigned long newVarValue = 0;

//================Command Addresses=================//
const uint8_t modeChange = 1;
const uint8_t varRedefine = 2;


//================Variable Addresses===============//
//Testing Variables//
const uint8_t flash = 17;
const uint8_t interval = 18;

//Common Paramters for all scans//
const uint8_t numSteps = 1;
const uint8_t runsPerStep = 2;

//frequency sweep paramters//
const uint8_t sweepUpperBound = 3;
const uint8_t sweepLowerBound = 4;
const uint8_t sweepCenterFrequency = 5;
const uint8_t sweepRate = 6;
const uint8_t sweepSpan = 7;
//frequency sweep scan specific paramters//
const uint8_t sweepRateStart = 8;
const uint8_t sweepRateStop = 9;

//single frequency mode
const uint8_t frequency = 10;
const uint8_t outputStateSF = 11;

//single frequency spectroscopy
const uint8_t pulseTime = 12;
const uint8_t freqStart = 13;
const uint8_t freqStop = 14;

//Rabi Flopping Scan Paramters
const uint8_t pulseTimeStart = 15;
const uint8_t pulseTimeStop = 16;

bool inProgress = false;
bool allReceived = false;



bool getSerialData()
{
	if (Serial.available() > 0) //check if there is serial data to be read in.
	{
		uint8_t x = Serial.read(); //read in one byte of data
		if (x == startMarker) //if start marker is detected, turn on inProgress, and reset data recieved counter.
		{
			bytesRecvd = 0;
			inProgress = true;
		}
		else
		{
			return false; //returning true or false is useful mostly for debugging.
		}

		while (inProgress) // with in progress turned on, keep reading in the message (when available) until end marker.
		{
			if (Serial.available() > 0)
			{
				tempBuffer[bytesRecvd] = x; //add read in data to the temporary buffer
				bytesRecvd++; //keep count of the number of bytes recieved
				x = Serial.read();
				if (x == endMarker)
				{	
					tempBuffer[bytesRecvd] = x;  //if an end marker is found, add it to the end of the buffer
					bytesRecvd++;
					//debugToPC(bytesRecvd);
					inProgress = false; //turn of in progress to indicate message reading is finished
					allReceived = true; //tells another part of program that the entire message is recieved
					dataSentNum = tempBuffer[1]; //store the first byte of data which contains the length of the message
					decodeHighBytes(); //decode the data
					return true;
				}
			}
		}
	}
	else
	{
		return false;
	}
}

void decodeHighBytes(){
	dataRecvCount = 0;
	//loop through the message looking for special bytes
	for (uint8_t n = 2; n < bytesRecvd - 1; n++) //n=2 skips the start marker and the count byte, -1 omits the end marker
	{
		uint8_t x = tempBuffer[n];
		if (x == specialByte) //if special byte(253) is detecetd, add the next byte to its value to get the real value intended to be sent. 
		{
			n++;
			x = x + tempBuffer[n];
		}

		dataRecvd[dataRecvCount] = x; //stores the actual amount of data sent, rather than bytes sent, which can be different due to special bytes.
		dataRecvCount++;

	}
}

void encodeHighBytes() {
  // Copies to temBuffer[] all of the data in dataSend[]
  //  and converts any bytes of 253 or more into a pair of bytes, 253 0, 253 1 or 253 2 as appropriate
  dataTotalSend = 0;
  for (byte n = 0; n < dataSendCount; n++) {
    if (dataSend[n] >= specialByte) {
      tempBuffer[dataTotalSend] = specialByte;
      dataTotalSend++;
      tempBuffer[dataTotalSend] = dataSend[n] - specialByte;
    }
    else {
      tempBuffer[dataTotalSend] = dataSend[n];
    }
    dataTotalSend++;
  }
}

//=============================================================================================
//Code below this point may change a good bit
void processData() {

    // processes the data that is in dataRecvd[]

  if (allReceived) {		



	interpretData(); //This is specific to our experiments/lab needs.

	// send what was recieved on this end. Doing it this way so that when we want to send other things, we can use the same dataToPC funciton.
	// otherwise I would have not copied dataRecvd into data send... would have just sent dataRecvd...
	dataSendCount = dataRecvCount;
    for (int n = 0; n < dataRecvCount; n++) {
       dataSend[n] = dataRecvd[n];
    }
    dataToPC();

    delay(100); //not so sure about this delay.
    allReceived = false; //ready to read and interpret a new message.
  }
}

void interpretData()
{
	command = dataRecvd[0]; //first message byte is a command byte.
	if (command == modeChange) //if command byte is change mode, redefine the mode var here.
	{
		mode = dataRecvd[1];
	}
	if (command == varRedefine) //if command byte is change variable
	{
		variableToChange = dataRecvd[1]; //first byte after command tells what variable to change
		unsigned long bignumber = 0;
		for (int x = 2; x < 6; x++) //interpret the remaining bytes (which should be a 32 bit number, 4 bytes)
		{
			bignumber = (bignumber<<8);
			bignumber = bignumber + (unsigned long)dataRecvd[x];
		}
		newVarValue = bignumber; //save the value of the variable redefinition.
	}
}

void dataToPC() {

	// expects to find data in dataSend[]
	//   uses encodeHighBytes() to copy data to tempBuffer
	//   sends data to PC from tempBuffer
	encodeHighBytes();
	//Serial.write("I got here");
	Serial.write(startMarker);
	Serial.write(dataSendCount);
	Serial.write(tempBuffer, dataTotalSend);
	Serial.write(endMarker);
}


//=========================

void debugToPC( char arr[]) {
    byte nb = 0;
    Serial.write(startMarker);
    Serial.write(nb);
    Serial.print(arr);
    Serial.write(endMarker);
}

//=========================

void debugToPC( byte num) {
    byte nb = 0;
    Serial.write(startMarker);
    Serial.write(nb);
    Serial.print(num);
    Serial.write(endMarker);
}

//=========================

bool varUpdate(variableRegisterArray& vars)
{
	bool msgrecieved;
	msgrecieved = getSerialData(); //get a message from the computer
	//processData();
	if (msgrecieved == true) //once a message has been recieved do the following
	{
		processData(); //process the data to read in commands
		if (command == modeChange)
		{
			vars.mode = mode; //if command is mode change, change the mode 
		} 
		//change the appropriate variable to the given value.
		if (command == varRedefine)//See header file for what these are
		{
			if (variableToChange == flash)
			{
				vars.flash = newVarValue;
			}
			if (variableToChange == interval)
			{
				vars.interval = newVarValue;
			}
			if (variableToChange == numSteps)
			{
				vars.numSteps = (int)newVarValue;
			}
			if (variableToChange == runsPerStep)
			{
				vars.runsPerStep = (int)newVarValue;
			}
			if (variableToChange == sweepUpperBound)
			{
				vars.sweepUpperBound = newVarValue;
			}
			if (variableToChange == sweepLowerBound)
			{
				vars.sweepLowerBound = newVarValue;
			}
			if (variableToChange == sweepCenterFrequency)
			{
				vars.sweepCenterFrequency = newVarValue;
			}
			if (variableToChange == sweepRate)
			{
				vars.sweepRate = newVarValue;
			}
			if (variableToChange == sweepSpan)
			{
				vars.sweepSpan = newVarValue;
			}
			if (variableToChange == sweepRateStart)
			{
				vars.sweepRateStart = newVarValue;
			}
			if (variableToChange == sweepRateStop)
			{
				vars.sweepRateStop = newVarValue;
			}
			if (variableToChange == frequency)
			{
				vars.frequency = newVarValue;
			}
			if (variableToChange == outputStateSF)
			{
				vars.outputStateSF = (bool)newVarValue;
			}
			if (variableToChange == pulseTime)
			{
				vars.pulseTime = newVarValue;
			}
			if (variableToChange == freqStart)
			{
				vars.freqStart = newVarValue;
			}
			if (variableToChange == freqStop)
			{
				vars.freqStop = newVarValue;
			}
			if (variableToChange == pulseTimeStart)
			{
				vars.pulseTimeStart = newVarValue;
			}
			if (variableToChange == pulseTimeStop)
			{
				vars.pulseTimeStop = newVarValue;
			}
			
		}
		command = 0;
		mode = 0;
		variableToChange = 0;
		newVarValue = 0;
		//debugToPC("made it here");
		//testcomment
	}
	return msgrecieved;
}
