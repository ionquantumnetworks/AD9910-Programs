#pragma once
#include <SPI.h>
#include <stdint.h>
#include <hardwareSerial.h>

extern const int startMarker;
extern const int endMarker;
extern const int specialByte;
extern const int maxMessage;

extern uint8_t bytesRecvd;
extern uint8_t dataSentNum; //The transmitted value of the number of bytes in the data package - this will be given by the second byte recieved
extern uint8_t dataRecvCount;

extern uint8_t dataRecvd[];
extern uint8_t dataSend[];
extern uint8_t tempBuffer[];

extern uint8_t dataSendCount; //Number of 'real' bytes to be sent to the PC
extern uint8_t dataTotalSend; // the number of bytes to send to PC taking into account encoded bytes

extern bool inProgress;
extern bool allReceived;


struct variableRegisterArray 
{
	byte mode;
	//======For Testing Communications======//
	unsigned long flash;
	unsigned long interval;

	//=====Common paramters for all scans=====//
	int numSteps; //number of steps in scan
	int runsPerStep; //number of runs at each step


	//=====frequency sweep parameters======//
	unsigned long sweepUpperBound; //absolute upper boundary on frequency sweep //32-bit (4 byte) value
	unsigned long sweepLowerBound; //absolute lower boundary on frequency sweep //32-bit (4 byte) value
	unsigned long sweepCenterFrequency; //center frequency of sweep// 32-bit (4 byte) value
	unsigned long sweepRate; //Sweep rate for state detection mode (i.e. single sweep rate)
	unsigned long sweepSpan; //Span of sweep// 32-bit (4 byte) value
	//=====frequency sweep scan specific parameters========///
	unsigned long sweepRateStart; //32-bit value
	unsigned long sweepRateStop; //32-bit value


	//=====single frequency mode======//
	unsigned long frequency; //Frequency for single frequency mode or rabi flopping mode// 32-bit (4 byte) value
	bool outputStateSF; //Single frequency mdoe output state (on or off)

	//=====Single Frequency Spectroscopy Paramters=====//
	unsigned long pulseTime; //length of aom pulse at each frequency
	unsigned long freqStart;
	unsigned long freqStop;

	//=====Rabi Flopping Parameters======//
	unsigned long pulseTimeStart;
	unsigned long pulseTimeStop;
};


bool getSerialData();

void processData(); //I'm thinking this will be the main function that decides what will happen after reading the data in.
//I think with this, I want to have it read the data in, send what it read back to the pc for verification, and then either redefine variables itself, or
//give the command string to another function that will.

void decodeHighBytes();

void dataToPC();

void encodeHighBytes();

void dataToPC();

void debugToPC(char arr[]);

void debugToPC(byte num);

bool varUpdate(variableRegisterArray& vars);

void interpretData();