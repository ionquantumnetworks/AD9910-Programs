#include "pythonArduinoComm.h" //contains function and globals to communicate with python

byte MODE = 0x01;
byte M1 = 0x01;
byte M2 = 0x02;


bool var1;
int LED1 = 13;
int LED1State = LOW;


int LED2 = 8;
int LED2State = LOW;

int LED3 = 5;



//unsigned long interval = 1; 
unsigned long previousMillis = 0; 
unsigned long intervalmult = 10;

//===================================================================

void setup() {
  pinMode(LED1, OUTPUT); // the onboard LED
  pinMode(LED2, OUTPUT);
  Serial.begin(9600);
  Serial.setTimeout(10000);
  debugToPC("Arduino Ready");
  
  delay(500);
}




//===================================================================


void loop() {
  static variableRegisterArray vars = {0x05, false, 1};
  //vars.mode = 0x01;
//  bool initialrecv = false;
//  while(initialrecv == false)
//  {
//    digitalWrite(LED3,HIGH);
//    varUpdate(vars);
//    debugToPC("Here");
//   
//  }
  varUpdate(vars);
  //Serial.println(test);
  //Serial.println(vars.mode);
//  if(vars.mode == 0x01)
//  {
//    digitalWrite(LED1, HIGH);
//    digitalWrite(LED2, LOW);
//    digitalWrite(LED3, LOW);
//  }
//  else if(vars.mode == 0x02)
//  {    
//    digitalWrite(LED1, LOW);
//    digitalWrite(LED2, HIGH);
//    digitalWrite(LED3, LOW);
//  }
//  else
//  {
//    digitalWrite(LED1, LOW);
//    digitalWrite(LED2, LOW);
//    digitalWrite(LED3, HIGH);
//  }
//  delay(100);
//  digitalWrite(LED1, LOW);
//  digitalWrite(LED2, LOW);
//  digitalWrite(LED3, LOW);
//  delay(100);
  Serial.println(vars.mode);
  digitalWrite(LED3,LOW);
  delay(100);
  MODE1(vars);
  MODE2(vars);
  digitalWrite(LED3,HIGH);
  delay(100);
}


//===================================================================

void MODE1(variableRegisterArray& vars)
{
  bool msg = false;
  if(vars.mode == M1)
  {
    digitalWrite(LED3,LOW);
    digitalWrite(LED2,LOW);
    while(vars.flash == false && vars.mode == M1)
    {
      digitalWrite(LED1, HIGH);
      varUpdate(vars);
//      getSerialData();
//      processData();
//      MODE = dataRecvd[0];
//      var1 = dataRecvd[1];
//      interval = dataRecvd[2];
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
//      if(msg == false)
//      {
//        digitalWrite(LED3, HIGH);
//      }
//      if(msg == true)
//      {
//        digitalWrite(LED3,LOW);
//        delay(1000);
//        //return;
//      }
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

void MODE2(variableRegisterArray& vars)
{
  if(vars.mode == M2)
  {
    digitalWrite(LED1,LOW);
    digitalWrite(LED2,LOW);
    while(vars.flash == false && vars.mode == M2)
    {
      digitalWrite(LED2, HIGH);
      varUpdate(vars);
//      getSerialData();
//      processData();
//      MODE = dataRecvd[0];
//      var1 = dataRecvd[1];
//      interval = dataRecvd[2];
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


//void readAndRedefineInit()
//{
//  initialrecv = getSerialData();
//  processData();
//  MODE = dataRecvd[0];
//  var1 = dataRecvd[1];
//  interval = dataRecvd[2];
//}

//===================================================================
