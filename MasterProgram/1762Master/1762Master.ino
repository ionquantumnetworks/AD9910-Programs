#include <SPI.h>
#include <stdint.h>
#include <AD9910.h>
#include "SweepCalculator.h"
//Communication Parameters and Variables//
const byte numChars = 64;
String modeMarker = String("0");
boolean newData = false;
char receivedChars[numChars];
char tempChars[numChars];
//======================================

//AD9910-Arduino Pin Assignment and Relevant Variable Defintions
# define cs 10
# define rst 3 //3
# define update 2
# define sdio 11
# define sclk 13
# define mrst 4
# define sTrig 5
# define CLOCKSPEED 16000000
///Calling AD9910 Class, naming DDS////////
AD9910 DDS(cs, rst, update, sdio, sclk, mrst, sTrig);
////amplitude on a 0-1 scale of DDS output/////
double amp = 1;
//=======================================

/////defining units/////
double k = 1000;
double M = 1000000;
double ns = 0.000000001;
double ms = 0.001;
///////////////////////

//Scan Parameters and useful variable definitions//
double centerfreq;
double span;
double startScanRate;
double stopScanRate;
int scanSteps; //number of points to divide the scan into (in between ends of scan)
int runs; //May need to rename
double scanStepSize;
double sweepStepSize;
double sweepStepTime;
double currentRate;
int counter;
///////////////////////////////////////////////////

//boundaries of scan... stay away from motional sidebands//
double maxFreq = 41 * M;
double minFreq = 39 * M;
//////////////

///define FPGA communication pin (trigger and ready pin) and OSK pin
int triggerpin = 7;
int readypin = 9;
int OSKpin = 8;

start_stop limits;

 
//=============

void setup() {
    pinMode(triggerpin,INPUT_PULLUP); // This allows the pin to act as an input pin, sitting high until grounded. Can be used to trigger on ground
    pinMode(readypin, OUTPUT);
    pinMode(OSKpin, OUTPUT);
    digitalWrite(readypin, LOW);
    digitalWrite(OSKpin, LOW);

    SPI.begin();
  
    DDS.begin();
    DDS.setAmpScaleFactor(1.0);
    DDS.OSKenable(0);
    DDS.freqSweepMode(1);
    
    Serial.begin(115200);
    Serial.println(F("Choose a Starting Mode."));
    
   // Serial.println("I made it here!");
  // put your setup code here, to run once:

}

//==========

void loop() {

  while(modeMarker == "SF"  && newData == true)
  {
    Serial.print(F("Recieved message: "));
    Serial.println(modeMarker);
    Serial.println(F("Entered Single Frequency mode..."));
    newData = false;
    while(newData == false)
    {
      //PutCode here

      //
      recvWithStartEndMarkers();
      modeMarker = String(receivedChars);
    }
    Serial.println(F("Exiting mode..."));
    return;
  }


  
  while(modeMarker == "SP" && newData == true)
  {
    Serial.print(F("Recieved message: "));
    Serial.println(modeMarker);
    Serial.println(F("Entered SPectroscopy mode..."));
    newData = false;
    while(newData == false)
    {
      recvWithStartEndMarkers();
      modeMarker = String(receivedChars);
    }
    Serial.println(F("Exiting mode..."));
    return;
  }


 
    while(modeMarker == "SS" && newData == true)
  {
    Serial.print(F("Recieved message: "));
    Serial.println(modeMarker);
    Serial.println(F("Entered Sweep Scan mode..."));
    //Get Variables
    //
    getSweepScanVar();
    //
    newData = false;
    while(newData == false)
    {
      start_stop limits = calcStartStop(centerfreq, span, maxFreq, minFreq); //Finds boundaries of scan
      scanStepSize = (stopScanRate-startScanRate)/(scanSteps-1); //splits scan into scanSteps number of equal steps
      sweepStepTime = 8 * ns;
      printStartStopSweep(limits);
      for(int i = 0; i < scanSteps; i++)
      {
        currentRate = startScanRate + i * scanStepSize;
        sweepStepSize = calcStepSize(sweepStepTime, currentRate).step;
        DDS.freqSweepParameters(limits.stop, limits.start, sweepStepSize, sweepStepSize, sweepStepTime, sweepStepTime);
        counter = 0;
        digitalWrite(readypin,HIGH);
        repeatedTrigSweep(runs, false);
        if (newData == true)
        {
          return;
        }
      }
      if (newData == false)
      {
        Serial.println(F("Returning to beginning of Scan"));
        Serial.println();
      }

      
      
      recvWithStartEndMarkers();//get rid of this in a moment
      modeMarker = String(receivedChars);
    }
    Serial.println(F("Exiting mode..."));
    return;
  }



      while(modeMarker == "SD" && newData == true)
  {
    Serial.print(F("Recieved message: "));
    Serial.println(modeMarker);
    Serial.println(F("Entered State Detect mode..."));
    newData = false;
    while(newData == false)
    {
      recvWithStartEndMarkers();
      modeMarker = String(receivedChars);
    }
    Serial.println(F("Exiting mode..."));
    return;
  }



  if(newData == true)
  {
    Serial.print(F("Recieved message: "));
    newData = false;
    Serial.println(modeMarker);
    Serial.println(F("Invalid mode selection"));
  }

  recvWithStartEndMarkers();
  modeMarker = String(receivedChars);
}


