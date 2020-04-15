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

bool inProgress = false;
bool allReceived = false;



bool getSerialData()
{
	if (Serial.available() > 0)
	{
		uint8_t x = Serial.read();
		if (x == startMarker)
		{
			bytesRecvd = 0;
			inProgress = true;
		}

		while (inProgress)
		{
			if (Serial.available() > 0)
			{
				tempBuffer[bytesRecvd] = x;
				bytesRecvd++;
				x = Serial.read();
				if (x == endMarker)
				{	
					tempBuffer[bytesRecvd] = x;
					bytesRecvd++;
					//debugToPC(bytesRecvd);
					inProgress = false;
					allReceived = true;
					dataSentNum = tempBuffer[1];
					decodeHighBytes();
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
	for (uint8_t n = 2; n < bytesRecvd - 1; n++) //n=2 skips the start marker and the count byte, -1 omits the end marker
	{
		uint8_t x = tempBuffer[n];
		if (x == specialByte)
		{
			n++;
			x = x + tempBuffer[n];
		}

		dataRecvd[dataRecvCount] = x;
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
  
      // for demonstration just copy dataRecvd to dataSend
    dataSendCount = dataRecvCount;
    for (int n = 0; n < dataRecvCount; n++) {
       dataSend[n] = dataRecvd[n];
//       Serial.write("\n");
//       Serial.write(dataRecvd[n]);
//       Serial.write("\n");
//       Serial.write(dataSend[n]);
    }
//	debugToPC("here");
    dataToPC();

    delay(100); //not so sure about this delay.
    allReceived = false; 
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


//========================= I DEFINITELY INTEND ON CHANGING or REMOVING THESE

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
	bool msgprocessed;
	msgprocessed = getSerialData();
	processData();
	//vars.mode = dataRecvd[0];
	//vars.flash = dataRecvd[1];
	//vars.interval = dataRecvd[2];
	if (msgprocessed == true)
	{
		vars.mode = dataRecvd[0];
		vars.flash = dataRecvd[1];
		vars.interval = dataRecvd[2];
	}
	return msgprocessed;
}
