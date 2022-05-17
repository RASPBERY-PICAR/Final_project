/*
 * reference: https://codrinsideas.medium.com/diy-raspberry-pi-parking-system-with-platerecognizers-alpr-8e2254298917, coding-arduino;
 * https://microdigisoft.com/2-digit-7-segment-counter00-99with-arduino-in-proteus/, led display
*/


#include <SoftwareSerial.h>
#include <Servo.h>
//
#define echoPin 6 // attach pin D6 Arduino to pin Echo of HC-SR04
#define trigPin 5 //attach pin D6 Arduino to pin Trig of HC-SR04
//
int RX_pin=11; //define pin 11 as RX
int TX_pin=12; //define pin 12 as TX

SoftwareSerial BTserial(RX_pin,TX_pin);
String BT_data;
String Arduino_data;
Servo myservo;  // define object Servo tocontrol
int pos = 0;    // variable store the angle
int state = 0;  // state of the door (open'1' or close'0')]

//
long duration; // variable for the duration of sound wave travel
int distance; // variable for the distance measurement
int ledPin = 2; // the pin in charge with turning on/off the LED
int led2Pin = 3;
//int digledA = 4;
//int digledB = 7;
//int digledC = 8;
//int digledD = 10;
//int digledE = 13;
//int digledF = 14;
//int digledG = 15;
int digled1 = 16;
int digled2 = 17;
int digled_Pins[] = {15,14,13,10,8,7,4,16,17};
int digit[10] = {0b0000001,0b1001111,0b0010010,0b0000110,0b1001100,0b0100100,0b0100000,0b0001111,0b0000000,0b0000100};
//int digit[10]={0b1111110,0b0110000,0b1101101,0b1111001,0b0110011,0b1011011,0b1011111,0b1110000,0b1111111,0b1111011};
String a;

void dis(int num)
{
  for (int i = 0; i < 7; i++)
  {
    digitalWrite(digled_Pins[i], bitRead(digit[num], i));
  }
}

boolean isValidNumber(String str){
  for(byte i=0;i<str.length();i++)
  {
    if(isDigit(str.charAt(i))) return true;
  }
  return false;
}

void setup(){
  Serial.begin(9600);// Serial Communication is starting with 9600 of baudrate speed
  BTserial.begin(9600);// Bluetooth Serial Communication is starting with 9600 of baudrate speed
  myservo.attach(9);  // signal line connects to pin9

  pinMode(trigPin, OUTPUT); // Sets the trigPin as an OUTPUT
  pinMode(echoPin, INPUT); // Sets the echoPin as an INPUT
  Serial.println("Ultrasonic Sensor HC-SR04 Test"); // print some text in Serial Monitor
  Serial.println("with Arduino UNO R3");
  for (int n=0; n<9; n++){
    pinMode(digled_Pins[n],OUTPUT);
    }
  myservo.write(180);              // servo initial angle
  delay(5);                     // wait to rotate to a certain angle
}
void loop(){

  // Clears the trigPin condition
  digitalWrite(trigPin, LOW);
  delayMicroseconds(2);
  // Sets the trigPin HIGH (ACTIVE) for 10 microseconds
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);
  // Reads the echoPin, returns the sound wave travel time in microseconds
  duration = pulseIn(echoPin, HIGH);
  // Calculating the distance
  distance = duration * 0.034 / 2; // Speed of sound wave divided by 2 (go and back)
  // Displays the distance on the Serial Monitor
  Serial.print("Distance: ");
  Serial.print(distance);
  Serial.println(" cm");

  if (distance<20){ //If Distance is less than 10 mm for testing purposes (When testing in real field increase to 100ish)   
      digitalWrite(ledPin,HIGH); //turn on LED
      BTserial.println("1"); // write a 1 on the receiver's end (in our case in the Raspberry Pi)
      Serial.println("1"); // write in the serial port a 1 
      
      delay(1000);
  }else{
     digitalWrite(ledPin,LOW); //turn of LED
  }
  
  while (BTserial.available()){
  //while (Serial.available()){
    //a = Serial.readString();
    a = BTserial.readString();
    delay(5);
    Serial.println(a);
    if(a=="success"){
      digitalWrite(led2Pin,HIGH);
      delay(5);
      }else{digitalWrite(led2Pin,LOW);
      }
    }
  
  Serial.print("State: ");
  Serial.print(state);
  Serial.print(", A:");
  Serial.print(a);
  Serial.println(", ");
  
  
  if (state==0 && a=="success") {
      for (pos = 180; pos >= 90; pos --) { // 180° to 90°
      // in steps of 1 degree
      myservo.write(pos);              // wait to write into the servo angle
      delay(5);                       // wait to rotate to a certain angle
      state = 1;
      a = "";
      }
   }
   if (distance >= 30 && state==1){
      delay(5000);
      for (pos = 90; pos <= 180; pos ++) { // 90° to 180°
      // in steps of 1 degree
      myservo.write(pos);              
      delay(5);                      
      state = 0;
      
      }
   }
   
   if(isValidNumber(a)){
      Serial.print("parking spacing number:");
      Serial.println(a);
      int num = a.toInt();
      int d1 = num/10;
      int d2 = num%10;
      for ( int k = 0; k < 300; k++)// For loop to control the digit control to print 00-99
      {
      digitalWrite(digled1, HIGH);
      digitalWrite(digled2, LOW);
      dis(d1);
      delay(10);
      digitalWrite(digled1, LOW);
      digitalWrite(digled2, HIGH);
      dis(d2);
      delay(10);
        }
      a = "";
      Serial.println(a);
      digitalWrite(digled1,LOW);
      digitalWrite(digled2,LOW);
    }

   
  delay(1000); //Wait 650ms  (Increase this to 2000ish when actually testing in real field, so it does not trigger multiple times  by the same car)
    
  }
