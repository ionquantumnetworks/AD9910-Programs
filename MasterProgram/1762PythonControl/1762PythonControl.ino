#include <SPI.h>
#include <stdint.h>
#include <AD9910.h>
#include "SweepCalculator.h"
#include "pythonArduinoComm.h"

//===============Mode Address Definitions=================


byte M1 = 0x01;
byte M2 = 0x02;
byte SweepScanMode = 0x03;
byte singleFreqMode = 0x04;
byte spectroscopyMode = 0x05;
//===============Units Definitions-======================
double k = 1000;
double M = 1000000;
double ns = 0.000000001;
double ms = 0.001;
int commMult = 10; //To take into account unit of 0.1Hz
//===============Variable Definitions==================


unsigned long previousMillis = 0;
unsigned long intervalmult = 1;




//================SPI Communication Stuff=================
//AD9910-Arduino Pin Assignment and Relevant Variable Defintions
# define cs 10
# define rst 3 //3
# define update 2
# define sdio 11
# define sclk 13
# define mrst 4
# define sTrig 5
//# define CLOCKSPEED 16000000
///Calling AD9910 Class, naming DDS////////
AD9910 DDS(cs, rst, update, sdio, sclk, mrst, sTrig);
////amplitude on a 0-1 scale of DDS output/////
double amp = 1;

//===============LED, Input, and Output Pins===========
int LED1 = 9;
int LED1State = LOW;

int LED2 = 8;
int LED2State = LOW;

int LED3 = 6;

///define FPGA communication pin (trigger and ready pin) and OSK pin
int triggerpin = 7;
int readypin = 9;
int OSKpin = 8;

//Setup serial comms, spi comms, inilize AD9910, setup pins for led and ttl communications.
void setup() {
  Serial.begin(115200);
  pinMode(LED1, OUTPUT); // the onboard LED
  pinMode(LED2, OUTPUT);
  pinMode(OSKpin, OUTPUT);
  pinMode(triggerpin, INPUT);//pinMode(triggerpin, INPUT_PULLUP);
  pinMode(6, OUTPUT); // This is currently tied to PO
  SPI.begin();
  DDS.begin();
  DDS.setAmpScaleFactor(100); //DO NOT CHANGE WITHOUT CHECKIGN OUTPUT BEFORE PUTTING IT AMPLIFIER
  DDS.OSKenable(0); //temporarily turning off output shift keying
  //DDS.OSKdisable();
//  DDS.OSKenable(0);
  //DDS.freqSweepMode(1);
  DDS.singleFreqMode();
  DDS.set_freq(400000000,0);
  digitalWrite(6, LOW);
  debugToPC("Arduino Ready");
}

void loop() {
  
  /*
   *  The outermost portion of this program will be a loop that programs the DDS a single time to output a single frequency. 
   *  It will then take commands to turn on or off the DDS, without doing any thing else.
   *  It will also take commands to reprogram variables on the arduino without repograming the AD9910.
   *  The AD9910 will only be reprogrammed when entering one of the modes.
   *  The arduino program will remain in a mode until the modes operation is completed, or until an EXIT command is given.
   *  Variables will not be redefined in these modes to prevent missing any data, as the arduino will be communicating with the lab FPGA.
   *  (though maybe we can allow variables to be redefined using interrupts.. such that a TTL for instance will trigger the proper mode functionality.)
   * 
   */
  static variableRegisterArray vars = {0x04, true, 256}; //Initial array that contains information about current mode, sub modes, and a variable... very simplistic right now.
  static bool initilize = true;
  if (initilize == true)
  {
      vars.numSteps = 10;
      vars.runsPerStep = 5;
      vars.sweepUpperBound = 41000000;
      vars.sweepLowerBound = 39000000;
      vars.sweepCenterFrequency = 40000000;
      vars.sweepSpan = 500000;
      vars.sweepRateStart = 100000000;
      vars.sweepRateStop = 1000000000;
      initilize = false;
  }
  varUpdate(vars);
  //digitalWrite(LED3,LOW);
  //delay(10);
  MODE1(vars);
  //digitalWrite(LED3, HIGH);
  //delay(10);
  //digitalWrite(LED3, LOW);
  MODE2(vars);
  //digitalWrite(LED3,HIGH);
  //delay(10);
  //SweepScan2(vars, triggerpin, readypin);
  SweepScan3(vars, triggerpin, readypin);
  //SweepScanAlwaysOn(vars, triggerpin, readypin);
  singleFreq(vars);
  spectroscopy(vars, triggerpin, readypin);
}


