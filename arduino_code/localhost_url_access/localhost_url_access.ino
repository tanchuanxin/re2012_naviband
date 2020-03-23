#include <ESP8266WiFi.h>

const char* ssid     = "Whizz";      // SSID of local network
const char* password = "2billion";   // Password on network

WiFiClient client;
char servername[]="192.168.1.81";  // remote server we will connect to. will be your local ip address. run cmd and then "ipconfig" to find
String result;


void setup() {
  // put your setup code here, to run once:
  Serial.begin(115200);
  Serial.println("------------Beginning setup------------");
  Serial.println("Connecting to WiFi");
  
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    Serial.println("Connecting to WiFi...");
    delay(500);
  }
  
  Serial.println("Connected to WiFi");
  delay(1000);
  Serial.println("------------Finish setup------------");
}

void loop() {
  // put your main code here, to run repeatedly:
  Serial.println("Getting data");
  getData();
  delay(1000);

  Serial.println("Sending data");
  sendData();
  delay(1000);

  
}

void getData()
{
  if (client.connect(servername, 80)) {  //starts client connection, checks for connection
    client.println("GET /getdata");
    client.println("Host: 192.168.1.82");
    client.println("User-Agent: Naviband");
    client.println("Connection: close");
    client.println();
  } 
  else {
    Serial.println("connection failed"); //error message if no client connect
    Serial.println();
  }

  while(client.connected() && !client.available()) delay(1); //waits for data
  while (client.connected() || client.available()) { //connected or data available
    char c = client.read(); //gets byte from ethernet buffer
    result = result+c;
  } 

  client.stop(); //stop client
  result.replace('[', ' ');
  result.replace(']', ' ');
  Serial.println(result);
}

void sendData()
{
  String data = "123";

  if (client.connect(servername, 80)) {  //starts client connection, checks for connection
    client.println("GET /senddata?data=" + data);
    client.println("Host: 192.168.1.82");
    client.println("User-Agent: Naviband");
    client.println("Connection: close");
    client.println();
  } 
  else {
    Serial.println("connection failed"); //error message if no client connect
    Serial.println();
  }

  while(client.connected() && !client.available()) delay(1); //waits for data
  while (client.connected() || client.available()) { //connected or data available
    char c = client.read(); //gets byte from ethernet buffer
    result = result+c;
  } 

  client.stop(); //stop client
  result.replace('[', ' ');
  result.replace(']', ' ');
  Serial.println(result);
}
