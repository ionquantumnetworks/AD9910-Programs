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
	bool flash;
	unsigned long interval;
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