void MODE1(variableRegisterArray& vars)
{
  bool msg = false;
  if(vars.mode == M1)
  {
    Serial.print(F("Entering Mode 1...\n"));
    digitalWrite(LED3,LOW);
    digitalWrite(LED2,LOW);
    while(vars.flash == false && vars.mode == M1)
    {
      digitalWrite(LED1, HIGH);
      varUpdate(vars);
    }
    while(vars.flash == true && vars.mode == M1)
    {
      unsigned long currentMillis = millis();
      if(currentMillis - previousMillis >= vars.interval*intervalmult)
      {
        previousMillis = currentMillis;
        if(LED1State == LOW)
        {
          LED1State = HIGH;
        }
        else
        {
          LED1State = LOW;
        }
        digitalWrite(LED1, LED1State);
      }
      msg = varUpdate(vars);
    }
    digitalWrite(LED1,LOW);
    digitalWrite(LED2,LOW);
    digitalWrite(LED3,LOW);
  }
}


//===================================================================

void MODE2(variableRegisterArray& vars)
{
  if(vars.mode == M2)
  {
    Serial.println(F("Entering Mode 2..."));
    digitalWrite(LED1,LOW);
    digitalWrite(LED2,LOW);
    while(vars.flash == false && vars.mode == M2)
    {
      digitalWrite(LED2, HIGH);
      varUpdate(vars);
    }
    while(vars.flash == true && vars.mode == M2)
    {
      unsigned long currentMillis = millis();
      if(currentMillis - previousMillis >= vars.interval*intervalmult)
      {
        previousMillis = currentMillis;
        if(LED2State == LOW)
        {
          LED2State = HIGH;
        }
        else
        {
          LED2State = LOW;
        }
        digitalWrite(LED2, LED2State);
      }
      varUpdate(vars);
//      getSerialData();
//      processData();
//      MODE = dataRecvd[0];
//      var1 = dataRecvd[1];
//      interval = dataRecvd[2];            
    }
    digitalWrite(LED1,LOW);
    digitalWrite(LED2,LOW);
    digitalWrite(LED3,LOW);
  }
}


//===================================================================

