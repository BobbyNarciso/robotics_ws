#define VRX 34
#define VRY 35

void setup() {
  Serial.begin(115200);
}

void loop() {
  int x = analogRead(VRX);
  int y = analogRead(VRY);

  Serial.print(x);
  Serial.print(",");
  Serial.println(y);

  delay(20);
}