//==================
//This function reads in a serial message of the form "<message>" where < and > tell the function to stop reading in characters 
void recvWithStartEndMarkers() { //static definitions make sure that the variables are not used by other functions
    static boolean recvInProgress = false;
    static byte ndx = 0;
    char startMarker = '<';
    char endMarker = '>';
    char rc;

    while (Serial.available() > 0 && newData == false) {
        rc = Serial.read();

        if (recvInProgress == true) {
            if (rc != endMarker) {
                receivedChars[ndx] = rc;
                ndx++;
                if (ndx >= numChars) {
                    ndx = numChars - 1;
                }
            }
            else {
                receivedChars[ndx] = '\0'; // terminate the string
                recvInProgress = false;
                ndx = 0;
                newData = true;
            }
        }

        else if (rc == startMarker) {
            recvInProgress = true;
        }
    }
}
//======================


//Sweep and Sweep Scan Functions

//get Sweep Scan Variables
void getSweepScanVar()
{
  newData = false;
  Serial.println(F("Give sweep center frequency value (less than 200 MHz) and sweep span."));
  Serial.println(F("Message form: <centerfreq,span>"));

  while (newData == false)
  {
    recvWithStartEndMarkers();
    if(newData == true)
    {
      strcpy(tempChars, receivedChars);
      char * strtokIndx; //Used by strtok, a function that truncates a string
  
      strtokIndx = strtok(tempChars, ",");
      centerfreq = (double)atol(strtokIndx);

      strtokIndx = strtok(NULL, ",");
      span = (double)atol(strtokIndx);
    }
  }
  Serial.print(F("Sweep Center Freq: "));
  Serial.print(centerfreq/M);
  Serial.println(F("MHz"));
  Serial.print(F("Sweep Span Freq: "));
  Serial.print(span/k);
  Serial.println(F("kHz"));
  Serial.println();
  newData = false;
  Serial.println(F("Give starting and ending sweep rates in Hz/ms."));
  Serial.println(F("Message form: <startrate,endrate>"));
  while (newData == false)
  {
    recvWithStartEndMarkers();
    if(newData == true)
    {
      strcpy(tempChars, receivedChars);
      char * strtokIndx; //Used by strtok, a function that truncates a string
  
      strtokIndx = strtok(tempChars, ",");
      startScanRate = (double)atol(strtokIndx)/ms;

      strtokIndx = strtok(NULL, ",");
      stopScanRate = (double)atol(strtokIndx)/ms;
    }
  }
  newData = false;
  Serial.println(F("Give number of steps and runs per step"));
  Serial.println(F("Message form: <numsteps,runs>"));
  while (newData == false)
  {
    recvWithStartEndMarkers();
    if(newData == true)
    {
      strcpy(tempChars, receivedChars);
      char * strtokIndx; //Used by strtok, a function that truncates a string
  
      strtokIndx = strtok(tempChars, ",");
      scanSteps = (int)atol(strtokIndx);

      strtokIndx = strtok(NULL, ",");
      runs = (int)atol(strtokIndx);
    }
  }
  }
  
  
   

//This function performs a sweep whenever triggered on the sTrig pin. If repeat = false, repeats up to "runs" amount of times.
void repeatedTrigSweep(int runs, boolean repeat)
{//All the messages in this function are temporary until I can test with the real thing.
    while(counter < runs)
  {
    int triggervalue = digitalRead(triggerpin); 
    if (triggervalue == LOW) //this loop simply counts a number of triggers (triggering low)
    {
      if(repeat == false)
      {
        counter = counter + 1;
      }
      digitalWrite(readypin,LOW); //turn off led to show that trigger occured
      
      Serial.print(F("Current scan rate is: "));
      Serial.print(currentRate/M * ms);
      Serial.println(F(" MHz/ms"));
      Serial.print(F("Current digitized sweep step size is: "));
      Serial.print(sweepStepSize);
      Serial.println(F("Hz"));
      Serial.print(F("Each step corresponds to "));
      Serial.print(sweepStepSize/span*100,5);
      Serial.println(F("% of the entire scan."));
      Serial.print(F("Run number at this Scan Rate: "));
      Serial.println(counter); //print over serial what trigger number we are at.
      delay(300); //delay so I can see LED is low.. also I can't press a button too quickly... temporary.

      digitalWrite(OSKpin, HIGH);
      digitalWrite(sTrig,HIGH);
      delay(300);
      digitalWrite(sTrig,LOW);
      digitalWrite(OSKpin,LOW);

      
      Serial.println();
    }
    else
    {
      digitalWrite(readypin, HIGH);
      recvWithStartEndMarkers();
      modeMarker = String(receivedChars);
    }
    if(newData == true)
    {
      return;
    }
  }
}

void printStartStopSweep(start_stop limits)
{
    //Messages
  Serial.print(F("Start Freq is: "));
  Serial.print(limits.start/M, 6);
  Serial.println(F(" MHz"));
  Serial.print(F("Stop Freq is: "));
  Serial.print(limits.stop/M, 6);
  Serial.println(F(" MHz"));
  Serial.print(F("This corresponds to a total span of: "));
  Serial.print(span/k);
  Serial.println(F(" kHz."));
  Serial.println();
  //Messages
}