void SweepScan(variableRegisterArray& vars, int triggerpin, int readypin)
{
    if (vars.mode == SweepScanMode)
    {
        Serial.println(F("Entering freq sweep scan mode."));
        digitalWrite(sTrig, LOW); //Make sure a sweep wont trigger immediately.
        //turn on DDS with no dwell high mode. The frequency will sweep back down after up
        DDS.freqSweepMode(1);
        //Some Messages to let us know where we are
        //Serial.print("Trigger pin is:");
        //Serial.println(triggerpin);
        //Serial.print("sweep upper bound: ");
        //Serial.println(vars.sweepUpperBound);
        //Serial.print("sweep lower bound: ");
        //Serial.println(vars.sweepLowerBound);
        //Serial.print("sweep center frequency: ");
        //Serial.println(vars.sweepCenterFrequency);
        Serial.println(F("-----------------------"));
        Serial.print(F("Sweep starting rate: "));
        Serial.print(vars.sweepRateStart*ms/M);
        Serial.println(F(" MHz/ms"));
        Serial.print(F("Sweep ending rate: "));
        Serial.print(vars.sweepRateStop*ms/M);
        Serial.println(F(" MHz/ms"));
        //set limits of sweep, making sure some bound is overstepped.
        start_stop limits = calcStartStop(vars.sweepCenterFrequency, vars.sweepSpan, vars.sweepUpperBound, vars.sweepLowerBound);
        //calculate step size of rate(how much rate will change by each step)
        unsigned long scanStepSize = (vars.sweepRateStop - vars.sweepRateStart) / (vars.numSteps - 1);
        double sweepStepTime = 8 * ns;
        //Let the user know what the step size is
        Serial.print(F("Scan step size is: "));
        Serial.print(scanStepSize);
        Serial.print(scanStepSize*ms/M);
        Serial.println(F(" MHz/ms"));
        Serial.println(F("-----------------------"));
        //print information about where the sweep will be going from
        printStartStopSweep(limits);
        //for loop to step through sweep rates
        for (int i = 0; i < vars.numSteps+1; i++)
        {
            if (vars.mode != SweepScanMode)//exit out if mode has been changed over serial
            {
                return;
            }
            double currentRate = vars.sweepRateStart + i * scanStepSize;//calc current rate
            double sweepStepSize = calcStepSize(sweepStepTime, currentRate).step;//calc the proper step size to give the current rate using the given time at each step
            DDS.freqSweepParameters(limits.stop, limits.start, sweepStepSize, sweepStepSize, sweepStepTime, sweepStepTime); //program in step size and other parameters of sweep
            //let the user know what the current scan rate is.
            Serial.print(F("Current scan rate is: "));
            Serial.print((float)(currentRate*ms/M));
            Serial.println(F(" MHz/ms"));
            //Serial.println(F(" MHz/ms"));
            Serial.print(F("Current digitized sweep step size is: "));
            Serial.print(sweepStepSize);
            Serial.println(F("Hz"));
            Serial.print(F("Each step corresponds to "));
            Serial.print(sweepStepSize / vars.sweepSpan * 100, 5);
            Serial.println(F("% of the entire scan."));

            digitalWrite(readypin, HIGH);
            repeatedTrigSweep(vars.runsPerStep, false, vars, triggerpin, readypin);
            digitalWrite(readypin, LOW);

        }
    }
}


void printStartStopSweep(start_stop limits)
{
    //Messages
    Serial.print(F("Start Freq is: "));
    Serial.print(limits.start / M, 6);
    Serial.println(F(" MHz"));
    Serial.print(F("Stop Freq is: "));
    Serial.print(limits.stop / M, 6);
    Serial.println(F(" MHz"));
    Serial.print(F("This corresponds to a total span of: "));
    Serial.print((limits.stop-limits.start) / k);
    Serial.println(F(" kHz."));
    Serial.println(F("-----------------------"));
    //Serial.println();
    //Messages
}

//This function performs a sweep whenever triggered on the sTrig pin. If repeat = false, repeats up to "runs" amount of times.
void repeatedTrigSweep(int runs, boolean repeat, variableRegisterArray& vars, int triggerpin, int readypin)
{
    int triggervalue;
    int counter = 0;
    //All the messages in this function are temporary until I can test with the real thing.
    while (counter < runs)
    {
        //I may replace a good portion of this code with interrupts instead. This would allow the counter and sweeps to happen even if reading serial *by pausing serial reading*
        triggervalue = digitalRead(triggerpin);
        if (triggervalue == LOW) //this loop simply counts a number of triggers (triggering low)
        {
            if (repeat == false)
            {
                counter = counter + 1;
            }

            digitalWrite(readypin, LOW); //turn off led to show that trigger occured
            Serial.print(F("Run number at this Scan Rate: "));
            Serial.println(counter); //print over serial what trigger number we are at.

            delay(300); //delay so I can see LED is low.. also I can't press a button too quickly... temporary.
            //the delay below will need to be replaced with a value that corresponds to how long the sweep should be going on for.
            //right now just set up for at-home testing.
            digitalWrite(OSKpin, HIGH);
            digitalWrite(sTrig, HIGH);
            //delay(1000);
            digitalWrite(sTrig, LOW);
            delay(1000);
            //digitalWrite(OSKpin, LOW);
        }
        else
        {
            varUpdate(vars);
            digitalWrite(readypin, HIGH);//read and implement any changes have been made over serial
        }
        if (vars.mode != SweepScanMode)//exit out if mode has been changed over serial.
        {
            return;
        }
    }
}

