int photoresistorPin = A0;
int photoresistorVal = 0;

int thermometerPin = A1;
int thermometerVal = 0;

int diodePin = 9;
int diodeVal = 0;

void setup()
{
  pinMode(photoresistorPin, INPUT);
  pinMode(thermometerPin, INPUT);
  pinMode(diodePin, OUTPUT);
  Serial.begin(9600);
}

void loop()
{
  if (Serial.available() > 0) {
    diodeVal = Serial.parseInt();
    
    if (diodeVal > 255) {
      diodeVal = 255;
    } else if (diodeVal < 0) {
      diodeVal = 0;
    }
    
    analogWrite(diodePin, diodeVal); 
  }
  
  photoresistorVal = map(analogRead(photoresistorPin), 0, 1000, 0, 255);
  thermometerVal = ((analogRead(thermometerPin) * 5 / 1024.0) - 0.5) / 0.01 - 5;

  Serial.print(photoresistorVal);
  Serial.print(';');
  Serial.print(thermometerVal);
  Serial.print(';');
  Serial.println(diodeVal);
  delay(300);
}
