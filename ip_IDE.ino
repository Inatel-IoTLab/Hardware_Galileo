void setup() {
  Serial.begin(9600);
  //aperte 'a' para mostrar o ip
  while(Serial.read()!='a'){
    Serial.println("hello");
    delay(1000);
  }
  //ifconfig para serial monitor
  system("ifconfig > /dev/ttyGS0");
}
 
void loop() {
 
}