void SweepScan2(variableRegisterArray& vars,int triggerpin, int readypin) //For testing purposes
{
  if(vars.mode == SweepScanMode)
  {
    Serial.println(F("Entering freq sweep scan mode."));
    digitalWrite(sTrig, LOW); //Make sure a sweep wont trigger immediately.
    //DDS.freqSweepParameters(vars.sweepCenterFrequency+vars.sweepSpan/2,vars.sweepCenterFrequency-vars.sweepSpan/2,vars.sweepSpan/1000000000,vars.sweepSpan/1000000000,0.000000008,0.000000008);
    //DDS.freqSweepParameters(vars.sweepCenterFrequency+vars.sweepSpan/2,vars.sweepCenterFrequency-vars.sweepSpan/2,2,2,0.000000008,0.000000008);
    //DDS.freqSweepParameters(1000000000,100000000,2,10*.2,0.000000008,0.000000008);
    DDS.freqSweepParameters(vars.sweepUpperBound,vars.sweepLowerBound,8,8,0.000000008,0.000000008);
    Serial.print(F("Target Sweep Rate Start: "));
    Serial.println(vars.sweepRateStart);
    Serial.print(F("Upper Bound: "));
    Serial.println(vars.sweepUpperBound);
    Serial.print(F("Lower Bound: "));
    Serial.println(vars.sweepLowerBound);
    Serial.print(F("Freq per step: "));
    Serial.println(vars.sweepSpan/1000000000);
    DDS.freqSweepMode(1);
    digitalWrite(OSKpin, HIGH);
    while(vars.mode == SweepScanMode){
      digitalWrite(sTrig,HIGH);
      digitalWrite(sTrig,LOW);
      varUpdate(vars);
      delay(20);
    }
    } 
  }

void SweepScan3(variableRegisterArray& vars,int triggerpin, int readypin)
{
  if(vars.mode == SweepScanMode)
  {
    unsigned long currentRate;
    unsigned long stepSize;
    unsigned long scanStepSize;
    unsigned long sweepSpan;
    double sweepTime;
    unsigned long sweepTimeMilli;
    unsigned long sweepTimeMicro;
    unsigned long tempSweepTime;
    unsigned long adjustmentTime = 4; //To make pulses correct length
    Serial.println(F("Entering freq sweep scan mode."));
    digitalWrite(sTrig, LOW); //Make sure a sweep wont trigger immediately.
    Serial.print(F("Target Sweep Rate Start: "));
    Serial.println(vars.sweepRateStart);
    Serial.print(F("Target Sweep Rate Stop: "));
    Serial.println(vars.sweepRateStop);
    Serial.print(F("Upper Bound: "));
    Serial.println(vars.sweepUpperBound);
    Serial.print(F("Lower Bound: "));
    Serial.println(vars.sweepLowerBound);
    scanStepSize = (vars.sweepRateStop-vars.sweepRateStart)/vars.numSteps; //Max stop rate is 10^9 Hz/s //Units are Hz/s even though python program labeled as MHz/ms
    sweepSpan = vars.sweepUpperBound-vars.sweepLowerBound;
    DDS.freqSweepMode(1);
    digitalWrite(OSKpin, LOW); //Might make this low
    for (unsigned long i = 0; i < vars.numSteps; i++)
    {
      if (vars.mode != SweepScanMode)//exit out if mode has been changed over serial
      {
        return;
        }
     DDS.singleFreqMode();
     delay(10);
     DDS.freqSweepMode(1);
     delay(10);
     currentRate = vars.sweepRateStart + (i) * scanStepSize;//Expecting a trigger to begin with, so we will start at a frequency before what we want
     stepSize = ((currentRate/100)*8)/10000; //Factor of 10 for units of 0.1 Hz, Factor of 10^9 for 8 ns ((currentRate/1000)*8)/100000;
     sweepTime = sweepSpan/stepSize*0.000000008;// /1000000000;
     //Serial.println(sweepSpan);
     Serial.print(F("current sweep rate (Hz/s): "));
     Serial.println(currentRate);
     Serial.print(F("Sweep Step Size (Hz/10): ")); 
     Serial.println(stepSize);
     Serial.print(F("Time to sweep (ms): "));
     Serial.println(sweepTime*1000,6);
     if (stepSize < 2)
     {
      Serial.println(F("Step size under 0.2 Hz. Setting to 0.2 Hz"));
      stepSize = 2;
      //Serial.println(stepSize);
      }
     DDS.freqSweepParameters(vars.sweepUpperBound,vars.sweepLowerBound,stepSize,stepSize,0.000000008,0.000000008);
     delay(10);
     int counter = 0;
     int triggervalue;
     sweepTimeMilli=(unsigned long)(sweepTime*1000);
     sweepTimeMicro= (unsigned long)((sweepTime*1000-(double)(sweepTimeMilli))*1000);
     while (counter < vars.runsPerStep)//Without being triggered this whole loop takes around 22 us, 17 of which is not the ready pin 
     {
      triggervalue = digitalRead(triggerpin);
      varUpdate(vars);
      if(triggervalue == HIGH)
      {
        digitalWrite(readypin,LOW);
        counter = counter + 1;
        //Serial.println(counter);
        if (sweepTime*1000 >= 1)
        {
          digitalWrite(sTrig,HIGH);
          digitalWrite(OSKpin, HIGH);
          //delay(sweepTime*1000);
          delay(sweepTimeMilli);
          delayMicroseconds(sweepTimeMicro);
          digitalWrite(OSKpin,LOW);
          digitalWrite(sTrig,LOW);
          delay(1);
          }
        else
        {
          tempSweepTime = (unsigned long)(sweepTime*1000000)-adjustmentTime;
          if(tempSweepTime > 2000)
          {
            tempSweepTime = 0;
            }
          digitalWrite(sTrig,HIGH);
          digitalWrite(OSKpin, HIGH);
          delayMicroseconds(tempSweepTime);
          //delayMicroseconds((int)(sweepTime*1000000));
          //Serial.println((int)(sweepTime*1000000));
          digitalWrite(OSKpin,LOW);
          digitalWrite(sTrig,LOW);
          //Serial.println(tempSweepTime);
          delay(1);
          }

        }
      else
      {
        varUpdate(vars);
        digitalWrite(readypin,HIGH); //THIS TAKES AROUND 5 us
        //delayMicroseconds(5);
        digitalWrite(readypin,LOW);
        }
      if (vars.mode != SweepScanMode)
      {
        return;
        }
      }
     }
    } 
  }

