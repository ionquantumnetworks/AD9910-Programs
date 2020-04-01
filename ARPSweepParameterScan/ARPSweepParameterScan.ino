#include <SPI.h>
#include <stdint.h>
#include <AD9910.h>
#include "SweepCalculator.h"

double k = 1000;
double M = 1000000;
double ns = 0.000000001;
double ms = 0.001;

//Scan Parameters
double centerfreq = 40 * M;
double span = 500.0*k;
double startScanRate = 10 * M / ms;
double stopScanRate = 100 * M / ms;
double scanStepSize;
double sweepStepSize;
double sweepStepTime;
int scanSteps = 10; //number of points to divide the scan into
double currentRate;
//////

//boundaries of scan... stay away from motional sidebands//
double maxFreq = 41 * M;
double minFreq = 39 * M;
//////////////

int runs = 5;
int triggerpin = 2;
int ledpin = 13;
int counter;

void setup() {
  Serial.begin(9600);

  pinMode(triggerpin,INPUT_PULLUP); // This allows the pin to act as an input pin, sitting high until grounded. Can be used to trigger on ground
  pinMode(ledpin, OUTPUT);

  
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
  //Arduino simply counts how many runs have occured.
  //Once the specified number has occured, it is time to reprogram the DDS for the next set of sweep parameters
  counter = 0;
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
  while(counter < runs)
  {
    int triggervalue = digitalRead(triggerpin); 
    if (triggervalue == LOW) //this loop simply counts a number of triggers (triggering low)
    {
      counter = counter + 1;
      digitalWrite(ledpin,LOW); //turn off led to show that trigger occured
      
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
      Serial.println();
    }
    else
    {
      digitalWrite(ledpin, HIGH);
    }
}
}
while(1==1)
{
  
}

}
