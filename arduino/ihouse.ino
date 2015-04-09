int photoresistorPin = A0;
int photoresistorVal = 0;

int thermometerPin = A1;
int thermometerVal = 0;

void setup()
{
  pinMode(photoresistorPin, INPUT);
  pinMode(thermometerPin, INPUT);
  Serial.begin(9600);
}

void loop()
{  
  photoresistorVal = map(analogRead(photoresistorPin), 0, 1000, 0, 255);
  thermometerVal = ((analogRead(thermometerPin) * 5 / 1024.0) - 0.5) / 0.01 - 5;

  Serial.print(photoresistorVal);
  Serial.print(';');
  Serial.println(thermometerVal);
  delay(2000);
}