void SweepScanAlwaysOn(variableRegisterArray& vars,int triggerpin, int readypin)
{
  if(vars.mode == SweepScanMode)
  {
    unsigned long currentRate;
    unsigned long stepSize;
    unsigned long scanStepSize;
    unsigned long sweepSpan;
    double sweepTime;
    unsigned long sweepTimeMilli;
    unsigned long sweepTimeMicro;
    unsigned long tempSweepTime;
    unsigned long adjustmentTime = 4; //To make pulses correct length
    unsigned long startFrequency = 100000000; //to be far off resonance with AOM
    Serial.println(F("Entering freq sweep scan mode."));
    digitalWrite(sTrig, LOW); //Make sure a sweep wont trigger immediately.
    Serial.print(F("Target Sweep Rate Start: "));
    Serial.println(vars.sweepRateStart);
    Serial.print(F("Target Sweep Rate Stop: "));
    Serial.println(vars.sweepRateStop);
    Serial.print(F("Upper Bound: "));
    Serial.println(vars.sweepUpperBound);
    Serial.print(F("Lower Bound: "));
    Serial.println(vars.sweepLowerBound);
    scanStepSize = (vars.sweepRateStop-vars.sweepRateStart)/vars.numSteps; //Max stop rate is 10^9 Hz/s //Units are Hz/s even though python program labeled as MHz/ms
    sweepSpan = vars.sweepUpperBound-vars.sweepLowerBound;
    DDS.freqSweepMode(1);
    digitalWrite(OSKpin, HIGH); //Might make this low
    for (unsigned long i = 0; i < vars.numSteps; i++)
    {
      if (vars.mode != SweepScanMode)//exit out if mode has been changed over serial
      {
        return;
        }
     DDS.singleFreqMode();
     delay(10);
     DDS.freqSweepMode(1);
     delay(10);
     digitalWrite(OSKpin, HIGH);
     currentRate = vars.sweepRateStart + (i) * scanStepSize;//Expecting a trigger to begin with, so we will start at a frequency before what we want
     stepSize = ((currentRate/100)*8)/10000; //Factor of 10 for units of 0.1 Hz, Factor of 10^9 for 8 ns ((currentRate/1000)*8)/100000;
     sweepTime = sweepSpan/stepSize*0.000000008;// /1000000000;
     //Serial.println(sweepSpan);
     Serial.print(F("current sweep rate (Hz/s): "));
     Serial.println(currentRate);
     Serial.print(F("Sweep Step Size (Hz/10): ")); 
     Serial.println(stepSize);
     Serial.print(F("Time to sweep (ms): "));
     Serial.println(sweepTime*1000,6);
     if (stepSize < 2)
     {
      Serial.println(F("Step size under 0.2 Hz. Setting to 0.2 Hz"));
      stepSize = 2;
      //Serial.println(stepSize);
      }
     //DDS.freqSweepParameters(vars.sweepUpperBound,vars.sweepLowerBound,stepSize,stepSize,0.000000008,0.000000008);
     DDS.freqSweepParameters(vars.sweepUpperBound,startFrequency,stepSize,stepSize,0.000000008,0.000000008);
     delay(10);
     int counter = 0;
     int triggervalue;
     sweepTimeMilli=(unsigned long)(sweepTime*1000);
     sweepTimeMicro= (unsigned long)((sweepTime*1000-(double)(sweepTimeMilli))*1000);
     double startTime = (vars.sweepLowerBound-startFrequency)*0.000000008/(stepSize);
     unsigned long startTimeMilli = (unsigned long)(startTime*1000);
     unsigned long startTimeMicro = (unsigned long)((startTime*1000-(double)(startTimeMilli))*1000);
     while (counter < vars.runsPerStep)//Without being triggered this whole loop takes around 22 us, 17 of which is not the ready pin 
     {
      triggervalue = digitalRead(triggerpin);
      varUpdate(vars);
      if(triggervalue == HIGH)
      {
        digitalWrite(readypin,LOW);
        counter = counter + 1;
        //Serial.println(counter);
        if (sweepTime*1000 >= 1)
        {
          digitalWrite(OSKpin,LOW);
          digitalWrite(sTrig,HIGH);
          delay(startTimeMilli);
          delayMicroseconds(startTimeMicro);
          digitalWrite(OSKpin, HIGH);
          //delay(sweepTime*1000);
          delay(sweepTimeMilli);
          delayMicroseconds(sweepTimeMicro);
          digitalWrite(OSKpin,LOW);
          digitalWrite(sTrig,LOW);
          delay(1);
          digitalWrite(OSKpin,HIGH);
          }
        else
        {
          tempSweepTime = (unsigned long)(sweepTime*1000000)-adjustmentTime;
          if(tempSweepTime > 2000)
          {
            tempSweepTime = 0;
            }
          digitalWrite(OSKpin,LOW);
          digitalWrite(sTrig,HIGH);
          delay(startTimeMilli);
          delayMicroseconds(startTimeMicro);
          digitalWrite(OSKpin, HIGH);
          delayMicroseconds(tempSweepTime);
          //delayMicroseconds((int)(sweepTime*1000000));
          //Serial.println((int)(sweepTime*1000000));
          digitalWrite(OSKpin,LOW);
          digitalWrite(sTrig,LOW);
          //Serial.println(tempSweepTime);
          delay(1);
          digitalWrite(OSKpin,HIGH);
          }

        }
      else
      {
        varUpdate(vars);
        digitalWrite(readypin,HIGH); //THIS TAKES AROUND 5 us
        //delayMicroseconds(5);
        digitalWrite(readypin,LOW);
        }
      if (vars.mode != SweepScanMode)
      {
        return;
        }
      }
     }
    } 
  }

