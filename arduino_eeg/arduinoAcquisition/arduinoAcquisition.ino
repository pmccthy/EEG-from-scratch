/*A file to define an loop for reading the data from
port A0 of an Arduino Uno and printing the value to
the console. */

// set input pin to A0
int inputPin = A0;
int baudRate = 9600 float samplingFrequency = 500;

// setup routine
void setup()
{
  // initialize serial communication at 9600 bps
  Serial.begin(baudRate);
}

// define loop routine
void loop()
{
  // read the input on analog pin 0:
  int pinValue = analogRead(inputPin);
  // print out the value you read:
  Serial.println(pinValue);
  // delay in ms
  delay(1 / samplingFrequency);
}
