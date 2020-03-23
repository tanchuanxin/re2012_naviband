const int pin = 12;

void setup() {
  pinMode(pin, OUTPUT);
}

void loop() {
  tone(pin, 261); //Middle C
  delay(1000);

  tone(pin, 277); //C#
  delay(1000);

  tone(pin, 294); //D
  delay(1000);

  tone(pin, 311); //D#
  delay(1000);

  tone(pin, 330); //E
  delay(1000);
 
  tone(pin, 349); //F
  delay(1000);

  tone(pin, 370); //F#
  delay(1000);

  tone(pin, 392); //G
  delay(1000);

  tone(pin, 415); //G#
  delay(1000);

  tone(pin, 440); //A
  delay(1000);
  // put your main code here, to run repeatedly:

}