//==================================================================
//Need to write these functions still
void singleFreq(variableRegisterArray& vars)
{
    if(vars.mode == singleFreqMode)
    {
        Serial.println(F("Entering single frequency mode..."));
        Serial.print(F("Frequency is: "));
        Serial.print(vars.frequency/M/commMult);
        Serial.println(F(" MHz"));
        DDS.singleFreqMode();//SET DDS to single frequency mode
        //NEED TO ADD PROFILE PIN STUFF OR HARDWIRE PINS - Went with hardwiring for now.
        bool justEntered = true;
        while(vars.mode == singleFreqMode)
        {
            digitalWrite(6, LOW);
            if(vars.outputStateSF == true)
            {
                digitalWrite(OSKpin, HIGH);
            }
            else
            {
                digitalWrite(OSKpin, LOW);
            }
            unsigned long currentFreq = vars.frequency;
            varUpdate(vars);
            if((vars.frequency != currentFreq) or (justEntered == true))
            {
                DDS.set_freq(vars.frequency, 0);
                Serial.print(F("Frequency changed to: "));
                Serial.print(vars.frequency/M/commMult,5); //Factor of 10 is to compensate for being in units of 0.1 Hz as opposed to Hz.
                Serial.println(F(" MHz."));
                justEntered = false;
            }
            
        }
    }
}

