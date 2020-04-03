#include <SPI.h>
#include <stdint.h>
#include <AD9910.h>
#include "SweepCalculator.h"

//Defining pins that arduino will use to communicate with AD9910
# define cs 10
# define rst 3 //3
# define update 2
# define sdio 11
# define sclk 13
# define mrst 4
# define sTrig 5
///////////////////
# define CLOCKSPEED 16000000//Clockspeed used for SPI serial communication between arduino and AD9910... setting to 16 MHz... which I think is clockspeed of an arduino uno.
///Calling AD9910 Class, naming DDS////////
AD9910 DDS(cs, rst, update, sdio, sclk, mrst, sTrig);
////amplitude on a 0-1 scale of DDS output/////
double amp = 1;

/////defining units/////
double k = 1000;
double M = 1000000;
double ns = 0.000000001;
double ms = 0.001;
///////////////////////

//Scan Parameters and useful variable definitions//
double centerfreq = 40 * M;
double span = 500.0*k;
double startScanRate = 10 * M / ms;
double stopScanRate = 100 * M / ms;
double scanStepSize;
double sweepStepSize;
double sweepStepTime;
int scanSteps = 10; //number of points to divide the scan into (in between ends of scan)
double currentRate;
int runs = 1;
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

void setup() {
  pinMode(triggerpin,INPUT_PULLUP); // This allows the pin to act as an input pin, sitting high until grounded. Can be used to trigger on ground
  pinMode(readypin, OUTPUT);
  pinMode(OSKpin, OUTPUT);
  digitalWrite(readypin, LOW);
  digitalWrite(OSKpin, LOW);
  
  Serial.begin(115200);
  SPI.begin();
  
  DDS.begin();
  DDS.setAmpScaleFactor(1.0);
  DDS.OSKenable(0);
  DDS.freqSweepMode(1);
}

void loop() {
  // put your main code here, to run repeatedly:

start_stop limits = calcStartStop(centerfreq, span, maxFreq, minFreq); //Finds boundaries of scan
scanStepSize = (stopScanRate-startScanRate)/(scanSteps-1); //splits scan into scanSteps number of equal steps
sweepStepTime = 8 * ns; 

for(int i = 0; i < scanSteps; i++)
{
  currentRate = startScanRate + i * scanStepSize;
  sweepStepSize = calcStepSize(sweepStepTime, currentRate).step;

  DDS.freqSweepParameters(limits.stop, limits.start, sweepStepSize, sweepStepSize, sweepStepTime, sweepStepTime);
  

  //Messages
  Serial.print("Start Freq is: ");
  Serial.print(limits.start/M, 6);
  Serial.println(" MHz");
  Serial.print("Stop Freq is: ");
  Serial.print(limits.stop/M, 6);
  Serial.println(" MHz");
  Serial.print("This corresponds to a total span of: ");
  Serial.print(span/k);
  Serial.println(" kHz.");
  Serial.println();
  //Messages

  //Arduino simply counts how many runs have occured.
  //Once the specified number has occured, it is time to reprogram the DDS for the next set of sweep parameters
  
  counter = 0;
  digitalWrite(readypin,HIGH);
  
  while(counter < runs)
  {
    int triggervalue = digitalRead(triggerpin); 
    if (triggervalue == LOW) //this loop simply counts a number of triggers (triggering low)
    {
      counter = counter + 1;
      digitalWrite(readypin,LOW); //turn off led to show that trigger occured
      
      Serial.print("Current scan rate is: ");
      Serial.print(currentRate/M * ms);
      Serial.println(" MHz/ms");
      Serial.print("Current digitized sweep step size is: ");
      Serial.print(sweepStepSize);
      Serial.println(" Hz");
      Serial.print("Each step corresponds to ");
      Serial.print(sweepStepSize/span*100,5);
      Serial.println("% of the entire scan.");
      Serial.print("Run number at this Scan Rate: ");
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
    }
}
}

Serial.println("Parameter Scan Complete.");

while(1==1)
{
  digitalWrite(readypin, HIGH);
  delay(500);
  digitalWrite(readypin,LOW);
  delay(500);
}

}