//===================================================================
void spectroscopy(variableRegisterArray& vars, int triggerpin, int readypin)
{
    if(vars.mode == spectroscopyMode)
    {
        Serial.println(F("Entering spectroscopy mode..."));
        Serial.print(F("1762 pulse temporal length is: "));
        Serial.print(vars.pulseTime);
        Serial.println(F("uS."));
        Serial.print(F("Starting frequency is: "));
        Serial.print(vars.freqStart/M/commMult);
        Serial.println(F(" MHz."));
        Serial.print(F("Ending frequency is: "));
        Serial.print(vars.freqStop/M/commMult);
        Serial.println(F(" MHz."));
        unsigned long scanStepSize = (vars.freqStop-vars.freqStart)/vars.numSteps;
        Serial.print(F("A step size of "));
        Serial.print(scanStepSize/commMult);
        Serial.print(F(" Hz for"));
        Serial.print(vars.numSteps);
        Serial.println(F(" total number of steps."));

        digitalWrite(OSKpin, HIGH);
        
        for(unsigned long i = 0;  i < vars.numSteps+2; i++)
        {
            if (vars.mode != spectroscopyMode)//exit out if mode has been changed over serial
            {
                return;
            }
            unsigned long currentFreq = vars.freqStart + (i-1) * scanStepSize;//Expecting a trigger to begin with, so we will start at a frequency before what we want
            DDS.set_freq(currentFreq, 0);
            int counter = 0;
            int triggervalue;
//            Serial.print(F("Current frequency: "));
//            Serial.print(currentFreq/M/commMult);
//            Serial.println(F(" MHz."));
            while(counter < vars.runsPerStep)
            {
                //I may replace a good portion of this code with interrupts instead. This would allow the counter and sweeps to happen even if reading serial *by pausing serial reading*
                triggervalue = digitalRead(triggerpin);
                if (triggervalue == HIGH) //this loop simply counts a number of triggers (triggering low)
                {
                    counter = counter + 1;
                    //Need to put in code to turn on and off the AOM output. Probably using OSK pin.
//                    delay(100); //Delay since currently using a button.
//                    digitalWrite(OSKpin, HIGH);
//                    delayMicroseconds(vars.pulseTime);
//                    digitalWrite(OSKpin, HIGH); //For testing purposes set this high. NEED TO SET LOW if you want arduino to do the pulsing, as opposed to an external box.
//                    digitalWrite(readypin, LOW); //turn off led to show that trigger occured
//                    Serial.print(F("Run number at this frequency: "));
//                    Serial.println(counter); //print over serial what trigger number we are at.
                }
                else
                {
                    varUpdate(vars);
//                    digitalWrite(readypin, HIGH);//read and implement any changes have been made over serial
                }
                if (vars.mode != spectroscopyMode)//exit out if mode has been changed over serial.
                {
                    return;
                }
            }
        }
    }
}




//===================================================================
void rabiFlopScan();

//===================================================================
